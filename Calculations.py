import numpy as np 
from scipy.signal import welch
from colorama import Fore
import pandas as pd
from scipy.stats import kurtosis, entropy
import os

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="scipy")

"""------------------------------------------ Calculations for features ------------------------------------------"""

def calculate_power_mean(iq_data):
    power_mean = np.mean(np.abs(iq_data)**2)
    return power_mean


def calculate_snr(iq_data):
    signal_power = np.mean(np.abs(iq_data)**2)  
    noise_floor = np.var(iq_data)  
    snr = 10 * np.log10(signal_power / noise_floor)  
    return snr


def calculate_entropy(iq_data):

    iq_data_normalized = np.abs(iq_data) / np.max(np.abs(iq_data))
    
    hist, _ = np.histogram(iq_data_normalized, bins=50, range=(0, 1), density=True)
    
    hist = hist[hist > 0]  
    entropy = -np.sum(hist * np.log2(hist))  
    return entropy


def calculate_kurtosis(iq_data):
    iq_kurtosis = kurtosis(np.abs(iq_data))
    return iq_kurtosis


def calculate_psd(iq_data, fs=2e6, nperseg=1024):
    freqs, psd = welch(iq_data, fs=fs, nperseg=nperseg)
    mean_psd = np.mean(psd)
    return mean_psd


def calculate_papr(iq_data):
    magnitude_squared = np.abs(iq_data) ** 2
    peak_power = np.max(magnitude_squared)
    avg_power = np.mean(magnitude_squared)

    if avg_power > 0:
        papr = peak_power / avg_power
    else:
        papr = 0 
        
    return papr

"""------------------------------------------ End of calucations ------------------------------------------"""


def feature_for_live(sample_file):

    power_mean = calculate_power_mean(sample_file)
    snr = calculate_snr(sample_file)
    entropy_value = calculate_entropy(sample_file)
    kurtosis_value = calculate_kurtosis(sample_file)
    psd_mean = calculate_psd(sample_file)
    papr = calculate_papr(sample_file)


    return pd.DataFrame([[power_mean, snr, papr, psd_mean]],
                            columns=['Power', 'SNR','PAPR', 'PSD Mean'])
