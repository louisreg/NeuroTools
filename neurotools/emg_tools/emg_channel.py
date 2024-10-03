import numpy as np
from scipy import signal
from numpy.typing import NDArray
import matplotlib.pyplot as plt
from ..utils import trigger, filters
from .muap import eCMAP


class eEMG():
    def __init__(self,data:NDArray,t:NDArray):
        self.__raw = np.array(data)
        self.__data = np.array(data)
        self.__t = np.array(t)
        self.__n_samples = len(data)
        self.__trigger: trigger.trigger|None = None
        self.__fs = 1/(t[1]-t[0])
        self.__eCMAPS: list[eCMAP] = []
        self.__avg_eCMAPS: NDArray|None = None
        self.__t_eCMAPS: NDArray|None = None

    @property
    def trigger(self):
        return(self.__trigger)
    
    @trigger.setter
    def trigger(self, trigger):
        self.__trigger = trigger

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
    
    @property
    def eCMAPS(self):
        return(self.__eCMAPS)

    @property
    def avg_eCMAP(self) -> NDArray:
        if self.__avg_eCMAPS is None:
            self.average_eCMAPS()
        return(self.__avg_eCMAPS)

    @property
    def rms(self):
        return(np.sqrt(np.mean(self.__data**2)))
    

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
    
    def get_eCMAPS(self, duration:float, delay:float|None = None,
                          n_skip: int = 1, skip_last:bool = True) -> list[eCMAP]|NDArray:
        """
        Get trigger-event aligned evoked muaps

        Parameters
        ----------
        duration : float
            After-event + delay duration
        delay : float | None, optional
            After-event delay, by default None 
        n_skip : int
            Number of event to skip, by default skip the first one
        skip_last : bool, optional
            If true, skip the last event, by default True

        Returns
        -------
        list[eCMAP]
            Returns a list of triger-aligned eCMAP objects
        NDArray
            Time vector of an eCMAP
        """


        if self.__trigger is None:
            raise("No trigger was attached to this EMG channel")
        
        inter_event_idx = self.__trigger.get_inter_event_sample()
        inter_event_idx = inter_event_idx[n_skip:]
        if skip_last: 
            inter_event_idx = inter_event_idx[0:-1]
        n_delay = 0
        if delay is not None:
            n_delay = int(self.__fs*delay)
        n_duration = int(self.__fs*duration)
        eCMAPS = []
        time = np.linspace(0,duration,num=n_duration)
        for inter_event in inter_event_idx: 
            idx = inter_event[n_delay:n_delay+n_duration]
            data = self.__data[idx]
            eCMAPS.append(eCMAP(data,time))
        self.__eCMAPS = eCMAPS
        self.__t_eCMAPS = eCMAP(data,time).t
        return(self.__eCMAPS,self.__t_eCMAPS)
    
    def average_eCMAPS(self) -> eCMAP:
        data = np.array([])
        self.__avg_eCMAPS = data
        if len(self.__eCMAPS):
            arg = [a.data for a in self.__eCMAPS]
            data = np.vstack(arg)
            self.__avg_eCMAPS = eCMAP(np.mean(data,axis = 0), self.__t_eCMAPS)
        return(self.__avg_eCMAPS)


    def plot_raw(self, ax: plt.Axes, **kwargs):
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("EMG (µV)")
        ax.set_xlim(np.min(self.__t),np.max(self.__t))
        ax.plot(self.__t,self.__raw, **kwargs)

    def plot(self, ax: plt.Axes, **kwargs):
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("EMG (µV)")
        ax.set_xlim(np.min(self.__t),np.max(self.__t))
        ax.plot(self.__t,self.__data, **kwargs)

    def plot_eCMAPS(self, ax: plt.Axes, **kwargs):
        if self.__eCMAPS is not None:
            for eCMAPS in self.__eCMAPS:
                eCMAPS.plot(ax, **kwargs)

    def plot_avg_eCMAP(self, ax: plt.Axes, **kwargs):
        if self.__eCMAPS is not None:
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("EMG (µV)")
            ax.set_xlim(np.min(self.__t_eCMAPS),np.max(self.__t_eCMAPS))
            ax.plot(self.__t_eCMAPS,self.avg_eCMAP.data, **kwargs)