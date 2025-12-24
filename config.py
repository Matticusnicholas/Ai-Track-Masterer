"""
Configuration settings for AI Track Masterer
"""
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Upload settings
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'output')
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac', 'ogg', 'aiff', 'm4a', 'wma'}

# Audio processing settings
SAMPLE_RATE = 44100
TARGET_LUFS = -14.0  # Streaming standard (Spotify, YouTube, etc.)
TARGET_TRUE_PEAK = -1.0  # dB
MAX_SAMPLE_RATE = 192000

# Output format settings
OUTPUT_FORMATS = {
    'wav': {'extension': 'wav', 'subtype': 'PCM_24', 'description': 'WAV (24-bit)'},
    'wav_16': {'extension': 'wav', 'subtype': 'PCM_16', 'description': 'WAV (16-bit)'},
    'flac': {'extension': 'flac', 'subtype': 'PCM_24', 'description': 'FLAC (Lossless)'},
    'mp3_320': {'extension': 'mp3', 'bitrate': '320k', 'description': 'MP3 (320 kbps)'},
    'mp3_256': {'extension': 'mp3', 'bitrate': '256k', 'description': 'MP3 (256 kbps)'},
    'mp3_192': {'extension': 'mp3', 'bitrate': '192k', 'description': 'MP3 (192 kbps)'},
}

# Mastering presets
MASTERING_PRESETS = {
    'streaming': {
        'name': 'Streaming Optimized',
        'target_lufs': -14.0,
        'compression_ratio': 3.0,
        'eq_boost_presence': True,
        'stereo_width': 1.1,
        'description': 'Optimized for Spotify, Apple Music, YouTube'
    },
    'loud': {
        'name': 'Maximum Loudness',
        'target_lufs': -9.0,
        'compression_ratio': 4.0,
        'eq_boost_presence': True,
        'stereo_width': 1.2,
        'description': 'For maximum impact and loudness'
    },
    'dynamic': {
        'name': 'Dynamic Preservation',
        'target_lufs': -16.0,
        'compression_ratio': 2.0,
        'eq_boost_presence': False,
        'stereo_width': 1.0,
        'description': 'Preserves natural dynamics'
    },
    'radio': {
        'name': 'Radio Ready',
        'target_lufs': -12.0,
        'compression_ratio': 3.5,
        'eq_boost_presence': True,
        'stereo_width': 1.15,
        'description': 'Broadcast-ready mastering'
    },
    'vinyl': {
        'name': 'Vinyl Simulation',
        'target_lufs': -18.0,
        'compression_ratio': 2.0,
        'eq_boost_presence': False,
        'stereo_width': 0.95,
        'description': 'Warm, analog-style mastering'
    }
}

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
