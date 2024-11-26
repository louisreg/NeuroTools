import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
import os
sys.path.append("../../")
from neurotools.emg_tools.hd_sEMG import NeuroNexus_H32_tri,NeuroNexus_H32_tri_interp,HD_sEMG,interpolate_HD_sEMG, array_grid
import neurotools.emg_tools.spatial_filtering as sp 
from neurotools.utils.trigger import trigger as trigger_b


data_file = "./source/test_emg_array.hdf5"
df_emg = pd.read_hdf(data_file)
HD_sEMG_no_interp = HD_sEMG(df = df_emg, array = NeuroNexus_H32_tri)   

hd_sEMG = interpolate_HD_sEMG(HD_sEMG_no_interp, NeuroNexus_H32_tri_interp, raw = False)      #interpolate from raw data   
hd_sEMG.filter_eEMGs(f_LPF = 10_000, f_HPF = 10, n_LPF = 5, n_HFP = 5)                        #filter orignal data 
trigger = trigger_b(df_emg['Tr0 '],df_emg['time'])         #add a trigger
hd_sEMG.trigger = trigger
del HD_sEMG_no_interp

hd_semg_TSD = sp.spatial_filter(hd_sEMG,sp.TSD_kernel,raw = True)

hd_semg_TSD.get_eCMAPS(duration = 0.015, delay = 0.001)
hd_semg_TSD.plot_eCMAPs(label=False)

plt.show()