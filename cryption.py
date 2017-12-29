from Crypto import Random
from Crypto.Cipher import AES
import os
import binascii


class Cryption:
    def __init__(self):
        self.iv = Random.new().read(AES.block_size)

    def cipher_gen(self, key):
        self.cipher = AES.new(key, AES.MODE_CBC, self.iv)

    def encrypt(self, raw):
        return self.cipher.encrypt(raw)

    def decrypt(self, encrypted):
        return self.cipher.decrypt(encrypted)


def keygen():
    return os.urandom(16)


if __name__ == "__main__":
    print binascii.hexlify(keygen())