# SpeechFeatureVectorizer  
**TextGrid Acoustic Feature Extractor Software**  
This software provides a user interface to extract acoustic features from intervals labeled in `.TextGrid` files and computes values such as intensity, harmonic-to-noise ratio (HNR), duration, zero-crossing rate (ZCR), and spectral center of gravity (CoG). It is designed for linguistic and phonetic research, particularly for data annotated using **Praat**.

# Features
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

# How to Use
1. Prepare your files: Place your .wav and .TextGrid files in separate directories (ensure matching filenames).
2. Run the script.
3. Use the GUI prompts to: Select the directory containing .wav files. Select the directory containing .TextGrid files. Choose where to save the output file (.txt format). The script will automatically process all matching file pairs and save the results.

# Output
The resulting .txt file will include the following columns:
- a) participant:	Name of the file (without extension)
- b) word:	Label from the TextGrid tier
- c) intensity:	Intensity in dB (band-limited to 500 Hz)
- d) hnr:	Harmonic-to-noise ratio (in dB, capped at 20 dB)
- e) duration:	Duration in seconds
- f) zcr:	Zero-crossing rate (full spectrum)
- g) cog:	Center of Gravity in Hz
- h) cog_log:	Log-transformed CoG (natural log)

# Customization
- To change the frequency thresholds (min_freq, max_freq, lp_cutoff), edit the corresponding variables in the run_gui() function.
- To change the target tier name (e.g., change "phrase" to "word"), update the tier_name parameter.

# Known Limitations
- Assumes filenames match between .wav and .TextGrid (e.g., file1.wav with file1.TextGrid).
- Skips intervals with empty labels by default.
- Uses log1p() for safer log transformations (avoiding log(0)).
- Output is a plain .txt file, not Excel — can be opened in any spreadsheet software.

# Requirements
- Python 3.7+
- `librosa` (audio processing)
- `numpy` (numerical operations)
- `tgt` (for reading TextGrid files)
- `tkinter` (built-in GUI support)

# Contact
For questions, suggestions, or bug reports, please contact the authors using the emails below.

Wellington Mendes (UFU)
📧 Email: wellington.mendes@ufu.br  |  https://orcid.org/0000-0002-1459-4183

Elisa Mattos (UFV)
📧 Email: elisa.mattos@ufv.br  |  https://orcid.org/0000-0002-4787-1837

# License
This script is distributed under the MIT License. Feel free to modify and use it in your academic or professional projects.
