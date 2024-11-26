
from ..Neurostimulator import TwistLogger
from ..utils.files import list_files_in_subdir
from ..ns5_tools.ns5_tools import ns5Files
from datetime import datetime, timedelta
import os
import re
from tqdm import tqdm
import pandas as pd

def name_from_folder(folder:str):
    ns5_files = list_files_in_subdir(folder,".ns5")
    folder_name = re.findall(r'\d+', folder)[-1]
    if len(ns5_files):
        ns5_file = ns5_files[0].replace(ns5_files[0][0:ns5_files[0].rfind('/')+1],"")
        UA_tag = ns5_file[0:5]
        return(f"{UA_tag}_{folder_name}.xlsx")
    return("")

def generate_xls_matching(folder:str, xls_name:str|None = None, xlx_path:str|None = None):
    log_l,template_l,ummatched_log_l,ummatched_template_l = match_log_with_ns5(folder) 
    if xls_name is None:
        xls_name = name_from_folder(folder)
    if xlx_path is not None: 
        if xlx_path[-1] == "/":
            xls_name = xlx_path + xls_name
        else:
            xls_name = xlx_path + ["/"] + xls_name
    
    #add matched files to df
    df_matched = pd.DataFrame()
    if len(log_l) > 0:
        #Remove full path to ease reading
        log_dir_path = log_l[0][0:log_l[0].rfind('/')+1] 
        df_matched['matched_log'] = [log.replace(log_dir_path,"") for log in log_l]
        df_matched['matched_ns5'] = [ns5.replace(ns5[0:ns5.rfind('/')+1],"") for ns5 in template_l]
        df_matched['log_path'] = log_dir_path
        df_matched['ns5_path'] = [ns5[0:ns5.rfind('/')+1] for ns5 in template_l]
    else:
        df_matched['matched_log'] = []
        df_matched['matched_ns5'] = []
        df_matched['log_path'] = []
        df_matched['ns5_path'] = []

    #add unmatched files to another df
    df_unmatched = pd.DataFrame()

    #get unmatched log/ns5 file sizes to ease manual matching
    ummatched_log_size = []
    ummatched_template_size = []
    for ummatched_log in ummatched_log_l:
        ummatched_log_size.append(TwistLogger.log(ummatched_log).n_step)
    ns5_files = list_files_in_subdir(folder,".ns5")
    for ummatched_template in ummatched_template_l:
        ummatched_template_size.append(get_template_size(ummatched_template,ns5_files))
    
    ummatched_template_path = [ns5[0:ns5.rfind('/')+1] for ns5 in ummatched_template_l]

    #fill with "" and 0 columns
    if len(ummatched_log_l)>len(ummatched_template_l):
        n_fill = len(ummatched_log_l) - len(ummatched_template_l)
        fill = ["" for _ in range(n_fill)]
        fill_zeros = [0 for _ in range(n_fill)]
        ummatched_template_l+=fill
        ummatched_template_path+=fill
        ummatched_template_size+=fill_zeros
    if len(ummatched_log_l)<len(ummatched_template_l):
            n_fill = len(ummatched_template_l) - len(ummatched_log_l)
            fill = ["" for _ in range(n_fill)]
            fill_zeros = [0 for _ in range(n_fill)]
            ummatched_log_size+=fill_zeros
            ummatched_log_l+=fill
    
    if len(ummatched_log_l):
        log_dir_path = ummatched_log_l[0][0:ummatched_log_l[0].rfind('/')+1] 
    else:
        log_dir_path = ""
    df_unmatched['ummatched_log'] = [log.replace(log_dir_path,"") for log in ummatched_log_l]
    df_unmatched['ummatched_log_size'] = ummatched_log_size
    df_unmatched['ummatched_template'] = [ns5.replace(ns5[0:ns5.rfind('/')+1],"") for ns5 in ummatched_template_l]
    df_unmatched['ummatched_template_size'] = ummatched_template_size
    df_unmatched['log_path'] = log_dir_path
    df_unmatched['ns5_path'] = ummatched_template_path

    if os.path.isfile(xls_name):
        writer = pd.ExcelWriter(xls_name, engine = 'openpyxl', mode="a", if_sheet_exists = "replace")
    else:
        writer = pd.ExcelWriter(xls_name, engine = 'openpyxl', mode="w")
    df_unmatched.to_excel(writer,sheet_name='unmatched_files',index=False)
    df_matched.to_excel(writer,sheet_name='matched_files',index=False)
    print(f"Matching table saved to {xls_name}")
    writer.close()

def get_ns5_templates(ns5_files:list[str], min_size = 5) -> list:
    files_step = [(re.findall(r'\d+', e[0:-4])[-1]) for e in ns5_files]
    templates = []
    for file, step in  zip(ns5_files,files_step):
        f_start = file.rfind('/')+1
        templates.append(file[f_start:-4-len(step)])
    templates = list(set(templates))        #we ensure unicity of the templates even if located in multiple subfolders
    for i,temp in enumerate(templates):
        dir  = [s for s in ns5_files if temp in s][0]
        dir = dir[0:dir.rfind('/')+1]
        templates[i] = dir + temp
    templates = [e for e in templates if get_template_size(e, ns5_files)>=min_size]
    return(templates)

def get_template_size(template:str,ns5_files:list[str]) -> int:
    return(len(match_ns5_template(template, ns5_files)))

def get_log_folder(foldername:str) -> str:
    folder_d = datetime.strptime(foldername[-9:-1], "%Y%m%d") 
    log_f = f"{foldername}log_{folder_d.strftime("%b_%d_%Y")}"
    if (os.path.isdir(log_f)):
        return(log_f)
    else:
        print("Log folder not found")
        return("")

def find_all_logs(log_folder:str, min_size = 5, exclusion_list = ["SimpleStim","SD_curves","SD_Curve"]) -> list:
    logs = list_files_in_subdir(log_folder,".json")
    logs += list_files_in_subdir(log_folder,".csv") #older log format
    if len(logs) == 0:
        print("No log files found!!")
        return([])
    else:
        for exclusion in exclusion_list: 
            logs = [log for log in logs if exclusion not in log]

        return([log for log in logs if TwistLogger.log(log).n_step>= min_size])
    

def find_log_from_template(template:str, logs:list[str], ns5files:list[str]) -> str:
    #This could use multithread such as describe here: https://stackoverflow.com/questions/2562757/is-there-a-multithreaded-map-function
    ns5files = match_ns5_template(template, ns5files)
    for log_f in logs:
        log = TwistLogger.log(log_f)
        if validate_nsteps(log,ns5files):
            valid = validate_all_timings(log,ns5files)
            if valid == None: 
                #print("No matching log file found")
                return("")
            elif valid == True: 
                return(log_f)
    #print("No matching log file found")
    return("")

def match_log_with_ns5(folder:str) -> list|list|list|list:
    ns5_files = list_files_in_subdir(folder,".ns5")
    logs = find_all_logs(get_log_folder(folder))
    templates = get_ns5_templates(ns5_files)
    log_l = []
    template_l = []

    for template in tqdm(templates, desc="Matching files"):
        log = find_log_from_template(template,logs,ns5_files)
        if log != "":
            log_l.append(log)
            template_l.append(template)
            logs = [i for i in logs if i != log] #we remove log file from logs when matched (to make search faster)
    
    ummatched_template_l = [tmp for tmp in templates if tmp not in template_l]
    print("Matching done!")
    print(f"Number of matched files: {len(log_l)}")
    print(f"Remaining unmatched log files: {len(logs)}")
    print(f"Remaining unmatched ns5 templates: {len(ummatched_template_l)}")
    return(log_l,template_l,logs,ummatched_template_l)


def validate_timing(log_step:TwistLogger.stim_step, ns5file:str,d_drift:timedelta=timedelta(seconds=0), delta_s: int = 10) -> bool|timedelta:
    delta_s = timedelta(seconds=delta_s)
    ns5_obj = ns5Files(ns5file)
    if str(ns5_obj.datetime.time()) == "19:00:00":          #not datetime
        #print("ns5file contained no timecode. None value returned")
        return(None,timedelta(seconds=0))       
    else:
        log_datetime = datetime.combine(ns5_obj.datetime.date(), log_step.start_time)
        delta = abs(ns5_obj.datetime - log_datetime)
        if delta_s > (delta-d_drift):
            return(True,delta)
        return(False,delta)
    
def validate_all_timings(log: TwistLogger.log, ns5_files:list[str]) -> bool:
    n_none = 0
    d_drift = timedelta(seconds=0)
    for step, file in zip(log.steps, ns5_files):
        valid,d_drift = validate_timing(step,file,d_drift)
        if valid == None: 
            n_none+=1
            if n_none == log.n_step:
                #("Too many missing timecode - Can't evaluate match")
                return(None)
        elif valid == False:
            return(False)
    return(True)

def validate_nsteps(log: TwistLogger.log, ns5_files:list[str]) -> bool:         #return true if n_step in log file matches number of ns5 files
    return(log.n_step == len(ns5_files))

def validate_step_ns5_number(step_numb: int, ns5file:str) -> bool:              #return true if ns5file number matches n_step index
    return(step_number_ns5(ns5file) == step_numb+1)

def step_number_ns5(filename:str) -> int:                                       #return ns5file index number
    return(int(re.findall(r'\d+', filename[0:-4])[-1]))

def get_ns5_template(filename:str) -> str:                                      #return ns5file template (filename withtout index number)
    step_str = (re.findall(r'\d+', filename[0:-4])[-1])
    return(filename[0:-4-len(step_str)])

def match_ns5_template(template:str, ns5_files:list[str]) -> list:              #return ns5files sorted list matching template
    files = [e for e in ns5_files if template in e]
    files = sorted(files, key=lambda x:int(re.findall(r'\d+', x[0:-4])[-1]))
    return(files)

def find_ns5_file(log_step:TwistLogger.stim_step, ns5_files: list[str], delta_s: int = 3) -> str:
    delta_s = timedelta(seconds=delta_s)
    for ns5_file in ns5_files:
        ns5_obj = ns5Files(ns5_file)
        if str(ns5_obj.datetime.time()) != "19:00:00":          #not datetime
            log_datetime = datetime.combine(ns5_obj.datetime.date(), log_step.start_time)
            if delta_s > abs(ns5_obj.datetime - log_datetime):
                return(ns5_file)
    return("")



"""def find_ns5_folder(log: TwistLogger.log, data_archive_dir:str) -> str:
    filenames = [file for file in os.listdir(data_archive_dir) if file.isdigit()]
    file = filenames[0]
    for file in filenames:
        file_d = datetime.strptime(file, "%Y%m%d") 
        if log.datetime.date() == file_d.date():
            return(data_archive_dir+"/"+file+"/")
    return("")"""

