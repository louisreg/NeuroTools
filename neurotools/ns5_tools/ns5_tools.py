from json import loads as json_load
from ast import literal_eval
from subprocess import Popen, PIPE
import os
import pandas as pd
from pathlib import Path
import numpy as np
from numpy.typing import NDArray
from datetime import datetime, timedelta

class ns5_py2_Exception(Exception):
    def __init__(self, message):            
        super().__init__(message)

class InvalidFileExtension(Exception):
    "Invalide ns5 file extension"

class InvalidFile(Exception):
    "Invalide file"
class UnknownAnalogLabelException(Exception):
    "Unknown Analog Label"

class ns5Files():
    def __init__(self,file_path: str):
        self.file_path = file_path
        self.open_ns5(file_path)
        
        self.__file_info = self.__get_file_info()
        self.__sampling_rate = None
        self.__time = None
        self.__n_samples = None


    @property
    def datetime(self):
        datetime_str = self.__file_info["date"] + " "+self.__file_info["time"]
        ripple_datetime = datetime.strptime(datetime_str,'%Y/%d/%m %H:%M:%S')
        return(ripple_datetime - timedelta(hours=5))
    
    
    def open_ns5(self,file_path: str):
        '''
        Validate if file exist and if it is openable
        '''
        if not file_path.endswith(".ns5"): 
            raise(InvalidFileExtension)
        if not os.path.isfile(file_path):
            raise(InvalidFile)
        #self.__call_ns5_py2() #dummy read

    def __stdout_2_dict(self,stdout: str) -> dict:
        '''
        Convert a litteral dict to a dict
        '''
        out = stdout.replace("\'", "\"")
        return(json_load(out))

    def __stdout_2_list(self,stdout: str) -> list:
        '''
        Convert a litteral list to a list
        '''
        return(literal_eval(stdout))

    def __get_file_info(self) -> dict:
        '''
        Return file info in a dict object
        '''
        stdout = self.__call_ns5_py2("get_file_info")
        return(self.__stdout_2_dict(stdout))

    def get_analog_entitie_labels(self) -> list:
        '''
        Return file analog label entities in a list
        '''
        stdout = self.__call_ns5_py2("get_analog_labels")
        return(self.__stdout_2_list(stdout))

    def __call_ns5_py2(self,cmd:str='',arg=None) -> str:
        '''
        call the ns5_py2.py script with a specified file path and cmd
        '''

        file_path = self.file_path.replace(" ", "*")
        py2_file = os.path.dirname(__file__)+'/ns5_py2.py'
        if arg is None:
            py2_cmd = f"python2  {py2_file} {file_path} {cmd}"
        else:
            py2_cmd = f"python2  {py2_file} {file_path} {cmd} {arg}"
        process = Popen([py2_cmd], stdout=PIPE, stderr=PIPE, shell=True, stdin=None)
        stdout, stderr = process.communicate()
        if (process.returncode):
            err = stderr.decode()
            raise ns5_py2_Exception(err)

        return(stdout.decode())

    def get_analog_entitie(self,label:str) -> list: 
        """
        return list of values of an analog entitie

        Warning: THIS IS SLOW!
        """
        self.__analog_entitie_labels = self.get_analog_entitie_labels()
        if label not in self.__analog_entitie_labels:
            raise UnknownAnalogLabelException
        return(self.__stdout_2_list(self.__call_ns5_py2("get_analog_data",label)))
    
    def get_sampling_rate(self) -> float:
        """return data sampling rate

        Returns
        -------
        float
            sampling rate in Hz
        """
        if self.__sampling_rate is None:
            sampling_rate = self.__stdout_2_list(self.__call_ns5_py2("get_sampling_rate"))
            self.__sampling_rate = float(sampling_rate)
        return(self.__sampling_rate)
    
    def get_n_samples(self) -> int:
        """Return data number of samples

        Returns
        -------
        int
            Number of samples
        """
        if self.__n_samples is None:
            n_samples = self.__stdout_2_list(self.__call_ns5_py2("get_n_samples"))
            self.__n_samples = int(n_samples)
        return(self.__n_samples)

    def get_time_vector(self) -> NDArray:
        """Return the time vector np.array

        Returns
        -------
        np.array
            time vector array
        """
        if self.__time is None: 
            sampling_rate = self.get_sampling_rate()
            self.__time = np.arange(0, self.get_n_samples(),dtype = np.float32)/sampling_rate
        return(self.__time)

    def to_hdf(self,output_file:str, keys:list|None=None) -> None:
        """
        Save ns5 file to HF5 format

        Parameters
        ----------
        output_file : str
            Output file path
        keys : list | None, optional
            keys to save. If none, all keys are saved.
        """
        thisfile_path = str(Path(os.path.dirname(__file__))) 
        temp_p = thisfile_path + "/temp.pkl" 
        if keys is None:
            args = temp_p
        else:
            args = list(keys)
            args.insert(0,temp_p)
            args = ''.join(str(x).replace(' ','_')+ ' ' for x in args)

        self.get_sampling_rate()
        self.get_n_samples()
        self.__call_ns5_py2(cmd = "to_pickle", arg = args)

        df = pd.read_pickle(temp_p)
        os.remove(temp_p)
        df['time'] = self.get_time_vector()
        df.to_hdf(output_file, key='df', mode='w')