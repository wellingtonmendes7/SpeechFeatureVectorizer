import os
import librosa
import numpy as np
import tgt  # For reading TextGrid files
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import warnings
import math

warnings.filterwarnings("ignore", category=UserWarning)

def band_limit_segment(segment, sr, lp_cutoff=500):
    """
    Returns a band-limited version of 'segment' by zeroing out
    frequencies above 'lp_cutoff' in the STFT, then reconstructing
    with inverse STFT.
    """
    # Use a larger n_fft for better frequency resolution
    n_fft_value = min(2048, len(segment))
    # Compute the magnitude+phase STFT (complex)
    stft_complex = librosa.stft(segment, n_fft=n_fft_value)
    # Frequency axis
    freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft_value)

    nyquist = sr / 2
    effective_cutoff = min(lp_cutoff, nyquist)

    # Create mask for frequencies <= effective_cutoff
    freq_mask = (freqs <= effective_cutoff)

    # Zero-out frequencies above the cutoff
    stft_complex[~freq_mask, :] = 0.0

    # Inverse STFT to recover time-domain band-limited signal
    band_limited_signal = librosa.istft(stft_complex)
    return band_limited_signal


def extract_features(wav_file, textgrid_file, tier_name,
                     min_freq=0, max_freq=8000, lp_cutoff=500):
    """
    Extract various acoustic features:
      - Intensity (dB) below lp_cutoff (default 500 Hz)
      - HNR below lp_cutoff (default 500 Hz)
      - Duration
      - ZCR (full band)
      - CoG (full-band up to max_freq) in Hz
      - CoG_log (log-frequency transform of CoG)
    """

    # Load audio file with native sampling rate
    y, sr = librosa.load(wav_file, sr=None)

    nyquist = sr / 2
    effective_max_freq = min(max_freq, nyquist)

    # Read the TextGrid
    tg = tgt.io.read_textgrid(textgrid_file)
    tier = tg.get_tier_by_name(tier_name)

    results = []

    for interval in tier.intervals:
        label = interval.text
        if label.strip() != "":
            start_time = interval.start_time
            end_time = interval.end_time

            # Extract segment from audio
            start_sample = int(start_time * sr)
            end_sample = int(end_time * sr)
            segment = y[start_sample:end_sample]

            # ---------------------------------------------------------------
            # 1) Band-limit for Intensity & HNR (up to lp_cutoff=500 Hz)
            # ---------------------------------------------------------------
            segment_lp = band_limit_segment(segment, sr, lp_cutoff=lp_cutoff)

            # Intensity (dB) on band-limited signal
            rms_lp = librosa.feature.rms(y=segment_lp).mean()
            if rms_lp > 0:
                intensity = 10 * np.log10(rms_lp)
            else:
                intensity = -80  # fallback if no sound is detected

            # HNR on band-limited signal
            harmonic_lp = librosa.effects.harmonic(segment_lp)
            residual_lp = segment_lp - harmonic_lp

            rms_harm = librosa.feature.rms(y=harmonic_lp).mean()
            rms_noise = librosa.feature.rms(y=residual_lp).mean()

            if rms_harm < 1e-10:
                rms_harm = 1e-10
            if rms_noise < 1e-10:
                rms_noise = 1e-10

            hnr = 10 * np.log10(rms_harm / rms_noise)
            if hnr > 20:
                hnr = 20

            # ---------------------------------------------------------------
            # 2) Duration
            # ---------------------------------------------------------------
            duration = end_time - start_time

            # ---------------------------------------------------------------
            # 3) ZCR (full band)
            # ---------------------------------------------------------------
            zcr = librosa.feature.zero_crossing_rate(y=segment).mean()

            # ---------------------------------------------------------------
            # 4) CoG (full-band up to max_freq), plus log transform
            # ---------------------------------------------------------------
            n_fft_value = min(512, len(segment))
            stft_mag = np.abs(librosa.stft(segment, n_fft=n_fft_value))
            freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft_value)

            freq_mask = (freqs >= min_freq) & (freqs <= effective_max_freq)
            filtered_stft = stft_mag[freq_mask, :]
            filtered_freqs = freqs[freq_mask]

            if filtered_stft.size == 0:
                cog = 0.0
            else:
                power_spectrum = np.mean(filtered_stft, axis=1)**2
                total_power = np.sum(power_spectrum)
                if total_power <= 0:
                    cog = 0.0
                else:
                    cog = np.sum(filtered_freqs * power_spectrum) / total_power

            # Log-frequency scaling (natural log)
            # Using log1p to avoid log(0):
            cog_log = math.log1p(cog)

            # ---------------------------------------------------------------
            # Save all features
            # ---------------------------------------------------------------
            participant = os.path.splitext(os.path.basename(wav_file))[0]
            results.append((
                participant,
                label,
                intensity,
                hnr,
                duration,
                zcr,
                cog,
                cog_log
            ))

    return results


def process_directory(sound_dir, textgrid_dir, results_file,
                      tier_name="phrase",
                      min_freq=0, max_freq=8000, lp_cutoff=500):
    """
    Process an entire directory of wav and TextGrid files,
    extracting acoustic features for each labeled interval.
    """
    with open(results_file, 'w') as f:
        # Now we have 8 columns: + "cog_log"
        f.write("participant\tword\tintensity\thnr\tduration\tzcr\tcog\tcog_log\n")

        for filename in os.listdir(textgrid_dir):
            if filename.endswith(".TextGrid"):
                textgrid_path = os.path.join(textgrid_dir, filename)
                wav_file = os.path.join(sound_dir, filename.replace(".TextGrid", ".wav"))

                if os.path.exists(wav_file):
                    results = extract_features(
                        wav_file,
                        textgrid_path,
                        tier_name,
                        min_freq=min_freq,
                        max_freq=max_freq,
                        lp_cutoff=lp_cutoff
                    )
                    for result in results:
                        (participant, label, intensity,
                         hnr, duration, zcr, cog, cog_log) = result

                        f.write(
                            f"{participant}\t"
                            f"{label}\t"
                            f"{intensity:.1f}\t"
                            f"{hnr:.1f}\t"
                            f"{duration:.4f}\t"
                            f"{zcr:.4f}\t"
                            f"{cog:.2f}\t"
                            f"{cog_log:.3f}\n"
                        )


def select_directory(title):
    return filedialog.askdirectory(title=title)


def select_file(title):
    return filedialog.asksaveasfilename(title=title, defaultextension='.txt')


def run_gui():
    root = tk.Tk()
    root.title("Feature Extractor")

    sound_dir = select_directory("Select Directory of Sound Files")
    if not sound_dir:
        messagebox.showerror("Error", "No sound directory selected.")
        return

    textgrid_dir = select_directory("Select Directory of TextGrid Files")
    if not textgrid_dir:
        messagebox.showerror("Error", "No TextGrid directory selected.")
        return

    results_file = select_file("Select Location to Save Results File")
    if not results_file:
        messagebox.showerror("Error", "No results file selected.")
        return

    # Adjust parameters as needed:
    tier_name = "phrase"
    min_freq = 0       # Lower bound for CoG
    max_freq = 8000    # Upper bound for CoG
    lp_cutoff = 500    # Band-limit for Intensity & HNR

    process_directory(
        sound_dir,
        textgrid_dir,
        results_file,
        tier_name,
        min_freq,
        max_freq,
        lp_cutoff
    )

    messagebox.showinfo("Success", "Processing completed successfully.")


if __name__ == "__main__":
    run_gui()
