from decryptions.base import Decryption


class Xor(Decryption):
    def __init__(self, key):
        super().__init__(key)

    def decode(self, byte):
        return byte ^ self._key
