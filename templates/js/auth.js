/**
 * Authentication Module
 * Handles sign-up, sign-in, sign-out, and user account management
 */

let currentUser = null;

async function checkAuth() {
  const r = await api('GET', '/api/me');
  if (r.success) {
    currentUser = r.user;
    return true;
  }
  return false;
}

async function signup() {
  const email = $('#authEmail').value.trim();
  const password = $('#authPassword').value.trim();
  const msg = $('#authMsg');

  if (!email || !password) {
    msg.textContent = 'Please enter email and password.';
    return;
  }

  const btn = $('#authGo'), label = btn.textContent;
  btn.disabled = true;
  btn.textContent = 'Creating account…';

  const r = await api('POST', '/api/signup', { email, password });
  btn.disabled = false;
  btn.textContent = label;

  if (!r.success) {
    msg.textContent = r.message || 'Could not create account.';
    return;
  }

  currentUser = r.user;
  signin_show(false);
  showView('projects');
  nav(location.hash);
}

async function signin() {
  const email = $('#authEmail').value.trim();
  const password = $('#authPassword').value.trim();
  const msg = $('#authMsg');

  if (!email || !password) {
    msg.textContent = 'Please enter email and password.';
    return;
  }

  const btn = $('#authGo'), label = btn.textContent;
  btn.disabled = true;
  btn.textContent = 'Signing in…';

  const r = await api('POST', '/api/signin', { email, password });
  btn.disabled = false;
  btn.textContent = label;

  if (!r.success) {
    msg.textContent = r.message || 'Could not sign in.';
    return;
  }

  currentUser = r.user;
  signin_show(false);
  showView('projects');
  nav(location.hash);
}

function signin_show(yes) {
  $('#signin').classList.toggle('hidden', !yes);
  $('#app').classList.toggle('hidden', yes);
}

async function signout() {
  await api('POST', '/api/signout');
  currentUser = null;
  resetWorkspace();
  signin_show(true);
  $('#authEmail').value = '';
  $('#authPassword').value = '';
  $('#authMsg').textContent = '';
  location.hash = '#/signin';
}

async function deleteAccount() {
  if (!confirm('Delete your account and all data? This cannot be undone.')) return;

  const r = await api('POST', '/api/delete-account');
  if (!r.success) {
    alert(r.message || 'Could not delete account.');
    return;
  }

  currentUser = null;
  location.hash = '#/signup';
}

// Event listeners
$('#authSwap').addEventListener('click', () => {
  const isSignIn = !$('#authSwap').dataset.signin;
  $('#authSwap').dataset.signin = isSignIn;
  $('#authSwap').textContent = isSignIn ? 'Sign in' : 'Sign up';
  $('#authForm button[type="submit"]').textContent = isSignIn ? 'Sign in' : 'Create account';
  $('#authMsg').textContent = '';
  $('#authEmail').value = '';
  $('#authPassword').value = '';
});

$('#authForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const isSignUp = !$('#authSwap').dataset.signin;
  isSignUp ? await signup() : await signin();
});

$('#deleteBtn').addEventListener('click', async () => {
  if (confirm('Delete your account? This cannot be undone.')) {
    await deleteAccount();
  }
});

$('#signoutBtn').addEventListener('click', async () => {
  if (confirm('Sign out?')) {
    await signout();
  }
});
