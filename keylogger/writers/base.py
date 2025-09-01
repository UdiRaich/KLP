from abc import ABC, abstractmethod


class IWriter(ABC):
    def __init__(self, destination: str, machine_id: int) -> None:
        self._destination = destination
        self._machine_id = machine_id

        
    @abstractmethod
    def send_data(self, data) -> None:
        pass
