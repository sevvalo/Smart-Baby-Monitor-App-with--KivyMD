from jnius import autoclass
import threading
import socket
import time
import numpy as np

# Load required Java classes


class Sender:
    def __init__(self, channels=1, bit_depth=16):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "electronpi"
        self.port = 8443
        self.sample_rate = 16000
        self.channels = channels
        self.bit_depth = bit_depth
        self.AudioRecord = autoclass('android.media.AudioRecord')
        self.AudioFormat = autoclass('android.media.AudioFormat')
        self.AudioSource = autoclass('android.media.MediaRecorder$AudioSource')

        self.is_recording = False

        # Determine channel configuration
        if self.channels == 1:
            self.channel_in = self.AudioFormat.CHANNEL_IN_MONO
        elif self.channels == 2:
            self.channel_in = self.AudioFormat.CHANNEL_IN_STEREO
        else:
            raise ValueError("Unsupported number of channels")

        # Determine encoding format
        if self.bit_depth == 16:
            self.encoding = self.AudioFormat.ENCODING_PCM_16BIT
        else:
            raise ValueError("Unsupported bit depth")

        # Get minimum buffer size
        self.min_buffer_size = 1024
        
        # Initialize AudioRecord
        self.audio_record = self.AudioRecord(
            self.AudioSource.MIC,
            self.sample_rate,
            self.channel_in,
            self.encoding,
            self.min_buffer_size
        )

    def start_recording(self):
        self.is_recording = True
        try:
            talk_thread = threading.Thread(target=self.record)
            talk_thread.daemon =True
            talk_thread.start()

        except Exception as e:
            print(f"Error in client: {e}")    

    def stop_recording(self):
        self.is_recording = False
        self.audio_record.stop()
        self.audio_record.release()
        self.client_socket.close()
        print("Closing connections.")
        

    def record(self):
        time.sleep(1)
        self.audio_record.startRecording()
        
        self.client_socket.connect((self.host, self.port))
        while self.is_recording:
            buffer = np.zeros(self.min_buffer_size, dtype=np.int16)
            self.audio_record.read(buffer, 0, self.min_buffer_size)
            self.client_socket.sendall(buffer.tobytes())

