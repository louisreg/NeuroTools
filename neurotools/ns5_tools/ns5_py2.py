# -*- coding: utf-8 -*-
#!/usr/bin/env python2.7

import pyns
import sys
from datetime import datetime, time

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

def main():
    if (len(sys.argv))>1:
        file_path = str(sys.argv[1])
        if (len(sys.argv))>2:
            cmd = sys.argv[2] 
        else:
            cmd = ''
        nsfile = pyns.NSFile(file_path)
        if (len(cmd)):
            eval(cmd+"(nsfile)")

        

if __name__ == "__main__":
    main()

        

