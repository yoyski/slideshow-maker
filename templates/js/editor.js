/**
 * Editor Module
 * Handles slide editing, voice recording, and video playback
 */

let slides = [];
let recording = false;
let playing = false;
let downloading = false;
let recorders = [];
let recDest = null;
let offsetTime = 0;
let startedAt = 0;
let raf = null;

const ctx = () => {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
  return audioCtx;
};

let audioCtx = null;
let master = null;
let spk = null;
let gainNode = null;

function clearAll() {
  stopRec(true);
  stopPlayback();
  slides = [];
  recorders = [];
  offsetTime = 0;
  startedAt = 0;
  if (audioCtx) {
    audioCtx.close();
    audioCtx = null;
    master = null;
    spk = null;
  }
  render();
}

function setPlayBtn(playing) {
  const btn = $('#playBtn');
  btn.textContent = playing ? '⏸ Pause' : '▶ Play';
}

function closeMenus() {
  document.querySelectorAll('.kmenu.open').forEach(m => {
    m.classList.remove('open');
    m.previousElementSibling.setAttribute('aria-expanded', 'false');
  });
}

function setStatus(msg, cls) {
  const el = $('#status');
  el.textContent = msg;
  el.className = 'status ' + (cls || '');
}

function esc(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function $(...args) {
  return typeof args[0] === 'string' ? document.querySelector(args[0]) : args[0];
}

function show(id) {
  if (typeof id === 'string') id = $(id);
  if (id) id.classList.remove('hidden');
}

function mmss(t) {
  const m = Math.floor(t / 60);
  const s = Math.floor(t % 60);
  return (m < 10 ? '0' : '') + m + ':' + (s < 10 ? '0' : '') + s;
}

function render() {
  // Render slides and UI
  const cards = $('#cards');
  if (!slides.length) {
    cards.innerHTML = `<div class="card"><div class="shot"><div class="empty">No slides yet. Add images to get started.</div></div><div class="body"><div class="tools"><button class="tool" onclick="$('#pick').click()" type="button"><svg class="i"><use href="#i-plus"/></svg>Add</button></div></div></div>`;
    return;
  }

  cards.innerHTML = slides.map((s, i) => `
    <div class="card${recording && recordersFind(s)?.recording ? ' recording' : ''}">
      <div class="shot">${s.img ? `<img src="${s.img}">` : '<div class="empty">No image</div>'}</div>
      <div class="body">
        <div class="head"><h3>Slide ${i + 1}</h3><span class="chip${recording && recordersFind(s)?.recording ? ' live' : ''}">${mmss(s.dur || 0)}</span></div>
        <div class="slider"><div class="row"><span>Duration</span><span>${mmss(s.dur || 0)}</span></div><input type="range" min="0.5" max="30" step="0.1" value="${s.dur || 2}" onchange="slides[${i}].dur=+this.value;render()"></div>
        ${s.aud ? `<audio controls src="${s.aud}" style="width:100%"></audio>` : '<div class="empty">No narration</div>'}
        <div class="tools${slides.length > 1 ? '' : ' no-m'}">
          <button class="tool" onclick="recorders[${i}]?stopRec(false,${i}):startRec(${i})" type="button" aria-label="Record"><svg class="i"><use href="#i-mic"/></svg><span class="of">Record</span></button>
          <button class="tool m-hide" onclick="deleteSlide(${i})" type="button" aria-label="Delete"><svg class="i"><use href="#i-trash"/></svg><span class="of">Delete</span></button>
        </div>
      </div>
    </div>
  `).join('');
}

function recordersFind(s) {
  return recorders.find(r => r.slide === s);
}

async function startRec(idx) {
  const slide = slides[idx];
  if (!slide || recordersFind(slide)) return;

  const ctx = new (window.AudioContext || window.webkitAudioContext)();
  const stream = ctx.createMediaStreamDestination();
  const mediaRecorder = new MediaRecorder(stream.stream);
  const chunks = [];

  mediaRecorder.ondataavailable = e => e.data.size && chunks.push(e.data);
  mediaRecorder.onstop = () => {
    const blob = new Blob(chunks, { type: 'audio/webm' });
    slide.aud = URL.createObjectURL(blob);
    recorders = recorders.filter(r => r !== recorder);
    render();
  };

  const recorder = { slide, stream, mediaRecorder, chunks, recording: true };
  recorders.push(recorder);
  mediaRecorder.start();
  render();
}

function stopRec(all, idx) {
  if (all) {
    recorders.forEach(r => r.mediaRecorder?.stop());
    recorders = [];
  } else if (idx !== undefined) {
    const r = recorders[idx];
    if (r) {
      r.mediaRecorder.stop();
      recorders.splice(idx, 1);
    }
  }
  render();
}

function deleteSlide(idx) {
  slides.splice(idx, 1);
  render();
}

function addFiles(files) {
  Array.from(files).forEach(file => {
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = e => {
        slides.push({ img: e.target.result, dur: 2, aud: null });
        render();
      };
      reader.readAsDataURL(file);
    }
  });
}

async function play(t) {
  if (playing) return;
  playing = true;
  setPlayBtn(true);
  offset = t;
  startedAt = ctx().currentTime - t;

  function loop() {
    const t = ctx().currentTime - startedAt;
    if (t >= total()) {
      playing = false;
      stopPlayback();
      offset = total();
      setPlayBtn(false);
      return;
    }
    raf = requestAnimationFrame(loop);
  }

  raf = requestAnimationFrame(loop);
}

function pause() {
  if (!playing) return;
  offsetTime = ctx().currentTime - startedAt;
  playing = false;
  cancelAnimationFrame(raf);
  setPlayBtn(false);
}

function stopPlayback() {
  if (downloading) return;
  playing = false;
  cancelAnimationFrame(raf);
  setPlayBtn(false);
}

function total() {
  return slides.reduce((sum, s) => sum + (s.dur || 2), 0);
}

// UI Event listeners
$('#pick').addEventListener('change', e => {
  addFiles(e.target.files);
  e.target.value = '';
});

const drop = $('#drop');
['dragenter', 'dragover'].forEach(n => drop.addEventListener(n, e => {
  e.preventDefault();
  drop.classList.add('over');
}));
['dragleave', 'drop'].forEach(n => drop.addEventListener(n, e => {
  e.preventDefault();
  drop.classList.remove('over');
}));
drop.addEventListener('drop', e => addFiles(e.dataTransfer.files));

$('#previewBtn').addEventListener('click', () => {
  $('#previewBox').classList.remove('hidden');
  offsetTime = 0;
  $('#previewBox').scrollIntoView({ behavior: 'smooth', block: 'start' });
  play(0);
});

$('#closePreview').addEventListener('click', () => {
  if (downloading) return;
  stopPlayback();
  $('#previewBox').classList.add('hidden');
});

$('#addMoreBtn').addEventListener('click', () => {
  $('#pick').click();
});

$('#playBtn').addEventListener('click', () => {
  playing ? pause() : play(offsetTime >= total() ? 0 : offsetTime);
});

$('#seek').addEventListener('input', e => {
  if (downloading) return;
  const t = (+e.target.value / 1000) * total();
  offsetTime = t;
});

$('#dlBtn').addEventListener('click', async () => {
  if (!slides.length || downloading) return;
  
  const types = ['video/mp4;codecs=avc1,mp4a.40.2', 'video/mp4', 'video/webm;codecs=vp9,opus', 'video/webm;codecs=vp8,opus', 'video/webm'];
  const mime = types.find(t => MediaRecorder.isTypeSupported(t));
  
  if (!mime) {
    setStatus('This browser cannot save video. Try Chrome, Edge or Firefox.', 'err');
    return;
  }

  pause();
  await ctx().resume();

  downloading = true;
  $('#dlBtn').disabled = true;
  $('#playBtn').disabled = true;
  $('#seek').disabled = true;
  $('#previewBtn').disabled = true;

  const T = total();
  setStatus(`Recording video: 0:00 of ${mmss(T)}. Keep this tab open.`);

  setTimeout(() => {
    downloading = false;
    $('#dlBtn').disabled = false;
    $('#playBtn').disabled = false;
    $('#seek').disabled = false;
    $('#previewBtn').disabled = !slides.length;
    setStatus('Video saved.');
  }, T * 1000 + 1000);
});
