"""
Mock authentication module - stores user data in session
"""
import json
from pathlib import Path
from datetime import datetime
import uuid


class MockAuthManager:
    """Mock authentication manager for demo purposes"""
    
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.users_file = self.data_dir / 'users.json'
        self._init_users()
    
    def _init_users(self):
        """Initialize users file if it doesn't exist"""
        if not self.users_file.exists():
            with open(self.users_file, 'w') as f:
                json.dump({}, f)
    
    def _load_users(self):
        """Load users from file"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_users(self, users):
        """Save users to file"""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)
    
    def signup(self, name, email, password):
        """
        Create a new user account
        
        Args:
            name: User's display name
            email: User's email
            password: User's password (plain text for demo)
        
        Returns:
            dict with user data and status
        """
        users = self._load_users()
        
        # Check if email already exists
        for user in users.values():
            if user.get('email') == email:
                return {
                    'success': False,
                    'message': 'Email already registered'
                }
        
        user_id = str(uuid.uuid4())
        user_data = {
            'id': user_id,
            'name': name,
            'email': email,
            'password': password,  # In real app, this would be hashed
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        users[user_id] = user_data
        self._save_users(users)
        
        return {
            'success': True,
            'message': 'Account created successfully',
            'user': {
                'id': user_id,
                'name': name,
                'email': email
            }
        }
    
    def signin(self, email, password):
        """
        Authenticate user
        
        Args:
            email: User's email
            password: User's password
        
        Returns:
            dict with user data if successful
        """
        users = self._load_users()
        
        for user in users.values():
            if user.get('email') == email and user.get('password') == password:
                return {
                    'success': True,
                    'message': 'Signed in successfully',
                    'user': {
                        'id': user['id'],
                        'name': user['name'],
                        'email': user['email']
                    }
                }
        
        return {
            'success': False,
            'message': 'Invalid email or password'
        }
    
    def get_user(self, user_id):
        """Get user by ID"""
        users = self._load_users()
        user = users.get(user_id)
        
        if user:
            return {
                'id': user['id'],
                'name': user['name'],
                'email': user['email']
            }
        return None
    
    def update_user(self, user_id, **kwargs):
        """Update user data"""
        users = self._load_users()
        
        if user_id not in users:
            return {'success': False, 'message': 'User not found'}
        
        allowed_fields = ['name', 'email']
        for field in allowed_fields:
            if field in kwargs:
                users[user_id][field] = kwargs[field]
        
        users[user_id]['updated_at'] = datetime.utcnow().isoformat()
        self._save_users(users)
        
        return {
            'success': True,
            'message': 'User updated',
            'user': {
                'id': users[user_id]['id'],
                'name': users[user_id]['name'],
                'email': users[user_id]['email']
            }
        }


class SessionManager:
    """Manage user sessions"""
    
    @staticmethod
    def create_session_data(user):
        """Create session data from user"""
        return {
            'user_id': user['id'],
            'name': user['name'],
            'email': user['email']
        }
    
    @staticmethod
    def get_session_user(session):
        """Extract user from session"""
        if 'user' in session:
            return session['user']
        return None
    
    @staticmethod
    def set_session_user(session, user):
        """Set user in session"""
        session['user'] = SessionManager.create_session_data(user)
    
    @staticmethod
    def clear_session(session):
        """Clear user from session"""
        if 'user' in session:
            del session['user']
