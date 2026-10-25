"""
Advanced audio processing features
"""
import numpy as np
from scipy import signal
import logging

logger = logging.getLogger(__name__)

class AdvancedAudioProcessing:
    """Advanced audio processing techniques"""
    
    @staticmethod
    def wiener_filter(y, sr, noise_duration=0.5):
        """
        Wiener filter for noise reduction
        Estimates noise from quiet portions and filters accordingly
        """
        # Frame parameters
        frame_length = int(0.025 * sr)  # 25ms frames
        hop_length = int(0.010 * sr)    # 10ms hop
        
        # Pad signal
        pad_amount = frame_length // 2
        y_padded = np.pad(y, (pad_amount, pad_amount), mode='reflect')
        
        # Extract frames
        frames = []
        for i in range(0, len(y_padded) - frame_length, hop_length):
            frames.append(y_padded[i:i + frame_length])
        
        if len(frames) == 0:
            return y
        
        frames = np.array(frames)
        
        # Estimate noise power from quiet frames (first 0.5s)
        noise_frames = int(noise_duration * sr / hop_length)
        noise_frames = min(noise_frames, len(frames) // 4)
        
        noise_power = np.mean(frames[:noise_frames] ** 2, axis=0)
        
        # Process frames with Wiener filter
        processed_frames = []
        for frame in frames:
            frame_power = frame ** 2
            wiener_gain = frame_power / (frame_power + noise_power + 1e-8)
            processed_frame = frame * wiener_gain
            processed_frames.append(processed_frame)
        
        processed_frames = np.array(processed_frames)
        
        # Overlap-add reconstruction
        output = np.zeros(len(y_padded))
        window = signal.windows.hann(frame_length, sym=False)
        
        for i, frame in enumerate(processed_frames):
            start = i * hop_length
            output[start:start + frame_length] += frame * window
        
        # Remove padding and normalize
        output = output[pad_amount:-pad_amount]
        
        # Normalize to match input loudness
        if len(output) == len(y):
            scale = np.std(y) / (np.std(output) + 1e-8)
            output = output * scale
        
        return output[:len(y)]
    
    @staticmethod
    def gate_and_expand(y, threshold=-40, ratio=4.0, attack=0.005, release=0.1, sr=44100):
        """
        Gate and expand - removes quiet noise between speech
        """
        # Convert to dB
        epsilon = 1e-6
        y_db = 20 * np.log10(np.abs(y) + epsilon)
        
        # Convert time constants to samples
        attack_samples = int(attack * sr)
        release_samples = int(release * sr)
        
        output = y.copy()
        
        for i in range(len(y)):
            if y_db[i] < threshold:
                # Below threshold - expand down
                expansion = (threshold - y_db[i]) * (ratio - 1)
                new_db = y_db[i] - expansion
                gain = 10 ** ((new_db - y_db[i]) / 20)
                output[i] = y[i] * gain
        
        return output
    
    @staticmethod
    def apply_eq(y, sr, eq_settings=None):
        """
        Apply parametric EQ
        
        eq_settings: list of (freq, gain_db, q_factor)
        """
        if eq_settings is None:
            eq_settings = [
                (100, 1, 0.7),      # Bass shelf
                (3500, 3, 0.9),     # Presence peak
                (10000, 1.5, 0.7),  # Brightness
            ]
        
        output = y.copy()
        nyquist = sr / 2
        
        for freq, gain_db, q in eq_settings:
            normalized_freq = freq / nyquist
            
            if normalized_freq >= 1:
                continue
            
            # Design peaking EQ filter
            w0 = 2 * np.pi * normalized_freq
            alpha = np.sin(w0) / (2 * q)
            A = 10 ** (gain_db / 40)
            
            b0 = 1 + alpha * A
            b1 = -2 * np.cos(w0)
            b2 = 1 - alpha * A
            a0 = 1 + alpha / A
            a1 = -2 * np.cos(w0)
            a2 = 1 - alpha / A
            
            b = [b0 / a0, b1 / a0, b2 / a0]
            a = [1, a1 / a0, a2 / a0]
            
            output = signal.filtfilt(b, a, output)
        
        return output
    
    @staticmethod
    def voice_vad(y, sr, threshold_db=-40, frame_length=0.025):
        """
        Simple voice activity detection
        Returns frame-level voice/silence labels
        """
        frame_len = int(frame_length * sr)
        hop_length = frame_len // 2
        
        frames = []
        for i in range(0, len(y) - frame_len, hop_length):
            frame = y[i:i + frame_len]
            frames.append(frame)
        
        # Calculate frame energy
        frame_energy_db = 20 * np.log10(np.abs(frames) + 1e-6).mean(axis=1)
        
        # Threshold
        labels = frame_energy_db > threshold_db
        
        return labels
    
    @staticmethod
    def adaptive_noise_gate(y, sr, noise_reduction=0.5):
        """
        Adaptive noise gate that learns noise profile and gates accordingly
        """
        # Parameters
        frame_length = int(0.025 * sr)
        hop_length = frame_length // 2
        
        # Extract frames
        num_frames = (len(y) - frame_length) // hop_length
        if num_frames <= 0:
            return y
        
        output = np.zeros_like(y)
        
        # Learn noise profile from first 0.5 seconds
        noise_learn_frames = min(int(0.5 * sr / hop_length), num_frames // 4)
        
        noise_profile = np.zeros(frame_length)
        for i in range(noise_learn_frames):
            start = i * hop_length
            noise_profile += np.abs(y[start:start + frame_length])
        noise_profile /= max(noise_learn_frames, 1)
        
        # Process each frame
        for i in range(num_frames):
            start = i * hop_length
            frame = y[start:start + frame_length]
            
            # Estimate frame energy
            frame_mag = np.abs(frame)
            frame_energy = np.mean(frame_mag)
            noise_energy = np.mean(noise_profile)
            
            # Calculate gating factor
            snr = (frame_energy - noise_energy) / (noise_energy + 1e-8)
            
            if snr > noise_reduction:
                # Scale gate
                gate = 1.0
            else:
                # Reduce based on noise reduction setting
                gate = max(0, (snr / noise_reduction))
            
            output[start:start + frame_length] = frame * gate
        
        return output[:len(y)]


class VoiceEnhancer:
    """Voice enhancement for podcasts and speech"""
    
    def __init__(self, sr=44100):
        self.sr = sr
        self.adv = AdvancedAudioProcessing()
    
    def enhance_podcast_voice(self, y, aggressive=False):
        """
        Enhance voice for podcast quality
        """
        # Stage 1: Noise gating
        y = self.adv.adaptive_noise_gate(y, self.sr, noise_reduction=0.4 if aggressive else 0.3)
        
        # Stage 2: Wiener filtering
        y = self.adv.wiener_filter(y, self.sr)
        
        # Stage 3: EQ for presence and clarity
        if aggressive:
            eq_settings = [
                (100, 2, 0.7),      # Reduce rumble more
                (3500, 5, 0.9),     # More presence peak
                (10000, 2.5, 0.7),  # More brightness
            ]
        else:
            eq_settings = [
                (100, 1, 0.7),
                (3500, 3, 0.9),
                (10000, 1.5, 0.7),
            ]
        
        y = self.adv.apply_eq(y, self.sr, eq_settings)
        
        # Stage 4: Normalize
        y = np.clip(y, -1, 1)
        
        return y
    
    def reduce_room_noise(self, y, strength=0.5):
        """
        Reduce room noise/background noise
        """
        return self.adv.adaptive_noise_gate(y, self.sr, noise_reduction=strength)
    
    def enhance_clarity(self, y):
        """
        Enhance speech clarity
        """
        # High-pass filter to remove rumble
        nyquist = self.sr / 2
        sos = signal.butter(5, 100 / nyquist, btype='high', output='sos')
        y = signal.sosfilt(sos, y)
        
        # Presence boost
        return self.adv.apply_eq(y, self.sr, [(3500, 4, 0.9)])
