'''
Created on May 3, 2017

@author: findj
'''
import socket, time, multiprocessing, Queue

class ClientSide(object):
    BUFF_SIZ = 1024

    def __init__(self):
        self.config = True

    def connectTo(self, host, port):
        self.CONN_PORT = port
        self.CONN_HOST = host
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.CONN_HOST, self.CONN_PORT))
        return self.sock

    # send data by flag so that the receiving side can handle different data types
    def sendData(self, flag):
        # length of the flag
        flag_length = len(flag)

        # send data according to different flags
        self.sock.send()

    def clientRun(self):
        while True:
            message = raw_input("Enter your message (type 'exit' to quit): ")
            # type exit to quit looping
            if message == "exit":
                break
            self.sock.send(message)
            response = self.sock.recv(self.BUFF_SIZ)
            # print out the received message
            print response

    def login_auth(self, user, pw):
        # set flag for data
        flag = 'LAUTH'
        # send username and password for user authentication
        self.sendData()


if __name__ == "__main__":
    host = 'localhost'
    port = 777
    cs = ClientSide()
    cs.connectTo(host, port)
    cs.clientRun()
        
        