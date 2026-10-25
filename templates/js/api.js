/**
 * API Communication Layer
 * Handles all server API calls for auth, projects, and slideshows
 */

async function api(method, url, body) {
  let r;
  try {
    r = await fetch(url, {
      method,
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined
    });
  } catch {
    return { success: false, message: 'Could not reach the server. Check your connection and try again.' };
  }
  try {
    return await r.json();
  } catch {
    return { success: false, message: 'The server sent an unexpected reply. Try again.' };
  }
}

// Auth
async function signup(name, email, password) {
  return api('POST', '/api/auth/signup', { name, email, password });
}

async function signin(email, password) {
  return api('POST', '/api/auth/signin', { email, password });
}

async function signout() {
  return api('POST', '/api/auth/signout', {});
}

async function getCurrentUser() {
  return api('GET', '/api/auth/me');
}

async function deleteAccount(password) {
  return api('DELETE', '/api/auth/account', { password });
}

// Projects
async function createProject(name, description = '') {
  return api('POST', '/api/projects', { name, description });
}

async function listProjects() {
  return api('GET', '/api/projects');
}

async function getProject(id) {
  return api('GET', `/api/projects/${id}`);
}

async function updateProject(id, name, description) {
  return api('PATCH', `/api/projects/${id}`, { name, description });
}

async function deleteProject(id) {
  return api('DELETE', `/api/projects/${id}`, {});
}

// Slideshows
async function createSlideshow(name, projectId, data = '{}') {
  return api('POST', '/api/slideshows', { name, project_id: projectId, data });
}

async function listSlideshows(projectId = null) {
  let url = '/api/slideshows';
  if (projectId) url += `?project_id=${projectId}`;
  return api('GET', url);
}

async function getSlideshow(id) {
  return api('GET', `/api/slideshows/${id}`);
}

async function updateSlideshow(id, updates) {
  return api('PATCH', `/api/slideshows/${id}`, updates);
}

async function deleteSlideshow(id) {
  return api('DELETE', `/api/slideshows/${id}`, {});
}
