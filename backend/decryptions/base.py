from abc import ABC, abstractmethod


class Decryption(ABC):
    def __init__(self, key):
        self._key = key

    @abstractmethod
    def decode(self, char):
        pass
