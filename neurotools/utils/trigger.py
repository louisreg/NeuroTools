import numpy as np
from scipy import signal
from numpy.typing import NDArray
import matplotlib.pyplot as plt

class trigger():
    def __init__(self,data:NDArray,t:NDArray):
        self.__data = np.array(data)
        self.__t = np.array(t)
        self.__normalized = None
        self.__n_samples = len(data)

    @property
    def t(self):
        return(self.__t)
    
    @property
    def raw(self):
        return(self.__data)
    
    @property
    def n_samples(self):
        return(self.__n_samples)
    
    def __normalize(self) -> NDArray:
        """Normalize trigger data between 0 and 1

        Returns
        -------
        NDArray
            Normalized trigger
        """

        if (self.__normalized) is None:
            self.__normalized =  self.__data.copy()
            self.__normalized[self.__normalized>2] = 1
            self.__normalized[self.__normalized!=1] = 0
        return(self.__normalized)
    
    @property
    def normalized(self):
        return(self.__normalize())
    
    def get_events(self) -> list[NDArray]|list[NDArray]|list[NDArray]:
        """Get the index, value and timing of each trigger event

        Returns
        -------
        list[NDArray]
            List of trigger index values of the event s
            List of trigger values of the events (should be 1)
            List of times at which the events occured
        """

        event_idx, _ = signal.find_peaks(self.__normalize(), height=0)
        for idx, _ in enumerate(event_idx):
            while self.__normalized[event_idx[idx]] == 1:
                event_idx[idx] -= 1
            event_idx[idx] += 1
        return(event_idx,self.__normalized[event_idx],self.__t[event_idx])
    

    def get_inter_event_sample(self) -> list[NDArray]:
        """Get the number of samples between each trigger event

        Returns
        -------
        list[NDArray]
            List of np.array containing the samples between each event
        """
        n_idx = np.arange(self.__n_samples)
        tr_start_idx,_,_ = self.get_events()
        n_event = len(tr_start_idx)
        n_list = []
        for pk_idx in range(n_event-1):
            n_start = tr_start_idx[pk_idx]
            n_stop = tr_start_idx[pk_idx+1]
            n_list.append(n_idx[n_start:n_stop])
        n_start = tr_start_idx[n_event-1]
        n_stop = n_idx[-1]
        n_list.append(n_idx[n_start:n_stop])
        return(n_list)
    
    def plot_raw(self, ax: plt.Axes, **kwargs):
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Trigger (µV)")
        ax.set_xlim(np.min(self.__t),np.max(self.__t))
        ax.plot(self.__t,self.__data, **kwargs)

    def plot_normalized(self, ax: plt.Axes, **kwargs):
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Trigger (norm.)")
        ax.set_xlim(np.min(self.__t),np.max(self.__t))
        ax.plot(self.__t,self.__normalize(), **kwargs)