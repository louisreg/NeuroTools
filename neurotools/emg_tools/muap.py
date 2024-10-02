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
    def t(self):
        return(self.__t)
    
    @property
    def fs(self):
        return(self.__fs)

    @property
    def raw(self):
        return(self.__raw)
    
    @property
    def data(self):
        return(self.__data)
    
    @property
    def n_samples(self):
        return(self.__n_samples)
    
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