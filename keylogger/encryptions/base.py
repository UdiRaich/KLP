from abc import ABC, abstractmethod


class Encryption(ABC):
    def __init__(self, key):
        self._key = key

    @abstractmethod
    def encode(self, char):
        pass
