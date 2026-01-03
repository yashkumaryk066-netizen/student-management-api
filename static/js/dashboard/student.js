// Student Dashboard JS
document.addEventListener('DOMContentLoaded', async () => {
    checkAuth();

    // Initial basic user info from local storage
    const user = getCurrentUser();
    document.getElementById('studentName').textContent = user.fullName || 'Student';
    document.getElementById('profileName').textContent = user.fullName || 'Student';

    await loadStudentData();
});

async function loadStudentData() {
    try {
        const data = await DashboardAPI.getStudentDashboard();

        // 1. Profile Info
        const student = data.student || {};
        document.getElementById('studentName').textContent = student.name || student.first_name || 'Student';
        document.getElementById('profileName').textContent = student.name || 'Student';
        document.getElementById('profileId').textContent = `ID: ${student.id || 'N/A'}`;
        document.getElementById('rollNo').textContent = student.id || 'N/A'; // Using ID as roll if not present
        document.getElementById('studentGrade').textContent = `Class ${student.grade || 'N/A'}`;
        document.getElementById('className').textContent = student.grade || 'N/A';
        document.getElementById('dob').textContent = student.dob || 'N/A';
        document.getElementById('contact').textContent = student.phone || 'N/A';

        // 2. Attendance
        const att = data.attendance || {};
        const attPct = att.attendance_percentage || 0;
        document.getElementById('attendancePercent').textContent = `${attPct}%`;
        document.getElementById('attendanceBar').style.width = `${attPct}%`;

        // 3. Notifications
        const notices = data.notifications || [];
        const noticeList = document.getElementById('notificationList');
        if (notices.length > 0) {
            noticeList.innerHTML = notices.map(n => `
                <div style="padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <div style="color: white; font-weight: 500;">${n.title}</div>
                    <div style="color: #94a3b8; font-size: 0.9rem;">${n.message}</div>
                    <div style="color: #64748b; font-size: 0.75rem; margin-top: 4px;">${new Date(n.created_at).toLocaleDateString()}</div>
                </div>
            `).join('');
        } else {
            noticeList.innerHTML = '<p class="text-muted">No new notifications.</p>';
        }

        // 4. Fee Status
        const payments = data.payments || { total_due: 0, payments: [] };
        const dueBadge = document.getElementById('totalDueBadge');
        if (payments.total_due > 0) {
            dueBadge.textContent = `Due: ₹${payments.total_due}`;
            dueBadge.className = 'status-badge status-warning'; // create CSS class if needed or use inline
            dueBadge.style.background = '#f59e0b';
            dueBadge.style.color = 'black';
        } else {
            dueBadge.textContent = 'No Dues';
            dueBadge.style.background = '#10b981';
            dueBadge.style.color = 'white';
        }

        const feeTable = document.getElementById('feeTableBody');
        if (payments.payments && payments.payments.length > 0) {
            feeTable.innerHTML = payments.payments.map(p => `
                <tr>
                    <td>${p.description}</td>
                    <td>${new Date(p.due_date).toLocaleDateString()}</td>
                    <td>₹${p.amount}</td>
                    <td>
                        ${p.status === 'PAID'
                    ? '<span class="status-badge status-success">PAID</span>'
                    : `<button onclick="payFee('${p.amount}', '${p.description}')" style="background:#3b82f6; border:none; color:white; padding:5px 10px; border-radius:4px; cursor:pointer;">Pay Now</button>`}
                    </td>
                </tr>
            `).join('');
        } else {
            feeTable.innerHTML = '<tr><td colspan="4" style="text-align: center; color: #94a3b8;">No records found</td></tr>';
        }

    } catch (e) {
        console.error('Failed to load student dashboard', e);
        // Show silent error in console, keep UI as partial load
    }
}


async function submitManualPayment(amount, description) {
    const txnId = prompt(`Please enter the Bank UTR / Transaction No. you received after paying ₹${amount}:`);
    if (!txnId) return;

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('/api/payment/manual/submit/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                amount: amount,
                description: description,
                transaction_id: txnId
            })
        });

        const data = await response.json();

        if (response.ok) {
            alert('Payment Submitted Successfully! Verification Pending.');
            window.location.reload();
        } else {
            alert('Submission Error: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Payment Error:', error);
        alert('Failed to submit payment.');
    }
}
async function payFee(amount, description) {
    // Show Modal or Options
    // Since user has no merchant gateway, we default to the Manual Flow or show options.
    // For simplicity, let's guide them to the Manual Flow directly as Eazypay is not active without keys.
    const choice = confirm(`Proceed to pay ₹${amount}?\n\nClick OK to Enter Transaction ID (If you have already paid via QR/Bank)\nClick Cancel to go back.`);

    if (choice) {
        submitManualPayment(amount, description);
    }
}

function logout() {
    localStorage.clear();
    window.location.href = '/login/';
}
