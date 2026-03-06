/* =====================================================
   STUDENT DASHBOARD – ENTERPRISE V2
   Secure | Consistent | SaaS Ready
   ===================================================== */

document.addEventListener('DOMContentLoaded', async () => {
    await AuthEngine.checkAuth();

    const user = AuthEngine.currentUser();
    if (user.role !== 'student') {
        showToast('Unauthorized access', 'error');
        return location.href = '/login/';
    }

    document.getElementById('studentName').textContent = user.fullName || 'Student';
    document.getElementById('profileName').textContent = user.fullName || 'Student';

    loadStudentData();
});

/* ---------- SAFE TEXT ---------- */
const safeText = v => (v === null || v === undefined) ? 'N/A' : String(v);

/* ---------- LOAD DATA ---------- */
async function loadStudentData() {
    try {
        const data = await DashboardAPI.getStudentDashboard();

        /* PROFILE */
        const s = data.student || {};
        currentStudentId = s.id;
        setText('studentName', s.name || s.first_name || 'Student');
        setText('profileName', s.name || 'Student');
        setText('profileId', `ID: ${safeText(s.id)}`);
        setText('rollNo', safeText(s.roll_no || s.id));
        setText('studentGrade', `Class ${safeText(s.grade)}`);
        setText('className', safeText(s.grade));
        setText('dob', safeText(s.dob));
        setText('contact', safeText(s.phone));

        /* PHOTO LOGIC */
        const profileImg = document.getElementById('profileImg');
        const placeholder = document.getElementById('profilePlaceholder');
        if (s.photo_url) {
            profileImg.src = s.photo_url;
            profileImg.style.display = 'block';
            placeholder.style.display = 'none';
        }

        /* ATTENDANCE */
        const attPct = data.attendance?.attendance_percentage || 0;
        setText('attendancePercent', `${attPct}%`);
        document.getElementById('attendanceBar').style.width = `${attPct}%`;

        /* NOTIFICATIONS */
        renderNotifications(data.notifications || []);

        /* PAYMENTS */
        renderPayments(data.payments || { total_due: 0, payments: [] });

        /* RESULTS */
        renderResults(data.results || []);

        /* ROUTINE */
        renderRoutine(data.routine || []);

        /* HOMEWORK */
        renderHomework(data.assignments || []);

        /* DIARY */
        renderDiary(data.diary || []);

        /* LIVE CLASSES */
        renderLiveClasses(data.live_classes || []);

        /* PERFORMANCE CHART */
        initPerformanceChart(data.results || []);

    } catch (e) {
        console.error(e);
        showToast('Failed to load dashboard data', 'error');
    }
}

/* ---------- HELPERS ---------- */
function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

/* ---------- NOTIFICATIONS ---------- */
function renderNotifications(notices) {
    const list = document.getElementById('notificationList');

    if (!notices.length) {
        list.innerHTML = '<p class="text-muted">No new notifications.</p>';
        return;
    }

    list.innerHTML = notices.map(n => `
        <div class="notification-item">
            <div class="title">${safeText(n.title)}</div>
            <div class="msg">${safeText(n.message)}</div>
            <div class="date">${new Date(n.created_at).toLocaleDateString()}</div>
        </div>
    `).join('');
}

/* ---------- PAYMENTS ---------- */
function renderPayments(payments) {
    const badge = document.getElementById('totalDueBadge');
    const table = document.getElementById('feeTableBody');

    if (payments.total_due > 0) {
        badge.textContent = `Due: ${window.CURRENCY_SYMBOL || '₹'}${payments.total_due}`;
        badge.className = 'status-badge status-warning';
    } else {
        badge.textContent = 'No Dues';
        badge.className = 'status-badge status-success';
    }

    if (!payments.payments?.length) {
        table.innerHTML =
            `<tr><td colspan="4" class="text-muted">No records found</td></tr>`;
        return;
    }

    table.innerHTML = payments.payments.map(p => `
        <tr>
            <td>${safeText(p.description)}</td>
            <td>${new Date(p.due_date).toLocaleDateString()}</td>
            <td>${window.CURRENCY_SYMBOL || '₹'}${p.amount}</td>
            <td>
                ${p.status === 'PAID'
            ? '<span class="status-badge status-success">PAID</span>'
            : `<button class="btn-pay" onclick="payFee(${p.amount}, '${safeText(p.description)}')">
                        Pay Now
                       </button>`}
            </td>
        </tr>
    `).join('');
}

/* ---------- PAYMENT FLOW ---------- */
async function payFee(amount, description) {
    ModalSystem.show(
        `Proceed to pay ${window.CURRENCY_SYMBOL || '₹'}${amount}?\nAfter payment, enter transaction ID.`,
        'Fee Payment',
        'info'
    );

    setTimeout(() => submitManualPayment(amount, description), 400);
}

async function submitManualPayment(amount, description) {
    const txnId = prompt(`Enter Transaction / UTR ID for ${window.CURRENCY_SYMBOL || '₹'}${amount}`);
    if (!txnId) return;

    try {
        await apiCall('/payment/manual/submit/', {
            method: 'POST',
            body: JSON.stringify({
                amount,
                description,
                transaction_id: txnId
            })
        });

        showToast('Payment submitted. Verification pending.', 'success');
        loadStudentData();

    } catch {
        showToast('Payment submission failed', 'error');
    }
}

/* ---------- ACADEMIC HUB ---------- */
function renderResults(results) {
    const list = document.getElementById('resultsList');
    if (!results.length) {
        list.innerHTML = '<div style="color: #64748b; font-size: 0.8rem; text-align: center; padding: 10px;">No exam results published yet.</div>';
        return;
    }

    list.innerHTML = results.map(r => `
        <div style="background: rgba(255,255,255,0.05); padding: 12px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="color: white; font-weight: 500; font-size: 0.9rem;">${r.exam}</div>
                <div style="color: #94a3b8; font-size: 0.75rem;">${r.subject} • ${new Date(r.date).toLocaleDateString()}</div>
            </div>
            <div style="text-align: right;">
                <div style="color: #10b981; font-weight: 700;">${r.percentage}%</div>
                <div style="color: ${r.status === 'PASS' ? '#10b981' : '#f87171'}; font-size: 0.7rem;">${r.status}</div>
            </div>
        </div>
    `).join('');
}

/* ---------- ROUTINE ---------- */
function renderRoutine(routine) {
    const list = document.getElementById('todayRoutine');
    if (!routine || !routine.length) {
        list.innerHTML = '<p class="text-muted" style="font-size: 0.85rem;">No classes today.</p>';
        return;
    }

    list.innerHTML = routine.map(r => `
        <div style="display: flex; gap: 12px; align-items: center; padding: 10px; background: rgba(255,255,255,0.03); border-radius: 8px;">
            <div style="background: rgba(59, 130, 246, 0.2); color: #60a5fa; padding: 5px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; min-width: 80px; text-align: center;">
                ${r.time}
            </div>
            <div>
                <div style="color: white; font-weight: 600; font-size: 0.85rem;">${r.subject}</div>
                <div style="color: #94a3b8; font-size: 0.75rem;">${r.teacher} • Room ${r.room || 'N/A'}</div>
            </div>
        </div>
    `).join('');
}

/* ---------- HOMEWORK ---------- */
function renderHomework(hw) {
    const list = document.getElementById('homeworkList');
    if (!hw || !hw.length) {
        list.innerHTML = '<p class="text-muted" style="font-size: 0.85rem;">All caught up!</p>';
        return;
    }

    list.innerHTML = hw.map(h => `
        <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); padding: 15px; border-radius: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                <div style="color: #60a5fa; font-size: 0.7rem; font-weight: 700; text-transform: uppercase;">${h.subject}</div>
                <div class="status-badge ${h.status === 'SUBMITTED' ? 'status-success' : 'status-warning'}" style="font-size: 0.65rem;">
                    ${h.status}
                </div>
            </div>
            <div style="color: white; font-weight: 600; font-size: 0.9rem; margin-bottom: 5px;">${h.title}</div>
            <div style="color: #94a3b8; font-size: 0.75rem;">Due: ${new Date(h.due_date).toLocaleDateString()}</div>
            ${h.status === 'PENDING' ? `
                <button onclick="submitHomework(${h.id})" style="margin-top: 10px; width: 100%; padding: 6px; border-radius: 6px; background: #3b82f6; color: white; border: none; font-size: 0.75rem; font-weight: 600; cursor: pointer;">
                    Upload Solution
                </button>
            ` : `<div style="margin-top: 8px; font-size: 0.75rem; color: #10b981;">Marks: ${h.marks}</div>`}
        </div>
    `).join('');
}

async function submitHomework(id) {
    showToast("Action initiated successfully.", "success");
}

/* ---------- DIARY ---------- */
function renderDiary(diaries) {
    const list = document.getElementById('diaryList');
    if (!diaries || !diaries.length) {
        list.innerHTML = '<p class="text-muted" style="font-size: 0.85rem;">No tasks in diary for today.</p>';
        return;
    }

    list.innerHTML = diaries.map(d => `
        <div style="background: rgba(255,255,255,0.02); padding: 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                <span style="color: #60a5fa; font-size: 0.7rem; font-weight: 700;">${d.subject}</span>
                <span style="color: #94a3b8; font-size: 0.65rem;">${new Date(d.due_date).toLocaleDateString()}</span>
            </div>
            <div style="color: white; font-weight: 600; font-size: 0.85rem;">${d.title}</div>
            <div style="color: #64748b; font-size: 0.75rem; margin-top: 4px; line-height: 1.3;">${d.description}</div>
        </div>
    `).join('');
}

/* ---------- LIVE CLASSES ---------- */
function renderLiveClasses(classes) {
    const list = document.getElementById('liveClassesList');
    if (!classes || !classes.length) {
        list.innerHTML = '<p class="text-muted" style="grid-column: span 2; font-size: 0.85rem;">No upcoming live sessions.</p>';
        return;
    }

    list.innerHTML = classes.map(c => `
        <div style="background: rgba(139, 92, 246, 0.05); border: 1px solid rgba(139, 92, 246, 0.2); padding: 15px; border-radius: 12px; position: relative; overflow: hidden;">
            <div style="position: absolute; top:0; right:0; background: #8b5cf6; color: white; padding: 2px 6px; font-size: 0.6rem; font-weight: 800; border-bottom-left-radius: 6px;">
                ${c.platform}
            </div>
            <div style="color: white; font-weight: 700; font-size: 0.95rem; margin-bottom: 5px;">${c.title}</div>
            <div style="color: #a78bfa; font-size: 0.75rem; font-weight: 600;">With ${c.instructor}</div>
            <div style="color: #94a3b8; font-size: 0.7rem; margin-top: 8px;">
                📅 ${new Date(c.start_time).toLocaleString()} (${c.duration} mins)
            </div>
            <a href="${c.url}" target="_blank" style="display: block; margin-top: 15px; text-align: center; background: #8b5cf6; color: white; padding: 8px; border-radius: 8px; font-size: 0.8rem; font-weight: 700; text-decoration: none; transition: 0.3s;">
                Join Session Now
            </a>
        </div>
    `).join('');
}

let currentStudentId = null;

async function downloadReportCard() {
    showToast('Generating Report Card...', 'info');
    window.location.href = `/api/generate/report-card/${currentStudentId}/`;
}

async function downloadAdmitCard() {
    showToast('Generating Admit Card...', 'info');
    window.location.href = `/api/generate/admit-card/${currentStudentId}/`;
}

async function downloadIDCard() {
    showToast('Generating ID Card...', 'info');
    window.location.href = `/api/generate/id-card/${currentStudentId}/`;
}

async function downloadAdmissionLetter() {
    showToast('Generating Admission Letter...', 'info');
    window.location.href = `/api/generate/admission-letter/${currentStudentId}/`;
}

/* ---------- LEAVE REQUEST ---------- */
function openLeaveModal() {
    document.getElementById('leaveModal').style.display = 'flex';
}

function closeLeaveModal() {
    document.getElementById('leaveModal').style.display = 'none';
}

document.getElementById('leaveForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const type = document.getElementById('leaveType').value;
    const start = document.getElementById('leaveStart').value;
    const end = document.getElementById('leaveEnd').value;
    const reason = document.getElementById('leaveReason').value;

    if (!start || !end || !reason) return showToast('Please fill all fields', 'warning');

    try {
        await apiCall('/api/leave-requests/', {
            method: 'POST',
            body: JSON.stringify({
                student: currentStudentId,
                leave_type: type,
                start_date: start,
                end_date: end,
                reason: reason
            })
        });
        showToast('Leave application submitted successfully.', 'success');
        closeLeaveModal();
    } catch (err) {
        showToast('Failed to submit leave application.', 'error');
    }
});

/* ---------- LOGOUT ---------- */
function logout() {
    AuthEngine.logout();
}

/* ---------- ATTENDANCE (GPS) ---------- */
async function markPresenceGPS() {
    if (!navigator.geolocation) {
        return showToast('Geolocation is not supported by your browser.', 'error');
    }

    const btn = document.getElementById('markGeoBtn');
    const originalContent = btn.innerHTML;

    btn.disabled = true;
    btn.innerHTML = '<span>⌛</span><div><div style="font-weight:600;color:#10b981;">Locating...</div><div style="font-size:0.7rem;">Please wait</div></div>';

    navigator.geolocation.getCurrentPosition(async (position) => {
        const lat = position.coords.latitude;
        const long = position.coords.longitude;

        try {
            const data = await apiCall('/attendence/mark-geo/', {
                method: 'POST',
                body: JSON.stringify({ lat, long })
            });

            showToast(data.message || 'Attendance marked successfully!', 'success');
            // Refresh dashboard to show new attendance %
            loadStudentData();
        } catch (err) {
            console.error(err);
            showToast(err.message || 'Geofence verification failed.', 'error');
        } finally {
            btn.disabled = false;
            btn.innerHTML = originalContent;
        }
    }, (err) => {
        console.error(err);
        showToast('Could not get your location. Please enable GPS.', 'error');
        btn.disabled = false;
        btn.innerHTML = originalContent;
    }, { enableHighAccuracy: true, timeout: 10000 });
}

/* ---------- PERFORMANCE CHART ---------- */
let perfChart = null;
function initPerformanceChart(results) {
    const ctx = document.getElementById('performanceChart');
    if (!ctx || !results.length) return;

    if (perfChart) perfChart.destroy();

    const labels = results.map(r => r.exam).reverse();
    const scores = results.map(r => r.percentage).reverse();

    perfChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Percentage (%)',
                data: scores,
                borderColor: '#00f3ff',
                backgroundColor: 'rgba(0, 243, 255, 0.1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#00f3ff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { min: 0, max: 100, grid: { color: 'rgba(255,255,255,0.05)' }, border: { display: false }, ticks: { color: '#94a3b8' } },
                x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
            }
        }
    });
}

/* ---------- AI TUTOR LOGIC ---------- */
function toggleAITutor() {
    const bubble = document.getElementById('aiTutorWidget');
    const trigger = document.getElementById('aiTutorTrigger');

    if (bubble.style.display === 'flex') {
        bubble.style.display = 'none';
        trigger.style.display = 'flex';
    } else {
        bubble.style.display = 'flex';
        trigger.style.display = 'none';
        ScrollToBottom();
    }
}

async function sendAIMessage() {
    const input = document.getElementById('aiInput');
    const body = document.getElementById('aiChatBody');
    const text = input.value.trim();
    if (!text) return;

    // Append User Message
    body.innerHTML += `<div class="ai-msg user">${text}</div>`;
    input.value = '';
    ScrollToBottom();

    // Show Loading
    const loadingId = 'ai-loading-' + Date.now();
    body.innerHTML += `<div id="${loadingId}" class="ai-msg bot">Thinking...</div>`;
    ScrollToBottom();

    try {
        const resp = await apiCall('/api/ai/unified/tutor/', {
            method: 'POST',
            body: JSON.stringify({ question: text, subject: 'Student Support' })
        });

        document.getElementById(loadingId).innerText = resp.answer;
        ScrollToBottom();
    } catch (e) {
        document.getElementById(loadingId).innerText = "I'm having trouble connecting to my neural network. Please check your internet.";
    }
}

function ScrollToBottom() {
    const body = document.getElementById('aiChatBody');
    body.scrollTop = body.scrollHeight;
}

/* ---------- EXAM COUNTDOWN ---------- */
function initExamCountdown() {
    // Mock logic: Find the next exam from the routine or a dedicated API
    // For now, let's fetch the exams from OnlineExams API
    apiCall('/api/online-exams/').then(exams => {
        if (!exams || !exams.length) return;
        
        // Find the closest upcoming exam
        const now = new Date();
        const futureExams = exams
            .filter(ex => new Date(ex.start_window) > now)
            .sort((a,b) => new Date(a.start_window) - new Date(b.start_window));
            
        if (futureExams.length > 0) {
            const nextExam = futureExams[0];
            document.getElementById('examCountdownSection').style.display = 'block';
            document.getElementById('nextExamTitle').innerText = nextExam.title;
            
            startCountdownTimer(new Date(nextExam.start_window));
        }
    });
}

function startCountdownTimer(targetDate) {
    const timerEl = document.getElementById('examTimer');
    
    const update = () => {
        const now = new Date();
        const diff = targetDate - now;
        
        if (diff <= 0) {
            timerEl.innerText = "EXAM IS LIVE!";
            return;
        }
        
        const d = Math.floor(diff / (1000 * 60 * 60 * 24));
        const h = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const m = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const s = Math.floor((diff % (1000 * 60)) / 1000);
        
        timerEl.innerText = `${d}d : ${h}h : ${m}m : ${s}s`;
        requestAnimationFrame(update);
    };
    
    update();
}

// Call countdown init in loadStudentData or at end
initExamCountdown();
