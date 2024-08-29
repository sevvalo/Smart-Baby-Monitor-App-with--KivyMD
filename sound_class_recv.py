import socket
import time
import threading


class Sound_class:

    def __init__(self):
        time.sleep(3)
        self.control = 1

        self.HOST ="electronpi"
        self.PORT = 8775
        self.BUFFER_SIZE = 1024
        self.sound = ""
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        
        try:
            self.client_socket.connect((self.HOST, self.PORT))
            print("Connected Sound Classification")

        except Exception as e:
            print(e)

    def take_class(self):

        try:
            talk_thread = threading.Thread(target=self.recv_class)
            talk_thread.daemon = True  # Daemonize the thread so it exits when the main app exits
            talk_thread.start()    
            
        except Exception as e:
            print(e)
    
    def recv_class(self):
        while self.control:
            time.sleep(3)
            data_ = self.client_socket.recv(self.BUFFER_SIZE).decode()
            try:
                fl_data = data_
                self.sound = int(fl_data)

            except Exception as e:
                print(e)
        
    