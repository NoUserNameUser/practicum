'''
Created on May 3, 2017

@author: findj
'''
import socket, os, hashlib
from communication import send, receive

class ClientSide(object):
    BUFF_SIZ = 1024

    def __init__(self):

        self.CONNECTION = {
            'host' : "localhost",
            'port' : 8888
        }

        self.user = {} # dictionary to hold user info

        self.groups = [] # array to hold share groups info


    def connectTo(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.CONNECTION['host'], self.CONNECTION['port']))
        return self.sock

    def disconnect(self):
        self.sock.close()

    # send data by flag so that the receiving side can handle different data types
    def sendData(self, flag, data):
        flag_length = len(flag) # length of the flag
        send(self.sock, flag, data)
        # send data according to different flags
        # self.sock.send()

    # This is the main run function of the client
    def clientRun(self):

        input = raw_input("Enter a username: ")

        self.login_auth(input) # first thing first
        while True:
            input = raw_input("Message (type 'exit' to quit): ")

            if input == "exit": # type exit to quit looping
                break
            elif input == "ftrans":
                path = raw_input("enter file path: ")
                self.file_transfer(path)
            else:
                send(self.sock, input)
                response = receive(self.sock)
                print response # print out the received message

    def mainloop(self):
        return

    # function to authenticate users
    def login_auth(self, username):
        send(self.sock, "LAUTH:" + username) # send username and password for user authentication
        response = receive(self.sock)
        if response: # True for good response and False for bad ones
            self.user = response
            self.get_groups()
            return True
        else:
            print "AUTHENTICATION_ERROR:No server response"
            return False

    def logout(self):
        send(self.sock, "LOGOUT:")
        response = receive(self.sock)
        if response:
            self.disconnect()
            self.connectTo()
            return True
        return False

    def create_share_group(self, gname):
        print "sending create_share_group request"
        send(self.sock, "NEWGROUP:"+gname)
        sp = receive(self.sock)
        if sp == "NEWGROUP:SUCCESS":
            # update self.groups
            self.get_groups()
        return sp

    def join_share_group(self, sharephrase):
        print "sending join_share_group request"
        send(self.sock, "JOINGROUP:"+sharephrase)
        group_info = receive(self.sock)
        return group_info

    def user_update(self):
        send(self.sock, "GETUSERINFO:"+str(self.user['_id']))
        result = receive(self.sock)
        if result:
            self.user = result

    # function to get groups info and push the results into self.groups array
    def get_groups(self):
        # update user first
        self.user_update()
        self.groups = [] # reload groups
        # pull all the group info for user
        if len(self.user['share_groups']) != 0: # checking if the user has any groups
            for sg in self.user['share_groups']: # iterate through the groups
                send(self.sock, "GETGROUPS:"+str(sg)) # send request of each group id to get details info
                result = receive(self.sock) # receive response
                if result: # if the response is not 'no result' flag
                    self.groups.append(result) # append result to the groups array
                else:
                    print "unexpected error when requesting group info"
        else:
            print "User has no groups yet"

        return self.groups

    def file_transfer(self, file_path):
        # output = open('copy.txt', 'wb')
        fname = os.path.basename(file_path)
        # TODO: do encryption
        data = 'FINFO:' + fname + '\\' + self.md5Gen(file_path)
        send(self.sock, data)

        with open(file_path, 'rb') as f:
            send('FSTRT:')
            for line in f:
                data = 'FDATA:' + line
                send(self.sock, data)
            send('FFN:')

    def md5Gen(self, file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for line in f:
                hash_md5.update(line)

        return hash_md5.hexdigest()

    def is_group_owner(self, gid):
        if(self.user['_id'] == gid):
            return True
        return False



if __name__ == "__main__":
    cs = ClientSide()
    cs.connectTo()
    cs.clientRun()

    # cs.file_transfer("epoll.py")
    # cs.file_transfer("C:\Users\/findj\Desktop\Fortinet_Technical_Test_Web.doc")
        
        