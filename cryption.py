from Crypto import Random
from Crypto.Cipher import AES
import os
import binascii


def encrypt(raw):
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(self.key, AES.MODE_CBC, iv)
    return cipher.encrypt(raw)


def keygen():
    return os.urandom(16)


if __name__ == "__main__":
    print binascii.hexlify(keygen())