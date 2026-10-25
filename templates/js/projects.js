/**
 * Projects Management Module
 * Handles project CRUD and UI rendering
 */

let projects = [];
let currentProject = null;

async function loadProjects() {
  const r = await listProjects();
  if (!r.success) return;
  projects = r.projects || [];
  renderProjectsList();
}

function renderProjectsList() {
  const list = $('#projectsBody');
  if (!projects.length) {
    list.innerHTML = `
      <div class="empty-state">
        <div class="ico"><svg class="i"><use href="#i-folder"/></svg></div>
        <h2>No projects yet</h2>
        <p>Create a project to organize your slideshows and get started.</p>
      </div>
    `;
    return;
  }
  list.innerHTML = `<div class="grid-cards">` + projects.map(p => `
    <div class="pwrap">
      <div class="pcard" onclick="selectProject(${p.id})">
        <div class="ico" style="background:var(--accent-soft);color:var(--accent)"><svg class="i"><use href="#i-folder"/></svg></div>
        <h3>${esc(p.name)}</h3>
        <p class="desc">${p.description ? esc(p.description) : 'No description'}</p>
        <div class="meta"><svg class="i"><use href="#i-slides"/></svg>${p.slideshow_count || 0} slideshow(s)</div>
      </div>
      <div class="km-wrap">
        <button class="km-btn" onclick="openProjectMenu(event, ${p.id})" aria-label="Options" type="button"><svg class="i"><use href="#i-dots"/></svg></button>
        <div class="kmenu" id="menu-${p.id}">
          <button onclick="editProjectStart(${p.id})" type="button"><svg class="i"><use href="#i-edit"/></svg>Edit</button>
          <button onclick="deleteProjectStart(${p.id})" type="button" class="danger"><svg class="i"><use href="#i-trash"/></svg>Delete</button>
        </div>
      </div>
    </div>
  `).join('') + `</div>`;
}

function selectProject(id) {
  currentProject = projects.find(p => p.id === id);
  if (currentProject) {
    showView('vProject');
    $('#projectTitle').textContent = currentProject.name;
    $('#projectDescTxt').textContent = currentProject.description || 'No description';
    loadSlideshows(id);
  }
}

function openProjectMenu(e, id) {
  e.stopPropagation();
  const menu = $(`#menu-${id}`);
  menu.classList.toggle('open');
}

function editProjectStart(id) {
  const project = projects.find(p => p.id === id);
  if (!project) return;
  currentProject = project;
  $('#editProjectName').value = project.name;
  $('#editProjectDesc').value = project.description || '';
  $('#editProjectMsg').textContent = '';
  $('#editProjectDlg').showModal();
}

function deleteProjectStart(id) {
  currentProject = projects.find(p => p.id === id);
  if (!currentProject) return;
  $('#deleteProjectMsg').textContent = '';
  $('#deleteProjectDlg').showModal();
}

// Event Listeners
$('#newProjectBtn').addEventListener('click', () => {
  $('#projectName').value = '';
  $('#projectDesc').value = '';
  $('#newProjectMsg').textContent = '';
  $('#newProjectDlg').showModal();
});

$('#newProjectCancel').addEventListener('click', () => $('#newProjectDlg').close());
$('#newProjectForm').addEventListener('submit', async e => {
  e.preventDefault();
  const name = $('#projectName').value.trim();
  const desc = $('#projectDesc').value.trim();
  if (!name) {
    $('#newProjectMsg').textContent = 'Enter a project name.';
    return;
  }
  const btn = $('#newProjectGo'), label = btn.textContent;
  btn.disabled = true;
  btn.textContent = 'Creating…';
  const r = await createProject(name, desc);
  btn.disabled = false;
  btn.textContent = label;
  if (!r.success) {
    $('#newProjectMsg').textContent = r.message;
    return;
  }
  projects.push(r.project);
  renderProjectsList();
  $('#newProjectDlg').close();
});

$('#editProjectCancel').addEventListener('click', () => $('#editProjectDlg').close());
$('#editProjectForm').addEventListener('submit', async e => {
  e.preventDefault();
  if (!currentProject) return;
  const name = $('#editProjectName').value.trim();
  if (!name) {
    $('#editProjectMsg').textContent = 'Enter a project name.';
    return;
  }
  const desc = $('#editProjectDesc').value.trim();
  const btn = $('#editProjectGo'), label = btn.textContent;
  btn.disabled = true;
  btn.textContent = 'Saving…';
  const r = await updateProject(currentProject.id, name, desc);
  btn.disabled = false;
  btn.textContent = label;
  if (!r.success) {
    $('#editProjectMsg').textContent = r.message;
    return;
  }
  Object.assign(currentProject, { name, description: desc });
  projects = projects.map(p => p.id === currentProject.id ? currentProject : p);
  renderProjectsList();
  $('#editProjectDlg').close();
});

$('#deleteProjectCancel').addEventListener('click', () => $('#deleteProjectDlg').close());
$('#deleteProjectGo').addEventListener('click', async () => {
  if (!currentProject) return;
  const btn = $('#deleteProjectGo'), label = btn.textContent;
  btn.disabled = true;
  btn.textContent = 'Deleting…';
  const r = await deleteProject(currentProject.id);
  btn.disabled = false;
  btn.textContent = label;
  if (!r.success) {
    $('#deleteProjectMsg').textContent = r.message;
    return;
  }
  projects = projects.filter(p => p.id !== currentProject.id);
  renderProjectsList();
  $('#deleteProjectDlg').close();
  currentProject = null;
  showView('vProjects');
});
