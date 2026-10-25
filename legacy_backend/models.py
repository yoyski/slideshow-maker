"""
Data models for the slideshow maker
"""
from dataclasses import dataclass, asdict
from typing import List, Optional
from pathlib import Path
import json
import uuid
from datetime import datetime

@dataclass
class Slide:
    """Represents a single slide"""
    id: str
    image_path: str
    audio_path: Optional[str] = None
    duration: float = 3.0  # seconds without voice
    noise_reduction: float = 0.6  # 0-1
    apply_polish: bool = True
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)


@dataclass
class Project:
    """Represents a slideshow project"""
    id: str
    name: str
    created_at: str
    updated_at: str
    slides: List[Slide]
    user_name: str = "Guest"
    user_email: Optional[str] = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'slides': [slide.to_dict() for slide in self.slides],
            'user_name': self.user_name,
            'user_email': self.user_email
        }
    
    @classmethod
    def from_dict(cls, data):
        slides = [Slide.from_dict(s) for s in data.get('slides', [])]
        return cls(
            id=data['id'],
            name=data['name'],
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            slides=slides,
            user_name=data.get('user_name', 'Guest'),
            user_email=data.get('user_email')
        )


class ProjectManager:
    """Manage projects on disk"""
    
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.projects_dir = self.base_dir / 'projects'
        self.projects_dir.mkdir(exist_ok=True)
    
    def create_project(self, name, user_name="Guest", user_email=None):
        """Create a new project"""
        project_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        project = Project(
            id=project_id,
            name=name,
            created_at=now,
            updated_at=now,
            slides=[],
            user_name=user_name,
            user_email=user_email
        )
        
        return project
    
    def save_project(self, project):
        """Save project to disk"""
        project_dir = self.projects_dir / project.id
        project_dir.mkdir(exist_ok=True)
        
        metadata_path = project_dir / 'project.json'
        
        project.updated_at = datetime.utcnow().isoformat()
        
        with open(metadata_path, 'w') as f:
            json.dump(project.to_dict(), f, indent=2)
        
        return str(project_dir)
    
    def load_project(self, project_id):
        """Load project from disk"""
        metadata_path = self.projects_dir / project_id / 'project.json'
        
        if not metadata_path.exists():
            return None
        
        with open(metadata_path, 'r') as f:
            data = json.load(f)
        
        return Project.from_dict(data)
    
    def delete_project(self, project_id):
        """Delete project and all its files"""
        import shutil
        project_dir = self.projects_dir / project_id
        
        if project_dir.exists():
            shutil.rmtree(project_dir)
            return True
        return False
    
    def list_projects(self):
        """List all projects"""
        projects = []
        
        for project_dir in self.projects_dir.iterdir():
            if project_dir.is_dir():
                project = self.load_project(project_dir.name)
                if project:
                    projects.append(project)
        
        # Sort by created_at descending
        projects.sort(key=lambda p: p.created_at, reverse=True)
        return projects
    
    def get_project_path(self, project_id):
        """Get the project directory path"""
        return self.projects_dir / project_id
