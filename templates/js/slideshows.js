/**
 * Slideshows Management Module
 * Handles slideshow CRUD and UI rendering
 */

let slideshows = [];
let currentSlideshow = null;

async function loadSlideshows(projectId) {
  if (!projectId) {
    slideshows = [];
    return;
  }
  const r = await listSlideshows(projectId);
  if (!r.success) {
    slideshows = [];
    renderSlideshowsList();
    return;
  }
  slideshows = r.slideshows || [];
  renderSlideshowsList();
}

function renderSlideshowsList() {
  const list = $('#slideshowsBody');
  if (!slideshows.length) {
    list.innerHTML = `
      <div class="empty-state">
        <div class="ico"><svg class="i"><use href="#i-slides"/></svg></div>
        <h2>No slideshows yet</h2>
        <p>Create a slideshow to start recording your narration.</p>
      </div>
    `;
    return;
  }
  list.innerHTML = `<div class="list-rows">` + slideshows.map(s => {
    const updated = new Date(s.updated_at).toLocaleDateString();
    return `
    <div class="row-card" onclick="loadSlideshow(${s.id})">
      <div class="ico"><svg class="i"><use href="#i-slides"/></svg></div>
      <div class="info">
        <div class="name">${esc(s.name)}</div>
        <div class="sub">Updated: ${updated}</div>
      </div>
      <div style="position:absolute;right:12px;display:flex;gap:6px">
        <button class="icon-btn" onclick="editSlideshowStart(event, ${s.id})" type="button" aria-label="Edit"><svg class="i"><use href="#i-edit"/></svg></button>
        <button class="icon-btn" onclick="deleteSlideshowStart(event, ${s.id})" type="button" aria-label="Delete"><svg class="i"><use href="#i-trash"/></svg></button>
      </div>
    </div>
  `;
  }).join('') + `</div>`;
}

async function loadSlideshow(id) {
  const r = await getSlideshow(id);
  if (!r.success) {
    $('#status').textContent = 'Could not load slideshow';
    return;
  }
  currentSlideshow = r.slideshow;
  if (currentSlideshow.data) {
    try {
      const data = JSON.parse(currentSlideshow.data);
      showView('vEditor');
      $('#editorTitle').textContent = currentSlideshow.name;
      $('#editorMeta').textContent = `Updated: ${new Date(currentSlideshow.updated_at).toLocaleString()}`;
      $('#status').textContent = `Loaded: ${currentSlideshow.name}`;
      $('#status').classList.add('ok');
    } catch (e) {
      $('#status').textContent = 'Error loading slideshow data';
    }
  }
}

function editSlideshowStart(e, id) {
  e.stopPropagation();
  const slideshow = slideshows.find(s => s.id === id);
  if (!slideshow) return;
  currentSlideshow = slideshow;
  $('#editSlideshowName').value = slideshow.name;
  $('#editSlideshowMsg').textContent = '';
  $('#editSlideshowDlg').showModal();
}

function deleteSlideshowStart(e, id) {
  e.stopPropagation();
  currentSlideshow = slideshows.find(s => s.id === id);
  if (!currentSlideshow) return;
  $('#deleteSlideshowMsg').textContent = '';
  $('#deleteSlideshowDlg').showModal();
}

// Event Listeners
$('#newSlideshowBtn').addEventListener('click', () => {
  if (!currentProject) {
    $('#status').textContent = 'Please select a project first';
    return;
  }
  $('#slideshowName').value = '';
  $('#newSlideshowMsg').textContent = '';
  $('#newSlideshowDlg').showModal();
});

$('#newSlideshowCancel').addEventListener('click', () => $('#newSlideshowDlg').close());
$('#newSlideshowForm').addEventListener('submit', async e => {
  e.preventDefault();
  if (!currentProject) return;
  const name = $('#slideshowName').value.trim();
  if (!name) {
    $('#newSlideshowMsg').textContent = 'Enter a slideshow name.';
    return;
  }
  const btn = $('#newSlideshowGo'), label = btn.textContent;
  btn.disabled = true;
  btn.textContent = 'Creating…';
  const r = await createSlideshow(name, currentProject.id, '{}');
  btn.disabled = false;
  btn.textContent = label;
  if (!r.success) {
    $('#newSlideshowMsg').textContent = r.message;
    return;
  }
  slideshows.push(r.slideshow);
  renderSlideshowsList();
  $('#newSlideshowDlg').close();
});

$('#editSlideshowCancel').addEventListener('click', () => $('#editSlideshowDlg').close());
$('#editSlideshowForm').addEventListener('submit', async e => {
  e.preventDefault();
  if (!currentSlideshow) return;
  const name = $('#editSlideshowName').value.trim();
  if (!name) {
    $('#editSlideshowMsg').textContent = 'Enter a slideshow name.';
    return;
  }
  const btn = $('#editSlideshowGo'), label = btn.textContent;
  btn.disabled = true;
  btn.textContent = 'Saving…';
  const r = await updateSlideshow(currentSlideshow.id, { name });
  btn.disabled = false;
  btn.textContent = label;
  if (!r.success) {
    $('#editSlideshowMsg').textContent = r.message;
    return;
  }
  Object.assign(currentSlideshow, { name });
  slideshows = slideshows.map(s => s.id === currentSlideshow.id ? currentSlideshow : s);
  renderSlideshowsList();
  $('#editSlideshowDlg').close();
});

$('#deleteSlideshowCancel').addEventListener('click', () => $('#deleteSlideshowDlg').close());
$('#deleteSlideshowGo').addEventListener('click', async () => {
  if (!currentSlideshow) return;
  const btn = $('#deleteSlideshowGo'), label = btn.textContent;
  btn.disabled = true;
  btn.textContent = 'Deleting…';
  const r = await deleteSlideshow(currentSlideshow.id);
  btn.disabled = false;
  btn.textContent = label;
  if (!r.success) {
    $('#deleteSlideshowMsg').textContent = r.message;
    return;
  }
  slideshows = slideshows.filter(s => s.id !== currentSlideshow.id);
  renderSlideshowsList();
  $('#deleteSlideshowDlg').close();
  currentSlideshow = null;
});
