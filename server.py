'''
Created on May 3, 2017

@author: findj
'''
import socket, signal, os
import select
from communication import send, receive, passphrase_gen
from pymongo import MongoClient
from bson import ObjectId
import datetime

class ServerSide(object):
    CONN_LIMIT = 5
    BUFF_SIZ = 1024

    def __init__(self, port):
        self.clients = 0
        self.authenticated = 0
        # Client map
        self.clientmap = {}
        # file map
        self.files = {}
        self.sending = {}
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
        self.phrasetable = self.db['share_phrases']
        self.filestable = self.db['files']

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
        return info[1]

    def gethost(self, client):
        # Return the printable name of the
        # client, given its socket...
        info = self.clientmap[client]
        return info[0][0]

    def getport(self, client):
        # Return the printable name of the
        # client, given its socket...
        info = self.clientmap[client]
        return info[0][1]

    def gethost_port(self, client):
        # Return the printable name of the
        # client, given its socket...
        info = self.clientmap[client]
        return info[0]

    def serve(self):

        self.inputs = [self.server]
        self.outputs = []

        running = 1

        while running:
            try:
                readable, writable, exceptional = select.select(self.inputs, self.outputs, [])
            except select.error:
                print 'socket error'

            for s in readable:

                if s == self.server:
                    # handle the server socket
                    client, address = self.server.accept()
                    print 'ServerSide: got connection %d from %s:%d' % (client.fileno(), address[0], address[1])

                    # first step authentication
                    # cid = self.authentication(client, address)

                    # if authentication failed, keep moving on
                    # if not cid:
                    #     continue

                    # Compute client name and send back
                    self.clients += 1

                    self.inputs.append(client)
                    self.clientmap[client] = (address, False)

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
                            if uid:
                                # switch for different flags in data
                                options = {
                                    'GETUSERINFO': self.get_user_info,
                                    'FINFO': self.file_info,
                                    'FDATA': self.file_receive,
                                    'NEWGROUP': self.create_group,
                                    'GETGROUPS': self.get_group_info,
                                    'JOINGROUP': self.join_group,
                                    'LOGOUT': self.logout,
                                    'FSTRT': self.file_open,
                                    'FFN': self.file_close,
                                    'FDOWNLOAD': self.file_to_client,
                                    'MKPHRASE': self.make_phrase,
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
                                self.authentication(s, data, self.clientmap[s][0])
                        else:
                            print '%s hung up' % self.gethost(s)
                            # remove
                            self.sock_close(s)

                            # Send client leaving information to others
                            # msg = '\n(Hung up: Client from %s)' % self.gethost(s)
                            # for o in self.outputs:
                            #     send(o, msg)

                    except socket.error, e:
                        # Remove
                        self.sock_close(s)

        self.server.close()

    def authentication(self, conn, data, addr):
        # receive client info in correct form
        # try:
        if data:
            try:
                uname = data.split("LAUTH:")[1]
            except:
                print "incorrect authentication"
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
            else:
                print "user exists"
                user = result[0]
                uid = result[0]['_id']

            self.clientmap[conn] = (addr, uid) #map uid to corresponding client
            send(conn, user)
            self.login(uid)

            return uid

        else:
            print "%s connection has lost" % (addr[0])
            self.sock_close(conn)
        # except:
        #     conn.close()
        #     return False

    def sock_close(self, sock):
        self.clients -= 1
        sock.close()
        try:
            # sometimes if the socket is not in the list, error will raise
            self.inputs.remove(sock)
            self.outputs.remove(sock)
        except:
            # we can just ignore the error since socket closes anyway
            pass

    # set user login
    def login(self, uid):
        self.usertable.update_one({'_id': uid}, {'$set': {'login': {'online': True, 'last_login':self.utc_time()}}})

    # set user logout
    def logout(self, conn, data, uid):
        result = self.usertable.update_one({'_id': uid}, {'$set': {'login': {'online': False, 'last_logout': self.utc_time()}}})
        if result:
            print '%s:%d hung up' % self.gethost_port(conn)
            send(conn, True)
            # remove
            self.sock_close(conn)
        else:
            send(conn, False)

    def get_user_info(self, conn, data, uid):
        print "get user info function called"
        if data: # uid, need to cast
            result = self.usertable.find_one({'_id': ObjectId(data)})
            print result
            send(conn, result)

    def file_info(self, conn, data, uid):
        if data:
            finfo = data.split('\\')
            if conn not in self.files:
                self.files[conn] = {}
            self.files[conn]['file_name'] = finfo[0]
            self.files[conn]['md5'] = finfo[1]
            self.files[conn]['gid'] = ObjectId(finfo[2])
            file = {
                'md5': self.files[conn]['md5'],
                'file_name': self.files[conn]['file_name'],
                'related_group': self.files[conn]['gid'],
                'created': self.utc_time()
            }
            fid = self.filestable.insert(file)
            file = {}
            file['f_id'] = fid
            file['file_name'] = self.files[conn]['file_name']
            self.grouptable.update_one({'_id': self.files[conn]['gid']}, {'$push': {'files': file}})

            # self.file_name = finfo[0]
            # self.file_md5 = finfo[1]

    def file_receive(self, conn, data, uid):
        # need a file buffer
        # print
        self.files[conn]['fd'].write(data)

    def file_open(self, conn, data, uid):
        if not data:
            print 'in file_open if data'
            directory = "files/"
            if not os.path.exists(directory):
                os.makedirs(directory)
            path = directory + self.files[conn]['file_name'] + '_' + self.files[conn]['md5']
            self.fdescriptor = open(path, 'wb')
            print self.fdescriptor
            self.files[conn]['fd'] = self.fdescriptor


    def file_close(self, conn, data, uid):
        if not data:
            print 'close file ' + self.files[conn]['file_name']
            self.files[conn]['fd'].close()
            del self.files[conn]

    def file_to_client(self, conn, data, uid):
        if data:
            fid = data
            if uid not in self.sending:
                self.sending[uid] = {}

            if fid in self.sending[uid]: # if fd in sending list
                fd = self.sending[uid][fid]
            else:
                file = self.filestable.find_one({'_id':ObjectId(fid)})
                fpath = "files/" + file['file_name'] + '_' + file['md5']
                fd = open(fpath, 'rb')
                self.sending[uid][fid] = fd
            data = fd.read(self.BUFF_SIZ)
            if data != '':
                send(conn, data)
            else:
                send(conn, 'FDONE:')


    def create_group(self, conn, data, uid):
        if data: # group name, no cast
            # TODO check if the group name exists


            new_group = {
                'owner': uid,
                'name': data,
                'members': [],
                'files':[],
                'share_phrases':[],
                'created':self.utc_time()
            }
            # insert new group data
            sgid = self.grouptable.insert(new_group)
            print "sgid", sgid
            # update user data
            result = self.usertable.update_one({'_id': uid}, {'$push':{'share_groups':ObjectId(sgid)}})
            # send back share phrase
            send(conn, "NEWGROUP:SUCCESS")

    def join_group(self, conn, data, uid):
        if data: # passphrase,
            result = self.phrasetable.find_one({'phrase':str(data)})
            if result:
                gid = result['group']
            else:
                send(conn, 'UNKNOW')
                return False
            result = self.usertable.find({'_id':uid, 'share_groups':{'$in': [ObjectId(gid)]}})
            if result.count() == 0: # user not joined the group yet
                self.usertable.update_one({'_id': uid}, {'$push':{'share_groups':ObjectId(gid)}}) # make user in the group
                self.phrasetable.remove({'phrase':data}) # remove sharephrase in table
                send(conn, 'SUCCESS')
            else:
                send(conn, 'EXISTS')

    def share_phrase_gen(self, gid): # takes group id and generate a share phrase
        share_phrase = passphrase_gen(6)  # generate one-time share phrase
        result = self.phrasetable.find({'phrase': share_phrase})
        if result.count() == 0:
            phrase = {
                'phrase': share_phrase,
                'group': gid,
                'created': self.utc_time(),
            }
            phrase_id = self.phrasetable.insert(phrase)
            self.grouptable.update_one({'_id':gid}, {'$push':{'share_phrases': phrase_id}})
            return phrase
        else:
            self.share_phrase_gen(gid)

    def get_group_info(self, conn, data, uid):
        if data: # gid, cast
            result = self.grouptable.find_one({'_id': ObjectId(data)}) # need to be careful with data types
            send(conn, result)

    def make_phrase(self, conn, data, uid):
        if data:
            # do something
            phrase = self.share_phrase_gen(data)
            send(conn, phrase)
        return

    def utc_time(self):
        return datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")


if __name__ == "__main__":
    ss = ServerSide(8888).serve()