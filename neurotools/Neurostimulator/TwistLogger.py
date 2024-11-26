
import json, csv
from datetime import datetime, timedelta
import re

#TODO: old log format (csv)

class log ():
    def __init__(self,file_path:str):
        self.__APPname:str = ""
        self.__comment:str = ""
        self.__datetime: datetime|None = None
        self.__log_path:str|None = None
        self.__file:dict|None = None
        self.__keys:list|None = None
        self.__n_step: int = 0
        self.__stim_steps:list[stim_step|None] = [None]
        if file_path.endswith(".json"):
            self.__open_json(file_path)
        else:
            self.__open_csv(file_path)
        if self.__n_step>1:
            self.__get_stim_steps()
    
    @property
    def Appname(self):
        return(self.__APPname)

    @property
    def comment(self):
        return(self.__comment)
    
    @property
    def datetime(self):
        return(self.__datetime)
    
    @property
    def log_path(self):
        return(self.__log_path)
    
    @property
    def keys(self):
        return(self.__keys)
    
    @property
    def n_step(self):
        return(self.__n_step)
    
    @property
    def steps(self):
        return(self.__stim_steps)
    
    def __open_json(self, file_path: str) -> None:
        self.__log_path = file_path
        with open(file_path, 'r') as file:
            self.__file = json.load(file)
        self.__keys =  self.__file.keys()
        self.__APPname = self.__file["APP"]
        if "Comment" in self.__file.keys():
            self.__comment = self.__file["Comment"]
        datetime_str = self.__file["Date"] + " " + self.__file["Start Time"]
        self.__datetime = datetime.strptime(datetime_str,"%b-%d-%Y %H:%M:%S")
        self.__n_step = len([key for key in self.__keys if "STIM_" in key])


    def __open_csv(self, file_path: str) -> None:
        self.__log_path = file_path
        state_list = []
        pw_list = []
        amp_list = []
        #print(file_path)
        with open(file_path, 'r') as file:
            csvreader = csv.reader(file)
            self.__keys = []
            log_dic = {}
            for row in enumerate(csvreader):
                if len(row[1]) == 2:
                    data = row[1][1]
                    if "Amp (uA)" in row[1][0]:
                        amp_list = [data]
                    elif "Elapsed Time (s)" in row[1][0]:
                        time_list = [data]
                    elif "State" in row[1][0]:
                        state_list = [data]
                    else:
                        log_dic[row[1][0]] = data
                elif len(row[1]) > 2:
                    if "Amp (uA)" in row[1][0]:
                        amp_list = row[1][1:]
                    if "PW (us)" in row[1][0]:
                        pw_list = row[1][1:]
                    elif "Elapsed Time (s)" in row[1][0]:
                        time_list = row[1][1:]
                    elif "State" in row[1][0]:
                        state_list = row[1][1:]
                    else:
                        data = row[1][1]
                        log_dic[row[1][0]] = data
                    #something else in here???

            self.__file = log_dic
            self.__keys =  self.__file.keys()
            self.__APPname = self.__file["APP"]
            if "Comment" in self.__file.keys():
                self.__comment = self.__file["Comment"]
            datetime_str = self.__file["Date"] + " " + self.__file["Start Time"]
            self.__datetime = datetime.strptime(datetime_str,"%b-%d-%Y %H:%M:%S")
            self.__n_step = len(amp_list)
            if len (state_list) == 0:
                state_list = ["BLOCK"]*self.__n_step
            amp_list = [float(re.findall(r'\d', amp)[0]) for amp in amp_list]
            time_list = [float(time) for time in time_list]
            resting_t = self.__file["Rest Duration (s)"]
            self.__gen_fake_stim_steps(amp_list,time_list,state_list,resting_t)

    def __gen_fake_stim_steps(self, amp_list, time_list,state_list,resting_t) -> list:
        keys = self.__stim_keys()
        start_time = self.__datetime
        id=0
        for i,_ in enumerate(keys):
            stop_time = start_time + timedelta(seconds=time_list[i])            
            if state_list[i] == "BLOCK":
                key = f"STIM_{id+1}"
                id+=1
                self.__file[key] = {}
                self.__file[key]["Start Time"] = start_time.strftime("%H:%M:%S")
                self.__file[key]["Stop Time"] = stop_time.strftime("%H:%M:%S") 
                self.__file[key]["Elasped Time"] = float(time_list[i])
                self.__file[key]["Output Channel"] = self.__get_out_chan(self.__file["StimChannel"])
                if "BlockingChan" in self.__keys:
                    self.__file[key]["Blocking Channel"] = self.__get_out_chan(self.__file["BlockingChan"])
                else:
                    self.__file[key]["Blocking Channel"] = []
                self.__file[key]["Inverted Channel"] = self.__get_out_chan(self.__file["InvertedChannel"])
                self.__file[key]["Output Mode"] = "Unknown"
                if "Stim Wavefrom" in self.__keys:
                    self.__file[key]["Waveform"] = self.__file["Stim Wavefrom"]
                else:
                    self.__file[key]["Waveform"] = self.__file["Waveform"]
                self.__file[key]["Stimulation Amplitude"] = amp_list[i]

                if "Pulse Width (us)" in self.__keys:
                    self.__file[key]["Pulse Width"] = float(self.__file["Pulse Width (us)"])
                else:
                    if float(self.__file["Frequency (Hz)"])>0:
                        self.__file[key]["Pulse Width"] =  1e6/(float(self.__file["Frequency (Hz)"]))
                    else:
                        self.__file[key]["Pulse Width"] = 0

                self.__file[key]["Pulse Mode"] = "Unknown"
                self.__n_step = len([key for key in self.__file.keys() if "STIM_" in key])
                stop_time += timedelta(seconds=float(resting_t)) 
            start_time = stop_time


    def __get_out_chan(self,chans: str) -> list:
        output_chan = []
        i = 0
        for c in reversed(chans):
            if c == '1':
                output_chan.append(2**i)
            i+=1
        return(output_chan)
    


    def __stim_keys(self) -> list:
        return([f"STIM_{i+1}" for i in range(self.__n_step)])
    
    def __get_stim_steps(self) -> list:
        self.__stim_steps = []
        for key in self.__stim_keys():
            step = stim_step(self.__file[key])
            self.__stim_steps.append(step)
    

class stim_step:
    def __init__(self,dict:dict):
        self.start_time: datetime = datetime.strptime(dict["Start Time"],"%H:%M:%S").time()
        self.stop_time: datetime = datetime.strptime(dict["Stop Time"],"%H:%M:%S").time()
        self.duration: float = dict["Elasped Time"]
        self.output_mode:str = "".join([str(i) for i in dict["Output Mode"]])
        self.output_channel:list[int] = dict["Output Channel"]
        self.inverted_channel:list[int] = dict["Inverted Channel"]
        self.blocking_channel:list[int] = dict["Blocking Channel"]
        self.waveform:str = "".join([str(i) for i in dict["Waveform"]])
        self.pulse_width:float = dict["Pulse Width"]
        if "Cathodic Ratio" in dict.keys():
            self.cathodic_ratio:float = dict["Cathodic Ratio"]
        self.pulse_mode:str = "".join([str(i) for i in dict["Pulse Mode"]])
        if "Single Pulse Frequency" in dict.keys():
            self.pulse_frequency:float = dict["Single Pulse Frequency"]
        self.stimulation_amp:float = dict["Stimulation Amplitude"]