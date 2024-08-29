from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from jnius import autoclass
import socket
import threading
import time

AUDIO_FORMAT = 2  # Corresponds to Android's AudioFormat.ENCODING_PCM_16BIT
CHANNEL_CONFIG = 4  # Corresponds to AudioFormat.CHANNEL_OUT_MONO
SAMPLERATE = 16000
CHUNK = 1024

class Receiver:

    def __init__(self, ):
        time.sleep(1)
        
        self.control = 1
        self.CHANNELS = 1
        self.RATE = 16000
        self.BUFFER_SIZE = 1024
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.HOST = "electronpi"  # "DESKTOP-2URLQHL"  # '192.168.211.197'  # "electronpi"   # Use '0.0.0.0' to accept connections from any interface
        self.PORT = 8543
        self.AudioTrack = autoclass('android.media.AudioTrack')
        self.AudioManager = autoclass('android.media.AudioManager')
        self.stream_type = self.AudioManager.STREAM_MUSIC
        self.min_buffer_size = 1024
        self.audio_track = self.AudioTrack(self.stream_type, SAMPLERATE, CHANNEL_CONFIG, AUDIO_FORMAT, self.min_buffer_size, self.AudioTrack.MODE_STREAM)
        self.audio_track.play()

        try:
            # Create a socket

            self.client_socket.connect((self.HOST, self.PORT))
            print(f'Connected to {self.HOST} and {self.PORT}')
            print("Connected to Listen")
            
        except Exception as e:
            print(f"Error in client: {e}")

    def listen(self):
        self.control = 1

        try:
            talk_thread = threading.Thread(target=self.recv)
            talk_thread.daemon = True  # Daemonize the thread so it exits when the main app exits
            talk_thread.start()

        except Exception as e:
            print(f"Error in client: {e}")

    def close(self):
        self.control = 0
        # Clean up
        self.audio_track.stop()
        self.audio_track.release()
        #self.client_socket.close()
        print("Closing connections.")


    def recv(self):
        
        time.sleep(1)
        

        try:
            while self.control:
                # Read audio data from the stream
                outdata = self.client_socket.recv(self.BUFFER_SIZE)
                self.audio_track.write(outdata,0,len(outdata))
        except Exception as e:
            print(f"Error in client: {e}")
        #finally:
            