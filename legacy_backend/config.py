import os
from pathlib import Path

class Config:
    """Base configuration"""
    BASE_DIR = Path(__file__).parent
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    TEMP_FOLDER = BASE_DIR / 'temp'
    OUTPUT_FOLDER = BASE_DIR / 'output'
    
    # Create folders if they don't exist
    UPLOAD_FOLDER.mkdir(exist_ok=True)
    TEMP_FOLDER.mkdir(exist_ok=True)
    OUTPUT_FOLDER.mkdir(exist_ok=True)
    
    MAX_UPLOAD_SIZE = 500 * 1024 * 1024  # 500MB
    MAX_SLIDES = 100
    MAX_AUDIO_DURATION = 120  # seconds
    MAX_VIDEO_DURATION = 3600  # seconds (1 hour)
    
    # Audio processing
    SAMPLE_RATE = 44100
    TARGET_LOUDNESS = -16  # dB
    NOISE_REDUCTION_STRENGTH = 0.5
    
    # Video processing
    VIDEO_RESOLUTION = (1280, 720)
    VIDEO_FPS = 30
    VIDEO_CODEC = 'libx264'
    VIDEO_FORMAT = 'mp4'
    
    # Session
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SESSION_COOKIE_SECURE = False  # Set to True in production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
