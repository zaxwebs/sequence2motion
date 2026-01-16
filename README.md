# Sequence to Motion

A versatile Python utility to convert image sequences into high-quality, motion-optimized formats for the web.

<img src="https://res.cloudinary.com/webster1000/image/upload/v1768469439/apple_cyr2kw.avif" alt="apple avif" width="80">

## Features

- **Multi-Format Support**:
    - **AVIF**: High efficiency, modern web format.
    - **WebM (VP9)**: High quality video with alpha channel support.
    - **Safari (HEVC)**: MOV format using HEVC (`libx265`), designed for Apple devices.
    - **GIF**: Classic animated images.
    - **APNG**: Animated PNG for lossless snippets.
- **Smart GUI**: 
    - Auto-extension updating.
    - Shared FPS and Width settings.
    - Grouped settings for better usability.
    - "Open Folder" convenience button.
- **Shared Settings**: Easily control FPS, Width, and Quality across formats.
- **Lightweight**: Built with `Pillow`, `imageio`, and `Tkinter`.

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

1. **Input**: Select the folder containing your PNG sequence.
2. **Settings**: 
   - **Tab**: Select your desired output format.
   - **FPS/Width**: Adjust shared settings.
   - **Quality**: Adjust quality (maps to CRF for video formats).
3. **Output**: Choose where to save the file.
4. **Convert**: Click to process!

## Known Issues

- **Safari (HEVC) Alpha Channel**: While the exporter produces valid HEVC files with an alpha channel (using `hvc1` tags), **Safari currently does not render the transparency correctly in the browser**. The video plays, but the background may appear black or opaque. This is a known limitation currently being investigated.

## Requirements

- Python 3.x
- `Pillow`
- `pillow-avif-plugin`
- `imageio`
- `imageio-ffmpeg`
- `numpy`
