# Voice Slideshow Maker

A Python-based web application that converts your slides and voice recordings into polished video slideshows with professional-grade noise removal and podcast-style audio enhancement.

## Features

- **Upload Slides**: Add images (PNG, JPG, GIF, BMP) as slides
- **Record Voice**: Record directly in the app or upload audio files
- **Professional Audio Processing**:
  - Spectral subtraction for noise removal
  - Dynamic range compression
  - Podcast-style voice enhancement
  - Configurable noise reduction per slide
  - Optional podcast polish effect
- **Video Generation**: Creates MP4 videos from slides and audio
- **Preview**: Watch your video before downloading
- **Mock Authentication**: Demo user system (no real auth yet)
- **Project Management**: Save and manage multiple projects
- **Private by Design**: All processing happens on your device

## Installation

### Prerequisites
- Python 3.8+
- FFmpeg (for audio/video processing)

### Setup

1. Clone or download the project:
```bash
cd "Voice Slideshow Maker"
```

2. Create virtual environment (if not already done):
```bash
python -m venv venv
```

3. Activate virtual environment:

On Windows:
```bash
venv\Scripts\activate
```

On macOS/Linux:
```bash
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run the application:
```bash
python app.py
```

6. Open your browser and go to:
```
http://localhost:5000
```

## Usage

### Getting Started

1. **Sign Up / Sign In**: Create an account (mock authentication - any email/password works)
2. **Add Slides**: Drag and drop or click to upload your slide images
3. **Add Voice**:
   - Click "Record" to record your voice directly
   - Or click "Upload" to use existing audio files
4. **Adjust Settings**:
   - Use the "Noise Removal" slider to adjust noise reduction (0-100%)
   - Enable/disable "Podcast voice polish" for voice enhancement
5. **Preview**: Click "Preview video" to see your slideshow
6. **Download**: Click "Download video" to save as MP4

### Audio Processing

#### Noise Removal
- **0%**: No noise reduction
- **30-60%**: Recommended for most voices (light to moderate)
- **80-100%**: Heavy noise reduction (use for very noisy recordings)

#### Podcast Polish
- Applies professional voice enhancement
- High-pass filter to remove rumble
- Dynamic range compression to even out loud and quiet parts
- Presence boost for clarity
- Automatic loudness normalization

## Architecture

### Backend (Python/Flask)
- `app.py` - Main Flask application with all API endpoints
- `config.py` - Configuration settings
- `models.py` - Data models for projects and slides
- `auth.py` - Mock authentication system
- `audio_processor.py` - Audio processing and noise removal
- `video_generator.py` - Video creation from slides and audio

### Frontend (HTML/JavaScript)
- `templates/index.html` - Single-page application
- RESTful API communication
- Real-time project management
- Canvas-based video preview

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Create account
- `POST /api/auth/signin` - Sign in
- `POST /api/auth/signout` - Sign out
- `GET /api/auth/me` - Get current user

### Projects
- `POST /api/projects` - Create project
- `GET /api/projects` - List projects
- `GET /api/projects/<id>` - Get project
- `PUT /api/projects/<id>` - Update project
- `DELETE /api/projects/<id>` - Delete project

### Slides
- `POST /api/projects/<id>/slides` - Add slides
- `GET /api/projects/<id>/slides/<sid>` - Get slide
- `PUT /api/projects/<id>/slides/<sid>` - Update slide
- `DELETE /api/projects/<id>/slides/<sid>` - Delete slide
- `POST /api/projects/<id>/slides/<sid>/audio` - Upload audio
- `DELETE /api/projects/<id>/slides/<sid>/audio` - Delete audio

### Video
- `GET /api/projects/<id>/preview` - Get preview data
- `POST /api/projects/<id>/render` - Generate video
- `GET /api/projects/<id>/download/<filename>` - Download video

## File Structure

```
Voice Slideshow Maker/
├── app.py                 # Flask application
├── config.py             # Configuration
├── models.py             # Data models
├── auth.py               # Authentication
├── audio_processor.py    # Audio processing
├── video_generator.py    # Video generation
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
├── templates/
│   └── index.html        # Frontend
├── uploads/              # Project storage (created)
├── projects/             # Project data (created)
├── output/               # Generated videos (created)
└── README.md             # This file
```

## Configuration

Edit `config.py` to customize:
- Audio sample rate
- Video resolution and FPS
- Maximum file sizes
- Noise reduction settings
- Output format

## Known Limitations

- Mock authentication (for demo purposes)
- No real account system yet
- Videos are generated locally (can be slow for long videos)
- Requires FFmpeg for audio/video muxing

## Future Enhancements

- Real user authentication with database
- Cloud rendering option
- Real-time audio monitoring
- Multiple audio tracks
- Background music support
- Subtitle/caption generation
- Video templates and effects
- Batch rendering

## Troubleshooting

### FFmpeg not found
Install FFmpeg:
- **Windows**: `choco install ffmpeg` (using Chocolatey)
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt-get install ffmpeg`

### Audio not working
- Ensure microphone is allowed in browser
- Check browser supports Web Audio API
- Try different audio file format (WAV, MP3)

### Video generation fails
- Check disk space
- Verify images are valid
- Try smaller image sizes
- Check logs for specific errors

## License

MIT License - Feel free to use and modify

## Support

For issues and questions, please check the logs or contact support.

## Notes

- All processing happens locally - nothing is uploaded
- Projects are stored in `uploads/projects/` directory
- Generated videos are in `uploads/projects/<id>/output/`
- Maximum audio duration per slide: 120 seconds
- Maximum file upload: 500MB
