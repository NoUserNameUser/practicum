'''
Created on May 3, 2017

@author: findj
'''
import socket, signal, sys
import select
from communication import send, receive, passphrase_gen
from pymongo import MongoClient
import datetime

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
        self.usertable = self.db['users']
        self.grouptable = self.db['share_groups']

    def sighandler(self, signum, frame):
        # Close the server
        print 'Shutting down server...'
        # Close existing client sockets
        for o in self.outputs:
            o.close()

        self.server.close()

    def getuid(self, client):
        # Return the printable name of the
        # client, given its socket...
        info = self.clientmap[client]
        host, uid = info[0][0], str(info[1])
        return uid

    def gethost(self, client):
        # Return the printable name of the
        # client, given its socket...
        info = self.clientmap[client]
        host, uid = info[0][0], str(info[1])
        return host

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
                            uid = self.getuid(s)
                            # switch for different flags in data
                            options = {
                                'FINFO': self.file_info,
                                'FCONTENT': self.file_receive,
                                'NEWGROUP': self.create_group,
                            }
                            # handle different data
                            if ':' in data:
                                flag = data.split(':')[0]
                                # make sure flag is in options list
                                if options.has_key(flag):
                                    data = data.split(flag+':')[1]
                                    options[flag](s, data, uid)
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
                            msg = '\n(Hung up: Client from %s)' % self.gethost(s)
                            for o in self.outputs:
                                # o.send(msg)
                                send(o, msg)

                    except socket.error, e:
                        # Remove
                        inputs.remove(s)
                        self.outputs.remove(s)

        self.server.close()

    def authentication(self, conn, addr):
        # receive client info in correct form
        # try:
        input = receive(conn)
        if input:
            try:
                uname = input.split("LAUTH:")[1]
            except:
                print "data received without flag"
                return False

            ip = addr[0]

            result = self.usertable.find({'username':uname, 'ipaddr':ip})
            res_count = result.count()

            if res_count == 0:
                print "new user added"
                user = {
                    'username': uname,
                    'ipaddr': ip,
                    'share_groups': [],
                    'created': self.utc_time(),
                }
                uid = self.usertable.insert(user)
                send(conn, user)
            else:
                print "user exists"
                uid = result[0]['_id']
                send(conn, result[0])

            return uid

        else:
            print "%s connection has lost" % (addr[0])
            conn.close()
            return False
        # except:
        #     conn.close()
        #     return False


    def file_info(self, conn, data, uid):
        print data.split(',')

    def file_receive(self, conn, data, uid):
        # need a file buffer
        print data

    def create_group(self, conn, data, uid):
        if data:
            new_group = {
                'owner': uid,
                'members': [],
                'files':[],
                'share_phrase':[],
                'created':self.utc_time()
            }
            # insert new group data
            sgid = self.grouptable.insert(new_group)

            # update user data
            self.usertable.update({'_id': uid}, {'share_groups':[sgid]})

            # send back share phrase
            send(conn, "NEWGROUP:SUCCESS")

    def share_phrase_gen(self, gid): # takes group id and generate a share phrase
        # generate one-time share phrase
        share_phrase = passphrase_gen(6)
        self.grouptable.find_one_and_update({'_id':gid}, {'$push':{'share_groups': share_phrase}})



    def utc_time(self):
        return datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")


if __name__ == "__main__":
    ss = ServerSide(8888).serve()