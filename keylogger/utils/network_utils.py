import uuid

def get_mac_address():
    mac_int = uuid.getnode()
    mac_str = ':'.join(f'{(mac_int >> i) & 0xff:02x}' for i in range(40, -1, -8))
    return mac_str