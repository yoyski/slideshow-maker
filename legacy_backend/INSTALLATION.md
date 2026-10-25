# Installation Guide - Voice Slideshow Maker

## System Requirements

- **Python**: 3.8 or newer
- **OS**: Windows, macOS, or Linux
- **RAM**: 4GB minimum (8GB recommended)
- **Disk Space**: 2GB for application and dependencies
- **Internet**: For initial dependency download only

## Quick Start (Recommended)

### Windows
1. Download and extract the project
2. Open Command Prompt in the project folder
3. Double-click `run.bat`
4. Open browser to `http://localhost:5000`

### macOS / Linux
1. Download and extract the project
2. Open Terminal in the project folder
3. Run: `chmod +x run.sh && ./run.sh`
4. Open browser to `http://localhost:5000`

## Manual Installation

### Step 1: Install Python
- Download from [python.org](https://www.python.org)
- **Important**: Check "Add Python to PATH" during installation

### Step 2: Install FFmpeg (Recommended)

#### Windows
```bash
# Using Chocolatey (if installed)
choco install ffmpeg

# Or download from:
# https://ffmpeg.org/download.html
```

#### macOS
```bash
brew install ffmpeg
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# CentOS/RHEL
sudo yum install ffmpeg

# Fedora
sudo dnf install ffmpeg
```

### Step 3: Setup Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment

# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
# Make sure you're in the project directory and venv is activated
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Step 5: Run the Application

#### Option A: Using main.py
```bash
python main.py
```

#### Option B: Using Flask directly
```bash
python app.py
```

#### Option C: Using the run scripts
- Windows: Double-click `run.bat` or run in Command Prompt
- macOS/Linux: Run `./run.sh`

### Step 6: Access the Application
Open your web browser and go to:
```
http://localhost:5000
```

## Dependency Installation Issues

### Issue: "pip: command not found"
- **Solution**: Python is not in PATH. Reinstall Python and check "Add Python to PATH"

### Issue: SSL Certificate errors when installing packages
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### Issue: Permission denied on macOS/Linux
```bash
# Make scripts executable
chmod +x run.sh
./run.sh
```

### Issue: LibROSA audio reading fails
```bash
# Install audioread dependency
pip install audioread

# On macOS (if needed):
brew install ffmpeg
```

## Optional Packages

### For Enhanced Audio Processing
```bash
pip install webrtcvad  # Voice activity detection
pip install pyroomacoustics  # Room acoustics simulation
```

### For Advanced Video Features
```bash
pip install moviepy  # Additional video editing
pip install imageio-ffmpeg  # Alternative FFmpeg wrapper
```

## Verification

### Check Installation
```bash
python test_setup.py
```

This will verify all required packages are installed.

### Test Dependencies
```bash
python -c "import librosa, numpy, flask, cv2; print('All dependencies OK')"
```

## Troubleshooting

### Port 5000 Already in Use
```bash
# Change port in app.py or run with different port:
# On Windows:
set FLASK_PORT=5001 && python app.py

# On macOS/Linux:
FLASK_PORT=5001 python app.py
```

### FFmpeg Not Found Error
- FFmpeg is optional but recommended for audio/video muxing
- Install FFmpeg from https://ffmpeg.org/download.html
- Make sure it's in your system PATH

### Audio Processing Errors
- Ensure you have write permissions in the application directory
- Check available disk space
- Try with a smaller audio file first

### Windows Defender / Antivirus Issues
- Some audio processing libraries may trigger warnings
- Add the application folder to your antivirus whitelist

## Uninstallation

### To Remove the Application
```bash
# Deactivate virtual environment
deactivate

# Delete the project folder and venv
rm -rf "Voice Slideshow Maker"  # macOS/Linux
rmdir /s "Voice Slideshow Maker"  # Windows
```

## Virtual Environment

### Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### Deactivate Virtual Environment
```bash
deactivate
```

## Development Setup

### For Development/Contributing
```bash
# Install with development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov flake8 black

# Run tests
pytest

# Code quality check
flake8 app.py config.py models.py
```

## Environment Variables

Create a `.env` file in the project root:

```env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
FLASK_PORT=5000
```

## Running in Production

**Not Recommended for Production without proper setup!**

For production deployment:
1. Set `FLASK_ENV=production`
2. Use a production WSGI server like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn app:app
   ```
3. Setup proper database
4. Use real authentication
5. Setup SSL/HTTPS
6. Configure firewall
7. Use process manager (systemd, supervisord, etc.)

## Support

- Check the README.md for usage instructions
- Review app logs for error details
- Ensure all dependencies are installed correctly
- Try running `python test_setup.py` to verify setup

## Next Steps

After installation:
1. Read README.md for usage guide
2. Open the application in your browser
3. Create an account (demo authentication)
4. Try uploading a slide and recording voice
5. Generate and preview your first video!

Enjoy making slideshows!
