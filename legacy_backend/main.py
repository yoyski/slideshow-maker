"""
Main entry point for Voice Slideshow Maker application
"""
import os
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup logging
from utils import initialize_logging
initialize_logging()

logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed"""
    logger.info("Checking dependencies...")
    
    required_packages = [
        'flask',
        'flask_cors',
        'librosa',
        'numpy',
        'scipy',
        'cv2',
        'PIL',
        'soundfile',
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing packages: {', '.join(missing_packages)}")
        logger.error("Please install with: pip install -r requirements.txt")
        return False
    
    logger.info("All dependencies installed")
    return True

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    logger.info("Checking FFmpeg...")
    
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
        if result.returncode == 0:
            logger.info("FFmpeg found")
            return True
    except:
        pass
    
    logger.warning("FFmpeg not found. Video generation may not work correctly.")
    logger.warning("Install FFmpeg from: https://ffmpeg.org/download.html")
    return False

def setup_directories():
    """Setup required directories"""
    from config import Config
    
    dirs = [
        Config.UPLOAD_FOLDER,
        Config.TEMP_FOLDER,
        Config.OUTPUT_FOLDER,
        Config.UPLOAD_FOLDER / 'projects',
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    logger.info("Directories initialized")

def main():
    """Main function"""
    print("\n" + "=" * 50)
    print("Voice Slideshow Maker")
    print("=" * 50 + "\n")
    
    logger.info("Starting Voice Slideshow Maker")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check FFmpeg (optional but recommended)
    check_ffmpeg()
    
    # Setup directories
    setup_directories()
    
    # Import and run Flask app
    logger.info("Importing Flask app...")
    from app import app
    logger.info("Flask app imported successfully")
    
    print("\n" + "=" * 50)
    print("Application starting...")
    print("=" * 50)
    print()
    print("Open your browser to: http://localhost:5000")
    print()
    print("Press Ctrl+C to stop the server")
    print()
    
    logger.info("Starting Flask development server")
    
    try:
        app.run(
            debug=False,
            host='0.0.0.0',
            port=5000,
            use_reloader=False
        )
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        print("\n\nShutdown complete")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error starting app: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
