from encryptions.xor import Xor
from utils.network_utils import get_mac_address
from writers.networkWriter import HttpWriter


CONFIG = {
    "destination": 'http://127.0.0.1:5000/update',
    "saving": HttpWriter,
    "save_interval_value": 1,
    "save_interval_unit": 'seconds',
    "container_interval_value": 1,
    "container_interval_units": 'seconds',
    "encryption": Xor,
    "key_encryption": 7,
    "machine_id": get_mac_address()
}
