/**
 * App Initialization and Workspace Management
 * Handles views, routing, navigation, and project/slideshow management
 */

let projects = null;
let slideshows = [];
let curProj = null;
let curShow = null;
let view = 'projects';
let navTok = 0;
let shownShowId = null;
let dlg = null;

const V = {
  projects: $('#vProjects'),
  project: $('#vProject'),
  editor: $('#vEditor')
};

const sameId = (a, b) => String(a) === String(b);
const hashP = id => '#/app/p/' + encodeURIComponent(id);
const hashS = (p, s) => hashP(p) + '/s/' + encodeURIComponent(s);
const fmtDate = d => {
  const x = new Date(d);
  return isNaN(x) ? '' : x.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
};
const plural = (n, w) => `${n} ${w}${n === 1 ? '' : 's'}`;

function resetWorkspace() {
  projects = null;
  slideshows = [];
  curProj = curShow = null;
  shownShowId = null;
  view = 'projects';
  clearAll();
}

function showView(v) {
  view = v;
  $('main.app').classList.toggle('narrow', v !== 'editor');
  Object.entries(V).forEach(([k, el]) => el.classList.toggle('hidden', k !== v));
  show('app');
  closeMenus();
  if (v !== 'editor') {
    stopPlayback();
    stopRec(true);
  }
  window.scrollTo(0, 0);
}

function crumbs(items) {
  const sep = '<svg class="i sep"><use href="#i-r"/></svg>';
  $('#crumbs').innerHTML = items.map((c, i) => 
    i === items.length - 1 
      ? `<span class="here" aria-current="page">${esc(c[0])}</span>`
      : `<a href="${c[1]}">${esc(c[0])}</a>${sep}`
  ).join('');
}

const kmenu = (kind, id, label) => 
  `<div class="km-wrap"><button type="button" class="km-btn" data-menu aria-label="${esc(label)}" aria-haspopup="menu" aria-expanded="false"><svg class="i"><use href="#i-dots"/></svg></button>
  <div class="kmenu down" role="menu"><button type="button" role="menuitem" data-wa="edit-${kind}" data-id="${esc(id)}"><svg class="i"><use href="#i-edit"/></svg>Edit details</button><hr><button type="button" role="menuitem" class="danger" data-wa="delete-${kind}" data-id="${esc(id)}"><svg class="i"><use href="#i-trash"/></svg>Delete</button></div></div>`;

async function ensureProjects() {
  if (projects) return true;
  const r = await api('GET', '/api/projects');
  if (!r.success) {
    setStatus(r.message || 'Could not load your projects.', 'err');
    return false;
  }
  projects = r.projects || [];
  return true;
}

async function loadShows(pid) {
  const r = await api('GET', '/api/slideshows?project_id=' + encodeURIComponent(pid));
  if (!r.success) {
    setStatus(r.message || 'Could not load slideshows.', 'err');
    slideshows = [];
    return false;
  }
  slideshows = r.slideshows || [];
  return true;
}

async function nav(h) {
  const tok = ++navTok;
  const m = h.match(/^#\/app(?:\/p\/([^/]+)(?:\/s\/([^/]+))?)?\/?$/);
  if (!m) {
    location.hash = '#/app';
    return;
  }
  
  const pid = m[1] && decodeURIComponent(m[1]);
  const sid = m[2] && decodeURIComponent(m[2]);
  setStatus('');

  if (!pid) {
    if (view !== 'projects' || !projects) {
      showView('projects');
      if (!projects) $('#projectsBody').innerHTML = '<p class="loading">Loading projects…</p>';
    }
    crumbs([['Projects']]);
    const ok = await ensureProjects();
    if (tok !== navTok) return;
    showView('projects');
    renderProjects(ok);
    return;
  }

  if (!projects) {
    showView(sid ? 'editor' : 'project');
    const ok = await ensureProjects();
    if (tok !== navTok) return;
    if (!ok) {
      location.hash = '#/app';
      return;
    }
  }

  curProj = projects.find(p => sameId(p.id, pid));
  if (!curProj) {
    setStatus('That project no longer exists.', 'err');
    location.hash = '#/app';
    return;
  }

  if (!sid) {
    curShow = null;
    crumbs([['Projects', '#/app'], [curProj.name]]);
    $('#projectTitle').textContent = curProj.name;
    $('#projectDescTxt').textContent = curProj.description || '';
    $('#projectDescTxt').classList.toggle('hidden', !curProj.description);
    showView('project');
    $('#slideshowsBody').innerHTML = '<p class="loading">Loading slideshows…</p>';
    const ok = await loadShows(pid);
    if (tok !== navTok) return;
    curProj.slideshow_count = slideshows.length;
    renderShows(ok);
    return;
  }

  if (!slideshows.length || !slideshows.some(s => sameId(s.id, sid)) || !sameId(slideshows[0].project_id ?? pid, pid)) {
    const ok = await loadShows(pid);
    if (tok !== navTok) return;
    if (!ok) {
      location.hash = hashP(pid);
      return;
    }
  }

  curShow = slideshows.find(s => sameId(s.id, sid));
  if (!curShow) {
    setStatus('That slideshow no longer exists.', 'err');
    location.hash = hashP(pid);
    return;
  }

  // slides live only in this browser tab, so switching to another slideshow starts a clean editor
  if (shownShowId !== null && !sameId(shownShowId, curShow.id)) clearAll();
  shownShowId = curShow.id;
  crumbs([['Projects', '#/app'], [curProj.name, hashP(curProj.id)], [curShow.name]]);
  $('#editorTitle').textContent = curShow.name;
  showView('editor');
  render();
  timelineChanged();
}

function renderProjects(ok) {
  const b = $('#projectsBody');
  if (!ok) {
    b.innerHTML = `<div class="empty-state"><div class="ico"><svg class="i"><use href="#i-folder"/></svg></div><h2>Could not load projects</h2><p>Check your connection and try again.</p><button class="btn" type="button" data-wa="retry">Try again</button></div>`;
    return;
  }
  if (!projects.length) {
    b.innerHTML = `<div class="empty-state"><div class="ico"><svg class="i"><use href="#i-folder"/></svg></div><h2>No projects yet</h2><p>Create your first project, then add slideshows to it.</p><button class="btn primary" type="button" data-wa="new-project"><svg class="i"><use href="#i-plus"/></svg>New project</button></div>`;
    return;
  }
  b.innerHTML = `<div class="grid-cards">` + projects.map(p => 
    `<div class="pwrap"><a class="pcard" href="${hashP(p.id)}"><span class="ico"><svg class="i"><use href="#i-folder"/></svg></span><h3>${esc(p.name)}</h3><p class="desc">${p.description ? esc(p.description) : 'No description'}</p><span class="meta"><svg class="i"><use href="#i-slides"/></svg>${plural(p.slideshow_count || 0, 'slideshow')}</span></a>${kmenu('project', p.id, 'Options for ' + p.name)}</div>`
  ).join('') + `<button class="pnew" type="button" data-wa="new-project"><svg class="i"><use href="#i-plus"/></svg>New project</button></div>`;
}

function renderShows(ok) {
  const b = $('#slideshowsBody');
  if (!ok) {
    b.innerHTML = `<div class="empty-state"><div class="ico"><svg class="i"><use href="#i-slides"/></svg></div><h2>Could not load slideshows</h2><p>Check your connection and try again.</p><button class="btn" type="button" data-wa="retry">Try again</button></div>`;
    return;
  }
  if (!slideshows.length) {
    b.innerHTML = `<div class="empty-state"><div class="ico"><svg class="i"><use href="#i-slides"/></svg></div><h2>No slideshows in this project</h2><p>A slideshow is one narrated video. Create one to add slides and record your voice.</p><button class="btn primary" type="button" data-wa="new-show"><svg class="i"><use href="#i-plus"/></svg>New slideshow</button></div>`;
    return;
  }
  b.innerHTML = `<div class="list-rows">` + slideshows.map(s => 
    `<div class="pwrap rowwrap"><a class="row-card" href="${hashS(curProj.id, s.id)}"><span class="ico"><svg class="i"><use href="#i-slides"/></svg></span><span class="info"><div class="name">${esc(s.name)}</div><div class="sub">${s.updated_at ? 'Updated ' + fmtDate(s.updated_at) : 'New'}</div></span></a>${kmenu('show', s.id, 'Options for ' + s.name)}</div>`
  ).join('') + `</div>`;
}

// Event delegation for menus and actions
function closeAllMenus() {
  closeMenus();
}

$('#appView').addEventListener('click', e => {
  const mb = e.target.closest('[data-menu]');
  if (mb) {
    e.preventDefault();
    const m = mb.nextElementSibling;
    const o = !m.classList.contains('open');
    closeMenus();
    m.classList.toggle('open', o);
    mb.setAttribute('aria-expanded', o);
    if (o) m.querySelector('button').focus();
    return;
  }

  const b = e.target.closest('[data-wa]');
  if (!b) return;

  const a = b.dataset.wa;
  const id = b.dataset.id;
  closeMenus();

  if (a === 'new-project') openProjectDlg();
  else if (a === 'edit-project') openProjectDlg(projects.find(p => sameId(p.id, id)));
  else if (a === 'delete-project') askDelete('project', projects.find(p => sameId(p.id, id)));
  else if (a === 'new-show') openShowDlg();
  else if (a === 'edit-show') openShowDlg(slideshows.find(s => sameId(s.id, id)));
  else if (a === 'delete-show') askDelete('show', slideshows.find(s => sameId(s.id, id)));
  else if (a === 'retry') {
    projects = null;
    nav(location.hash);
  }
});

$('#newProjectBtn').addEventListener('click', () => openProjectDlg());
$('#newSlideshowBtn').addEventListener('click', () => openShowDlg());

// Project dialog
function openProjectDlg(p) {
  dlg = { kind: 'project', item: p || null };
  $('#projectDlgTitle').textContent = p ? 'Edit project' : 'New project';
  $('#projectGo').textContent = p ? 'Save changes' : 'Create project';
  $('#projectName').value = p ? p.name : '';
  $('#projectDesc').value = p ? p.description || '' : '';
  $('#projectMsg').textContent = '';
  $('#projectDlg').showModal();
  $('#projectName').focus();
}

$('#projectCancel').addEventListener('click', () => $('#projectDlg').close());

$('#projectForm').addEventListener('submit', async e => {
  e.preventDefault();
  const name = $('#projectName').value.trim();
  const description = $('#projectDesc').value.trim();
  const edit = dlg && dlg.item;

  if (!name) {
    $('#projectMsg').textContent = 'Enter a project name.';
    return;
  }

  const btn = $('#projectGo'), label = btn.textContent;
  btn.disabled = true;
  btn.textContent = edit ? 'Saving…' : 'Creating…';

  const r = edit
    ? await api('PATCH', '/api/projects/' + edit.id, { name, description })
    : await api('POST', '/api/projects', { name, description });

  btn.disabled = false;
  btn.textContent = label;

  if (!r.success) {
    $('#projectMsg').textContent = r.message || 'Something went wrong. Try again.';
    return;
  }

  $('#projectDlg').close();

  if (edit) {
    Object.assign(edit, { name, description });
    if (curProj && sameId(curProj.id, edit.id)) {
      nav(location.hash);
    } else {
      renderProjects(true);
    }
  } else {
    const p = r.project || { id: r.id, name, description, slideshow_count: 0 };
    projects = [...(projects || []), p];
    location.hash = hashP(p.id);
  }
});

// Slideshow dialog
function openShowDlg(s) {
  if (!curProj) return;
  dlg = { kind: 'show', item: s || null };
  $('#showDlgTitle').textContent = s ? 'Rename slideshow' : 'New slideshow';
  $('#showGo').textContent = s ? 'Save changes' : 'Create slideshow';
  $('#showName').value = s ? s.name : '';
  $('#showMsg').textContent = '';
  $('#showDlg').showModal();
  $('#showName').focus();
}

$('#showCancel').addEventListener('click', () => $('#showDlg').close());

$('#showForm').addEventListener('submit', async e => {
  e.preventDefault();
  const name = $('#showName').value.trim();
  const edit = dlg && dlg.item;

  if (!name) {
    $('#showMsg').textContent = 'Enter a slideshow name.';
    return;
  }

  const btn = $('#showGo'), label = btn.textContent;
  btn.disabled = true;
  btn.textContent = edit ? 'Saving…' : 'Creating…';

  const r = edit
    ? await api('PATCH', '/api/slideshows/' + edit.id, { name })
    : await api('POST', '/api/slideshows', { name, project_id: curProj.id, data: '{}' });

  btn.disabled = false;
  btn.textContent = label;

  if (!r.success) {
    $('#showMsg').textContent = r.message || 'Something went wrong. Try again.';
    return;
  }

  $('#showDlg').close();

  if (edit) {
    Object.assign(edit, { name });
    renderShows(true);
  } else {
    const s = r.slideshow || { id: r.id, name, project_id: curProj.id };
    slideshows = [s, ...slideshows];
    location.hash = hashS(curProj.id, s.id);
  }
});

// Delete confirmation
function askDelete(kind, item) {
  if (!item) return;
  const msg = kind === 'project' ? `Delete "${esc(item.name)}" and all slideshows in it?` : `Delete "${esc(item.name)}"?`;
  if (!confirm(msg + ' This cannot be undone.')) return;
  doDelete(kind, item);
}

async function doDelete(kind, item) {
  const endpoint = kind === 'project' ? '/api/projects/' + item.id : '/api/slideshows/' + item.id;
  const r = await api('DELETE', endpoint);

  if (!r.success) {
    setStatus(r.message || 'Could not delete.', 'err');
    return;
  }

  if (kind === 'project') {
    projects = projects.filter(p => !sameId(p.id, item.id));
    if (curProj && sameId(curProj.id, item.id)) {
      location.hash = '#/app';
    } else {
      renderProjects(true);
    }
  } else {
    slideshows = slideshows.filter(s => !sameId(s.id, item.id));
    renderShows(true);
  }

  setStatus(kind === 'project' ? 'Project deleted.' : 'Slideshow deleted.', 'ok');
}

// Router
window.addEventListener('hashchange', () => {
  if (currentUser) {
    nav(location.hash);
  }
});

// Initialize app on load
async function initApp() {
  const ok = await checkAuth();
  if (!ok) {
    location.hash = '#/signin';
    signin_show(true);
    return;
  }

  signin_show(false);
  nav(location.hash || '#/app');
}

// Start the app when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initApp);
} else {
  initApp();
}
