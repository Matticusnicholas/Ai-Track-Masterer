#!/usr/bin/env python3
"""
AI Track Masterer - Launcher Script
Run this file to start the web application
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check and install required dependencies"""
    print("Checking dependencies...")

    try:
        import flask
        import librosa
        import soundfile
        import pyloudnorm
        import noisereduce
        print("All dependencies are installed!")
        return True
    except ImportError as e:
        print(f"Missing dependency: {e.name}")
        print("\nInstalling dependencies...")

        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
            ])
            print("Dependencies installed successfully!")
            return True
        except subprocess.CalledProcessError:
            print("Failed to install dependencies. Please run:")
            print("  pip install -r requirements.txt")
            return False


def check_ffmpeg():
    """Check if FFmpeg is available (needed for MP3 export)"""
    try:
        subprocess.run(['ffmpeg', '-version'],
                      capture_output=True, check=True)
        print("FFmpeg is available (MP3 export enabled)")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Warning: FFmpeg not found. MP3 export may not work.")
        print("Install FFmpeg for full format support:")
        print("  Ubuntu/Debian: sudo apt install ffmpeg")
        print("  MacOS: brew install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        return False


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("  AI Track Masterer")
    print("  Professional Audio Mastering powered by AI")
    print("="*60 + "\n")

    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    check_ffmpeg()

    print("\n" + "-"*60)
    print("Starting server...")
    print("-"*60 + "\n")

    # Import and run the app
    from app import app

    # Get host and port from environment or use defaults
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'true').lower() == 'true'

    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()
