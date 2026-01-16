# PNG Sequence to AVIF Converter

A simple Python utility to convert a sequence of PNG images into an animated AVIF file. This tool provides both a Command Line Interface (CLI) and a Graphical User Interface (GUI).

<img src="https://res.cloudinary.com/webster1000/image/upload/v1768469439/apple_cyr2kw.avif" alt="apple avif" width="80">

## Features

- **Convert PNG Sequences**: Turn a folder of images into a single animated AVIF.
- **Customizable Settings**: Adjust Frames Per Second (FPS) and Quality.
- **Progress Tracking**: Visual progress bar in GUI and console output in CLI.
- **Lightweight**: Built with `Pillow` and `pillow-avif-plugin`.

## Installation

1. Clone this repository or download the source code.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Graphical User Interface (GUI)

Run the GUI for an easy-to-use experience:

```bash
python gui.py
```

1. **Input Folder**: Select the folder containing your PNG sequence.
2. **Output File**: Choose where to save the generated `.avif` file.
3. **Settings**: Adjust FPS (def: 24) and Quality (def: 85).
4. **Convert**: Click the button and watch the progress!

### Command Line Interface (CLI)

Use the script directly from your terminal:

```bash
python convert.py "path/to/input_folder" "output/file.avif" --fps 24 --quality 85
```

**Arguments:**
- `input_folder`: Path to the folder containing .png images.
- `output_file`: Path for the output .avif file.
- `--fps`: (Optional) Frames Per Second. Default is 24.
- `--quality`: (Optional) Quality from 0-100. Default is 85.

## Requirements

- Python 3.x
- `Pillow`
- `pillow-avif-plugin`


