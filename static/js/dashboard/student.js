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
        setText('studentName', s.name || s.first_name || 'Student');
        setText('profileName', s.name || 'Student');
        setText('profileId', `ID: ${safeText(s.id)}`);
        setText('rollNo', safeText(s.roll_no || s.id));
        setText('studentGrade', `Class ${safeText(s.grade)}`);
        setText('className', safeText(s.grade));
        setText('dob', safeText(s.dob));
        setText('contact', safeText(s.phone));

        /* ATTENDANCE */
        const attPct = data.attendance?.attendance_percentage || 0;
        setText('attendancePercent', `${attPct}%`);
        document.getElementById('attendanceBar').style.width = `${attPct}%`;

        /* NOTIFICATIONS */
        renderNotifications(data.notifications || []);

        /* PAYMENTS */
        renderPayments(data.payments || { total_due: 0, payments: [] });

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
        badge.textContent = `Due: ₹${payments.total_due}`;
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
            <td>₹${p.amount}</td>
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
        `Proceed to pay ₹${amount}?\nAfter payment, enter transaction ID.`,
        'Fee Payment',
        'info'
    );

    setTimeout(() => submitManualPayment(amount, description), 400);
}

async function submitManualPayment(amount, description) {
    const txnId = prompt(`Enter Transaction / UTR ID for ₹${amount}`);
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

/* ---------- LOGOUT ---------- */
function logout() {
    AuthEngine.logout();
}
