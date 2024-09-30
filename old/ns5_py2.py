# -*- coding: utf-8 -*-
#!/usr/bin/env python2.7

import pyns
import sys
from datetime import datetime, time


trigger_channel = 'Tr0'
trigger_channel_2 = 'Tr1'
#trigger_channel = 'analog 1'
#trigger_channel_2 = 'analog 2'
force_channel = ['analog 5','analog 7','analog 9','analog 11','analog 13','analog 15']
force_channel = ['Fx','Fy','Fz','Mx','My','Mz']
force_label = ['Fx','Fy','Fz','Mx','My','Mz']
elect1_ch1 = 1
elect1_nch = 32
elect2_ch1 = 129
elect2_nch = 32


'''def ExtractForceData(nsfile):
    dict = {}
    analog_entities = [e for e in nsfile.get_entities() if e.entity_type == 2] 
    for entity in analog_entities:
        if trigger_channel in entity.electrode_label:
            trigger = entity.get_analog_data()
            analog_info = entity.get_analog_info()
            t = np.arange(0, len(trigger), dtype=float)/analog_info.sample_rate 
    for entity in analog_entities:
        if trigger_channel_2 in entity.electrode_label:
            trigger2 = entity.get_analog_data()

    dict ['trigger'] = trigger
    dict ['trigger2'] = trigger2
    dict ['sample_freq'] = analog_info.sample_rate
    dict ['min_val'] = analog_info.min_val
    dict ['max_val'] = analog_info.max_val
    dict ['units'] = analog_info.units
    dict ['resolution'] = analog_info.resolution
    dict ['time'] = t
    for entity in analog_entities:
        if entity.item_count > 0: 
            analog_input = entity.electrode_label
            for force in force_channel:
                if (force in analog_input):
                    data = entity.get_analog_data()
                    dict [force] = data#
    return(pd.DataFrame(dict))
    
def ExtractEMGData(nsfile):
    dict = {}
    analog_entities = [e for e in nsfile.get_entities() if e.entity_type == 2] 
    for entity in analog_entities:
        if trigger_channel in entity.electrode_label:
            trigger = entity.get_analog_data()
            analog_info = entity.get_analog_info()
            t = np.arange(0, len(trigger), dtype=float)/analog_info.sample_rate 
    for entity in analog_entities:
        if  trigger_channel_2 in entity.electrode_label:
            trigger2 = entity.get_analog_data()

    dict ['trigger'] = trigger
    dict ['trigger2'] = trigger2
    dict ['sample_freq'] = analog_info.sample_rate
    dict ['min_val'] = analog_info.min_val
    dict ['max_val'] = analog_info.max_val
    dict ['units'] = analog_info.units
    dict ['resolution'] = analog_info.resolution
    dict ['time'] = t

    for entity in analog_entities:
        if entity.item_count > 0: 
            analog_input = entity.electrode_label
            if "raw" in analog_input:
                raw_idx = np.int32(re.findall(r'\d+', analog_input)[0])
                if raw_idx >=elect2_ch1:
                    label = "elect2_"+str((raw_idx-elect2_ch1)+1)
                else:
                    label = "elect1_"+str(raw_idx)
                data = entity.get_analog_data()
                dict [label] = data
    return(pd.DataFrame(dict))'''

def get_file_info(nsfile):
    file_info = nsfile.get_file_info()
    info =  {}
    info['file_type'] = file_info.file_type
    info['entity_count'] = file_info.entity_count
    info['timestamp_resolution'] = file_info.timestamp_resolution
    info['time_span'] = file_info.time_span
    info['app_name'] = file_info.app_name
    dt = datetime(file_info.time_year, file_info.time_day, file_info.time_month)
    tm = time(file_info.time_hour, file_info.time_min,file_info.time_sec,file_info.time_millisec)
    info['date'] = dt.strftime("%Y/%d/%m")
    info['time'] = tm.strftime("%H:%M:%S")
    info['comment'] = file_info.comment
    print(info)

def get_analog_labels(nsfile):
    analog_entities = [e for e in nsfile.get_entities() if e.entity_type == 2] 
    entities_label = [e.electrode_label for e in analog_entities] 
    print(entities_label)

def main():
    if (len(sys.argv))>2:
        try:
            file_path = str(sys.argv[1])
            cmd = sys.argv[2] 
            nsfile = pyns.NSFile(file_path)
            eval(cmd+"(nsfile)")
        except Exception as e: print(e)

        

if __name__ == "__main__":
    main()

        

