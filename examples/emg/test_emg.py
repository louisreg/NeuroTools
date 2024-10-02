import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
import os
sys.path.append("../../")
from neurotools import ns5_tools
from neurotools.utils.trigger import trigger
from neurotools.emg_tools.emg_channel import eEMG

data_file = "./source/emg_single_channel.hdf5"
overwrite = False
if not (os.path.isfile(data_file)) or overwrite:
    ns5_path = "./source/UA014_SEL_AS_MS_BMG0_0007.ns5"
    ns5_file = ns5_tools.ns5Files(ns5_path)
    used_labels = ns5_file.get_analog_entitie_labels()[0:4]
    used_labels += ['Tr0 ', 'Tr1 ']
    ns5_file.to_hdf(data_file,used_labels)
df_emg = pd.read_hdf(data_file)


t = np.array(df_emg['time'])
emg_1 = eEMG(df_emg['raw 1'],t)
emg_2 = eEMG(df_emg['raw 2'],t)
emg_3 = eEMG(df_emg['raw 3'],t)

f_HPF = 5
o_HFP = 5
emg_1.HPF(f_HPF,o_HFP)

f_LPF = 10_000
o_LFP = 5
emg_1.LPF(f_LPF,o_LFP)

trigger = trigger(df_emg['Tr0 '],t)

emg_1.trigger = trigger
emg_1.get_eCMAPS(0.015,0.0005)

fig, ax = plt.subplots() 
emg_1.plot_eCMAPS(ax,color = 'b', alpha = 0.05)
emg_1.plot_avg_eCMAP(ax)

plt.show()