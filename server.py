'''
Created on May 3, 2017

@author: findj
'''
import socket, multiprocessing, time, signal, sys
import select
from communication import send, receive

class ServerSide(object):
    CONN_LIMIT = 5
    BUFF_SIZ = 1024

    def __init__(self, port):
        self.clients = 0
        # Client map
        self.clientmap = {}
        # Output socket list
        self.outputs = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('', port))
        print 'Listening to port', port, '...'
        self.server.listen(self.CONN_LIMIT)
        # Trap keyboard interrupts
        signal.signal(signal.SIGINT, self.sighandler)

    def sighandler(self, signum, frame):
        # Close the server
        print 'Shutting down server...'
        # Close existing client sockets
        for o in self.outputs:
            o.close()

        self.server.close()

    def getname(self, client):

        # Return the printable name of the
        # client, given its socket...
        info = self.clientmap[client]
        host, name = info[0][0], str(info[1])
        return '@'.join((name, host))

    def serve(self):

        inputs = [self.server]
        self.outputs = []

        running = 1

        while running:
            try:
                readable, writable, exceptional = select.select(inputs, self.outputs, inputs)
            except select.error, e:
                print e.args, e.message
                break

            for s in readable:

                if s == self.server:
                    print 'Waiting for connections.'
                    # handle the server socket
                    client, address = self.server.accept()
                    print 'ServerSide: got connection %d from %s' % (client.fileno(), address)

                    # Read the login name
                    # cname = receive(client).split('NAME: ')[1]

                    # first step authentication
                    cid = self.authentication(client)

                    # Compute client name and send back
                    self.clients += 1
                    send(client, 'CLIENT: ' + str(address[0]))
                    inputs.append(client)

                    self.clientmap[client] = (address, cid)

                    # Send joining information to other clients
                    # msg = '\n(Connected: New client (%d) from %s)' % (self.clients, self.getname(client))
                    # for o in self.outputs:
                    #     # o.send(msg)
                    #     send(o, msg)

                    self.outputs.append(client)

                # elif s == sys.stdin:
                #     # handle standard input
                #     junk = sys.stdin.readline()
                #     running = 0

                else:
                    # handle all other sockets
                    try:
                        # data = s.recv(BUFSIZ)
                        data = receive(s)
                        if data:
                            # switch for different flags in data
                            options = {
                                'finfo': self.file_info,
                                'fcontent': self.file_receive,
                            }
                            # handle different data
                            if ':' in data:
                                flag = data.split(':')[0]
                                # make sure flag is in options list
                                if options.has_key(flag):
                                    data = data.split(flag+':')[1]
                                    options[flag](data)
                                else:
                                    msg = 'Invalid flag'
                                    send(s, msg)
                            else:
                                msg = 'Handling data without a flag'
                                print msg
                                send(s, msg)
                        else:
                            print '%d hung up' % s.fileno()
                            self.clients -= 1
                            s.close()
                            inputs.remove(s)
                            self.outputs.remove(s)

                            # Send client leaving information to others
                            msg = '\n(Hung up: Client from %s)' % self.getname(s)
                            for o in self.outputs:
                                # o.send(msg)
                                send(o, msg)

                    except socket.error, e:
                        # Remove
                        inputs.remove(s)
                        self.outputs.remove(s)

        self.server.close()

    def authentication(self, conn):
        # receive client info in correct form
        cinfo = receive(conn).split('\\')
        # get cid based on client info
        cid = 18283444
        print cinfo[:]
        return cid

    def file_info(self, data):
        print data.split('\\')

    def file_receive(self, data):
        # need a file buffer
        print data


    # def recv_data(conn, addr):
    #     # need a while loop for receiving data
    #     while True:
    #         data = conn.recv(BUFF_SIZ)
    #         if data:
    #             data_process(conn, data)
    #         else:
    #                 conn.close()
    #                 print str(addr[0]), "disconnected"
    #                 break
    #
    # # this function is for data processing and sending responses
    # def data_process(conn, data):
    #     print data
    #     conn.send("received")
    #
    # def main_loop(sock):
    #     while True:
    #         print "ready for new connection"
    #         conn, addr = sock.accept()
    #         print "%s connected from port %s" % (str(addr[0]), str(addr[1]))
    #
    #         recv_data(conn, addr)

if __name__ == "__main__":
    ss = ServerSide(8888).serve()