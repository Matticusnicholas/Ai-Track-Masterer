# AI Track Masterer

Professional audio mastering powered by AI algorithms. Upload your tracks and get them mastered automatically with optimized loudness, clarity, dynamics, and stereo width.

## Features

- **AI-Powered Mastering**: Intelligent audio processing that analyzes your track and applies optimal mastering
- **Multiple Presets**: Choose from Streaming, Loud, Dynamic, Radio, or Vinyl mastering styles
- **Format Support**: Export to WAV (16/24-bit), FLAC, or MP3 (192/256/320 kbps)
- **Batch Processing**: Master multiple tracks at once
- **Audio Analysis**: See detailed analysis of your tracks (loudness, peak, dynamic range, etc.)
- **Noise Reduction**: Optional AI noise reduction for cleaner masters
- **Custom Output Folder**: Save mastered files to any location

## Mastering Algorithms

The AI mastering engine includes:
- **Loudness Normalization**: LUFS-based loudness targeting for streaming platforms
- **Multiband Compression**: Intelligent dynamics control across frequency bands
- **EQ Enhancement**: Clarity and presence boosting
- **Harmonic Exciter**: Subtle harmonic enhancement for warmth
- **Stereo Width Control**: Optimal stereo image adjustment
- **Soft Limiting**: Transparent limiting to prevent clipping

## Installation

### Prerequisites

- Python 3.8 or higher
- FFmpeg (optional, for MP3 export)

### Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**MacOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html

### Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Start the Server

```bash
python run.py
```

The web interface will be available at `http://localhost:5000`

### Using the Web Interface

1. **Upload**: Drag and drop audio files or click to browse
2. **Select Preset**: Choose a mastering style that fits your genre
3. **Choose Format**: Select your desired output format
4. **Master**: Click "Start Mastering" and wait for processing
5. **Download**: Get your mastered files

### Mastering Presets

| Preset | Target LUFS | Best For |
|--------|-------------|----------|
| Streaming Optimized | -14 LUFS | Spotify, Apple Music, YouTube |
| Maximum Loudness | -9 LUFS | EDM, Hip-Hop, maximum impact |
| Dynamic Preservation | -16 LUFS | Classical, Jazz, acoustic music |
| Radio Ready | -12 LUFS | Broadcast, radio play |
| Vinyl Simulation | -18 LUFS | Warm, analog-style sound |

### Output Formats

| Format | Quality | Use Case |
|--------|---------|----------|
| WAV 24-bit | Lossless | Professional, archival |
| WAV 16-bit | Lossless | CD quality |
| FLAC | Lossless, compressed | High-quality distribution |
| MP3 320kbps | High quality lossy | Streaming, distribution |
| MP3 256kbps | Good quality lossy | General distribution |
| MP3 192kbps | Acceptable quality lossy | Smaller file size |

## API Endpoints

- `POST /api/master` - Master a single audio file
- `POST /api/batch-master` - Master multiple files
- `POST /api/analyze` - Analyze audio without mastering
- `GET /api/presets` - Get available mastering presets
- `GET /api/formats` - Get available output formats
- `GET /api/list-output` - List mastered files
- `GET /api/download/<filename>` - Download a mastered file
- `DELETE /api/delete/<filename>` - Delete a mastered file

## Project Structure

```
Ai-Track-Masterer/
├── app.py              # Flask web application
├── audio_engine.py     # AI mastering algorithms
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── run.py              # Launcher script
├── uploads/            # Temporary upload storage
├── output/             # Mastered files output
├── templates/          # HTML templates
│   └── index.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── app.js
```

## Technical Details

### Audio Processing Pipeline

1. **Analysis Phase**
   - Loudness measurement (LUFS)
   - Peak detection
   - Dynamic range calculation
   - Spectral balance analysis
   - Stereo width measurement

2. **Processing Phase**
   - Noise reduction (optional)
   - Bass enhancement (if needed)
   - Clarity enhancement (EQ)
   - Harmonic excitement
   - Multiband compression
   - Stereo width adjustment
   - Loudness normalization
   - Final limiting

### Dependencies

- **Flask**: Web framework
- **Librosa**: Audio loading and analysis
- **SoundFile**: Audio file I/O
- **PyLoudNorm**: LUFS loudness measurement
- **SciPy**: Signal processing
- **NumPy**: Numerical operations
- **Noisereduce**: AI noise reduction
- **Pydub**: MP3 encoding (requires FFmpeg)

## License

MIT License - Free for personal and commercial use.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.
