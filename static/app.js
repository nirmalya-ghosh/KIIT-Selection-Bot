let currentSessionId = null;

// --- CRYPTO ENGINE ---
function str2ab(str) {
    const buf = new ArrayBuffer(str.length);
    const bufView = new Uint8Array(buf);
    for (let i = 0, strLen = str.length; i < strLen; i++) bufView[i] = str.charCodeAt(i);
    return buf;
}

function ab2b64(buf) {
    let binary = '';
    const bytes = new Uint8Array(buf);
    for (let i = 0; i < bytes.byteLength; i++) binary += String.fromCharCode(bytes[i]);
    return window.btoa(binary);
}

async function getPublicKey() {
    const res = await fetch('/api/public-key');
    const data = await res.json();
    const pemHeader = "-----BEGIN PUBLIC KEY-----";
    const pemFooter = "-----END PUBLIC KEY-----";
    const pemContents = data.public_key.substring(pemHeader.length, data.public_key.length - pemFooter.length).replace(/\s/g, '');
    const binaryDerString = window.atob(pemContents);
    const binaryDer = str2ab(binaryDerString);
    
    return await window.crypto.subtle.importKey(
        "spki", binaryDer,
        { name: "RSA-OAEP", hash: "SHA-256" },
        true, ["encrypt"]
    );
}

async function encryptData(publicKey, data) {
    const encoded = new TextEncoder().encode(data);
    const ciphertext = await window.crypto.subtle.encrypt({ name: "RSA-OAEP" }, publicKey, encoded);
    return ab2b64(ciphertext);
}

// --- LOGIN FLOW ---
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = document.getElementById('email').value;
    const passwordInput = document.getElementById('password');
    const password = passwordInput.value;
    
    // SECURITY OVERRIDE: Clear password from DOM instantly
    passwordInput.value = '';

    const btn = document.getElementById('login-btn');
    const btnText = btn.querySelector('.btn-text');
    const spinner = btn.querySelector('.spinner');

    // UI Loading State
    btn.disabled = true;
    btnText.textContent = 'Encrypting & Authenticating...';
    spinner.classList.remove('hidden');

    try {
        // Encrypt the password client-side
        const publicKey = await getPublicKey();
        const encryptedPassword = await encryptData(publicKey, password);

        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password: encryptedPassword })
        });

        const data = await response.json();

        if (response.ok) {
            currentSessionId = data.session_id;
            populateDashboard(data.data);
            transitionToDashboard();
        } else {
            alert(data.detail || 'Login failed. Please check credentials.');
        }
    } catch (error) {
        alert('Server connection failed.');
    } finally {
        btn.disabled = false;
        btnText.textContent = 'Connect to SAP';
        spinner.classList.add('hidden');
    }
});

// --- POPULATE DASHBOARD ---
function populateDashboard(data) {
    // Mentor
    document.getElementById('mentor-name').textContent = data.mentor_name || "N/A";
    document.getElementById('mentor-contact').textContent = data.mentor_contact || "N/A";
    document.getElementById('mentor-email').textContent = data.mentor_email || "N/A";

    // Attendance Table
    const tbody = document.getElementById('attendance-body');
    tbody.innerHTML = '';
    if (data.attendance && data.attendance.length > 0) {
        data.attendance.forEach(item => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${item.total_days || '0'}</td>
                <td>${item.absent || '0'}</td>
                <td>${item.present || '0'}</td>
                <td>${item.subject || 'N/A'}</td>
                <td><span style="color: ${parseInt(item.percentage) < 75 ? 'var(--error)' : 'var(--success)'}">${item.percentage || '0'}%</span></td>
            `;
            tbody.appendChild(tr);
        });
    }

    // Dropdowns
    const yearSelect = document.getElementById('year-select');
    yearSelect.innerHTML = '';
    (data.years || ["2026-2027"]).forEach(yr => {
        const opt = document.createElement('option');
        opt.value = yr; opt.textContent = yr;
        yearSelect.appendChild(opt);
    });

    const sessionSelect = document.getElementById('session-select');
    sessionSelect.innerHTML = '';
    (data.sessions || ["Autumn", "Spring", "Supplementary Exam"]).forEach(sec => {
        const opt = document.createElement('option');
        opt.value = sec; opt.textContent = sec;
        sessionSelect.appendChild(opt);
    });

    const subjectSelect = document.getElementById('subject-select');
    subjectSelect.innerHTML = '';
    (data.subjects || ["Loading..."]).forEach(sub => {
        const opt = document.createElement('option');
        opt.value = sub; opt.textContent = sub;
        subjectSelect.appendChild(opt);
    });

    const sectionSelect = document.getElementById('section-select');
    sectionSelect.innerHTML = '';
    (data.sections || ["Loading..."]).forEach(sec => {
        const opt = document.createElement('option');
        opt.value = sec; opt.textContent = sec;
        sectionSelect.appendChild(opt);
    });
}

// --- UI TRANSITION ---
function transitionToDashboard() {
    const loginCard = document.getElementById('login-card');
    const dashboardCard = document.getElementById('dashboard-card');
    
    loginCard.style.opacity = '0';
    loginCard.style.transform = 'translate(-50%, -60%) scale(0.95)';
    
    setTimeout(() => {
        loginCard.classList.add('hidden');
        dashboardCard.classList.remove('hidden');
        dashboardCard.style.opacity = '1';
        dashboardCard.style.transform = 'translate(-50%, -50%) scale(1)';
        dashboardCard.style.pointerEvents = 'all';
    }, 400);
}

// --- AGENTIC ACTIONS ---
document.getElementById('submit-selection-btn').addEventListener('click', async () => {
    const btn = document.getElementById('submit-selection-btn');
    const statusMsg = document.getElementById('selection-status');
    const subject = document.getElementById('subject-select').value;
    const section = document.getElementById('section-select').value;

    btn.disabled = true;
    btn.textContent = 'Processing...';
    
    try {
        const response = await fetch('/api/submit_selection', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: currentSessionId, subject, section })
        });
        
        statusMsg.classList.remove('hidden');
        if (response.ok) {
            statusMsg.textContent = 'Successfully locked selection in SAP!';
            statusMsg.style.color = 'var(--success)';
            btn.textContent = 'Locked';
        } else {
            statusMsg.textContent = 'Failed to submit selection.';
            statusMsg.style.color = 'var(--error)';
            btn.textContent = 'Try Again';
            btn.disabled = false;
        }
    } catch (e) {
        btn.disabled = false;
        btn.textContent = 'Lock Selection';
    }
});

document.getElementById('download-demand-btn').addEventListener('click', async () => {
    const btn = document.getElementById('download-demand-btn');
    const originalText = btn.innerHTML;
    btn.innerHTML = 'Downloading...';
    btn.disabled = true;
    
    try {
        const response = await fetch(`/api/download_demand_letter?session_id=${currentSessionId}`);
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'Demand_Letter.pdf';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
        } else {
            alert('Failed to download demand letter.');
        }
    } catch (e) {
        alert('Download error.');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
});

document.getElementById('logout-btn').addEventListener('click', async () => {
    if(currentSessionId) {
        fetch('/api/logout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: currentSessionId })
        });
    }
    location.reload();
});
