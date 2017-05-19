
import socket, select, sys, random, multiprocessing

BUFF_SIZE = 1024
CONN_LIMIT = 5
DROP_RATE = 0.25
LISTEN_PORT = 777
FORWARD_HOST = 'localhost'
FORWARD_PORT = 888

def socketListen(port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind(('', port))
	sock.listen(CONN_LIMIT)
	sock.setblocking(0)
	print "Port " + str(port) + " open and listening."
	return sock

def relayTo(host, port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((host, port))
	return sock

def relayStart(relayTo, relayFrom):
	while True:
		dataToSend = relayFrom.recv(BUFF_SIZE)
		dataToRecv = relayTo.recv(BUFF_SIZE)

		# packet dropper
		if random.random() < DROP_RATE:
			print '---------- Dropped packet %s ----------' % count
			count += 1
			continue

		if dataToSend:
			relayTo.send(data)

		if dataToRecv:
			relayFrom.send(data)

		if not dataToSend:
			print "No more data, shutting down connection."
			relayFrom.close()
			break

def select_loop(listener, conn):
	inputs = [listener]
	outputs = []

	while inputs:
		readable, writable, exceptional = select.select(inputs, outputs, inputs)
		for so in readable:
			if so is server:
				connection, addr = so.accept()
				connection.setblocking(0)
				inputs.append(connection)

			else:
				data = so.recv()
				if data:
					outputs.append(conn)

		for so in writable:
			so.send(data)

		for ex in exceptional:
			print ex



def epollRegister(listener, ):
	ep = select.epoll()
	ep.register()

if __name__ == "__main__":
	relayTo = relayTo(FORWARD_HOST, FORWARD_PORT)
	listener = socketListen(LISTEN_PORT)

	while True:
		print "Waiting for connections."
		newCon, addr = listener.accept()
		print "New connection from " + str(addr) + " accepted."
		print "Creating new process."
		process = multiprocessing.Process(target=relayStart, args=(relayTo, newCon))
		process.start()
