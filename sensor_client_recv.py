import socket
import time
import threading

class Data:

    def __init__(self):

        self.control = 1

        self.HOST ="electronpi"
        self.PORT = 8643
        self.BUFFER_SIZE = 1024

        self.temp = ""
        self.mov = 0
        self.sleeping = 0

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:

            self.client_socket.connect((self.HOST, self.PORT))
            print("Connected Sensor")

        except Exception as e:
            print(e)

    def take_data(self):

        try:
            talk_thread = threading.Thread(target=self.recv2)
            talk_thread.daemon = True  # Daemonize the thread so it exits when the main app exits
            talk_thread.start()    
            
        except Exception as e:
            print(e)
    
    def recv2(self):
        while self.control:
            time.sleep(1)
            data_ = self.client_socket.recv(self.BUFFER_SIZE).decode()
            try:
                fl_data = data_.split(";")
                self.temp = fl_data[0]
                self.mov = int(fl_data[1])
                self.sleeping = float(fl_data[2])

            except Exception as e:
                print(e)
        
    