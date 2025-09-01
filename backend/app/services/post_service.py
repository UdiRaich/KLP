import os
import datetime
from config import PATH_TO_DATA, xor

def generate_log_filename(time):
    #return file name based on time stamp
    dt = datetime.datetime.fromtimestamp(time, tz=datetime.timezone.utc)
    return dt.strftime("log_%Y-%m-%d_%H-%M-%S.txt")

def data_to_memo(data, machine_name):

    machine_folder = os.path.join(PATH_TO_DATA, machine_name)

    if not os.path.exists(machine_folder):
        os.makedirs(machine_folder)
    for batch in data:
        filename = generate_log_filename(batch[0])
        file_path = os.path.join(machine_folder, filename)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(str("".join(map(chr,map(xor.decode,batch[1]))))+"\n")
