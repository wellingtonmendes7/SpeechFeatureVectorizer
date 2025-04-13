# SpeechFeatureVectorizer  
**TextGrid Acoustic Feature Extractor Script**  
This script extracts acoustic features from intervals labeled in `.TextGrid` files and computes values such as intensity, harmonic-to-noise ratio (HNR), duration, zero-crossing rate (ZCR), and spectral center of gravity (CoG). It is designed for linguistic and phonetic research, particularly for data annotated using **Praat**.

## Features
- Extracts acoustic features for each labeled interval:
  - **Intensity** (band-limited up to 500 Hz)
  - **Harmonic-to-noise ratio (HNR)** (up to 500 Hz)
  - **Duration** (in seconds)
  - **Zero-crossing rate (ZCR)**
  - **Center of Gravity (CoG)**
  - **Log-transformed CoG** (natural log)
- Processes multiple `.wav` and `.TextGrid` file pairs in batch.
- Skips intervals with empty labels for cleaner analysis.
- Saves results in a tab-delimited `.txt` file (UTF-8).
- Includes a graphical interface (GUI) to select folders and save output.

## Requirements
- Python 3.7+
- `librosa` (audio processing)
- `numpy` (numerical operations)
- `tgt` (for reading TextGrid files)
- `tkinter` (built-in GUI support)

Install required libraries using pip:

```bash
pip install librosa numpy tgt
