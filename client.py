'''
Created on May 3, 2017

@author: findj
'''
import socket, os, hashlib
from communication import send, receive

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
    def sendData(self, flag, data):
        # length of the flag
        flag_length = len(flag)
        send(self.sock, flag, data)
        # send data according to different flags
        # self.sock.send()

    # This is the main run function of the client
    def clientRun(self):

        input = raw_input("Enter a username: ")
        # first thing first
        self.login_auth(input)
        while True:
            input = raw_input("Message (type 'exit' to quit): ")
            # type exit to quit looping
            if input == "exit":
                break
            elif input == "ftrans":
                path = raw_input("enter file path: ")
                self.file_transfer(path)
            else:
                send(self.sock, input)
                response = receive(self.sock)
            # print out the received message
                print response


    def login_auth(self, username):
        # set flag for data
        message = username
        # send username and password for user authentication
        send(self.sock, message)
        response = receive(self.sock)
        print response

    def file_transfer(self, file_path):
        # output = open('copy.txt', 'wb')
        fname = os.path.basename(file_path)
        data = 'finfo:' + fname + '\\' + self.md5Gen(file_path)
        send(self.sock, data)

        # with open(file_path, 'rb') as f:
        #     for line in f:
        #         data = 'file:' + line
        #         send(self.sock, data)
                # output.write(line)
        # output.close()

    def md5Gen(self, file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for line in f:
                hash_md5.update(line)

        return hash_md5.hexdigest()



if __name__ == "__main__":
    host = 'localhost'
    port = 8888
    cs = ClientSide()
    cs.connectTo(host, port)
    cs.clientRun()

    # cs.file_transfer("epoll.py")
    # cs.file_transfer("C:\Users\/findj\Desktop\Fortinet_Technical_Test_Web.doc")
        
        