# epoll server

import select, socket, sys, errno

BUFSIZ = 1024
CONN_LIMIT = 5

class EpollServer(object):
    """ simple epoll server """

    def __init__(self, listenPort=8080, _f=self.default_f(), d_ip, d_port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('', listenPort))
        print 'Listening to port' , listenPort
        self.server.listen(CONN_LIMIT)
        self.server.setblocking(0)
        self.clients = {}

    def start(self):
        epoll = select.epoll()
        epoll.register(self.server.fileno(), select.EPOLLIN)

        try:
            connections = {}; requests = {}; responses = {}
            while True:
                events = epoll.poll(1)
                for fileno, event in events:
                    # if server receives new connection
                    if fileno == self.server.fileno():
                        try:
                            while True:
                                client, addr = self.server.accept()
                                # make it non-block
                                client.setblocking(0)
                                print "Got new connection from %s, using fd %d" % (addr, client.fileno())
                                # add new client to the epoll in
                                epoll.register(client.fileno(), select.EPOLLIN | select.EPOLLET)
                                self.clients[client.fileno()] = client
                        except socket.error:
                            pass
                    # process existing connections
                    # if channel has data to be read
                    elif event & select.EPOLLIN:
                        try:
                            while True:
                                data = self.clients[fileno].recv(BUFSIZ)
                                if not data:
                                    print "No more data, closing fd %s" % fileno
                                    epoll.unregister(fileno)
                                    self.clients[fileno].close()
                                data = _f(data)
                                sent = self.clients[fileno].send(data)

                            # epoll.modify(fileno, select.EPOLLOUT | select.EPOLLET)
                        except socket.error, e:
                            pass
                        # if data:
                        #     responses[client.fileno()] = data
                            # epoll.modify(fileno, select.EPOLLOUT | select.EPOLLET)
                            # print data

                    elif event & select.EPOLLOUT:
                        # print "echo back data ..."
                        try:
                            sent = self.clients[fileno].send(data)
                            print sent
                            # responses[fileno] = responses[fileno][sent:]

                        except socket.error:
                            pass

                        if len(responses[fileno] == 0):
                            # epoll.modify(fileno, select.EPOLLET)
                            self.clients[fileno].shutdown(socket.SHUT_RDWR)

                    elif event & select.EPOLLHUP:
                        epoll.unregister(fileno)
                        self.clients[fileno].close()
                        del self.clients[fileno]


        finally:
            epoll.unregister(self.server.fileno())
            epoll.close()
            self.server.close()

    def default_f(data):
        return data

if __name__ == "__main__":
    EpollServer().start()
