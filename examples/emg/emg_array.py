
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
import os
sys.path.append("../../")
import neurotools.emg_tools.hd_sEMG as hd_sEMG #import NeuroNexus_H32_tri
from neurotools.emg_tools.hd_sEMG import NeuroNexus_H32_tri,HD_sEMG
from neurotools.ns5_tools.ns5_tools import ns5Files
from neurotools.utils.trigger import trigger

fig, axs = plt.subplots(1,2) 
NeuroNexus_H32_tri.plot_grid(axs[0])
NeuroNexus_H32_tri.plot_grid(axs[1], raw_idx=True)
fig.tight_layout()

##create or open the EMG arrays
keys = NeuroNexus_H32_tri.required_raw_keys() + ['Tr0 ', 'Tr1 ']


data_file = "./source/test_emg_array.hdf5"
overwrite = False
if not (os.path.isfile(data_file)) or overwrite:
    ns5_path = "./source/UA014_SEL_AS_MS_BMG0_0007.ns5"
    ns5_file = ns5Files(ns5_path)
    if set(keys).issubset(ns5_file.get_analog_entitie_labels()):
        ns5_file.to_hdf(data_file,keys)
    else:
        print("Requested keys not available")
        exit()

df_emg = pd.read_hdf(data_file)

test_HD_sEMG = HD_sEMG(df = df_emg, array = NeuroNexus_H32_tri)

trigger = trigger(df_emg['Tr0 '],df_emg['time'])
test_HD_sEMG.trigger = trigger

test_HD_sEMG.plot_raw()
test_HD_sEMG.filter_eEMGs(f_LPF = 1_000, f_HPF = 10, n_LPF = 5, n_HFP = 5)
test_HD_sEMG.get_eCMAPS(duration = 0.015, delay = 0)

test_HD_sEMG.plot_data()
test_HD_sEMG.plot_eCMAPs()
test_HD_sEMG.plot_avg_eCMAP()
fig, ax = plt.subplots() 
sc = test_HD_sEMG.test_heat(ax)
fig.colorbar(sc, ax = ax)
plt.show()