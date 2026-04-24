const users = [
  { username: 'user', password: 'user123', role: 'user', display: 'Demo User' },
  { username: 'admin', password: 'admin123', role: 'admin', display: 'Safety Admin' }
];

const countryOptions = [
  { name: 'India', dial: '+91', flag: '🇮🇳' },
  { name: 'United States', dial: '+1', flag: '🇺🇸' },
  { name: 'United Kingdom', dial: '+44', flag: '🇬🇧' },
  { name: 'UAE', dial: '+971', flag: '🇦🇪' },
  { name: 'Saudi Arabia', dial: '+966', flag: '🇸🇦' },
  { name: 'Singapore', dial: '+65', flag: '🇸🇬' }
];

const state = {
  session: null,
  streams: new Map()
};

const authSection = document.getElementById('authSection');
const userSection = document.getElementById('userSection');
const adminSection = document.getElementById('adminSection');
const logoutBtn = document.getElementById('logoutBtn');
const loginForm = document.getElementById('loginForm');
const workPermitForm = document.getElementById('workPermitForm');
const countryCodeSelect = document.getElementById('countryCode');
const userRequests = document.getElementById('userRequests');
const adminRequests = document.getElementById('adminRequests');

bootstrap();

function bootstrap() {
  seedCountryCodes();
  loadSession();
  bindEvents();
  render();
}

function bindEvents() {
  loginForm.addEventListener('submit', onLogin);
  workPermitForm.addEventListener('submit', onCreateRequest);
  logoutBtn.addEventListener('click', () => {
    localStorage.removeItem('wp_session');
    state.session = null;
    render();
  });
}

function seedCountryCodes() {
  countryCodeSelect.innerHTML = countryOptions
    .map(c => `<option value="${c.dial}">${c.flag} ${c.name} (${c.dial})</option>`)
    .join('');
}

function loadSession() {
  state.session = JSON.parse(localStorage.getItem('wp_session') || 'null');
}

function getRequests() {
  return JSON.parse(localStorage.getItem('wp_requests') || '[]');
}

function saveRequests(requests) {
  localStorage.setItem('wp_requests', JSON.stringify(requests));
}

function onLogin(e) {
  e.preventDefault();
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;
  const authError = document.getElementById('authError');

  const found = users.find(u => u.username === username && u.password === password);
  if (!found) {
    authError.textContent = 'Invalid username or password.';
    return;
  }

  authError.textContent = '';
  state.session = { username: found.username, role: found.role, display: found.display };
  localStorage.setItem('wp_session', JSON.stringify(state.session));
  render();
}

function onCreateRequest(e) {
  e.preventDefault();
  const formError = document.getElementById('formError');
  formError.textContent = '';

  const data = new FormData(workPermitForm);
  const mobile = data.get('mobile')?.toString().trim() || '';
  if (!/^[0-9]{7,15}$/.test(mobile)) {
    formError.textContent = 'Please enter a valid mobile number (7-15 digits).';
    return;
  }

  const request = {
    id: crypto.randomUUID(),
    createdBy: state.session.username,
    createdAt: new Date().toISOString(),
    status: 'pending',
    permit: {
      validFrom: data.get('validFrom'),
      validTo: data.get('validTo'),
      location: data.get('location'),
      workType: data.getAll('workType'),
      hazards: data.get('hazards'),
      precautions: data.get('precautions'),
      legalReq: data.get('legalReq'),
      notify: data.get('notify'),
      contractorName: data.get('contractorName'),
      contactPerson: data.get('contactPerson'),
      countryCode: data.get('countryCode'),
      mobile,
      department: data.get('department'),
      startTime: data.get('startTime'),
      endTime: data.get('endTime'),
      exactLocation: data.get('exactLocation'),
      ppe: data.getAll('ppe'),
      otherRequirement: data.get('otherRequirement')
    }
  };

  const requests = getRequests();
  requests.unshift(request);
  saveRequests(requests);
  workPermitForm.reset();
  seedCountryCodes();
  renderUserRequests();
}

function render() {
  const loggedIn = !!state.session;
  authSection.classList.toggle('hidden', loggedIn);
  logoutBtn.classList.toggle('hidden', !loggedIn);

  if (!loggedIn) {
    userSection.classList.add('hidden');
    adminSection.classList.add('hidden');
    return;
  }

  if (state.session.role === 'user') {
    userSection.classList.remove('hidden');
    adminSection.classList.add('hidden');
    renderUserRequests();
  } else {
    userSection.classList.add('hidden');
    adminSection.classList.remove('hidden');
    renderAdminRequests();
  }
}

function renderUserRequests() {
  const requests = getRequests().filter(r => r.createdBy === state.session.username);
  if (!requests.length) {
    userRequests.innerHTML = '<p class="muted">No requests submitted yet.</p>';
    return;
  }

  userRequests.innerHTML = requests.map(r => {
    const idDone = r.govId?.status === 'submitted';
    return `
      <article class="card" data-id="${r.id}">
        <div class="status ${r.status}">${r.status.toUpperCase()}</div>
        <h4>${r.permit.location}</h4>
        <p><strong>Contractor:</strong> ${r.permit.contractorName}</p>
        <p><strong>Contact:</strong> ${r.permit.contactPerson} (${r.permit.countryCode} ${r.permit.mobile})</p>
        <p><strong>Work Types:</strong> ${r.permit.workType.join(', ') || 'Not specified'}</p>
        ${r.status === 'approved' ? `<div class="gov-area">${idDone ? `<p class="muted">✅ Government ID submitted (${r.govId.idType})</p>` : ''}</div>` : ''}
      </article>
    `;
  }).join('');

  requests.filter(r => r.status === 'approved' && (!r.govId || r.govId.status !== 'submitted'))
    .forEach(r => injectGovIdForm(r.id));
}

function injectGovIdForm(requestId) {
  const card = userRequests.querySelector(`.card[data-id="${requestId}"] .gov-area`);
  if (!card) return;

  const tpl = document.getElementById('govIdTemplate');
  const node = tpl.content.cloneNode(true);
  const form = node.querySelector('.govIdForm');
  const video = node.querySelector('video');
  const canvas = node.querySelector('canvas');
  const preview = node.querySelector('.capture-preview');
  const fileInput = node.querySelector('input[name="photoUpload"]');
  const errorEl = node.querySelector('.govError');

  let capturedDataUrl = '';

  node.querySelector('.startCamera').addEventListener('click', async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      video.srcObject = stream;
      state.streams.set(requestId, stream);
    } catch {
      errorEl.textContent = 'Camera access denied or unavailable. Please upload from file manager.';
    }
  });

  node.querySelector('.stopCamera').addEventListener('click', () => stopStream(requestId));

  node.querySelector('.snapPhoto').addEventListener('click', () => {
    if (!video.srcObject) {
      errorEl.textContent = 'Start camera before capturing a photo.';
      return;
    }
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 360;
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
    capturedDataUrl = canvas.toDataURL('image/png');
    preview.src = capturedDataUrl;
    preview.classList.remove('hidden');
  });

  fileInput.addEventListener('change', () => {
    const file = fileInput.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      capturedDataUrl = reader.result?.toString() || '';
      preview.src = capturedDataUrl;
      preview.classList.remove('hidden');
    };
    reader.readAsDataURL(file);
  });

  form.addEventListener('submit', e => {
    e.preventDefault();
    errorEl.textContent = '';

    const data = new FormData(form);
    const idType = data.get('idType')?.toString().trim();
    const idNumber = data.get('idNumber')?.toString().trim();

    if (!idType || !idNumber) {
      errorEl.textContent = 'Please select ID type and enter ID number.';
      return;
    }
    if (!capturedDataUrl) {
      errorEl.textContent = 'Please upload or capture a photo of your ID.';
      return;
    }

    const requests = getRequests();
    const current = requests.find(r => r.id === requestId);
    if (!current) return;
    current.govId = {
      status: 'submitted',
      idType,
      idNumber,
      photoDataUrl: capturedDataUrl,
      submittedAt: new Date().toISOString()
    };
    saveRequests(requests);
    stopStream(requestId);
    renderUserRequests();
  });

  card.appendChild(node);
}

function stopStream(requestId) {
  const stream = state.streams.get(requestId);
  if (!stream) return;
  stream.getTracks().forEach(t => t.stop());
  state.streams.delete(requestId);
}

function renderAdminRequests() {
  const requests = getRequests();
  if (!requests.length) {
    adminRequests.innerHTML = '<p class="muted">No permit requests to review.</p>';
    return;
  }

  adminRequests.innerHTML = requests.map(r => `
    <article class="card" data-id="${r.id}">
      <div class="status ${r.status}">${r.status.toUpperCase()}</div>
      <h4>${r.permit.location}</h4>
      <p><strong>Requested by:</strong> ${r.createdBy}</p>
      <p><strong>Contact:</strong> ${r.permit.contactPerson} (${r.permit.countryCode} ${r.permit.mobile})</p>
      <p><strong>Hazards:</strong> ${r.permit.hazards}</p>
      <p><strong>PPE:</strong> ${r.permit.ppe.join(', ') || 'None selected'}</p>
      ${r.govId?.status === 'submitted' ? `<p class="muted">ID: ${r.govId.idType} (${r.govId.idNumber})</p>` : ''}
      <div class="actions">
        ${r.status === 'pending' ? `
          <button class="accent approve">Approve</button>
          <button class="ghost reject">Reject</button>
        ` : '<p class="muted">Decision already made.</p>'}
      </div>
    </article>
  `).join('');

  adminRequests.querySelectorAll('.card').forEach(card => {
    const id = card.dataset.id;
    const approve = card.querySelector('.approve');
    const reject = card.querySelector('.reject');

    approve?.addEventListener('click', () => updateStatus(id, 'approved'));
    reject?.addEventListener('click', () => updateStatus(id, 'rejected'));
  });
}

function updateStatus(id, status) {
  const requests = getRequests();
  const target = requests.find(r => r.id === id);
  if (!target) return;
  target.status = status;
  target.reviewedAt = new Date().toISOString();
  target.reviewedBy = state.session.username;
  saveRequests(requests);
  renderAdminRequests();
}
