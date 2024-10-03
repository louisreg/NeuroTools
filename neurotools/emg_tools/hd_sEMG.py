import numpy as np
from numpy.typing import NDArray
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.figure import Figure as PltFig

from .emg_channel import eEMG


__NeuroNexus32ch_to_ripple = np.array([31,29,27,25,23,21,19,17,
                        32,30,28,26,24,22,20,18,16,14,12,
                        10,8,6,4,2,15,13,11,9,7,5,3,1])

#-> A1 = RAW_1

__NeuroNexus32ch_idx = np.array([[np.nan, np.nan, 17, 16, np.nan, np.nan],
                                    [np.nan, 18, np.nan, np.nan, 15, np.nan],
                                    [20, np.nan, 19, 14, np.nan, 13],
                                    [np.nan, 21, np.nan, np.nan, 12, np.nan],
                                    [23, np.nan, 22, 11, np.nan, 10],
                                    [np.nan, 24, np.nan, np.nan, 9, np.nan],
                                    [26, np.nan, 25, 8, np.nan, 7],
                                    [np.nan, 27, np.nan, np.nan, 6, np.nan],
                                    [29, np.nan, 28, 5, np.nan, 4],
                                    [np.nan, 30, np.nan, np.nan, 3, np.nan],
                                    [32, np.nan, 31, 2, np.nan, 1]])


class array_grid():
    def __init__(self,elec_pos:NDArray,elec_to_raw:NDArray):
        self.__elec_pos = np.nan_to_num(elec_pos,0)
        self.__elec_pos: NDArray = np.int32(self.__elec_pos)
        self.__elec_to_raw: NDArray = elec_to_raw
        self.__n_ch: int = int(len(elec_to_raw))

    @property
    def n_ch(self) -> int:
        return(self.__n_ch)
    
    @property
    def elec_pos(self) -> NDArray:
        return(self.__elec_pos)


    @property
    def shape(self) -> tuple:
        return(self.__elec_pos.shape)

    @property
    def n_row(self) -> int:
        return(self.__elec_pos.shape[0])

    @property
    def n_col(self) -> int:
        return(self.__elec_pos.shape[1])

    def plot_grid(self,ax: plt.Axes, raw_idx: bool = False) -> None:
        norm = self.__elec_pos.copy()
        flipped = np.flip(self.__elec_pos,axis = 0)
        norm = flipped.copy()
        norm[norm>0] = 1
        cmap = colors.ListedColormap(['whitesmoke','goldenrod'])
        ax.pcolormesh(np.arange(-0.5, norm.shape[1]), np.arange(-0.5, norm.shape[0]), norm, cmap=cmap, edgecolor='k')
        color_dict = {0: 'normal', 1: 'high', 2: 'very\nhigh'}
        for i in range(norm.shape[0]):
            for j in range(norm.shape[1]):
                if norm[i, j]>0:
                    if raw_idx:
                        ax.text(j, i, self.get_raw_idx(flipped[i, j]), ha='center', va='center')
                    else:
                        ax.text(j, i, flipped[i, j], ha='center', va='center')

        ax.grid(True, which='minor', axis='both', linestyle='-', color='k')
        ax.set_xlabel("x-axis")
        ax.set_ylabel("y-axis")
        ax.set_title("EMG array")
        if raw_idx:
            ax.set_title("EMG array (raw index)")
        
    def get_raw_idx(self,array_idx: int) -> int:
        return(self.__elec_to_raw[array_idx-1])

    def get_raw_key(self,array_idx: int) -> int:
        return(f"raw {self.__elec_to_raw[array_idx-1]}")

    def required_raw_keys(self) -> list[str]:
        return([f"raw {e}" for e in self.__elec_to_raw])
    
    def create_fig(self, label: bool = True) -> PltFig|list[plt.Axes]:
        fig, axs = plt.subplots(self.n_row,self.n_col)
        l = []
        for i in range(axs.shape[0]):
            for j in range(axs.shape[1]):
                axs[i,j].axis("off")
                if self.__elec_pos[i, j]>0:
                    l.append(axs[i,j])
                    if label:
                        axs[i,j].set_title(f'{self.__elec_pos[i, j]}')
        return(fig,l)

    def create_map() -> plt.Axes:
        pass


#https://www.neuronexus.com/files/surface/eeg/H32-EEG-Maps(32-ch).pdf
# Note: doesn't match what's there: https://www.neuronexus.com/products/electrode-arrays/surface-grids/
NeuroNexus_H32_tri = array_grid(elec_to_raw=__NeuroNexus32ch_to_ripple,elec_pos = __NeuroNexus32ch_idx) 


class HD_sEMG():
    def __init__(self,df: pd.DataFrame(), array: array_grid):
        self.__df = df
        self.__array = array
        self.__trigger: trigger.trigger|None = None
        self.__t = df["time"]
        self.__fs = 1/(self.t[1]-self.t[0])
        self.__eEMGs: list[eEMG] = self.__get_eEMGs()

    def __get_eEMGs(self) -> None: 
        l_eEMGs = []
        for e in range(self.__array.n_ch): 
            l_eEMGs.append(eEMG(self.__df[self.__array.get_raw_key(e+1)],self.__t))
        return(l_eEMGs)

    @property
    def trigger(self):
        return(self.__trigger)
    
    @trigger.setter
    def trigger(self, trigger):
        self.__trigger = trigger
        for eEMG in self.eEMGs:
            eEMG.trigger = trigger

    @property
    def t(self):
        return(self.__t)
    
    @property
    def fs(self):
        return(self.__fs)

    @property
    def eEMGs(self) -> list[eEMG]:
        return(self.__eEMGs) 

    @property
    def array(self) -> array_grid:
        return(self.__array) 

    def filter_eEMGs(self, f_LPF:float,f_HPF:float, n_LPF:int=5, n_HFP:int=5) -> None:
        for eEMG in self.eEMGs:
            eEMG.LPF(f_LPF,n_LPF)
            eEMG.HPF(f_HPF,n_HFP)

    def filter_eCMAPs():
        pass

    def get_eCMAPS(self, duration:float, delay:float|None = None, 
                    n_skip: int = 1, skip_last:bool = True) -> None:
        for eEMG in self.eEMGs:
            eEMG.get_eCMAPS(duration,delay,n_skip,skip_last)

    def __set_plot_ylim(self,axs:list[plt.Axes], ymin:float, ymax:float)-> None:
        for ax in axs:
            ax.set_ylim(1.1*ymin,1.1*ymax)

    def __plot_smthing(self,something:str, **kwargs) -> PltFig|list[plt.Axes]:
        fig,axs = self.array.create_fig()
        min_l = []
        max_l = []
        for i,ax in enumerate(axs):
            data = getattr(self.eEMGs[i],something)
            ax.plot(self.eEMGs[i].t,data, **kwargs)
            min_l.append(np.min(data))
            max_l.append(np.max(data))
        self.__set_plot_ylim(axs,np.min(min_l),np.max(max_l))
        return(fig,axs)

    def plot_raw(self, **kwargs) -> PltFig|list[plt.Axes]:
        fig,axs = self.__plot_smthing("raw")
        fig.suptitle('Raw EMG data')
        return(fig,axs)
    
    def plot_data(self, **kwargs) -> PltFig|list[plt.Axes]:
        fig,axs = self.__plot_smthing("data")
        fig.suptitle('EMG data')
        return(fig,axs)

    def plot_eCMAPs (self, **kwargs) -> PltFig|list[plt.Axes]:
        fig,axs = self.array.create_fig()
        min_l = []
        max_l = []
        for i,ax in enumerate(axs):
            min_eCMAP = []
            max_eCMAP = []
            for eCMAP in self.eEMGs[i].eCMAPS:
                ax.plot(eCMAP.t,eCMAP.data, **kwargs)
                min_eCMAP.append(np.min(eCMAP.data))
                max_eCMAP.append(np.max(eCMAP.data))
            min_l.append(np.min(min_eCMAP))
            max_l.append(np.max(max_eCMAP))
        self.__set_plot_ylim(axs,np.min(min_l),np.max(max_l))
        fig.suptitle('EMG eCMAPs')
        return(fig,axs)

    def plot_avg_eCMAP (self, **kwargs) -> PltFig|list[plt.Axes]:
        fig,axs = self.array.create_fig()
        min_l = []
        max_l = []
        for i,ax in enumerate(axs):
            ax.plot(self.eEMGs[i].avg_eCMAP.t,self.eEMGs[i].avg_eCMAP.data, **kwargs)
            min_l.append(np.min(self.eEMGs[i].avg_eCMAP.data))
            max_l.append(np.max(self.eEMGs[i].avg_eCMAP.data))
        self.__set_plot_ylim(axs,np.min(min_l),np.max(max_l))
        fig.suptitle('EMG average eCMAP')
        return(fig,axs)

    def data_2_np(self, method_name):
        arr = np.empty(self.array.shape)
        arr[:] = np.nan
        for i in range(arr.shape[0]):
            for j in range(arr.shape[1]):
                idx = self.array.elec_pos[i, j] - 1
                if (idx >=0):
                    arr[i, j] = getattr(self.eEMGs[idx].avg_eCMAP,method_name)
        return(arr)

    def test_heat(self,ax):
        #print([self.array.elec_pos])
        arr = self.data_2_np("rms")
        print(arr)

    
        norm = self.array.elec_pos.copy()
        flipped = np.flip(self.array.elec_pos,axis = 0)
        norm = flipped.copy()
        norm[norm>0] = 1
        #cmap = colors.ListedColormap(['whitesmoke','goldenrod'])
        sc = ax.pcolormesh(np.arange(-0.5, norm.shape[1]), np.arange(-0.5, norm.shape[0]), arr, cmap="viridis")#, edgecolor='k')
        return(sc)
        #upside down!!!
    #def plot_heatmap_test(self):
    #    print(self.eEMGs[self.array.elec_pos].rms)

"""
todo: uniform scale for plot_raw,plot_data,plot_eCMAPs,plot_avg_eCMAP
    generalize data_2_np 
    generalize test_heat --> incorrect electrode order
    
    to interpolation"""