from encryptions.base import Encryption


class Xor(Encryption):
    def __init__(self, key):
        super().__init__(key)

    def encode(self, byte):
        return byte ^ self._key
