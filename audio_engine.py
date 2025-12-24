"""
AI Audio Mastering Engine
Provides intelligent audio processing for professional-quality mastering
"""

import numpy as np
import librosa
import soundfile as sf
from scipy import signal
from scipy.ndimage import uniform_filter1d
import pyloudnorm as pyln
import noisereduce as nr
from typing import Tuple, Optional, Dict, Any
import os


class AudioAnalyzer:
    """Analyzes audio characteristics for intelligent processing decisions"""

    def __init__(self, audio: np.ndarray, sample_rate: int):
        self.audio = audio
        self.sr = sample_rate
        self.meter = pyln.Meter(sample_rate)

    @staticmethod
    def _safe_float(value, default=0.0):
        """Convert value to JSON-safe float (handles NaN/Inf)"""
        if isinstance(value, (np.floating, np.integer)):
            value = float(value)
        if not isinstance(value, (int, float)):
            return default
        if np.isnan(value) or np.isinf(value):
            return default
        return value

    def get_loudness(self) -> float:
        """Get integrated loudness in LUFS"""
        if self.audio.ndim == 1:
            audio_for_meter = self.audio
        else:
            audio_for_meter = self.audio.T
        try:
            result = self.meter.integrated_loudness(audio_for_meter)
            return self._safe_float(result, -24.0)
        except:
            return -24.0  # Default fallback

    def get_peak(self) -> float:
        """Get true peak in dB"""
        peak = np.max(np.abs(self.audio))
        result = 20 * np.log10(peak + 1e-10)
        return self._safe_float(result, -60.0)

    def get_dynamic_range(self) -> float:
        """Calculate dynamic range in dB"""
        if self.audio.ndim == 1:
            mono = self.audio
        else:
            mono = np.mean(self.audio, axis=0)

        # Calculate RMS in windows
        window_size = int(self.sr * 0.4)  # 400ms windows
        hop_size = window_size // 4

        rms_values = []
        for i in range(0, len(mono) - window_size, hop_size):
            window = mono[i:i + window_size]
            rms = np.sqrt(np.mean(window ** 2))
            if rms > 1e-10:
                rms_values.append(20 * np.log10(rms))

        if len(rms_values) < 2:
            return 10.0

        rms_values = np.array(rms_values)
        # Dynamic range is difference between loud and quiet sections
        result = np.percentile(rms_values, 95) - np.percentile(rms_values, 10)
        return self._safe_float(result, 10.0)

    def get_spectral_balance(self) -> Dict[str, float]:
        """Analyze frequency balance"""
        if self.audio.ndim == 1:
            mono = self.audio
        else:
            mono = np.mean(self.audio, axis=0)

        # Compute spectrum
        n_fft = 4096
        spectrum = np.abs(librosa.stft(mono, n_fft=n_fft))
        freqs = librosa.fft_frequencies(sr=self.sr, n_fft=n_fft)

        # Calculate energy in different bands
        avg_spectrum = np.mean(spectrum, axis=1)

        def band_energy(low, high):
            mask = (freqs >= low) & (freqs < high)
            return np.sum(avg_spectrum[mask] ** 2)

        total = band_energy(20, 20000) + 1e-10

        return {
            'sub_bass': self._safe_float(band_energy(20, 60) / total, 0.1),
            'bass': self._safe_float(band_energy(60, 250) / total, 0.15),
            'low_mid': self._safe_float(band_energy(250, 500) / total, 0.15),
            'mid': self._safe_float(band_energy(500, 2000) / total, 0.2),
            'high_mid': self._safe_float(band_energy(2000, 4000) / total, 0.15),
            'presence': self._safe_float(band_energy(4000, 6000) / total, 0.1),
            'brilliance': self._safe_float(band_energy(6000, 20000) / total, 0.15)
        }

    def get_stereo_width(self) -> float:
        """Calculate stereo width (0-1 scale)"""
        if self.audio.ndim == 1:
            return 0.0

        left = self.audio[0]
        right = self.audio[1]

        mid = (left + right) / 2
        side = (left - right) / 2

        mid_energy = np.sum(mid ** 2)
        side_energy = np.sum(side ** 2)

        if mid_energy < 1e-10:
            return 0.0

        result = np.clip(side_energy / (mid_energy + side_energy), 0, 1)
        return self._safe_float(result, 0.5)

    def full_analysis(self) -> Dict[str, Any]:
        """Perform complete audio analysis"""
        duration = len(self.audio[0] if self.audio.ndim > 1 else self.audio) / self.sr
        return {
            'loudness_lufs': self.get_loudness(),
            'peak_db': self.get_peak(),
            'dynamic_range_db': self.get_dynamic_range(),
            'spectral_balance': self.get_spectral_balance(),
            'stereo_width': self.get_stereo_width(),
            'sample_rate': int(self.sr),
            'duration_seconds': self._safe_float(duration, 0.0),
            'channels': int(self.audio.shape[0] if self.audio.ndim > 1 else 1)
        }


class AudioProcessor:
    """Core audio processing algorithms"""

    @staticmethod
    def normalize_loudness(audio: np.ndarray, sr: int, target_lufs: float = -14.0) -> np.ndarray:
        """Normalize audio to target LUFS"""
        meter = pyln.Meter(sr)

        if audio.ndim == 1:
            audio_for_meter = audio
        else:
            audio_for_meter = audio.T

        try:
            current_loudness = meter.integrated_loudness(audio_for_meter)
            if np.isinf(current_loudness) or np.isnan(current_loudness):
                return audio

            gain_db = target_lufs - current_loudness
            gain_linear = 10 ** (gain_db / 20)

            normalized = audio * gain_linear

            # Prevent clipping
            peak = np.max(np.abs(normalized))
            if peak > 0.99:
                normalized = normalized * (0.99 / peak)

            return normalized
        except:
            return audio

    @staticmethod
    def multiband_compress(audio: np.ndarray, sr: int,
                          ratio: float = 3.0,
                          threshold_db: float = -20.0) -> np.ndarray:
        """Apply multiband compression for better dynamics control"""

        # Define frequency bands
        bands = [
            (20, 150),     # Sub/Bass
            (150, 500),    # Low-mid
            (500, 2000),   # Mid
            (2000, 6000),  # High-mid
            (6000, 20000)  # High
        ]

        # Process each channel
        if audio.ndim == 1:
            return AudioProcessor._compress_bands(audio, sr, bands, ratio, threshold_db)
        else:
            result = np.zeros_like(audio)
            for ch in range(audio.shape[0]):
                result[ch] = AudioProcessor._compress_bands(
                    audio[ch], sr, bands, ratio, threshold_db
                )
            return result

    @staticmethod
    def _compress_bands(mono: np.ndarray, sr: int, bands: list,
                       ratio: float, threshold_db: float) -> np.ndarray:
        """Compress individual frequency bands"""
        result = np.zeros_like(mono)

        for low, high in bands:
            # Design bandpass filter
            nyq = sr / 2
            low_norm = max(low / nyq, 0.001)
            high_norm = min(high / nyq, 0.999)

            if low_norm >= high_norm:
                continue

            try:
                b, a = signal.butter(4, [low_norm, high_norm], btype='band')
                band_signal = signal.filtfilt(b, a, mono)

                # Apply compression
                compressed = AudioProcessor._compress(band_signal, ratio, threshold_db)
                result += compressed
            except:
                continue

        # Normalize to prevent clipping
        peak = np.max(np.abs(result))
        if peak > 0:
            result = result / peak * np.max(np.abs(mono))

        return result

    @staticmethod
    def _compress(audio: np.ndarray, ratio: float, threshold_db: float) -> np.ndarray:
        """Apply dynamic range compression"""
        threshold_linear = 10 ** (threshold_db / 20)

        # Calculate envelope
        envelope = np.abs(audio)
        envelope = uniform_filter1d(envelope, size=1000)

        # Calculate gain reduction
        gain = np.ones_like(envelope)
        above_threshold = envelope > threshold_linear

        if np.any(above_threshold):
            # Soft knee compression
            excess_db = 20 * np.log10(envelope[above_threshold] / threshold_linear + 1e-10)
            gain_reduction_db = excess_db * (1 - 1/ratio)
            gain[above_threshold] = 10 ** (-gain_reduction_db / 20)

        # Apply gain with smoothing
        gain = uniform_filter1d(gain, size=500)

        return audio * gain

    @staticmethod
    def enhance_clarity(audio: np.ndarray, sr: int, amount: float = 0.3) -> np.ndarray:
        """Enhance presence and clarity in the mix"""
        if audio.ndim == 1:
            return AudioProcessor._enhance_clarity_mono(audio, sr, amount)
        else:
            result = np.zeros_like(audio)
            for ch in range(audio.shape[0]):
                result[ch] = AudioProcessor._enhance_clarity_mono(audio[ch], sr, amount)
            return result

    @staticmethod
    def _enhance_clarity_mono(mono: np.ndarray, sr: int, amount: float) -> np.ndarray:
        """Enhance clarity on mono signal"""
        nyq = sr / 2

        # Presence boost (2-6 kHz)
        try:
            presence_low = min(2000 / nyq, 0.99)
            presence_high = min(6000 / nyq, 0.999)

            if presence_low < presence_high:
                b, a = signal.butter(2, [presence_low, presence_high], btype='band')
                presence = signal.filtfilt(b, a, mono)
                mono = mono + presence * amount
        except:
            pass

        # Air boost (10-16 kHz) - subtle
        try:
            air_low = min(10000 / nyq, 0.99)
            air_high = min(16000 / nyq, 0.999)

            if air_low < air_high:
                b, a = signal.butter(2, [air_low, air_high], btype='band')
                air = signal.filtfilt(b, a, mono)
                mono = mono + air * (amount * 0.5)
        except:
            pass

        return mono

    @staticmethod
    def enhance_bass(audio: np.ndarray, sr: int, amount: float = 0.2) -> np.ndarray:
        """Enhance low-end frequencies"""
        nyq = sr / 2

        if audio.ndim == 1:
            mono = audio
        else:
            # Process bass in mono for phase coherence
            mono = np.mean(audio, axis=0)

        try:
            bass_freq = min(120 / nyq, 0.99)
            b, a = signal.butter(3, bass_freq, btype='low')
            bass = signal.filtfilt(b, a, mono)

            # Saturate bass slightly for warmth
            bass = np.tanh(bass * 1.5) / 1.5

            if audio.ndim == 1:
                return audio + bass * amount
            else:
                result = audio.copy()
                result[0] = result[0] + bass * amount
                result[1] = result[1] + bass * amount
                return result
        except:
            return audio

    @staticmethod
    def adjust_stereo_width(audio: np.ndarray, width: float = 1.0) -> np.ndarray:
        """Adjust stereo width (1.0 = unchanged, >1 = wider, <1 = narrower)"""
        if audio.ndim == 1:
            return audio  # Can't adjust width of mono

        left = audio[0]
        right = audio[1]

        mid = (left + right) / 2
        side = (left - right) / 2

        # Adjust side signal
        side = side * width

        # Reconstruct
        result = np.zeros_like(audio)
        result[0] = mid + side
        result[1] = mid - side

        return result

    @staticmethod
    def soft_clip(audio: np.ndarray, ceiling_db: float = -0.3) -> np.ndarray:
        """Apply soft clipping/limiting"""
        ceiling = 10 ** (ceiling_db / 20)

        # Soft clip using tanh
        result = np.tanh(audio / ceiling) * ceiling

        return result

    @staticmethod
    def reduce_noise(audio: np.ndarray, sr: int, strength: float = 0.5) -> np.ndarray:
        """Reduce background noise"""
        if audio.ndim == 1:
            return nr.reduce_noise(y=audio, sr=sr, prop_decrease=strength)
        else:
            result = np.zeros_like(audio)
            for ch in range(audio.shape[0]):
                result[ch] = nr.reduce_noise(y=audio[ch], sr=sr, prop_decrease=strength)
            return result

    @staticmethod
    def harmonic_exciter(audio: np.ndarray, sr: int, amount: float = 0.1) -> np.ndarray:
        """Add harmonic excitement for more presence"""
        if audio.ndim == 1:
            return AudioProcessor._excite_harmonics(audio, sr, amount)
        else:
            result = np.zeros_like(audio)
            for ch in range(audio.shape[0]):
                result[ch] = AudioProcessor._excite_harmonics(audio[ch], sr, amount)
            return result

    @staticmethod
    def _excite_harmonics(mono: np.ndarray, sr: int, amount: float) -> np.ndarray:
        """Generate and add subtle harmonics"""
        nyq = sr / 2

        # Focus on high frequencies
        try:
            high_freq = min(3000 / nyq, 0.99)
            b, a = signal.butter(2, high_freq, btype='high')
            highs = signal.filtfilt(b, a, mono)

            # Generate harmonics through soft saturation
            harmonics = np.tanh(highs * 3) / 3

            return mono + harmonics * amount
        except:
            return mono


class AIMasterer:
    """Main AI Mastering Engine"""

    def __init__(self, preset: str = 'streaming'):
        from config import MASTERING_PRESETS
        self.presets = MASTERING_PRESETS
        self.set_preset(preset)

    def set_preset(self, preset: str):
        """Set mastering preset"""
        if preset in self.presets:
            self.current_preset = self.presets[preset]
            self.preset_name = preset
        else:
            self.current_preset = self.presets['streaming']
            self.preset_name = 'streaming'

    def analyze(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """Analyze audio and return characteristics"""
        analyzer = AudioAnalyzer(audio, sr)
        return analyzer.full_analysis()

    def master(self, audio: np.ndarray, sr: int,
               analysis: Optional[Dict] = None,
               noise_reduction: bool = False,
               noise_strength: float = 0.3) -> Tuple[np.ndarray, Dict]:
        """
        Apply AI-driven mastering to audio

        Returns:
            Tuple of (mastered_audio, processing_report)
        """
        if analysis is None:
            analysis = self.analyze(audio, sr)

        report = {
            'preset': self.preset_name,
            'original_analysis': analysis,
            'processing_steps': []
        }

        # Sanitize input audio to prevent NaN/infinite errors
        result = self._sanitize(audio.copy())

        # Step 1: Noise reduction (if enabled)
        if noise_reduction:
            result = AudioProcessor.reduce_noise(result, sr, noise_strength)
            report['processing_steps'].append('Noise reduction applied')

        # Step 2: Intelligent EQ based on analysis
        spectral = analysis['spectral_balance']

        # Enhance bass if lacking
        if spectral['bass'] < 0.15:
            result = AudioProcessor.enhance_bass(result, sr, amount=0.25)
            report['processing_steps'].append('Bass enhancement applied')

        # Enhance clarity if needed (based on presence/brilliance)
        if spectral['presence'] < 0.08 and self.current_preset['eq_boost_presence']:
            result = AudioProcessor.enhance_clarity(result, sr, amount=0.35)
            report['processing_steps'].append('Clarity enhancement applied')
        elif self.current_preset['eq_boost_presence']:
            result = AudioProcessor.enhance_clarity(result, sr, amount=0.2)
            report['processing_steps'].append('Subtle clarity enhancement applied')

        # Step 3: Harmonic excitement for extra presence
        if self.current_preset['eq_boost_presence']:
            result = AudioProcessor.harmonic_exciter(result, sr, amount=0.08)
            report['processing_steps'].append('Harmonic exciter applied')

        # Step 4: Multiband compression
        compression_ratio = self.current_preset['compression_ratio']

        # Adjust threshold based on dynamic range
        if analysis['dynamic_range_db'] > 15:
            threshold = -18.0  # More compression for dynamic material
        else:
            threshold = -24.0  # Gentler for already compressed material

        result = AudioProcessor.multiband_compress(result, sr,
                                                   ratio=compression_ratio,
                                                   threshold_db=threshold)
        report['processing_steps'].append(f'Multiband compression (ratio: {compression_ratio}:1)')

        # Step 5: Stereo width adjustment
        target_width = self.current_preset['stereo_width']
        if analysis['channels'] > 1:
            current_width = analysis['stereo_width']

            if current_width < 0.3 and target_width > 1.0:
                # Narrow mix, widen it more
                result = AudioProcessor.adjust_stereo_width(result, target_width * 1.1)
                report['processing_steps'].append('Stereo widening applied (enhanced)')
            else:
                result = AudioProcessor.adjust_stereo_width(result, target_width)
                report['processing_steps'].append(f'Stereo width adjusted to {target_width}')

        # Step 6: Loudness normalization
        target_lufs = self.current_preset['target_lufs']
        result = AudioProcessor.normalize_loudness(result, sr, target_lufs)
        report['processing_steps'].append(f'Loudness normalized to {target_lufs} LUFS')

        # Step 7: Final limiting/soft clipping
        result = AudioProcessor.soft_clip(result, ceiling_db=-0.3)
        report['processing_steps'].append('Final limiting applied (-0.3 dB ceiling)')

        # Final sanitization to ensure clean output
        result = self._sanitize(result)

        # Final analysis
        final_analyzer = AudioAnalyzer(result, sr)
        report['final_analysis'] = final_analyzer.full_analysis()

        return result, report

    @staticmethod
    def _sanitize(audio: np.ndarray) -> np.ndarray:
        """Sanitize audio to remove NaN/infinite values"""
        audio = np.nan_to_num(audio, nan=0.0, posinf=0.99, neginf=-0.99)
        audio = np.clip(audio, -1.0, 1.0)
        if not np.all(np.isfinite(audio)):
            audio = np.where(np.isfinite(audio), audio, 0.0)
        return audio


def sanitize_audio(audio: np.ndarray) -> np.ndarray:
    """
    Sanitize audio array by removing NaN and infinite values.
    This fixes 'Audio buffer is not finite everywhere' errors.
    """
    # Replace NaN with 0
    audio = np.nan_to_num(audio, nan=0.0, posinf=0.99, neginf=-0.99)

    # Clip to valid range
    audio = np.clip(audio, -1.0, 1.0)

    # Ensure finite
    if not np.all(np.isfinite(audio)):
        # If still not finite, replace remaining issues
        audio = np.where(np.isfinite(audio), audio, 0.0)

    return audio


def load_audio(file_path: str) -> Tuple[np.ndarray, int]:
    """Load audio file and return as numpy array"""
    audio, sr = librosa.load(file_path, sr=None, mono=False)

    # Sanitize audio to fix NaN/infinite values
    audio = sanitize_audio(audio)

    return audio, sr


def save_audio(audio: np.ndarray, sr: int, output_path: str,
               format_key: str = 'wav') -> str:
    """Save audio in specified format"""
    from config import OUTPUT_FORMATS

    format_config = OUTPUT_FORMATS.get(format_key, OUTPUT_FORMATS['wav'])
    extension = format_config['extension']

    # Ensure output path has correct extension
    base_path = os.path.splitext(output_path)[0]
    output_path = f"{base_path}.{extension}"

    # Transpose if needed (librosa uses channels-first, soundfile uses channels-last)
    if audio.ndim > 1:
        audio_out = audio.T
    else:
        audio_out = audio

    if extension == 'mp3':
        # Use pydub for MP3 export
        from pydub import AudioSegment

        # Convert to 16-bit PCM first
        audio_16bit = (audio_out * 32767).astype(np.int16)

        # Create AudioSegment
        if audio.ndim > 1:
            channels = audio.shape[0]
        else:
            channels = 1

        audio_segment = AudioSegment(
            audio_16bit.tobytes(),
            frame_rate=sr,
            sample_width=2,
            channels=channels
        )

        bitrate = format_config.get('bitrate', '320k')
        audio_segment.export(output_path, format='mp3', bitrate=bitrate)
    else:
        # Use soundfile for WAV/FLAC
        subtype = format_config.get('subtype', 'PCM_24')
        sf.write(output_path, audio_out, sr, subtype=subtype)

    return output_path
