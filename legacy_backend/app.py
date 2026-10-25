"""
Flask application for Voice Slideshow Maker
"""
import os
import logging
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, session, send_file
from flask_cors import CORS
from config import Config
from models import ProjectManager, Slide
from auth import MockAuthManager, SessionManager
from audio_processor import AudioProcessor, get_audio_duration
from video_generator import VideoGenerator
import uuid
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# Initialize CORS
CORS(app)

# Initialize managers
project_manager = ProjectManager(app.config['UPLOAD_FOLDER'])
auth_manager = MockAuthManager(app.config['UPLOAD_FOLDER'])
audio_processor = AudioProcessor()
video_generator = VideoGenerator()

# Helper functions
def allowed_file(filename, allowed_extensions):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current user from session"""
    return session.get('user')

def get_user_project_dir(project_id):
    """Get project directory for current user"""
    project_dir = project_manager.get_project_path(project_id)
    return project_dir

# Authentication Routes
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """Sign up endpoint"""
    data = request.json
    
    if not data or not all(k in data for k in ['name', 'email', 'password']):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    result = auth_manager.signup(
        data['name'],
        data['email'],
        data['password']
    )
    
    if result['success']:
        # Log the user in
        session['user'] = SessionManager.create_session_data(result['user'])
        return jsonify(result), 201
    else:
        return jsonify(result), 400

@app.route('/api/auth/signin', methods=['POST'])
def signin():
    """Sign in endpoint"""
    data = request.json
    
    if not data or not all(k in data for k in ['email', 'password']):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    result = auth_manager.signin(data['email'], data['password'])
    
    if result['success']:
        session['user'] = SessionManager.create_session_data(result['user'])
        return jsonify(result), 200
    else:
        return jsonify(result), 401

@app.route('/api/auth/signout', methods=['POST'])
def signout():
    """Sign out endpoint"""
    SessionManager.clear_session(session)
    return jsonify({'success': True, 'message': 'Signed out'}), 200

@app.route('/api/auth/me', methods=['GET'])
@login_required
def get_me():
    """Get current user"""
    user = get_current_user()
    return jsonify({'success': True, 'user': user}), 200

# Project Routes
@app.route('/api/projects', methods=['POST'])
@login_required
def create_project():
    """Create a new project"""
    user = get_current_user()
    data = request.json or {}
    
    project_name = data.get('name', 'Untitled Slideshow')
    
    project = project_manager.create_project(
        project_name,
        user_name=user['name'],
        user_email=user['email']
    )
    
    project_manager.save_project(project)
    
    return jsonify({
        'success': True,
        'message': 'Project created',
        'project': project.to_dict()
    }), 201

@app.route('/api/projects', methods=['GET'])
@login_required
def list_projects():
    """List all projects for the user"""
    user = get_current_user()
    projects = project_manager.list_projects()
    
    # Filter projects for this user
    user_projects = [p for p in projects if p.user_email == user['email']]
    
    return jsonify({
        'success': True,
        'projects': [p.to_dict() for p in user_projects]
    }), 200

@app.route('/api/projects/<project_id>', methods=['GET'])
@login_required
def get_project(project_id):
    """Get a specific project"""
    user = get_current_user()
    project = project_manager.load_project(project_id)
    
    if not project:
        return jsonify({'success': False, 'message': 'Project not found'}), 404
    
    if project.user_email != user['email']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    return jsonify({
        'success': True,
        'project': project.to_dict()
    }), 200

@app.route('/api/projects/<project_id>', methods=['PUT'])
@login_required
def update_project(project_id):
    """Update project metadata"""
    user = get_current_user()
    project = project_manager.load_project(project_id)
    
    if not project:
        return jsonify({'success': False, 'message': 'Project not found'}), 404
    
    if project.user_email != user['email']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.json or {}
    
    if 'name' in data:
        project.name = data['name']
    
    project_manager.save_project(project)
    
    return jsonify({
        'success': True,
        'message': 'Project updated',
        'project': project.to_dict()
    }), 200

@app.route('/api/projects/<project_id>', methods=['DELETE'])
@login_required
def delete_project(project_id):
    """Delete a project"""
    user = get_current_user()
    project = project_manager.load_project(project_id)
    
    if not project:
        return jsonify({'success': False, 'message': 'Project not found'}), 404
    
    if project.user_email != user['email']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    project_manager.delete_project(project_id)
    
    return jsonify({
        'success': True,
        'message': 'Project deleted'
    }), 200

# Slide Routes
@app.route('/api/projects/<project_id>/slides', methods=['POST'])
@login_required
def add_slide(project_id):
    """Add slide(s) to a project"""
    user = get_current_user()
    project = project_manager.load_project(project_id)
    
    if not project:
        return jsonify({'success': False, 'message': 'Project not found'}), 404
    
    if project.user_email != user['email']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    if 'images' not in request.files:
        return jsonify({'success': False, 'message': 'No images provided'}), 400
    
    if len(project.slides) >= Config.MAX_SLIDES:
        return jsonify({
            'success': False,
            'message': f'Maximum {Config.MAX_SLIDES} slides allowed'
        }), 400
    
    project_dir = get_user_project_dir(project_id)
    slides_dir = project_dir / 'slides'
    slides_dir.mkdir(exist_ok=True)
    
    new_slides = []
    files = request.files.getlist('images')
    
    for file in files:
        if file and allowed_file(file.filename, {'png', 'jpg', 'jpeg', 'gif', 'bmp'}):
            filename = secure_filename(file.filename)
            slide_id = str(uuid.uuid4())
            
            # Create unique filename
            ext = filename.rsplit('.', 1)[1].lower()
            saved_filename = f"{slide_id}.{ext}"
            filepath = slides_dir / saved_filename
            
            file.save(str(filepath))
            
            # Create slide object
            slide = Slide(
                id=slide_id,
                image_path=str(filepath),
                duration=3.0,
                noise_reduction=0.6,
                apply_polish=True
            )
            
            project.slides.append(slide)
            new_slides.append(slide.to_dict())
    
    if new_slides:
        project_manager.save_project(project)
    
    return jsonify({
        'success': True,
        'message': f'{len(new_slides)} slide(s) added',
        'slides': new_slides
    }), 201

@app.route('/api/projects/<project_id>/slides/<slide_id>', methods=['GET'])
@login_required
def get_slide(project_id, slide_id):
    """Get slide details"""
    user = get_current_user()
    project = project_manager.load_project(project_id)
    
    if not project:
        return jsonify({'success': False, 'message': 'Project not found'}), 404
    
    if project.user_email != user['email']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    slide = next((s for s in project.slides if s.id == slide_id), None)
    
    if not slide:
        return jsonify({'success': False, 'message': 'Slide not found'}), 404
    
    return jsonify({
        'success': True,
        'slide': slide.to_dict()
    }), 200

@app.route('/api/projects/<project_id>/slides/<slide_id>/audio', methods=['POST'])
@login_required
def upload_audio(project_id, slide_id):
    """Upload audio for a slide"""
    user = get_current_user()
    project = project_manager.load_project(project_id)
    
    if not project:
        return jsonify({'success': False, 'message': 'Project not found'}), 404
    
    if project.user_email != user['email']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    slide = next((s for s in project.slides if s.id == slide_id), None)
    
    if not slide:
        return jsonify({'success': False, 'message': 'Slide not found'}), 404
    
    if 'audio' not in request.files:
        return jsonify({'success': False, 'message': 'No audio file provided'}), 400
    
    file = request.files['audio']
    
    if not file or not allowed_file(file.filename, {'wav', 'mp3', 'ogg', 'm4a', 'flac'}):
        return jsonify({'success': False, 'message': 'Invalid audio file'}), 400
    
    try:
        project_dir = get_user_project_dir(project_id)
        audio_dir = project_dir / 'audio'
        audio_dir.mkdir(exist_ok=True)
        
        ext = file.filename.rsplit('.', 1)[1].lower()
        audio_filename = f"{slide_id}.{ext}"
        audio_path = audio_dir / audio_filename
        
        file.save(str(audio_path))
        
        # Get audio duration
        duration = get_audio_duration(str(audio_path))
        
        if duration > Config.MAX_AUDIO_DURATION:
            audio_path.unlink()
            return jsonify({
                'success': False,
                'message': f'Audio too long. Maximum {Config.MAX_AUDIO_DURATION} seconds'
            }), 400
        
        slide.audio_path = str(audio_path)
        slide.dur = duration
        
        project_manager.save_project(project)
        
        return jsonify({
            'success': True,
            'message': 'Audio uploaded',
            'slide': slide.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Error uploading audio: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/projects/<project_id>/slides/<slide_id>/audio', methods=['DELETE'])
@login_required
def delete_audio(project_id, slide_id):
    """Delete audio from a slide"""
    user = get_current_user()
    project = project_manager.load_project(project_id)
    
    if not project:
        return jsonify({'success': False, 'message': 'Project not found'}), 404
    
    if project.user_email != user['email']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    slide = next((s for s in project.slides if s.id == slide_id), None)
    
    if not slide:
        return jsonify({'success': False, 'message': 'Slide not found'}), 404
    
    if slide.audio_path and Path(slide.audio_path).exists():
        Path(slide.audio_path).unlink()
    
    slide.audio_path = None
    project_manager.save_project(project)
    
    return jsonify({
        'success': True,
        'message': 'Audio deleted',
        'slide': slide.to_dict()
    }), 200

@app.route('/api/projects/<project_id>/slides/<slide_id>', methods=['PUT'])
@login_required
def update_slide(project_id, slide_id):
    """Update slide settings"""
    user = get_current_user()
    project = project_manager.load_project(project_id)
    
    if not project:
        return jsonify({'success': False, 'message': 'Project not found'}), 404
    
    if project.user_email != user['email']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    slide = next((s for s in project.slides if s.id == slide_id), None)
    
    if not slide:
        return jsonify({'success': False, 'message': 'Slide not found'}), 404
    
    data = request.json or {}
    
    if 'noise_reduction' in data:
        slide.noise_reduction = max(0, min(1, float(data['noise_reduction'])))
    
    if 'apply_polish' in data:
        slide.apply_polish = bool(data['apply_polish'])
    
    if 'duration' in data:
        slide.duration = max(1, min(Config.MAX_AUDIO_DURATION, float(data['duration'])))
    
    project_manager.save_project(project)
    
    return jsonify({
        'success': True,
        'message': 'Slide updated',
        'slide': slide.to_dict()
    }), 200

@app.route('/api/projects/<project_id>/slides/<slide_id>', methods=['DELETE'])
@login_required
def delete_slide(project_id, slide_id):
    """Delete a slide"""
    user = get_current_user()
    project = project_manager.load_project(project_id)
    
    if not project:
        return jsonify({'success': False, 'message': 'Project not found'}), 404
    
    if project.user_email != user['email']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    slide_index = next((i for i, s in enumerate(project.slides) if s.id == slide_id), None)
    
    if slide_index is None:
        return jsonify({'success': False, 'message': 'Slide not found'}), 404
    
    slide = project.slides[slide_index]
    
    # Delete associated files
    if slide.audio_path and Path(slide.audio_path).exists():
        Path(slide.audio_path).unlink()
    
    if slide.image_path and Path(slide.image_path).exists():
        Path(slide.image_path).unlink()
    
    project.slides.pop(slide_index)
    project_manager.save_project(project)
    
    return jsonify({
        'success': True,
        'message': 'Slide deleted'
    }), 200

@app.route('/api/projects/<project_id>/reorder', methods=['PUT'])
@login_required
def reorder_slides(project_id):
    """Reorder slides"""
    user = get_current_user()
    project = project_manager.load_project(project_id)
    
    if not project:
        return jsonify({'success': False, 'message': 'Project not found'}), 404
    
    if project.user_email != user['email']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.json or {}
    slide_ids = data.get('slide_ids', [])
    
    if len(slide_ids) != len(project.slides):
        return jsonify({'success': False, 'message': 'Invalid slide list'}), 400
    
    # Reorder slides
    slide_map = {s.id: s for s in project.slides}
    project.slides = [slide_map[sid] for sid in slide_ids if sid in slide_map]
    
    project_manager.save_project(project)
    
    return jsonify({
        'success': True,
        'message': 'Slides reordered',
        'project': project.to_dict()
    }), 200

# Video Generation Routes
@app.route('/api/projects/<project_id>/preview', methods=['GET'])
@login_required
def preview_project(project_id):
    """Get preview data for project"""
    user = get_current_user()
    project = project_manager.load_project(project_id)
    
    if not project:
        return jsonify({'success': False, 'message': 'Project not found'}), 404
    
    if project.user_email != user['email']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    if not project.slides:
        return jsonify({'success': False, 'message': 'No slides in project'}), 400
    
    preview_data = []
    total_duration = 0
    
    for slide in project.slides:
        slide_data = {
            'image_path': slide.image_path,
            'audio_path': slide.audio_path,
            'duration': slide.duration,
            'noise_reduction': slide.noise_reduction,
            'apply_polish': slide.apply_polish
        }
        preview_data.append(slide_data)
        
        if slide.audio_path:
            total_duration += get_audio_duration(slide.audio_path) + 0.3
        else:
            total_duration += slide.duration
    
    return jsonify({
        'success': True,
        'preview': preview_data,
        'total_duration': total_duration,
        'slide_count': len(project.slides)
    }), 200

@app.route('/api/projects/<project_id>/render', methods=['POST'])
@login_required
def render_video(project_id):
    """Generate video for project"""
    user = get_current_user()
    project = project_manager.load_project(project_id)
    
    if not project:
        return jsonify({'success': False, 'message': 'Project not found'}), 404
    
    if project.user_email != user['email']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    if not project.slides:
        return jsonify({'success': False, 'message': 'No slides in project'}), 400
    
    try:
        project_dir = get_user_project_dir(project_id)
        output_dir = project_dir / 'output'
        output_dir.mkdir(exist_ok=True)
        
        output_filename = f"{project.name.replace(' ', '_')}.mp4"
        output_path = output_dir / output_filename
        
        # Prepare slides data
        slides_data = []
        for slide in project.slides:
            slides_data.append({
                'image_path': slide.image_path,
                'audio_path': slide.audio_path,
                'duration': slide.duration,
                'noise_reduction': slide.noise_reduction,
                'apply_polish': slide.apply_polish
            })
        
        # Generate video
        logger.info(f"Starting video generation for project {project_id}")
        video_generator.create_video_from_slides(slides_data, str(output_path))
        
        return jsonify({
            'success': True,
            'message': 'Video generated',
            'video_path': str(output_path),
            'video_filename': output_filename
        }), 200
    
    except Exception as e:
        logger.error(f"Error rendering video: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/projects/<project_id>/download/<filename>', methods=['GET'])
@login_required
def download_video(project_id, filename):
    """Download generated video"""
    user = get_current_user()
    project = project_manager.load_project(project_id)
    
    if not project:
        return jsonify({'success': False, 'message': 'Project not found'}), 404
    
    if project.user_email != user['email']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        project_dir = get_user_project_dir(project_id)
        video_path = project_dir / 'output' / filename
        
        if not video_path.exists():
            return jsonify({'success': False, 'message': 'Video not found'}), 404
        
        return send_file(
            str(video_path),
            as_attachment=True,
            download_name=filename,
            mimetype='video/mp4'
        )
    
    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/projects/<project_id>/slides/<slide_id>/image', methods=['GET'])
@login_required
def get_slide_image(project_id, slide_id):
    """Get slide image"""
    user = get_current_user()
    project = project_manager.load_project(project_id)
    
    if not project:
        return jsonify({'success': False, 'message': 'Project not found'}), 404
    
    if project.user_email != user['email']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    slide = next((s for s in project.slides if s.id == slide_id), None)
    
    if not slide:
        return jsonify({'success': False, 'message': 'Slide not found'}), 404
    
    try:
        image_path = Path(slide.image_path)
        
        if not image_path.exists():
            return jsonify({'success': False, 'message': 'Image not found'}), 404
        
        return send_file(
            str(image_path),
            mimetype='image/jpeg'
        )
    
    except Exception as e:
        logger.error(f"Error serving image: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# Home route
@app.route('/')
def index():
    """Serve the main application"""
    return render_template('index.html')

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'success': False, 'message': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({'success': False, 'message': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
