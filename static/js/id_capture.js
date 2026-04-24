(function () {
  const video = document.getElementById('camera-preview');
  const canvas = document.getElementById('camera-canvas');
  const preview = document.getElementById('capture-preview');
  const fileInput = document.getElementById('id_id_photo');
  const errorEl = document.getElementById('camera-error');

  if (!video || !fileInput) return;

  let stream;

  async function startCamera() {
    try {
      stream = await navigator.mediaDevices.getUserMedia({ video: true });
      video.srcObject = stream;
      errorEl.textContent = '';
    } catch {
      errorEl.textContent = 'Camera unavailable/permission denied. You can upload from file manager.';
    }
  }

  function stopCamera() {
    if (!stream) return;
    stream.getTracks().forEach(track => track.stop());
    stream = null;
  }

  async function capturePhoto() {
    if (!video.srcObject) {
      errorEl.textContent = 'Start camera first.';
      return;
    }

    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 360;
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);

    const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.92));
    const file = new File([blob], `captured-id-${Date.now()}.jpg`, { type: 'image/jpeg' });

    const dt = new DataTransfer();
    dt.items.add(file);
    fileInput.files = dt.files;

    preview.src = URL.createObjectURL(file);
    preview.classList.remove('hidden');
    errorEl.textContent = '';
  }

  document.getElementById('start-camera')?.addEventListener('click', startCamera);
  document.getElementById('stop-camera')?.addEventListener('click', stopCamera);
  document.getElementById('capture-photo')?.addEventListener('click', capturePhoto);

  window.addEventListener('beforeunload', stopCamera);
})();
