import numpy as np
from numpy.typing import NDArray
from dataclasses import dataclass
import pandas as pd
from .hd_sEMG import HD_sEMG, array_grid
from scipy.ndimage import convolve

@dataclass
class kernel():
    __kernel: NDArray
    __label: str
    def __call__(self) -> NDArray:
        return(self.__kernel)
    
    @property
    def label(self):
        return(self.__label)

# source: Disselhorst-Klug, C., Silny, J., & Rau, G. (1997). 
# Improvement of spatial resolution in surface-EMG: a theoretical and experimental 
# comparison of different spatial filters. IEEE Transactions on Biomedical Engineering, 44(7), 567-574.

#Unit Differential Filters
unit_kernel = kernel(np.array([[1]]),"unit")
reverse_kernel = kernel(np.array([[-1]]),"reverse")

#1D Simple Differential Filters
TSD_kernel = kernel(np.array([[-1,1]]),"TSD")
LSD_kernel = kernel(np.array([[-1],[1]]),"LSD")

#1D Double Differential Filters
LDD_kernel = kernel(np.array([[-1],[2],[-1]]),"LDD")
TDD_kernel = kernel(np.array([[-1,2,-1]]),"TDD")

#2D Double Differential Filters
NDD_kernel = kernel(np.array([[0,-1,0],[-1,4,-1],[0,-1,0]]),"NDD")
IB2_kernel = kernel((1/16)*np.array([[-1,-2,-1],[-2,12,-2],[-1,-2,-1]]),"IB2")
IR_kernel = kernel((1/9)*np.array([[-1,-1,-1],[-1,8,-1],[-1,-1,-1]]),"IR")


def create_array_from_hd(hd_semg:HD_sEMG,filtered:NDArray, remove_empty: bool=False) -> array_grid:
    elec_pos = hd_semg.array.elec_pos.copy()
    t_0 = filtered[:,:,0]
    t_0[t_0==0] = 1
    t_0 = np.nan_to_num(t_0,0)
    elec_pos[t_0==0] = 0        #if NaN then electrode index is set to 0
    elec_pos = np.int32(elec_pos)
    if remove_empty:
        idx = np.argwhere(np.all(elec_pos[..., :] == 0, axis=0))
        elec_pos = np.delete(elec_pos, idx, axis=1)         #remove colums of zeros
        elec_pos = elec_pos[~np.all(elec_pos == 0, axis=1)] #remove raw of zeros
    e_idx = 1
    for i in range(elec_pos.shape[0]):
        for j in range(elec_pos.shape[1]):
            if elec_pos[i,j] > 0:
                elec_pos[i,j] = e_idx 
                e_idx+=1 
    elecs = elec_pos[elec_pos>0].flatten()
    return(array_grid(elec_pos,elecs))

def data_2_HD_sEMG(data:NDArray,array:array_grid,time) -> HD_sEMG:
    df = pd.DataFrame()
    for _,elec in enumerate(array.elec_to_raw): 
        key = array.get_elect_raw_key(elec)
        idxs = array.get_elec_xy(elec)
        df[key] = data[idxs[0],idxs[1],:]
    df["time"] = time
    return(HD_sEMG(df = df, array = array))  

def spatial_filter(hd_semg:HD_sEMG, kernel: kernel, raw:bool) -> HD_sEMG:
    if raw:
        data = hd_semg.raw_to_2Darray()
    else:
        data = hd_semg.data_to_2Darray()
    filtered = convolve(data, kernel()[:, :, None], mode='nearest')
    filtered[np.all(filtered == 0, axis=2)] = np.nan        #set to nan when data are zeroes
    array = create_array_from_hd(hd_semg,filtered)
    filtered_hd_emg = data_2_HD_sEMG(filtered,array,hd_semg.t)
    if hd_semg.trigger is not None:
        filtered_hd_emg.trigger = hd_semg.trigger
    filtered_hd_emg.sp_kernel = kernel
    return(filtered_hd_emg)