import numpy as np
import soundfile as sf
from scipy.signal import find_peaks
from typing import List, Dict
import Datagame

def detect_peaks(audio: np.ndarray, sr: int, threshold_ratio=0.05, min_time_between_peaks=0.2):
    audio = audio / np.max(np.abs(audio))
    energy = audio ** 2

    window_size = int(0.01 * sr)
    smoothed = np.convolve(energy, np.ones(window_size)/window_size, mode='same')

    threshold = threshold_ratio * np.max(smoothed)

    min_distance = int(min_time_between_peaks * sr)
    peaks, _ = find_peaks(smoothed, height=threshold, distance=min_distance)

    return [round(p / sr, 3) for p in peaks]

def load_and_detect(
    path: str,
    label: int,
    threshold_ratio=0.05,
    time_offset: float = 0.0,
    fall_speed: float = 500.0
) -> List[Dict]:
    y, sr = sf.read(path)
    if y.ndim > 1:
        y = y.mean(axis=1)
    peaks = detect_peaks(y, sr, threshold_ratio)
    return [
        {
            "time": round(t + time_offset, 3),
            "type": label,
            "speed": fall_speed
        }
        for t in peaks
    ]
global l
def generate_notes_from_parts(
    kick_path: str,
    snare_path: str,
    hihat_closed_path: str,
    hihat_open_path: str,
    instrumental_path: str = None,
    time_offset: float = 0.0,
    fall_speed: float = 500.0
) -> List[Dict]:
    notes = []
    notes += load_and_detect(kick_path, 0, time_offset=time_offset, fall_speed=fall_speed)
    notes += load_and_detect(snare_path, 1, time_offset=time_offset, fall_speed=fall_speed)
    #notes += load_and_detect(hihat_closed_path, 3, time_offset=time_offset, fall_speed=fall_speed)
    notes += load_and_detect(hihat_open_path, 2, time_offset=time_offset, fall_speed=fall_speed)

    notes.sort(key=lambda note: note["time"])
    return notes