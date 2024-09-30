# -*- coding: utf-8 -*-
#!/usr/bin/env python2.7

import pyns
import sys
from datetime import datetime, time
import pandas as pd
#import cPickle as cp

def isIter(val):
    return(hasattr(val, '__iter__')==True)

def get_file_info(nsfile):
    file_info = nsfile.get_file_info()
    info =  {}
    info['file_type'] = file_info.file_type
    info['entity_count'] = file_info.entity_count
    info['timestamp_resolution'] = file_info.timestamp_resolution
    info['time_span'] = file_info.time_span
    info['app_name'] = file_info.app_name
    if (file_info.time_day and file_info.time_month and file_info.time_year):
        dt = datetime(file_info.time_year, file_info.time_day, file_info.time_month)
    else:
        dt = datetime(2000,1,1)    
    if (file_info.time_hour and file_info.time_min and file_info.time_sec and file_info.time_millisec):
        tm = time(file_info.time_hour, file_info.time_min,file_info.time_sec,file_info.time_millisec)
    else:
        tm = time(0,0,0,0)
    info['date'] = dt.strftime("%Y/%d/%m")
    info['time'] = tm.strftime("%H:%M:%S")
    info['comment'] = file_info.comment
    print(info)

def get_analog_labels(nsfile):
    analog_entities = [e for e in nsfile.get_entities() if e.entity_type == 2] 
    entities_label = [e.electrode_label for e in analog_entities] 
    print(entities_label)

def get_analog_data(nsfile, label):
    analog_entities = [e for e in nsfile.get_entities() if e.entity_type == 2] 
    data = []
    for entity in analog_entities:
        if label in entity.electrode_label:
            data = entity.get_analog_data()
    print(list(data))

def unpack_arg(args):
    cleaned = args
    del cleaned[0], cleaned[1], cleaned[2]
    return(cleaned)

def to_pickle(nsfile,args):
    df = pd.DataFrame()
    if isIter(args):
        output_file = args[0]
        keys = args[1:-1]
    else:
        output_file = args
        keys = None
    analog_entities = [e for e in nsfile.get_entities() if e.entity_type == 2] 
    for entity in analog_entities:
        label = entity.electrode_label
        if keys is not None:
            if label in keys:
                df[label] = entity.get_analog_data()
        else:
            df[label] = entity.get_analog_data()
    """
    with open(output_file, "wb") as f :
        cp.dump(df,f,cp.HIGHEST_PROTOCOL)
    """
    df.to_pickle(output_file)
    del df


def main():
    if (len(sys.argv))>1:
        file_path = str(sys.argv[1])
        arg = None
        if (len(sys.argv))==3:
            cmd = sys.argv[2] 
        else:
            cmd = ''
        if (len(sys.argv))>3:
            cmd = sys.argv[2] 
            if (len(sys.argv))==4: 
                arg = sys.argv[3] 
            else:
                arg = unpack_arg(sys.argv)

        nsfile = pyns.NSFile(file_path)
        if arg is not None: 
            eval_d="(nsfile,arg)"
        else:
            eval_d="(nsfile)"
        if (len(cmd)):
            eval(cmd+eval_d)

        

if __name__ == "__main__":
    main()

        

