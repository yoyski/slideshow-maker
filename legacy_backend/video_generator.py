"""
Video generation module for creating slideshow videos with audio
"""
import cv2
import numpy as np
from pathlib import Path
import logging
from config import Config
from audio_processor import AudioProcessor, get_audio_duration
import librosa
import soundfile as sf
import os

logger = logging.getLogger(__name__)

class VideoGenerator:
    """Generate video from slides and audio"""
    
    def __init__(self):
        self.width, self.height = Config.VIDEO_RESOLUTION
        self.fps = Config.VIDEO_FPS
        self.sr = Config.SAMPLE_RATE
        self.audio_processor = AudioProcessor()
    
    def load_image(self, image_path):
        """Load image and fit to video resolution"""
        img = cv2.imread(str(image_path))
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Convert BGR to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Fit image to resolution maintaining aspect ratio
        img = self._fit_image(img)
        
        return img
    
    def _fit_image(self, img):
        """Fit image to video resolution with letterboxing"""
        h, w = img.shape[:2]
        target_w, target_h = self.width, self.height
        
        # Calculate scale to fit
        scale = min(target_w / w, target_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # Resize
        img_resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
        
        # Create canvas with black background
        canvas = np.zeros((target_h, target_w, 3), dtype=np.uint8)
        
        # Center the image
        x_offset = (target_w - new_w) // 2
        y_offset = (target_h - new_h) // 2
        
        canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = img_resized
        
        return canvas
    
    def create_video_from_slides(self, slides_data, output_path):
        """
        Create video from slides
        
        Args:
            slides_data: list of dicts with 'image_path', 'audio_path' (optional), 'duration', 'noise_reduction', 'apply_polish'
            output_path: path to save video
        """
        try:
            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(
                str(output_path),
                fourcc,
                self.fps,
                (self.width, self.height)
            )
            
            if not out.isOpened():
                raise RuntimeError("Failed to initialize video writer")
            
            # Prepare audio data
            audio_data = []
            
            # Process each slide
            for i, slide in enumerate(slides_data):
                logger.info(f"Processing slide {i+1}/{len(slides_data)}")
                
                # Load image
                img = self.load_image(slide['image_path'])
                
                # Calculate number of frames
                if slide.get('audio_path'):
                    # Get audio duration
                    duration = get_audio_duration(slide['audio_path'])
                    # Add tail (fade-out)
                    duration += 0.3
                else:
                    duration = slide.get('duration', 3.0)
                
                num_frames = int(duration * self.fps)
                
                # Write frames
                for _ in range(num_frames):
                    # Convert RGB to BGR for OpenCV
                    frame = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                    out.write(frame)
                
                # Process and add audio
                if slide.get('audio_path'):
                    try:
                        y, sr = librosa.load(slide['audio_path'], sr=self.sr, mono=True)
                        
                        # Process audio
                        y = self.audio_processor.process_voice(
                            y,
                            sr,
                            noise_reduction=slide.get('noise_reduction', 0.6),
                            apply_polish=slide.get('apply_polish', True)
                        )
                        
                        audio_data.append(y)
                    except Exception as e:
                        logger.error(f"Error processing audio for slide {i+1}: {e}")
                else:
                    # Silence for this slide
                    silence_duration = int(duration * self.sr)
                    audio_data.append(np.zeros(silence_duration, dtype=np.float32))
            
            out.release()
            logger.info(f"Video created: {output_path}")
            
            # Combine audio and save
            if audio_data:
                combined_audio = np.concatenate(audio_data)
                audio_path = Path(output_path).parent / (Path(output_path).stem + '_audio.wav')
                sf.write(audio_path, combined_audio, self.sr)
                
                # Mux audio into video using FFmpeg
                self._add_audio_to_video(str(output_path), str(audio_path), str(output_path))
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating video: {e}")
            raise
    
    def _add_audio_to_video(self, video_path, audio_path, output_path):
        """Add audio to video using FFmpeg"""
        import subprocess
        
        try:
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-y',  # Overwrite output
                output_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Clean up temporary audio file
            if os.path.exists(audio_path):
                os.remove(audio_path)
                
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e}")
            # Video was created without audio, which is acceptable
        except FileNotFoundError:
            logger.warning("FFmpeg not found. Video created without audio.")
    
    def create_preview_frame(self, image_path):
        """Create a preview frame for a slide"""
        return self.load_image(image_path)
