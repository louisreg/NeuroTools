import numpy as np
from scipy import signal
from numpy.typing import NDArray
import matplotlib.pyplot as plt
from ..utils import filters

class eCMAP():
    def __init__(self,data:NDArray,t:NDArray):
        self.__raw = np.array(data)
        self.__data = np.array(data)
        self.__t = np.array(t)
        self.__n_samples = len(data)
        self.__fs = 1/(t[1]-t[0])

    @property
    def t(self) -> NDArray:
        return(self.__t)
    
    @property
    def fs(self) -> float:
        return(self.__fs)

    @property
    def raw(self) -> NDArray:
        return(self.__raw)
    
    @property
    def data(self) -> NDArray:
        return(self.__data)
    
    @property
    def n_samples(self) -> int:
        return(self.__n_samples)

    @property
    def min(self) -> float:
        return(np.min(self.__data))
    
    @property
    def max(self) -> float:
        return(np.max(self.__data))

    @property
    def min_idx(self) -> int:
        return(np.where(self.__data==self.min)[0][0])
    
    @property
    def max_idx(self) -> int:
        return(np.where(self.__data==self.max)[0][0])
    
    @property
    def peak2peak(self) -> float:
        return(np.abs(np.max(self.__data)-np.min(self.__data)))

    @property
    def rms(self)->float:
        return(np.sqrt(np.mean(self.__data**2)))

    @property
    def ttmax(self)-> float:  #time to max
        return(self.__t[self.max_idx])

    @property
    def ttmin(self)-> float:   #time to min
        return(self.__t[self.min_idx])

    def __tmin_tmax_10(self, max: bool)-> int:
        idxs = np.where(self.__rectify()>0.1*self.max)[0]
        if max:
            return(idxs[-1])
        else:
            return(idxs[0])

    @property
    def tmax_10_idx(self)-> int:
        return(self.__tmin_tmax_10(True))

    @property
    def tmin_10_idx(self)-> int:
        return(self.__tmin_tmax_10(False))

    @property
    def tmax_10(self)-> float:
        return(self.__t[self.tmax_10_idx])

    @property
    def tmin_10(self)-> float:
        return(self.__t[self.tmin_10_idx])

    @property
    def latency(self)-> float:
        return(self.tmin_10)

    @property
    def duration(self)-> float:
        return(self.tmax_10-self.tmin_10)

    def __rectify(self)-> NDArray:
        return(np.sqrt(self.__data**2))


    def HPF(self,cutoff:float, order:int=5) -> NDArray:
        """Filter raw data with a butterworth high-pass filter

        Parameters
        ----------
        cutoff : float
            High-pass cutof frequency
        order : int, optional
            HPF filter order, by default 5

        Returns
        -------
        NDArray
            filtered data
        """
        self.__data = filters.butter_HPF(self.__data, cutoff, self.__fs, order)
        return(self.__data)
    
    def LPF(self,cutoff:float, order:int=5) -> NDArray:
        """Filter raw data with a butterworth low-pass filter

        Parameters
        ----------
        cutoff : float
            low-pass cutof frequency
        order : int, optional
            LPF filter order, by default 5

        Returns
        -------
        NDArray
            filtered data
        """
        self.__data = filters.butter_LPF(self.__data, cutoff, self.__fs, order)
        return(self.__data)
    
    def plot_raw(self, ax: plt.Axes, **kwargs):
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Trigger (µV)")
        ax.set_xlim(np.min(self.__t),np.max(self.__t))
        ax.plot(self.__t,self.__raw, **kwargs)

    def plot(self, ax: plt.Axes, **kwargs):
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Trigger (µV)")
        ax.set_xlim(np.min(self.__t),np.max(self.__t))
        ax.plot(self.__t,self.__data, **kwargs)