# API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication Endpoints

### Sign Up
Create a new user account (demo authentication).

**Endpoint:** `POST /auth/signup`

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Account created successfully",
  "user": {
    "id": "uuid",
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

**Errors:**
- `400`: Missing required fields or email already registered

---

### Sign In
Authenticate user with email and password.

**Endpoint:** `POST /auth/signin`

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "securepassword"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Signed in successfully",
  "user": {
    "id": "uuid",
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

**Errors:**
- `401`: Invalid email or password
- `400`: Missing required fields

---

### Sign Out
End user session.

**Endpoint:** `POST /auth/signout`

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Signed out"
}
```

---

### Get Current User
Get authenticated user information.

**Endpoint:** `GET /auth/me`

**Headers:**
```
Cookie: session=...
```

**Response (200 OK):**
```json
{
  "success": true,
  "user": {
    "id": "uuid",
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

**Errors:**
- `401`: Not authenticated

---

## Project Endpoints

### Create Project
Create a new slideshow project.

**Endpoint:** `POST /projects`

**Request Body:**
```json
{
  "name": "My Presentation"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Project created",
  "project": {
    "id": "uuid",
    "name": "My Presentation",
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00",
    "slides": [],
    "user_name": "John Doe",
    "user_email": "john@example.com"
  }
}
```

**Errors:**
- `400`: Invalid project name
- `401`: Not authenticated

---

### List Projects
Get all projects for the authenticated user.

**Endpoint:** `GET /projects`

**Response (200 OK):**
```json
{
  "success": true,
  "projects": [
    {
      "id": "uuid1",
      "name": "My Presentation",
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:00",
      "slides": [],
      "user_name": "John Doe",
      "user_email": "john@example.com"
    },
    {
      "id": "uuid2",
      "name": "Video Tutorial",
      "created_at": "2024-01-15T11:00:00",
      "updated_at": "2024-01-15T11:00:00",
      "slides": [],
      "user_name": "John Doe",
      "user_email": "john@example.com"
    }
  ]
}
```

**Errors:**
- `401`: Not authenticated

---

### Get Project
Get specific project details.

**Endpoint:** `GET /projects/<project_id>`

**Response (200 OK):**
```json
{
  "success": true,
  "project": {
    "id": "uuid",
    "name": "My Presentation",
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00",
    "slides": [
      {
        "id": "slide1",
        "image_path": "/path/to/image.png",
        "audio_path": "/path/to/audio.wav",
        "duration": 3.0,
        "noise_reduction": 0.6,
        "apply_polish": true
      }
    ],
    "user_name": "John Doe",
    "user_email": "john@example.com"
  }
}
```

**Errors:**
- `401`: Not authenticated
- `403`: Unauthorized (not project owner)
- `404`: Project not found

---

### Update Project
Update project metadata.

**Endpoint:** `PUT /projects/<project_id>`

**Request Body:**
```json
{
  "name": "Updated Presentation"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Project updated",
  "project": { ... }
}
```

**Errors:**
- `401`: Not authenticated
- `403`: Unauthorized
- `404`: Project not found

---

### Delete Project
Delete a project and all its files.

**Endpoint:** `DELETE /projects/<project_id>`

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Project deleted"
}
```

**Errors:**
- `401`: Not authenticated
- `403`: Unauthorized
- `404`: Project not found

---

## Slide Endpoints

### Add Slides
Add image files as slides to a project.

**Endpoint:** `POST /projects/<project_id>/slides`

**Request:** (multipart/form-data)
```
images: [image1.png, image2.jpg, image3.gif]
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "3 slide(s) added",
  "slides": [
    {
      "id": "slide1",
      "image_path": "/path/to/image1.png",
      "audio_path": null,
      "duration": 3.0,
      "noise_reduction": 0.6,
      "apply_polish": true
    }
  ]
}
```

**Errors:**
- `400`: No images provided or max slides exceeded
- `401`: Not authenticated
- `403`: Unauthorized
- `404`: Project not found

**Supported Formats:**
- PNG, JPG, JPEG, GIF, BMP

---

### Get Slide
Get slide information.

**Endpoint:** `GET /projects/<project_id>/slides/<slide_id>`

**Response (200 OK):**
```json
{
  "success": true,
  "slide": {
    "id": "slide1",
    "image_path": "/path/to/image.png",
    "audio_path": "/path/to/audio.wav",
    "duration": 3.0,
    "noise_reduction": 0.6,
    "apply_polish": true
  }
}
```

**Errors:**
- `401`: Not authenticated
- `403`: Unauthorized
- `404`: Slide or project not found

---

### Update Slide
Update slide settings.

**Endpoint:** `PUT /projects/<project_id>/slides/<slide_id>`

**Request Body:**
```json
{
  "noise_reduction": 0.75,
  "apply_polish": true,
  "duration": 5.0
}
```

**Parameters:**
- `noise_reduction`: 0-1 (0 = no reduction, 1 = maximum)
- `apply_polish`: true/false (podcast voice enhancement)
- `duration`: 1-120 (seconds, for slides without voice)

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Slide updated",
  "slide": { ... }
}
```

**Errors:**
- `401`: Not authenticated
- `403`: Unauthorized
- `404`: Slide or project not found

---

### Delete Slide
Delete a slide from project.

**Endpoint:** `DELETE /projects/<project_id>/slides/<slide_id>`

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Slide deleted"
}
```

**Errors:**
- `401`: Not authenticated
- `403`: Unauthorized
- `404`: Slide or project not found

---

## Audio Endpoints

### Upload Audio
Upload audio file for a slide.

**Endpoint:** `POST /projects/<project_id>/slides/<slide_id>/audio`

**Request:** (multipart/form-data)
```
audio: audio_file.mp3
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Audio uploaded",
  "slide": {
    "id": "slide1",
    "image_path": "/path/to/image.png",
    "audio_path": "/path/to/audio.wav",
    "duration": 3.0,
    "noise_reduction": 0.6,
    "apply_polish": true
  }
}
```

**Errors:**
- `400`: Invalid audio file or file too long
- `401`: Not authenticated
- `403`: Unauthorized
- `404`: Slide or project not found

**Supported Formats:**
- WAV, MP3, OGG, M4A, FLAC, AAC

**Limits:**
- Maximum 120 seconds per slide
- Maximum 500MB file size

---

### Delete Audio
Remove audio from a slide.

**Endpoint:** `DELETE /projects/<project_id>/slides/<slide_id>/audio`

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Audio deleted",
  "slide": { ... }
}
```

**Errors:**
- `401`: Not authenticated
- `403`: Unauthorized
- `404`: Slide or project not found

---

## Video Endpoints

### Get Preview Data
Get rendering information for preview.

**Endpoint:** `GET /projects/<project_id>/preview`

**Response (200 OK):**
```json
{
  "success": true,
  "preview": [
    {
      "image_path": "/path/to/image1.png",
      "audio_path": "/path/to/audio1.wav",
      "duration": 4.2,
      "noise_reduction": 0.6,
      "apply_polish": true
    }
  ],
  "total_duration": 12.5,
  "slide_count": 3
}
```

**Errors:**
- `400`: Project has no slides
- `401`: Not authenticated
- `403`: Unauthorized
- `404`: Project not found

---

### Render Video
Generate video from project slides and audio.

**Endpoint:** `POST /projects/<project_id>/render`

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Video generated",
  "video_path": "/path/to/video.mp4",
  "video_filename": "My_Presentation.mp4"
}
```

**Errors:**
- `400`: Project has no slides
- `401`: Not authenticated
- `403`: Unauthorized
- `404`: Project not found
- `500`: Rendering failed

**Processing:**
- Processes audio (noise removal, polish)
- Generates MP4 video
- Takes time proportional to video length
- Saved to `projects/<id>/output/`

---

### Download Video
Download generated video file.

**Endpoint:** `GET /projects/<project_id>/download/<filename>`

**Response:**
- File download (MP4 format)
- Content-Type: video/mp4

**Errors:**
- `401`: Not authenticated
- `403`: Unauthorized
- `404`: Video not found

**Example:**
```
GET /projects/uuid/download/My_Presentation.mp4
```

---

## Slide Image Endpoint

### Get Slide Image
Get the image for a slide.

**Endpoint:** `GET /projects/<project_id>/slides/<slide_id>/image`

**Response:**
- Image file (JPEG format)
- Content-Type: image/jpeg

**Errors:**
- `401`: Not authenticated
- `403`: Unauthorized
- `404`: Slide or image not found

---

## Error Responses

All error responses follow this format:

```json
{
  "success": false,
  "message": "Error description"
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Not authenticated |
| 403 | Forbidden - Access denied |
| 404 | Not Found - Resource not found |
| 500 | Server Error - Internal error |

---

## Rate Limiting

No rate limiting in development. Production deployment should implement:
- Per-user request limits
- Upload size quotas
- Processing queue management

---

## Authentication

All endpoints except `/auth/signup` and `/auth/signin` require authentication via session cookie.

Session cookie is automatically set on successful sign in.

---

## CORS

CORS is enabled for cross-origin requests. Credentials must be included:

```javascript
fetch(url, {
  credentials: 'include'  // Include cookies
})
```

---

## Example Usage

### JavaScript/Fetch

```javascript
// Sign in
const signInRes = await fetch('http://localhost:5000/api/auth/signin', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password'
  })
});

// Create project
const projectRes = await fetch('http://localhost:5000/api/projects', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({
    name: 'My Slideshow'
  })
});

// Upload images
const formData = new FormData();
formData.append('images', imageFile1);
formData.append('images', imageFile2);

const slidesRes = await fetch('http://localhost:5000/api/projects/PROJECT_ID/slides', {
  method: 'POST',
  credentials: 'include',
  body: formData
});

// Render video
const videoRes = await fetch('http://localhost:5000/api/projects/PROJECT_ID/render', {
  method: 'POST',
  credentials: 'include'
});

// Download video
const downloadUrl = 'http://localhost:5000/api/projects/PROJECT_ID/download/filename.mp4';
```

---

## Webhook Support

Not implemented yet. Future versions will support webhooks for:
- Render completion notifications
- Processing status updates

---

## Versioning

Current API version: **v1**

Future API versions will be available at `/api/v2/`, `/api/v3/`, etc.

---

## Support

For API issues, check:
1. Browser console for error messages
2. Server logs for detailed errors
3. Verify authentication state
4. Check request format and parameters

