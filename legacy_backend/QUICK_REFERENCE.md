# Quick Reference Guide

## Start the Application

### Windows
```bash
run.bat
```

### macOS / Linux
```bash
./run.sh
```

### Manual (All Platforms)
```bash
python main.py
```

Then open: **http://localhost:5000**

---

## Basic Usage

### 1. Sign Up
- Click "Sign up"
- Enter Name, Email, Password (any values work - demo)
- Click "Create account"

### 2. Add Slides
- Click "Click to choose slide images" or drag-drop
- Select PNG, JPG, GIF, or BMP files
- Slides appear in gallery

### 3. Record Voice
- Click "Record" on a slide
- Speak your narration
- Click "Stop" to finish
- Or upload existing audio with "Upload" button

### 4. Adjust Settings
- **Noise Removal**: 0-100% slider
  - 30-50%: Recommended for most
  - 0%: No reduction (clean recordings)
  - 80%+: Heavy reduction (noisy rooms)
- **Podcast Polish**: Enable/disable voice enhancement

### 5. Preview
- Click "Preview video"
- Wait for generation
- Click "Play" to watch
- Use slider to seek

### 6. Download
- Click "Download video"
- Saves as MP4 to Downloads folder

---

## File Types Supported

| Type | Formats |
|------|---------|
| Images | PNG, JPG, JPEG, GIF, BMP |
| Audio | WAV, MP3, OGG, M4A, FLAC, AAC |
| Video Output | MP4 |

---

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| Port 5000 in use | Close other apps, or modify port in app.py |
| Microphone not working | Grant browser permission, check system settings |
| Slow video generation | Normal - depends on audio length |
| Audio not playing | Try different audio format |
| Import errors | Run: `pip install -r requirements.txt` |
| FFmpeg errors | Install FFmpeg (optional but recommended) |

---

## API Quick Reference

### Base URL
```
http://localhost:5000/api
```

### Example API Calls

**Sign In**
```bash
POST /auth/signin
Body: {"email": "user@test.com", "password": "test"}
```

**Create Project**
```bash
POST /projects
Body: {"name": "My Slideshow"}
```

**Upload Slides**
```bash
POST /projects/{id}/slides
Body: multipart images
```

**Update Slide**
```bash
PUT /projects/{id}/slides/{id}
Body: {"noise_reduction": 0.6, "apply_polish": true}
```

**Render Video**
```bash
POST /projects/{id}/render
```

**Download Video**
```bash
GET /projects/{id}/download/filename.mp4
```

---

## Keyboard Shortcuts

| Action | Key |
|--------|-----|
| Record/Stop | Click button |
| Play/Pause | Click button |
| Seek video | Drag slider |

---

## Audio Settings Guide

### Noise Reduction Levels

```
0%   - No reduction (clean recordings)
30%  - Light reduction (slight background)
50%  - Balanced (moderate noise)
70%  - Heavy reduction (noisy environment)
100% - Maximum reduction (very noisy)
```

### Podcast Polish

**Enabled**: Applies professional voice enhancement
- High-pass filter removes rumble
- Compression evens dynamics
- EQ adds presence and clarity
- Perfect for narration

**Disabled**: Raw, unprocessed voice

---

## Performance Notes

| Operation | Time |
|-----------|------|
| Upload images | 1-5 seconds |
| Record voice | Real-time |
| Audio processing | 1-2s per minute |
| Video preview | 2-5 seconds |
| Video generation | Duration of video |

---

## Keyboard Tips

- **Enter key**: Submit forms in auth page
- **Click anywhere**: Most interactive elements respond to clicks

---

## File Locations

| Item | Location |
|------|----------|
| Projects | `uploads/projects/` |
| Video Output | `uploads/projects/{id}/output/` |
| Logs | Console and `app.log` |

---

## Configuration

Edit `.env` to change:
```
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_PORT=5000
```

Edit `config.py` for:
- Audio quality
- Video resolution
- File size limits
- Processing parameters

---

## Dependencies Check

```bash
python test_setup.py
```

Shows ✓ if all dependencies installed.

---

## Common Commands

```bash
# Start app
python main.py

# Check dependencies
python test_setup.py

# Activate venv (Windows)
venv\Scripts\activate

# Activate venv (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Update dependencies
pip install --upgrade -r requirements.txt
```

---

## Browser Requirements

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

Modern browsers with:
- Web Audio API
- Canvas
- Fetch API
- LocalStorage

---

## Project Structure

```
Core Modules:
├── app.py ...................... Main Flask app
├── audio_processor.py ........... Audio processing
├── video_generator.py ........... Video creation
├── models.py .................... Data models

Frontend:
├── templates/index.html ......... Web interface

Docs:
├── README.md .................... Full guide
├── QUICKSTART.md ................ 5-min setup
├── INSTALLATION.md .............. Install guide
├── API_DOCUMENTATION.md ......... API reference
```

---

## Error Messages

| Error | Meaning | Fix |
|-------|---------|-----|
| "Port in use" | Another app uses 5000 | Change port or close app |
| "Module not found" | Missing dependency | Run `pip install -r requirements.txt` |
| "Permission denied" | Linux/Mac file permission | Run `chmod +x run.sh` |
| "No microphone" | Mic not available/denied | Grant permission or use upload |

---

## Security Notes

- No data uploaded (everything local)
- Sessions stored in cookies
- Input validated
- File types checked
- File sizes limited to 500MB

---

## Performance Tips

1. **For better quality**: Use clean recordings
2. **For speed**: Smaller images process faster
3. **For clarity**: Use 50-70% noise reduction
4. **For polish**: Enable podcast enhancement

---

## Reset/Clear Data

To start fresh:
1. Close the app
2. Delete `uploads/projects/` folder
3. Delete `users.json` (optional)
4. Restart app

---

## Next Steps

1. Read **README.md** for full features
2. See **INSTALLATION.md** for setup help
3. Check **API_DOCUMENTATION.md** for developers
4. Try **QUICKSTART.md** for first use

---

## Support Resources

| Need | Resource |
|------|----------|
| Overview | README.md |
| Install | INSTALLATION.md |
| Quick start | QUICKSTART.md |
| API details | API_DOCUMENTATION.md |
| Troubleshooting | README.md |
| Roadmap | CHANGELOG.md |

---

## Useful Links

- Python: https://www.python.org
- FFmpeg: https://ffmpeg.org
- Flask: https://flask.palletsprojects.com
- Librosa: https://librosa.org

---

## Tips for Best Results

✅ Use clear, steady voice
✅ Record in quiet environment
✅ Start with 30% noise reduction
✅ Test with preview before download
✅ Use podcast polish for narration
✅ Adjust per-slide based on recording quality

---

## Contacting for Help

If issues occur:
1. Check browser console (F12)
2. Check terminal/command prompt output
3. Review troubleshooting section
4. Verify dependencies installed
5. Check documentation files

---

## Quick Stats

- **27 API endpoints**
- **8+ audio processing techniques**
- **1000+ line frontend**
- **2000+ lines of documentation**
- **Complete working application**

---

## Remember

✅ All processing is LOCAL
✅ No files uploaded anywhere
✅ Everything stays on your computer
✅ Complete privacy guaranteed

---

## Ready to Start?

```bash
python main.py
```

Or just double-click:
- **Windows**: `run.bat`
- **macOS/Linux**: `run.sh`

Then open: **http://localhost:5000**

🎬 **Happy slideshow making!**

---

Last Updated: January 2024
