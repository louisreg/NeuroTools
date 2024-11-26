from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np
from numpy.typing import NDArray
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.figure import Figure as PltFig

from .emg_channel import eEMG
from ..utils import trigger
from scipy import interpolate




if TYPE_CHECKING:
    from .spatial_filtering import kernel 



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

____NeuroNexus32ch_interp_idx = np.array([[np.nan, np.nan, 17, 16, np.nan, np.nan],
                                          [np.nan, 18, 60, 59, 15, np.nan],
                                          [20, 58, 19, 14, 57, 13],
                                          [56, 21, 55, 54, 12, 53],
                                          [23, 52, 22, 11, 51, 10],
                                          [50, 24, 49, 48, 9, 47],
                                          [26, 46, 25, 8, 45, 7],
                                          [44, 27, 43, 42, 6, 41],
                                          [29, 40, 28, 5, 39, 4],
                                          [38, 30, 37, 36, 3, 35],
                                          [32, 34, 31, 2, 33, 1]])


class array_grid():
    def __init__(self,elec_pos:NDArray,elec_to_raw:NDArray):

        self.__elec_pos: NDArray = np.nan_to_num(elec_pos,0)
        self.__elec_pos = np.int32(self.__elec_pos)
        self.__elec_to_raw: NDArray = elec_to_raw
        self.__n_ch: int = len(self.__elec_pos[self.__elec_pos>0])

        self.__fill_elec_to_raw()

    @property
    def n_ch(self) -> int:
        return(self.__n_ch)
    
    @property
    def elec_to_raw(self) -> NDArray:
        return(self.__elec_to_raw)
    
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
    
    def __fill_elec_to_raw(self) -> None:
        if len(self.elec_to_raw) < self.n_ch:
            n_raw = len(self.elec_to_raw)
            add_ = np.arange(n_raw+1, self.n_ch+1,step =1)
            self.__elec_to_raw = np.concatenate((self.elec_to_raw, add_))

    def elec_in_range(self, elec: int) -> bool:
        """Return True if elec is a valide electrode number

        Parameters
        ----------
        elec : int
            Electrode number

        Returns
        -------
        bool
            True if elec is a valide electrode number
        """
        if elec > 0 and elec <= self.n_ch:
            return(True)
        return(False)

    def idx_in_range(self, idx: int) -> bool:
        """Return True if elec index is a valide index

        Parameters
        ----------
        elec : int
            Electrode index

        Returns
        -------
        bool
            True if elec is a valid electrode index
        """
        if idx >= 0 and idx < self.n_ch:
            return(True)
        return(False)

    def get_elec(self, idx: int) -> int:
        """Returns the electrode number on the grid array 

        Parameters
        ----------
        idx : int
            electrode index 

        Returns
        -------
        int
            electrode number
        """
        if not self.idx_in_range(idx):
            raise ValueError(f"Invalide electrode idx. Must be comprised between 0 and n_ch - 1 ({self.n_ch-1})")
        return(idx+1)
    
    def get_elec_idx(self, elec: int) -> int:
        """Returns the electrode index 

        Parameters
        ----------
        elec : int
            Electrode number

        Returns
        -------
        int
            Electrode index
        """
        if not self.elec_in_range(elec):
            raise ValueError(f"Invalide electrode number. Must be comprised between 1 and n_ch ({self.n_ch})")
        return(elec-1)

    def get_elec_xy(self, elec: int) -> int|int:
        """_summary_

        Parameters
        ----------
        elec : int
            Electrode number

        Returns
        -------
        int
            Electrode x position in the array grid
        int
            Electrode y position in the array grid
        """
        idxs = np.where(self.elec_pos==elec)
        return(idxs[0][0],idxs[1][0])
    
    def get_xy(self) -> NDArray|NDArray:
        """Return (x,y) coordinates of valid electrode number
        Returns
        -------
        NDArray,NDArray
            2D grid
        """
        idxs = np.where(self.elec_pos>0)
        return(idxs[1],idxs[0])

    def get_elect_raw_idx(self,elec: int) -> int:
        """Return electrode ripple raw index.

        Parameters
        ----------
        elec : int
            Electrode name, between 1 and n_ch

        Returns
        -------
        int
            Ripple raw index
        """
        return(self.__elec_to_raw[self.get_elec_idx(elec)])

    def get_elect_raw_key(self,elec: int) -> int:
        """Return electrode ripple raw key.

        Parameters
        ----------
        elec : int
            Electrode name, between 1 and n_ch

        Returns
        -------
        int
            Ripple raw index
        """
        return(f"raw {self.__elec_to_raw[self.get_elec_idx(elec)]}")

    def required_raw_keys(self) -> list[str]:
        """Return the list of required ripple keys

        Returns
        -------
        list[str]
            List of ripple keys
        """
        return([f"raw {e}" for e in self.__elec_to_raw])

    def plot_grid(self,ax: plt.Axes, raw_idx: bool = False) -> None:
        norm = self.elec_pos.copy()
        norm[norm>0] = 1
        cmap = colors.ListedColormap(['whitesmoke','goldenrod'])
        ax.pcolormesh(np.arange(-0.5, norm.shape[1]), np.arange(-0.5, norm.shape[0]), norm, cmap=cmap, edgecolor='k')
        for i in range(norm.shape[0]):
            for j in range(norm.shape[1]):
                if norm[i, j]>0:
                    if raw_idx:
                        ax.text(j, i, self.get_elect_raw_idx(self.elec_pos[i, j]), ha='center', va='center')
                    else:
                        ax.text(j, i, self.elec_pos[i, j], ha='center', va='center')

        ax.grid(True, which='minor', axis='both', linestyle='-', color='k')
        ax.yaxis.set_inverted(True)
        ax.set_xlabel("x-axis")
        ax.set_ylabel("y-axis")
        ax.set_title("EMG array")
        if raw_idx:
            ax.set_title("EMG array (raw index)")
        

    def create_fig(self, label: bool) -> PltFig|list[plt.Axes]:
        fig, axs = plt.subplots(self.n_row,self.n_col)
        out_axs = [0] * self.n_ch
        for i in range(axs.shape[0]):
            for j in range(axs.shape[1]):
                axs[i,j].axis("off")
                if (self.__elec_pos[i, j]>0) and (self.elec_pos[i, j]<=self.n_ch):
                    out_axs[self.get_elec_idx(self.elec_pos[i, j])] = axs[i,j]
                    if label:
                        axs[i,j].set_title(f'{self.__elec_pos[i, j]}')
        return(fig,out_axs)

    def create_grid(self, n_step:int) -> NDArray|NDArray:
        """Create a 2D grid with n_step xy points 
        
        Parameters
        ----------
        n_step : int
            Step size of the grid 

        Returns
        -------
        NDArray,NDArray
            2D grid
        """
        X = np.linspace(0, self.n_col-1,num = n_step)
        Y = np.linspace(0, self.n_row-1,num = n_step)
        return(np.meshgrid(X,Y))

#https://www.neuronexus.com/files/surface/eeg/H32-EEG-Maps(32-ch).pdf
# Note: doesn't match what's there: https://www.neuronexus.com/products/electrode-arrays/surface-grids/
NeuroNexus_H32_tri = array_grid(elec_to_raw=__NeuroNexus32ch_to_ripple,
                                elec_pos = __NeuroNexus32ch_idx) 

NeuroNexus_H32_tri_interp = array_grid(elec_to_raw=__NeuroNexus32ch_to_ripple,
                                elec_pos = ____NeuroNexus32ch_interp_idx) 


class HD_sEMG():
    def __init__(self,df: pd.DataFrame, array: array_grid):
        self.__df = df
        self.__array = array
        self.__trigger: trigger.trigger|None = None
        self.__sp_kernel: kernel|None = None
        self.__t = df["time"]
        self.__fs = 1/(self.t[1]-self.t[0])
        self.__eEMGs: list[eEMG] = self.__get_eEMGs()

    def __get_eEMGs(self) -> list[eEMG]: 
        l_eEMGs = []
        for e_idx in range(self.__array.n_ch): 
            elec = self.__array.get_elec(e_idx)
            l_eEMGs.append(eEMG(self.__df[self.__array.get_elect_raw_key(elec)],self.__t))
        return(l_eEMGs)
    
    @property
    def sp_kernel(self):
        return(self.__sp_kernel)
    
    @sp_kernel.setter
    def sp_kernel(self,kernel:kernel):
        self.__sp_kernel = kernel

    def raw_to_1Darray(self) -> NDArray: 
        return(self.__emg_to_1D(raw=True))
    
    def data_to_1Darray(self) -> NDArray: 
        return(self.__emg_to_1D(raw=False))
    
    def raw_to_2Darray(self) -> NDArray: 
        return(self.__raw_to_2D(raw=True))
    
    def data_to_2Darray(self) -> NDArray: 
        return(self.__raw_to_2D(raw=False))
    
    def __emg_to_1D(self, raw:bool) -> NDArray: 
        pt = self.array.get_xy() 
        arr = np.empty((self.array.n_ch,len(self.t)))
        for i, (x,y) in enumerate(zip(pt[0],pt[1])):
            eEMG_numb = self.array.elec_pos[y,x]
            if raw:
                arr[i,:] = self.eEMGs[eEMG_numb-1].raw
            else:
                arr[i,:] = self.eEMGs[eEMG_numb-1].data
        return(arr)
    
    def __raw_to_2D(self, raw:bool) -> NDArray:
        arr = np.empty((self.array.shape[0],self.array.shape[1],len(self.t)))
        arr[:] = np.nan
        for i in range(arr.shape[0]):
            for j in range(arr.shape[1]):
                if self.array.elec_pos[i, j] <= self.array.n_ch:
                    idx = self.array.elec_pos[i, j] - 1
                    if (idx >=0):
                        if raw:
                            arr[i, j, :] = self.eEMGs[idx].raw
                        else:
                            arr[i, j, :] = self.eEMGs[idx].data
        return(arr)

    @property
    def df(self):
        return(self.__df)

    @property
    def trigger(self):
        return(self.__trigger)
    
    @trigger.setter
    def trigger(self, trigger):
        self.__trigger = trigger
        for e_emg in self.eEMGs:
            e_emg.trigger = trigger

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

    def get_eEMG(self, elec: int) -> eEMG:
        """Return eEMG object corresponding to electrode number elec

        Parameters
        ----------
        elec : int
            Electrode number

        Returns
        -------
        eEMG
            eEMG object of elec
        """
        if self.array.elec_in_range(elec):
            return(self.eEMGs[self.array.get_elec_idx(elec)])
        else:
            raise ValueError(f"Invalide electrode number. Must be comprised between 1 and n_ch ({self.array.n_ch})") 

    def filter_eEMGs(self, f_LPF:float,f_HPF:float, n_LPF:int=5, n_HFP:int=5) -> None:
        for e_emg in self.eEMGs:
            e_emg.LPF(f_LPF,n_LPF)
            e_emg.HPF(f_HPF,n_HFP)

    def filter_eCMAPs():
        pass

    def get_eCMAPS(self, duration:float, delay:float|None = None, 
                    n_skip: int = 1, skip_last:bool = True) -> None:
        for e_emg in self.eEMGs:
            e_emg.get_eCMAPS(duration,delay,n_skip,skip_last)

    def __set_plot_ylim(self,axs:list[plt.Axes], ymin:float, ymax:float)-> None:
        for ax in axs:
            ax.set_ylim(1.1*ymin,1.1*ymax)

    def __plot_smthing(self,something:str, label: bool,  **kwargs) -> PltFig|list[plt.Axes]:
        fig,axs = self.array.create_fig(label)
        min_l = []
        max_l = []
        for i,ax in enumerate(axs):
            data = getattr(self.eEMGs[i],something)
            ax.plot(self.eEMGs[i].t,data, **kwargs)
            if not np.isnan(data.any()):
                min_l.append(np.min(data))
                max_l.append(np.max(data))
        self.__set_plot_ylim(axs,np.min(min_l),np.max(max_l))
        return(fig,axs)

    def plot_raw(self,label: bool = True, **kwargs) -> PltFig|list[plt.Axes]:
        fig,axs = self.__plot_smthing("raw",label, **kwargs)
        fig.suptitle('Raw EMG data')
        return(fig,axs)
    
    def plot_data(self,label: bool = True, **kwargs) -> PltFig|list[plt.Axes]:
        fig,axs = self.__plot_smthing("data",label,**kwargs)
        fig.suptitle('EMG data')
        return(fig,axs)

    def __create_eCMAPS_fig(self,label: bool) -> PltFig|list[plt.Axes]:
        return(self.array.create_fig(label))

    def plot_eCMAPs (self, label: bool = True, **kwargs) -> PltFig|list[plt.Axes]:
        fig,axs = self.__create_eCMAPS_fig(label)
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

    def plot_avg_eCMAP (self, label: bool = True, **kwargs) -> PltFig|list[plt.Axes]:
        fig,axs = self.__create_eCMAPS_fig(label)
        min_l = []
        max_l = []
        for i,ax in enumerate(axs):
            ax.plot(self.eEMGs[i].avg_eCMAP.t,self.eEMGs[i].avg_eCMAP.data, **kwargs)
            min_l.append(np.min(self.eEMGs[i].avg_eCMAP.data))
            max_l.append(np.max(self.eEMGs[i].avg_eCMAP.data))
        self.__set_plot_ylim(axs,np.min(min_l),np.max(max_l))
        fig.suptitle('EMG average eCMAP')
        return(fig,axs)

    def get_eEMG_ax(self, axs:list[plt.Axes], elec: int) -> plt.Axes:
        """Return the ax in the axs list corresponding to the electrode number elec

        Parameters
        ----------
        elec : int
            Electrode number

        Returns
        -------
        plt.Axes
            plt.Axes of the electrode number elec
        """

        if self.array.elec_in_range(elec):
            return(axs[self.array.get_elec_idx(elec)])
        else:
            raise ValueError(f"Invalide electrode number. Must be comprised between 1 and n_ch ({self.array.n_ch})") 

    def __eCMAP_data_2_np(self, method_name):
        arr = np.empty(self.array.shape)
        arr[:] = np.nan
        for i in range(arr.shape[0]):
            for j in range(arr.shape[1]):
                if self.array.elec_pos[i, j] <= self.array.n_ch:
                    idx = self.array.elec_pos[i, j] - 1
                    if (idx >=0):
                        arr[i, j] = getattr(self.eEMGs[idx].avg_eCMAP,method_name)
        return(arr)

    def __eCMAP_avg_2_np(self):
        pt = self.array.get_xy() 
        arr = np.empty((self.array.n_ch,len(self.eEMGs[0].avg_eCMAP.t)))
        for i, (x,y) in enumerate(zip(pt[0],pt[1])):
            eEMG_numb = self.array.elec_pos[y,x]
            arr[i,:] = self.eEMGs[eEMG_numb-1].avg_eCMAP.data
        return(arr)

    def __eCMAP_avg_2_np(self) -> NDArray:
        arr = np.empty((self.array.shape[0],self.array.shape[1],len(self.eEMGs[0].avg_eCMAP.t)))
        arr[:] = np.nan
        for i in range(arr.shape[0]):
            for j in range(arr.shape[1]):
                if self.array.elec_pos[i, j] <= self.array.n_ch:
                    idx = self.array.elec_pos[i, j] - 1
                    if (idx >=0):
                        arr[i, j, :] = self.eEMGs[idx].avg_eCMAP.data
        return(arr)

    def plot_heatmap_eCMAP(self,ax:plt.Axes, data:str, n_interp: int|None = None):
        arr = self.__eCMAP_data_2_np(data)
        if (n_interp):
            arr = arr[~np.isnan(arr)]
            pt = self.array.get_xy() 
            X,Y = self.array.create_grid(n_interp)
            arr = interpolate.griddata(pt,arr,(X,Y),method='cubic')
            ax.set_xlim(np.min(pt[0]),np.max(pt[0]))
            ax.set_ylim(np.min(pt[1]),np.max(pt[1]))
        else:
            x = np.arange(-0.5, arr.shape[1])
            y = np.arange(-0.5, arr.shape[0])
            X, Y = np.meshgrid(x,y)
        ax.yaxis.set_inverted(True)
        sc = ax.pcolormesh(X,Y, arr, cmap="viridis")#, edgecolor='k')
        
        return(sc)
    
    def plot_avg_3D_timeshot(self,ax:plt.Axes, t_idx: int, min: float|None = None, max: float|None = None ,n_interp: int|None = None):
        arr = self.__eCMAP_avg_2_np()
        data = arr[:,:,t_idx]
        if (n_interp):
            X,Y = self.array.create_grid(n_interp)
            data = data[~np.isnan(data)]
            pt = self.array.get_xy() 
            interp = interpolate.griddata(pt,data,(X,Y),method='cubic')
        else:
            x = np.arange(0, self.array.n_col, 1)
            y = np.arange(0, self.array.n_row, 1)
            X, Y = np.meshgrid(x,y)

        not_nan = np.argwhere(~np.isnan(interp))
        surf = ax.plot_trisurf(X[not_nan[:,0],not_nan[:,1]], Y[not_nan[:,0],not_nan[:,1]], interp[not_nan[:,0],not_nan[:,1]], 
                            cmap="Spectral", antialiased=True, vmin = min, vmax = max)
        
        return(surf)






##hd_sEMG Interpolation functions!!

def __interpolate_array (hd_semg: HD_sEMG, array: array_grid, raw: bool) -> NDArray:
    x = np.linspace(0, array.n_col-1,num = array.n_col)
    y = np.linspace(0, array.n_row-1,num = array.n_row)
    X,Y = np.meshgrid(x,y)
    pt = hd_semg.array.get_xy()
    if raw:
        return(interpolate.griddata(pt,hd_semg.raw_to_1Darray(),(X,Y),method='cubic'))
    else:
        return(interpolate.griddata(pt,hd_semg.data_to_1Darray(),(X,Y),method='cubic'))

def __interpolate_to_df(hd_semg: HD_sEMG, array: array_grid, raw: bool) -> pd.DataFrame:
    interp = __interpolate_array(hd_semg, array, raw)
    df = pd.DataFrame()
    for e_idx in range(array.n_ch): 
        elec = array.get_elec(e_idx)
        key = array.get_elect_raw_key(elec)
        elec_xy = array.get_elec_xy(elec)
        df[key] = interp[elec_xy[0],elec_xy[1],:]
    df["time"] = hd_semg.df["time"]
    return(df)

def interpolate_HD_sEMG(hd_semg: HD_sEMG, array: array_grid, raw: bool) -> HD_sEMG:
    df  = __interpolate_to_df(hd_semg, array, raw)
    return(HD_sEMG(df = df, array = array))   

