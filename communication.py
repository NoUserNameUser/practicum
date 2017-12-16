import cPickle
import socket
import struct
import random


marshall = cPickle.dumps
unmarshall = cPickle.loads


def send(channel, *args):
    buf = marshall(args)
    value = socket.htonl(len(buf))
    size = struct.pack("L", value)
    channel.send(size)
    channel.send(buf)


def receive(channel):
    size = struct.calcsize("L")
    size = channel.recv(size)
    try:
        size = socket.ntohl(struct.unpack("L", size)[0])
    except struct.error, e:
        print e
        return ''

    buf = ""

    while len(buf) < size:
        buf += channel.recv(size - len(buf))

    return unmarshall(buf)[0]

def encrypt(message):
    return message

def decrypt(message):
    return message

def passphrase_gen(length):
    items = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    phrase = ""
    for i in range(length):
        phrase += random.choice(items)
    return phrase