'''
Created on May 3, 2017

@author: findj
'''
import socket, time, multiprocessing, Queue

CONN_PORT = 777
CONN_HOST = 'localhost'
BUFF_SIZ = 1024

def connect(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    return sock

def clientRun(conn):
    while True:
        message = raw_input("Enter your message (type 'exit' to quit): ")
        if message == "exit":
            break
        conn.send(message)
        response = conn.recv(BUFF_SIZ)
        print response
        
if __name__ == "__main__":
    conn = connect(CONN_HOST, CONN_PORT)
    clientRun(conn)
        
        