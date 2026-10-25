"""
Audio processing module for noise removal, normalization, and podcast-style enhancement
"""
import numpy as np
import librosa
import soundfile as sf
from scipy import signal
from scipy.fft import fft, ifft
from config import Config
import logging

logger = logging.getLogger(__name__)

class AudioProcessor:
    """Process audio with noise reduction, normalization, and voice enhancement"""
    
    def __init__(self):
        self.sr = Config.SAMPLE_RATE
        self.target_loudness = Config.TARGET_LOUDNESS
        
    def load_audio(self, file_path):
        """Load audio file"""
        try:
            y, sr = librosa.load(file_path, sr=self.sr, mono=True)
            return y, sr
        except Exception as e:
            logger.error(f"Error loading audio: {e}")
            raise
    
    def save_audio(self, y, file_path, sr=None):
        """Save audio file"""
        if sr is None:
            sr = self.sr
        try:
            sf.write(file_path, y, sr)
        except Exception as e:
            logger.error(f"Error saving audio: {e}")
            raise
    
    def highpass_filter(self, y, sr, cutoff=80):
        """Apply high-pass filter to remove rumble"""
        nyquist = sr / 2
        normalized_cutoff = cutoff / nyquist
        
        if normalized_cutoff >= 1:
            return y
        
        b, a = signal.butter(5, normalized_cutoff, btype='high')
        return signal.filtfilt(b, a, y)
    
    def spectral_subtraction(self, y, sr, noise_reduction_strength=0.5):
        """
        Spectral subtraction for noise reduction
        noise_reduction_strength: 0-1, higher = more aggressive
        """
        # Parameters
        n_fft = 2048
        hop_length = 512
        
        # STFT
        D = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
        magnitude = np.abs(D)
        phase = np.angle(D)
        
        # Estimate noise profile from quiet frames (first 0.5 seconds)
        noise_frames = int(0.5 * sr / hop_length)
        noise_profile = np.median(magnitude[:, :noise_frames], axis=1, keepdims=True)
        
        # Spectral subtraction
        reduction_factor = 1 + (2 * noise_reduction_strength)
        magnitude_cleaned = magnitude - (reduction_factor * noise_profile)
        magnitude_cleaned = np.maximum(magnitude_cleaned, 0.05 * magnitude)
        
        # Reconstruct
        D_cleaned = magnitude_cleaned * np.exp(1j * phase)
        y_cleaned = librosa.istft(D_cleaned, hop_length=hop_length)
        
        # Match original length
        if len(y_cleaned) < len(y):
            y_cleaned = np.pad(y_cleaned, (0, len(y) - len(y_cleaned)))
        else:
            y_cleaned = y_cleaned[:len(y)]
        
        return y_cleaned
    
    def reduce_noise_advanced(self, y, sr, noise_reduction_strength=0.5):
        """Advanced noise reduction using multiple techniques"""
        # High-pass filter
        y = self.highpass_filter(y, sr, cutoff=80)
        
        # Spectral subtraction
        y = self.spectral_subtraction(y, sr, noise_reduction_strength)
        
        return y
    
    def normalize_loudness(self, y):
        """Normalize to target loudness using RMS"""
        # Calculate RMS
        rms = np.sqrt(np.mean(y ** 2))
        
        if rms > 0:
            # Calculate gain needed
            target_rms = 10 ** (self.target_loudness / 20)
            gain = target_rms / rms
            
            # Limit gain to prevent clipping
            if np.max(np.abs(y * gain)) > 0.97:
                gain = 0.97 / np.max(np.abs(y))
            
            y = y * gain
        
        return np.clip(y, -1.0, 1.0)
    
    def apply_dynamics_processing(self, y, sr):
        """Apply compression and EQ for podcast-like voice enhancement"""
        # Simple compressor: reduce dynamic range
        threshold = -26
        ratio = 3.5
        attack = int(0.004 * sr)
        release = int(0.2 * sr)
        
        # Convert to dB
        epsilon = 1e-6
        y_db = 20 * np.log10(np.abs(y) + epsilon)
        
        # Apply compression
        y_compressed = y.copy()
        for i in range(attack + release, len(y)):
            if y_db[i] > threshold:
                reduction = (y_db[i] - threshold) * (1 - 1/ratio)
                gain = 10 ** (-reduction / 20)
                y_compressed[i] = y[i] * gain
        
        return y_compressed
    
    def apply_podcast_polish(self, y, sr):
        """Apply EQ and compression for podcast-clean voice"""
        # High-pass filter at 90Hz
        y = self.highpass_filter(y, sr, cutoff=90)
        
        # Apply dynamics processing
        y = self.apply_dynamics_processing(y, sr)
        
        # Simple presence peak boost (around 3.5kHz)
        nyquist = sr / 2
        freq = 3500 / nyquist
        if freq < 1:
            b, a = signal.butter(2, freq, btype='high')
            presence = signal.filtfilt(b, a, y) * 0.25
            y = y + presence
        
        # Normalize
        y = self.normalize_loudness(y)
        
        return y
    
    def process_voice(self, y, sr, noise_reduction=0.6, apply_polish=True):
        """
        Complete voice processing pipeline
        
        Args:
            y: audio samples
            sr: sample rate
            noise_reduction: 0-1, strength of noise reduction
            apply_polish: whether to apply podcast-style enhancement
        
        Returns:
            processed audio
        """
        # Ensure correct sample rate
        if sr != self.sr:
            y = librosa.resample(y, orig_sr=sr, target_sr=self.sr)
            sr = self.sr
        
        # Noise reduction
        if noise_reduction > 0:
            y = self.reduce_noise_advanced(y, sr, noise_reduction)
        
        # Apply podcast polish
        if apply_polish:
            y = self.apply_podcast_polish(y, sr)
        else:
            y = self.normalize_loudness(y)
        
        # Final safety check
        y = np.clip(y, -1.0, 1.0)
        
        return y

def get_audio_duration(file_path):
    """Get duration of audio file in seconds"""
    try:
        y, sr = librosa.load(file_path, sr=None)
        duration = librosa.get_duration(y=y, sr=sr)
        return duration
    except Exception as e:
        logger.error(f"Error getting audio duration: {e}")
        return 0
