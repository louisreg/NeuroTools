from json import loads as json_load
from ast import literal_eval
from subprocess import Popen, PIPE
import os

class ns5_py2_Exception(Exception):
    def __init__(self, message):            
        super().__init__(message)


def __stdout_2_dict(stdout: str) -> dict:
    '''
    Convert a litteral dict to a dict
    '''
    out = stdout.replace("\'", "\"")
    return(json_load(out))

def __stdout_2_list(stdout: str) -> list:
    '''
    Convert a litteral list to a list
    '''
    return(literal_eval(stdout))

def get_file_info(filepath: str) -> dict:
    '''
    Return file info in a dict object
    '''
    stdout = call_ns5_py2(filepath,"get_file_info")
    return(__stdout_2_dict(stdout))

def get_analog_label_entities(filepath: str) -> list:
    '''
    Return file analog label entities in a list
    '''
    stdout = call_ns5_py2(filepath,"get_analog_labels")
    return(__stdout_2_list(stdout))

def call_ns5_py2(path, cmd='') -> str:
    '''
    call the ns5_py2.py script with a specified file path and cmd
    '''
    py2_file = os.path.dirname(__file__)+'/ns5_py2.py'
    process = Popen([f"python2  {py2_file} {path} {cmd}"], stdout=PIPE, stderr=PIPE, shell=True, stdin=None)
    stdout, stderr = process.communicate()
    if (process.returncode):
        err = stderr.decode()
        raise ns5_py2_Exception(err)

    return(stdout.decode())

def get_analog_entitie(path:str, label:str) -> list: 
    """
    return list of values of an analog entitie
    """
    
