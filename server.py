'''
Created on May 3, 2017

@author: findj
'''
import socket, multiprocessing, time

CONN_LIMIT = 5
LISTEN_PORT = 777
BUFF_SIZ = 1024

def listen(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', port))
    sock.listen(CONN_LIMIT)
    return sock

def recv_data(conn, addr):
    # need a while loop for receiving data
    while True:
        data = conn.recv(BUFF_SIZ)
        if data:
            data_process(conn, data)
        else:
                conn.close()
                print str(addr[0]), "disconnected"
                break

# this function is for data processing and sending responses
def data_process(conn, data):
    print data
    conn.send("received")

def main_loop(sock):
    while True:
        print "ready for new connection"
        conn, addr = sock.accept()
        print "%s connected from port %s" % (str(addr[0]), str(addr[1]))
        
        recv_data(conn, addr)

if __name__ == "__main__":
    main_loop(listen(LISTEN_PORT))