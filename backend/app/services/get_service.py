from pathlib import Path
import os
from config import PATH_TO_DATA


def get_machines_name():
    path = Path(PATH_TO_DATA)
    folders = [p.name for p in path.iterdir() if p.is_dir()]
    return folders

def get_machine_data(machine_name):

    folder_path = os.path.join(PATH_TO_DATA, machine_name)

    if not os.path.isdir(folder_path):
        raise FileNotFoundError(f"The machines doesn't exist in the data")

    result = []

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            result.append([filename, content])
    return result

