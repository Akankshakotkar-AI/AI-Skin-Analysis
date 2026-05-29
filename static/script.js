// ════════════════════════════════════════════════════════════════════
//  AI SKIN DETECTOR — COMPLETE FIXED FRONTEND (script.js)
// ════════════════════════════════════════════════════════════════════
// Fixes: Camera capture, webcam streaming, proper image handling

let currentSkinScore = 0;
let currentSeverity = '';
let currentAcneCount = 0;
let currentAcneDetails = {};  // Store detailed acne info for dynamic recommendations
let selectedFile = null;
let cameraStream = null;
let capturedImageData = null;

// ════ INITIALIZATION ════
window.addEventListener('DOMContentLoaded', () => {
  setupDragDrop();
  setupFileInput();
  loadHistory();
});

// ════ TAB SWITCHING ════
function switchTab(tab) {
  const uploadContent = document.getElementById('tabUploadContent');
  const cameraContent = document.getElementById('tabCameraContent');
  const tabUploadBtn = document.getElementById('tabUpload');
  const tabCameraBtn = document.getElementById('tabCamera');

  if (tab === 'upload') {
    uploadContent.style.display = 'block';
    cameraContent.style.display = 'none';
    tabUploadBtn.classList.add('active');
    tabCameraBtn.classList.remove('active');
    stopCamera(); // Stop camera if it was running
  } else if (tab === 'camera') {
    uploadContent.style.display = 'none';
    cameraContent.style.display = 'block';
    tabUploadBtn.classList.remove('active');
    tabCameraBtn.classList.add('active');
  }
}

// ════ DRAG & DROP UPLOAD ════
function setupDragDrop() {
  const zone = document.getElementById('uploadZone');
  if (!zone) return;

  zone.addEventListener('dragover', (e) => {
    e.preventDefault();
    zone.classList.add('drag');
  });

  zone.addEventListener('dragleave', () => {
    zone.classList.remove('drag');
  });

  zone.addEventListener('drop', (e) => {
    e.preventDefault();
    zone.classList.remove('drag');
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      handleUploadFile(file);
    } else {
      toast('Please drop an image file (JPG, PNG, WEBP)');
    }
  });

  zone.addEventListener('click', (e) => {
    if (!e.target.closest('.up-btn')) {
      document.getElementById('fileInput').click();
    }
  });
}

function setupFileInput() {
  const input = document.getElementById('fileInput');
  if (input) {
    input.addEventListener('change', (e) => {
      if (e.target.files[0]) {
        handleUploadFile(e.target.files[0]);
      }
    });
  }
}

// ════ FILE UPLOAD HANDLER ════
function handleUploadFile(file) {
  if (!file.type.startsWith('image/')) {
    toast('Invalid file type. Use JPG, PNG, or WEBP');
    return;
  }

  if (file.size > 10 * 1024 * 1024) {
    toast('File too large. Max 10MB');
    return;
  }

  selectedFile = file;
  const reader = new FileReader();
  
  reader.onload = (e) => {
    document.getElementById('previewImg').src = e.target.result;
    document.getElementById('previewWrap').classList.add('show');
    document.getElementById('analyzeBtn').classList.add('show');
    document.getElementById('uploadZone').style.display = 'none';
  };
  
  reader.readAsDataURL(file);
}

function resetUpload() {
  selectedFile = null;
  document.getElementById('fileInput').value = '';
  document.getElementById('previewWrap').classList.remove('show');
  document.getElementById('analyzeBtn').classList.remove('show');
  document.getElementById('uploadZone').style.display = 'block';
  document.getElementById('previewImg').src = '';
}

// ════ CAMERA CAPTURE ════
async function startCamera() {
  try {
    // Request camera with high resolution constraints
    const constraints = {
      video: {
        facingMode: 'user',
        width: { ideal: 1280 },
        height: { ideal: 720 }
      },
      audio: false
    };

    cameraStream = await navigator.mediaDevices.getUserMedia(constraints);
    const video = document.getElementById('camVideo');
    video.srcObject = cameraStream;

    // Wait for video to load
    video.onloadedmetadata = () => {
      video.play();
      document.getElementById('camStart').style.display = 'none';
      document.getElementById('camControls').style.display = 'flex';
    };

  } catch (err) {
    console.error('Camera error:', err);
    if (err.name === 'NotAllowedError') {
      toast('Camera permission denied. Please allow camera access.');
    } else if (err.name === 'NotFoundError') {
      toast('No camera found on this device.');
    } else {
      toast('Error accessing camera: ' + err.message);
    }
  }
}

function stopCamera() {
  if (cameraStream) {
    cameraStream.getTracks().forEach(track => track.stop());
    cameraStream = null;
  }
  document.getElementById('camControls').style.display = 'none';
  document.getElementById('camStart').style.display = 'block';
  document.getElementById('camVideo').srcObject = null;
}

function capturePhoto() {
  const video = document.getElementById('camVideo');
  const canvas = document.getElementById('camCanvas');
  const ctx = canvas.getContext('2d');

  // Set canvas size to video size
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  // Draw video frame to canvas
  ctx.drawImage(video, 0, 0);

  // Convert to image data
  capturedImageData = canvas.toDataURL('image/jpeg', 0.95);
  
  // Show preview
  document.getElementById('camPreviewImg').src = capturedImageData;
  document.getElementById('camPreviewWrap').classList.add('show');
  document.getElementById('camControls').style.display = 'none';
}

function retakePhoto() {
  capturedImageData = null;
  document.getElementById('camPreviewWrap').classList.remove('show');
  document.getElementById('camPreviewImg').src = '';
  document.getElementById('camControls').style.display = 'flex';
}

async function analyzeCaptured() {
  if (!capturedImageData) {
    toast('No photo captured');
    return;
  }

  // Convert data URL to blob and send
  showLoader(true);
  
  try {
    const blob = await fetch(capturedImageData).then(r => r.blob());
    const formData = new FormData();
    formData.append('file', blob, 'camera-capture.jpg');

    const res = await fetch('/upload', { method: 'POST', body: formData });
    const data = await res.json();
    
    showLoader(false);

    if (!res.ok || data.error) {
      toast(data.error || 'Analysis failed');
      return;
    }

    displayResults(data);
    stopCamera();
    document.getElementById('tabUpload').click();

  } catch (err) {
    showLoader(false);
    toast('Server error: ' + err.message);
  }
}

// ════ MAIN ANALYSIS ════
async function analyzeImage() {
  if (!selectedFile) {
    toast('Please select a photo first');
    return;
  }

  showLoader(true);
  const formData = new FormData();
  formData.append('file', selectedFile);

  try {
    const res = await fetch('/upload', { method: 'POST', body: formData });
    const data = await res.json();

    showLoader(false);

    if (!res.ok || data.error) {
      toast(data.error || 'Analysis failed');
      return;
    }

    displayResults(data);

  } catch (err) {
    showLoader(false);
    toast('Server error: ' + err.message);
  }
}

// ════ DISPLAY RESULTS ════
function displayResults(data) {
  currentSkinScore = data.skin_score || 0;
  currentSeverity = data.severity || 'Unknown';
  currentAcneCount = data.acne_count || 0;
  currentAcneDetails = data.acne_details || {}; // NEW: Store detailed data

  // Hide upload, show results
  document.getElementById('uploadSection').style.display = 'none';
  document.getElementById('results').classList.add('show');

  // Display images
  document.getElementById('origImg').src = data.original_url || '';
  document.getElementById('resImg').src = data.result_url || '';

  // Display score
  document.getElementById('ringNum').textContent = currentSkinScore;

  // Animate score ring
  const col = currentSkinScore >= 70 ? '#22c55e' : currentSkinScore >= 40 ? '#eab308' : '#ef4444';
  const ring = document.getElementById('ringFill');
  ring.style.stroke = col;
  document.getElementById('ringNum').style.color = col;

  setTimeout(() => {
    ring.style.strokeDashoffset = 314 - (currentSkinScore / 100) * 314;
  }, 120);

  // Display stats
  document.getElementById('acneNum').textContent = currentAcneCount;
  document.getElementById('sevText').textContent = currentSeverity;
  document.getElementById('sevBadge').innerHTML = 
    `<span class="sev-badge sev-${currentSeverity}">${currentSeverity}</span>`;

  // Display dynamic recommendations (NOW BASED ON ACTUAL DATA)
  const icons = ['💧', '😴', '🥗', '🧴', '🌿', '☀️', '🏃', '🚫', '🛁', '💆'];
  const grid = document.getElementById('recoGrid');
  grid.innerHTML = '';
  
  (data.recommendations || []).forEach((r, i) => {
    const card = document.createElement('div');
    card.className = 'reco-card';
    card.innerHTML = `<span class="reco-icon">${icons[i % icons.length]}</span><span>${r}</span>`;
    grid.appendChild(card);
    setTimeout(() => card.classList.add('show'), i * 100);
  });

  saveHistory(data);
  document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
}

// ════ RESET ════
function resetAll() {
  document.getElementById('results').classList.remove('show');
  document.getElementById('uploadSection').style.display = 'block';
  resetUpload();
  window.scrollTo({ top: 0, behavior: 'smooth' });

  // Reset ring
  document.getElementById('ringFill').style.strokeDashoffset = '314';
  document.getElementById('ringNum').textContent = '--';
  document.getElementById('acneNum').textContent = '--';
  document.getElementById('sevText').textContent = '--';
  document.getElementById('recoGrid').innerHTML = '';

  // Reset chat
  document.getElementById('chatMsgs').innerHTML = `
    <div class="msg ai">
      <div class="avatar">🤖</div>
      <div class="bubble">Hi! I've analyzed your skin. Ask me anything! 😊</div>
    </div>`;
}

// ════ LOADER ════
function showLoader(show) {
  const overlay = document.getElementById('loader');
  if (show) {
    overlay.classList.add('show');
    const bar = document.getElementById('prog');
    bar.style.animation = 'none';
    bar.offsetHeight;
    bar.style.animation = '';
  } else {
    overlay.classList.remove('show');
  }
}

// ════ AI CHAT (CONTEXT-AWARE) ════
async function sendChat() {
  const inp = document.getElementById('chatInp');
  const question = inp.value.trim();
  if (!question) return;

  inp.value = '';
  addChatBubble(question, 'user');
  document.getElementById('typing').classList.add('show');
  scrollChat();

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question,
        skin_score: currentSkinScore,
        severity: currentSeverity,
        acne_count: currentAcneCount,
        acne_details: currentAcneDetails  // NEW: Send detailed data
      })
    });

    const data = await res.json();
    document.getElementById('typing').classList.remove('show');
    addChatBubble(data.reply || 'Sorry, no response.', 'ai');

  } catch (err) {
    document.getElementById('typing').classList.remove('show');
    addChatBubble('AI advisor unavailable.', 'ai');
  }

  scrollChat();
}

function addChatBubble(text, who) {
  const msgs = document.getElementById('chatMsgs');
  const div = document.createElement('div');
  div.className = `msg ${who}`;
  div.innerHTML = `
    <div class="avatar">${who === 'ai' ? '🤖' : '👤'}</div>
    <div class="bubble">${escapeHtml(text)}</div>`;
  msgs.appendChild(div);
  scrollChat();
}

function scrollChat() {
  const msgs = document.getElementById('chatMsgs');
  msgs.scrollTop = msgs.scrollHeight;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// ════ PDF DOWNLOAD ════
async function downloadPDF() {
  toast('Generating PDF report...');
  
  try {
    const recos = Array.from(document.querySelectorAll('.reco-card span:last-child'))
      .map(el => el.textContent);

    const res = await fetch('/report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        skin_score: currentSkinScore,
        acne_count: currentAcneCount,
        severity: currentSeverity,
        acne_details: currentAcneDetails,  // NEW
        recommendations: recos,
        original_url: document.getElementById('origImg').src,
        result_url: document.getElementById('resImg').src
      })
    });

    if (res.ok) {
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'SkinAI_Report.pdf';
      a.click();
      URL.revokeObjectURL(url);
      toast('PDF downloaded! ✅');
    } else {
      toast('PDF generation failed');
    }
  } catch (err) {
    toast('PDF error: ' + err.message);
  }
}

// ════ SHARE ════
function shareResult() {
  const text = `My skin score is ${currentSkinScore}/100 — Severity: ${currentSeverity}. Analyzed by SkinAI!`;
  if (navigator.share) {
    navigator.share({ title: 'My SkinAI Result', text });
  } else {
    navigator.clipboard.writeText(text);
    toast('Result copied to clipboard! 📋');
  }
}

// ════ HISTORY ════
function saveHistory(data) {
  const history = JSON.parse(localStorage.getItem('skinH') || '[]');
  history.unshift({
    date: new Date().toLocaleDateString(),
    score: data.skin_score,
    severity: data.severity,
    acne_count: data.acne_count,
    result_url: data.result_url
  });
  localStorage.setItem('skinH', JSON.stringify(history.slice(0, 12)));
  loadHistory();
}

function loadHistory() {
  const history = JSON.parse(localStorage.getItem('skinH') || '[]');
  const el = document.getElementById('histContent');

  if (!history.length) {
    el.className = 'hist-empty';
    el.innerHTML = 'No previous scans yet. Analyze your first photo to start tracking! 🌟';
    return;
  }

  el.className = 'hist-grid';
  el.innerHTML = history.map(item => {
    const color = item.score >= 70 ? '#22c55e' : item.score >= 40 ? '#eab308' : '#ef4444';
    return `
      <div class="hist-card">
        <img src="${item.result_url || ''}" alt="Scan" onerror="this.style.display='none'">
        <div class="hist-info">
          <div class="hist-score" style="color:${color}">${item.score}/100</div>
          <div class="hist-date">${item.severity} · ${item.date}</div>
        </div>
      </div>`;
  }).join('');
}

// ════ TOAST ════
function toast(msg) {
  document.querySelectorAll('.toast').forEach(el => el.remove());
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = msg;
  toast.style.cssText = `
    position:fixed;bottom:32px;left:50%;transform:translateX(-50%);
    background:rgba(22,22,42,.97);color:#f0f0f5;
    padding:13px 28px;border-radius:100px;font-size:14px;font-weight:500;
    border:1px solid rgba(124,92,191,.3);backdrop-filter:blur(16px);
    z-index:9999;animation:up .3s ease;box-shadow:0 12px 40px rgba(0,0,0,.5)`;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3200);
}