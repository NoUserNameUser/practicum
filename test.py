'''
Created on May 3, 2017

@author: findj
'''
import Tkinter as tk
import sys

import select
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)

# Bind the socket to the port
server_address = ('localhost', 10000)
print >>sys.stderr, 'starting up on %s port %s' % server_address
server.bind(server_address)

# Listen for incoming connections
server.listen(5)

# Sockets from which we expect to read
inputs = [ server ]

# Sockets to which we expect to write
outputs = [ ]

while inputs:
    readable, writable, exceptional = select.select(inputs, outputs, inputs)

    for s in readable:

        if s == server:
            # handle the server socket
            client, address = server.accept()
            print 'ServerSide: got connection %d from %s' % (client.fileno(), address)
            inputs.append(client)

# from scapy.all import *
# from scapy.arch.windows import compatibility
# from scapy.all import log_runtime, MTU, ETH_P_ALL, PcapTimeoutElapsed, plist
#
# def callback(pkt):
#     print pkt
#
# compatibility.log_runtime = log_runtime
# compatibility.MTU = MTU
# compatibility.PcapTimeoutElapsed = PcapTimeoutElapsed
# compatibility.ETH_P_ALL = ETH_P_ALL
# compatibility.plist = plist
#
# compatibility.sniff(filter="tcp and port 888", prn=callback) # call the sniff function however you like


# pack = IP(src='192.168.1.1')/TCP()
# pack.show()