"""
Utility functions for the application
"""
import os
import shutil
from pathlib import Path
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

class FileManager:
    """Manage file operations"""
    
    @staticmethod
    def ensure_dir(path):
        """Ensure directory exists"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def safe_delete(path):
        """Safely delete file or directory"""
        path = Path(path)
        try:
            if path.is_dir():
                shutil.rmtree(path)
            elif path.exists():
                path.unlink()
            return True
        except Exception as e:
            logger.error(f"Error deleting {path}: {e}")
            return False
    
    @staticmethod
    def get_file_size(path):
        """Get file size in MB"""
        return Path(path).stat().st_size / (1024 * 1024)
    
    @staticmethod
    def clean_filename(filename):
        """Clean filename for safe storage"""
        import re
        # Remove special characters
        clean = re.sub(r'[^\w\s.-]', '', filename)
        # Replace spaces with underscores
        clean = re.sub(r'\s+', '_', clean)
        # Remove consecutive dots
        clean = re.sub(r'\.+', '.', clean)
        return clean
    
    @staticmethod
    def list_files(directory, extension=None):
        """List files in directory"""
        path = Path(directory)
        if not path.exists():
            return []
        
        if extension:
            extension = extension if extension.startswith('.') else f'.{extension}'
            return list(path.glob(f'*{extension}'))
        else:
            return [f for f in path.iterdir() if f.is_file()]


class TimingUtils:
    """Timing and duration utilities"""
    
    @staticmethod
    def seconds_to_mmss(seconds):
        """Convert seconds to MM:SS format"""
        seconds = max(0, int(seconds))
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}:{secs:02d}"
    
    @staticmethod
    def mmss_to_seconds(mmss):
        """Convert MM:SS to seconds"""
        try:
            parts = mmss.split(':')
            if len(parts) == 2:
                return int(parts[0]) * 60 + int(parts[1])
        except:
            pass
        return 0
    
    @staticmethod
    def human_readable_time(seconds):
        """Convert seconds to human readable format"""
        seconds = int(seconds)
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            mins = seconds // 60
            secs = seconds % 60
            return f"{mins}m {secs}s" if secs else f"{mins}m"
        else:
            hours = seconds // 3600
            mins = (seconds % 3600) // 60
            return f"{hours}h {mins}m" if mins else f"{hours}h"


class ProcessMetrics:
    """Track and log processing metrics"""
    
    def __init__(self):
        self.metrics = {}
        self.start_time = datetime.utcnow()
    
    def record(self, key, value):
        """Record a metric"""
        self.metrics[key] = value
    
    def get(self, key, default=None):
        """Get a metric"""
        return self.metrics.get(key, default)
    
    def elapsed_time(self):
        """Get elapsed time since start"""
        return (datetime.utcnow() - self.start_time).total_seconds()
    
    def to_dict(self):
        """Convert metrics to dictionary"""
        return {
            **self.metrics,
            'elapsed_time': self.elapsed_time(),
            'start_time': self.start_time.isoformat()
        }
    
    def log_summary(self, prefix=""):
        """Log metrics summary"""
        elapsed = self.elapsed_time()
        logger.info(f"{prefix} - Metrics: {json.dumps(self.to_dict(), indent=2)}")
        logger.info(f"{prefix} - Completed in {TimingUtils.human_readable_time(elapsed)}")


class ValidationUtils:
    """Validation utilities"""
    
    ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'}
    ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a', 'flac', 'aac'}
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'avi', 'mov'}
    
    @staticmethod
    def validate_image(filename):
        """Check if file is a valid image"""
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        return ext in ValidationUtils.ALLOWED_IMAGE_EXTENSIONS
    
    @staticmethod
    def validate_audio(filename):
        """Check if file is a valid audio file"""
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        return ext in ValidationUtils.ALLOWED_AUDIO_EXTENSIONS
    
    @staticmethod
    def validate_video(filename):
        """Check if file is a valid video file"""
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        return ext in ValidationUtils.ALLOWED_VIDEO_EXTENSIONS
    
    @staticmethod
    def validate_project_name(name):
        """Validate project name"""
        if not name or not isinstance(name, str):
            return False
        if len(name) > 255:
            return False
        # No path traversal
        if '..' in name or '/' in name or '\\' in name:
            return False
        return True
    
    @staticmethod
    def validate_noise_reduction(value):
        """Validate noise reduction value"""
        try:
            val = float(value)
            return 0 <= val <= 1
        except:
            return False


class CacheManager:
    """Simple cache management"""
    
    def __init__(self, max_items=100):
        self.cache = {}
        self.max_items = max_items
        self.access_times = {}
    
    def get(self, key):
        """Get item from cache"""
        return self.cache.get(key)
    
    def set(self, key, value, ttl=None):
        """Set item in cache"""
        if len(self.cache) >= self.max_items:
            # Remove least recently used
            lru_key = min(self.access_times, key=self.access_times.get)
            del self.cache[lru_key]
            del self.access_times[lru_key]
        
        self.cache[key] = value
        self.access_times[key] = datetime.utcnow()
    
    def delete(self, key):
        """Delete item from cache"""
        if key in self.cache:
            del self.cache[key]
            del self.access_times[key]
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        self.access_times.clear()


class ErrorHandler:
    """Error handling utilities"""
    
    ERROR_MESSAGES = {
        'invalid_image': 'Invalid image file format',
        'invalid_audio': 'Invalid audio file format',
        'file_too_large': 'File is too large',
        'project_not_found': 'Project not found',
        'slide_not_found': 'Slide not found',
        'audio_too_long': 'Audio file is too long',
        'no_slides': 'Project has no slides',
        'rendering_failed': 'Failed to render video',
        'unauthorized': 'Unauthorized access',
        'server_error': 'Internal server error',
    }
    
    @staticmethod
    def get_error_message(error_code):
        """Get human-readable error message"""
        return ErrorHandler.ERROR_MESSAGES.get(error_code, 'An error occurred')
    
    @staticmethod
    def format_error_response(error_code, details=None):
        """Format error response"""
        message = ErrorHandler.get_error_message(error_code)
        response = {
            'success': False,
            'error_code': error_code,
            'message': message
        }
        if details:
            response['details'] = details
        return response


def initialize_logging(log_file='app.log'):
    """Initialize logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)
