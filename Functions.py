from picamera2 import Picamera2
import os
from datetime import datetime
from PIL import Image
import numpy as np
import time
from python_hackrf import pyhackrf
import subprocess
from colorama import Fore
import threading
from Calculations import *
import pickle
from pyfiglet import Figlet
import sys


def auto_camera():

    image_path = "/home/Josh/ObliviScan/Images"
    os.makedirs(image_path, exist_ok=True)

    picam2 = Picamera2()
    config = picam2.create_preview_configuration()
    picam2.configure(config)
    picam2.start()

    print("Capturing images every 5 seconds. Press Ctrl+C to stop.")

    try:
        while True:
            frame = picam2.capture_array()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"drone_{timestamp}.png"
            filepath = os.path.join(image_path, filename)

            img = Image.fromarray(frame)
            if img.mode == "RGBA":
                img = img.convert("RGB")

            img.save(filepath)
            print(f"Image saved: {filepath}")

            time.sleep(5)

    except KeyboardInterrupt:
        print("Stopped by user.")

    finally:
        picam2.stop()
        picam2.close()


last_idx = 0

def loadbar():
    for i in range(12):
        time.sleep(0.1)
        print(Fore.YELLOW + '#', end='', flush=True)

def find_hackRF():
    try:
        result = subprocess.run(["lsusb"], capture_output=True, text=True)
        return any("OpenMoko" in line or "HackRF" in line for line in result.stdout.splitlines())
    except Exception as e:
        print(Fore.RED + f"\nError checking SDR with lsusb: {e}")
        return False
    

def check_camera():
    test_image = "/tmp/test.jpg"

    try:
        result = subprocess.run(["rpicam-still", "-t", "10", "-n", "-o", test_image], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if os.path.exists(test_image) and result.returncode == 0:
            os.remove(test_image)
            return True
        else:
            print(Fore.RED + "\nIssue with camera, reconnect and try again")
            print(result.stderr)
            return False
        
    except FileNotFoundError as e:
        print(f"Camera check error {e}")
        return False


def startup_checks():
    print(Fore.YELLOW + "Running startup checks\n")
    loadbar()

    camera_ok = check_camera()
    hack_rf_ok = find_hackRF()

    if not camera_ok or not hack_rf_ok:
        print(Fore.RED + "\nIssue loading Camera or SDR")
        sys.exit(1)
    print("\n")
    print(Fore.YELLOW + "-" * 35)
    print(Fore.GREEN + "HackRF One found")
    print(Fore.GREEN + "Camera Module found")
    print(Fore.YELLOW + "-" * 35)
    print(Fore.GREEN + "\nStartup checks completed")


def live_sweep(duration=2.0, sample_rate=1e6,
               baseband_filter=1e6, lna_gain=32, vga_gain=40):
    
    f = Figlet(font='small')

    channels = [2412e6, 2417e6, 2422e6, 2427e6, 2432e6,
                2437e6, 2442e6, 2447e6, 2452e6, 2457e6, 2462e6]

    output_dir = os.path.expanduser("Live_data/")
    os.makedirs(output_dir, exist_ok=True)

    while True:
        pyhackrf.pyhackrf_init()
        sdr = pyhackrf.pyhackrf_open()
        allowed_bw = pyhackrf.pyhackrf_compute_baseband_filter_bw_round_down_lt(baseband_filter)

        sdr.pyhackrf_set_sample_rate(sample_rate)
        sdr.pyhackrf_set_baseband_filter_bandwidth(allowed_bw)
        sdr.pyhackrf_set_lna_gain(lna_gain)
        sdr.pyhackrf_set_vga_gain(vga_gain)
        sdr.pyhackrf_set_amp_enable(False)
        sdr.pyhackrf_set_antenna_enable(False)

        iq_buffer = []
        buffer_lock = threading.Lock()
        stop_event = threading.Event()

        def rx_callback(device, buffer, buffer_length, valid_length):
            iq = np.frombuffer(buffer[:valid_length], dtype=np.int8)
            iq = iq[::2] + 1j * iq[1::2]
            iq = iq / 128.0
            with buffer_lock:
                iq_buffer.append(iq.copy())
            return 0

        sdr.set_rx_callback(rx_callback)

        def consumer_worker():
            while not stop_event.is_set() or iq_buffer:
                with buffer_lock:
                    if iq_buffer:
                        chunk = iq_buffer.pop(0)
                    else:
                        chunk = None

                if chunk is not None:
                    with buffer_lock:
                        iq_data_storage.append(chunk)
                else:
                    time.sleep(0.01)

        try:
            drone_votes = 0
            total_channels = len(channels)

            for i, freq in enumerate(channels):
                sdr.pyhackrf_set_freq(freq)

                iq_data_storage = []

                stop_event.clear()
                consumer_thread = threading.Thread(target=consumer_worker)
                consumer_thread.start()

                with buffer_lock:
                    iq_buffer.clear()

                sdr.pyhackrf_start_rx()
                time.sleep(duration)
                sdr.pyhackrf_stop_rx()

                stop_event.set()
                consumer_thread.join()

                iq_data = np.concatenate(iq_data_storage)
                prediction, confidence = modelTest(iq_data)

                bar = '#' * (i + 1)
                print(Fore.YELLOW + f"\r{bar}", end='', flush=True)

                if prediction == 1 and confidence >= 80:
                    drone_votes += 1

            percent_drone = (drone_votes / total_channels) * 100
            time.sleep(3)

            return percent_drone
        
        finally:
            sdr.pyhackrf_close()
            pyhackrf.pyhackrf_exit()
            print(Fore.GREEN + "\n2.4GHz sweep complete.")
        

def modelTest(sample_file):

    with open("KNN_model.pkl", "rb") as model_file:
        KNN = pickle.load(model_file)

    with open("KNN_scaler.pkl", "rb") as scaler_file:
        scaler = pickle.load(scaler_file)

    new_features = feature_for_live(sample_file)
    new_features_selected = new_features[['Power', 'SNR', 'PAPR', 'PSD Mean']]  
    new_features_scaled = scaler.transform(new_features_selected)
    prediction = KNN.predict(new_features_scaled)
    prediction_proba = KNN.predict_proba(new_features_scaled)
    confidence = np.max(prediction_proba) * 100

    return prediction[0], confidence


def run_detection():

    subprocess.run(["./Detection.sh"], capture_output=True, text=True)


def detect_and_track():

    f = Figlet(font='small')
    
    percent_drone = live_sweep(duration=2.0)

    if percent_drone >= 80:
        print(Fore.RED + f.renderText("Drone Detected "))
        print(Fore.YELLOW + f"Detection confidence:  {percent_drone:.2f}%")
        run_detection()
    else:
        print(Fore.GREEN + f.renderText("No Drone Detected "))
