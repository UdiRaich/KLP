from abc import ABC, abstractmethod


class IWriter(ABC):
    def __init__(self, destination: str):
        self._destination = destination

        
    @abstractmethod
    def send_data(self, data, machine_name: str) -> None:
        pass
