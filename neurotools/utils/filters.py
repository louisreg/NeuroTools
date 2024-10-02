from scipy import signal


def butter_HP(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def butter_HPF(data, cutoff, fs, order=5):
    b, a = butter_HP(cutoff, fs, order=order)
    y = signal.filtfilt(b, a, data)
    return y

def butter_LP(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_LPF(data, cutoff, fs, order=5):
    b, a = butter_LP(cutoff, fs, order=order)
    y = signal.filtfilt(b, a, data)
    return y