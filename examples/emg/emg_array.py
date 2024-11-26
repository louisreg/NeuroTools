
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
import os
sys.path.append("../../")
from neurotools.emg_tools.hd_sEMG import NeuroNexus_H32_tri,HD_sEMG
from neurotools.emg_tools.emg_channel import eEMG
from neurotools.ns5_tools.ns5_tools import ns5Files
from neurotools.utils.trigger import trigger


##create or open the EMG arrays
keys = NeuroNexus_H32_tri.required_raw_keys() + ['Tr0 ', 'Tr1 ']

data_file = "./source/test_emg_array2.hdf5"
overwrite = False
if not (os.path.isfile(data_file)) or overwrite:
    ns5_path = "./source/UA014_SEL_AS_MS_BMG0_0003.ns5"
    ns5_file = ns5Files(ns5_path)
    if set(keys).issubset(ns5_file.get_analog_entitie_labels()):
        ns5_file.to_hdf(data_file,keys)
    else:
        print("Requested keys not available")
        exit()

df_emg = pd.read_hdf(data_file)
test_HD_sEMG = HD_sEMG(df = df_emg, array = NeuroNexus_H32_tri)

electrode = 14
raw_key = NeuroNexus_H32_tri.get_elect_raw_key(electrode)
emg_1 = eEMG(df_emg[raw_key], df_emg['time']) ##test
emg_1_mapped = test_HD_sEMG.eEMGs[NeuroNexus_H32_tri.get_elec_idx(electrode)]

"""
fig, ax = plt.subplots() 
emg_1.plot_raw(ax)
emg_1_mapped.plot_raw(ax)
plt.plot(df_emg['time'],emg_1.data-emg_1_mapped.data)
plt.show()
exit()
"""
idx = NeuroNexus_H32_tri.get_elec_xy(1)


trigger = trigger(df_emg['Tr0 '],df_emg['time'])
test_HD_sEMG.trigger = trigger

#test_HD_sEMG.plot_raw()

test_HD_sEMG.filter_eEMGs(f_LPF = 1_000, f_HPF = 20, n_LPF = 5, n_HFP = 5)
test_HD_sEMG.get_eCMAPS(duration = 0.015, delay = 0)

#test_HD_sEMG.plot_data()
#test_HD_sEMG.plot_eCMAPs()
#fig,axs = test_HD_sEMG.plot_avg_eCMAP()

#test_HD_sEMG.plot_data(interpolate = False)
#test_HD_sEMG.plot_eCMAPs(interpolate = False)
#fig,axs = test_HD_sEMG.plot_avg_eCMAP()


#emg_e1 = test_HD_sEMG.get_eEMG(electrode)
#ax = test_HD_sEMG.get_eEMG_ax(axs, electrode) 
#emg_e1.plot_avg_eCMAP(ax)


def plot_heatmap(data):
    fig, axs = plt.subplots(1,2) 
    sc = test_HD_sEMG.plot_heatmap_eCMAP(axs[0], data)
    fig.colorbar(sc, ax = axs[0])
    sc = test_HD_sEMG.plot_heatmap_eCMAP(axs[1], data, n_interp = 100)
    fig.colorbar(sc, ax = axs[1])
    fig.suptitle(f"eCMUAP characteristic: {data}")
    axs[0].set_title("Uninterpolated")
    axs[1].set_title("Interpolated")
    fig.tight_layout()

#plt.close("all")
plot_heatmap("rms")
plot_heatmap("peak2peak")
plot_heatmap("latency")
plot_heatmap("duration")
plot_heatmap("ttmax")
plot_heatmap("ttmin")
plt.show()
