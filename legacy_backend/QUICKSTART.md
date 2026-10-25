# Quick Start Guide

## 5-Minute Setup

### Windows Users
1. Extract the project folder
2. Open Command Prompt inside the folder
3. Type: `run.bat` and press Enter
4. Wait for "Open your browser to: http://localhost:5000"
5. Open http://localhost:5000 in your browser

### macOS/Linux Users
1. Extract the project folder
2. Open Terminal inside the folder
3. Type: `./run.sh` and press Enter
4. Wait for "Open your browser to: http://localhost:5000"
5. Open http://localhost:5000 in your browser

## First Use

### 1. Create Account
- Click "Sign up"
- Enter any name, email, and password (demo - not saved)
- Click "Create account"

### 2. Add Slides
- Click "Click to choose slide images" or drag and drop images
- Supported: PNG, JPG, GIF, BMP
- Start with 3-5 slides for testing

### 3. Record Voice
For each slide:
- Click "Record" button
- Speak your narration
- Click "Stop" when done
- Adjust "Noise Removal" slider (0-100%)
- Optional: Uncheck "Podcast voice polish" for raw voice

### 4. Preview
- Click "Preview video" button
- Video will be generated and shown
- Click "Play" to watch
- Use slider to jump to any point

### 5. Download
- Click "Download video" button
- Video saves to your Downloads folder

## Tips & Tricks

### Recording Quality
- Use a microphone or headset for better quality
- Speak clearly and at normal volume
- Minimize background noise before recording

### Noise Removal Levels
- **0%**: No noise reduction (for clean recordings)
- **30-50%**: Light noise reduction (ideal for most cases)
- **60-80%**: Moderate noise reduction (noisy rooms)
- **100%**: Heavy noise reduction (very noisy environments)

### Slide Timing
- Slides show as long as their voice recording
- Adjust "Seconds on screen" for slides without voice
- Minimum 1 second, maximum 120 seconds

### Podcast Polish
- Enhances voice with professional EQ and compression
- Makes voice sound clearer and more podcast-like
- Works best with clear speech
- Disable for raw, unprocessed voice

### File Management
- All files stay on your computer
- Delete slides you don't need
- Re-order slides by moving them
- Create multiple projects

## Troubleshooting

### "Port 5000 in use" Error
- Stop other applications using port 5000
- Or close and reopen the run script

### No Microphone Permission
- Grant microphone access when prompted
- Check browser settings for microphone permission
- Test microphone in system settings

### Slow Video Generation
- Normal for first generation (audio processing)
- Reduce slide count for faster testing
- Smaller images process faster

### Audio Not Working
- Try a different audio file format (MP3, WAV, etc.)
- Check microphone volume in system settings
- Browser audio permission required

## Example Workflow

1. **Prepare slides** (PowerPoint → Export as PNG)
2. **Import images** (drag and drop or click)
3. **Record one slide** (test the voice)
4. **Check recording** (play it back)
5. **Fine-tune noise removal** (adjust to preference)
6. **Record remaining slides** (one at a time)
7. **Preview video** (watch full slideshow)
8. **Make adjustments** (re-record or change settings)
9. **Download** (save as MP4)

## Keyboard Shortcuts

| Action | Windows | macOS |
|--------|---------|-------|
| Start recording | Click button or Space | Click button |
| Stop recording | Click button or Space | Click button |
| Play/Pause | Click button | Click button |
| Seek video | Click slider | Click slider |

## Common Questions

### Q: How do I make my slides look better?
A: Use professional designs, consistent fonts, good contrast. The app displays your slides as-is.

### Q: Can I edit slides after uploading?
A: Delete and re-upload. Delete a slide with the Delete button.

### Q: How do I fix a bad recording?
A: Click "Clear" to delete audio, then "Record" again.

### Q: Can I use background music?
A: Not yet. Currently voice-only. Future versions will support music beds.

### Q: What's the maximum video length?
A: 1 hour per video. Create multiple projects for longer content.

### Q: Where are my videos saved?
A: In your browser's Downloads folder as MP4 files.

### Q: Can I share videos from here?
A: Download first, then share. Videos are MP4 format, compatible with all platforms.

### Q: Do you upload my files?
A: No! Everything stays on your computer. Nothing is uploaded anywhere.

## Next Steps

- Read README.md for complete features list
- Check INSTALLATION.md for advanced setup
- Review API documentation for developers
- Explore advanced audio settings

## Need Help?

1. Check README.md troubleshooting section
2. Review INSTALLATION.md for setup issues
3. Check browser console (F12) for error messages
4. Verify all dependencies installed: `python test_setup.py`

## Share Your Feedback

This is a demo application. Feedback is welcome!

---

Ready? Open http://localhost:5000 and start creating! 🎬
