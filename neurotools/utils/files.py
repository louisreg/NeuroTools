
import os

def list_files_in_dir(dir:str, extension: str) -> list:
    filenames = os.listdir(dir)
    return [os.path.join(dir, filename) for filename in filenames if filename.endswith(extension)]


def list_files_in_subdir(dir:str, extension: str) -> list:
    files_l = []
    for path, _, files in os.walk(dir):
        for name in files:
            if name.endswith(extension):
                files_l.append(os.path.join(path, name))
    return(files_l)
