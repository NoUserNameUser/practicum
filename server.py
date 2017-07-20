'''
Created on May 3, 2017

@author: findj
'''
import socket, signal, sys
import select
from communication import send, receive
from pymongo import MongoClient

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

        self.db_client = MongoClient('localhost', 27017)
        self.db = self.db_client['FiSher']

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
                readable, writable, exceptional = select.select(inputs, self.outputs, [])
            except select.error:
                print 'socket error'

            for s in readable:

                if s == self.server:
                    # handle the server socket
                    client, address = self.server.accept()
                    print 'ServerSide: got connection %d from %s' % (client.fileno(), address)

                    # first step authentication
                    cid = self.authentication(client, address)

                    # if authentication failed, keep moving on
                    if not cid:
                        continue

                    # Compute client name and send back
                    self.clients += 1
                    inputs.append(client)
                    self.clientmap[client] = (address, cid)

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

    def authentication(self, conn, addr):
        usertable = self.db['users']
        # receive client info in correct form
        # try:
        input = receive(conn)
        if input:
            print input
            ip = addr[0]
            user = {
                'username': input,
                'ipaddr': ip
            }
            result = usertable.find(user)
            res_count = result.count()
            msg = "LAUTH:SUCCESS\\"
            if res_count == 0:
                uid = usertable.insert(user)
                print uid
                print user
                print "user added"
                send(conn, msg+str(user))
            else:
                print "user exists"
                uid = result[0]['_id']
                print uid
                print result[0]
                send(conn, msg+str(result[0]))

            return uid

        else:
            conn.close()
            return False
        # except:
        #     conn.close()
        #     return False


    def file_info(self, data):
        print data.split(',')

    def file_receive(self, data):
        # need a file buffer
        print data


if __name__ == "__main__":
    ss = ServerSide(8888).serve()