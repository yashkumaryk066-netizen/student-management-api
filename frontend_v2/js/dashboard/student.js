// Student Dashboard JS

document.addEventListener('DOMContentLoaded', async () => {
    checkAuth();

    // Set UI 
    const user = getCurrentUser();
    document.getElementById('userName').textContent = user.fullName || 'Student';

    await loadStudentData();
});

function showSection(id) {
    document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
    document.getElementById(`${id}-section`).classList.add('active');

    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    event.currentTarget.classList.add('active');
}

async function loadStudentData() {
    try {
        const data = await DashboardAPI.getStudentDashboard();

        // Update Attendance
        const attPct = data.attendance.attendance_percentage || 0;
        document.getElementById('attendanceVal').textContent = `${attPct}%`;
        document.getElementById('attendanceCircle').style.background = `conic-gradient(var(--primary) 0%, var(--primary) ${attPct}%, #eee ${attPct}%, #eee 100%)`;
        document.getElementById('daysPresent').textContent = data.attendance.present_days;

        // Update Fees
        document.getElementById('feeDue').textContent = `₹${data.payments.total_due}`;

        // Notifications
        if (data.notifications && data.notifications.length > 0) {
            document.getElementById('latestNotice').textContent = data.notifications[0].message;
        }

        // Pending Payments Render
        const paymentsList = document.getElementById('pendingPaymentsList');
        if (data.payments.payments && data.payments.payments.length > 0) {
            paymentsList.innerHTML = data.payments.payments.map(p => `
                <div class="payment-card" style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 15px; border-left: 5px solid ${p.status === 'OVERDUE' ? 'red' : 'orange'}; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h3>${p.description}</h3>
                            <div class="text-muted">Due: ${new Date(p.due_date).toLocaleDateString()}</div>
                        </div>
                        <div class="text-right">
                            <h3 style="color: var(--primary);">₹${p.amount}</h3>
                            <button class="btn btn-primary" onclick="alert('Payment Gateway Integration Pending')">Pay Now</button>
                        </div>
                    </div>
                </div>
            `).join('');
        } else {
            paymentsList.innerHTML = '<div class="alert alert-success">No pending dues! 🎉</div>';
        }

        // Profile Data
        if (data.student) {
            document.getElementById('profileName').textContent = data.student.name || data.student.first_name;
            document.getElementById('profileEmail').textContent = data.student.email || 'N/A';
            document.getElementById('profileDob').textContent = data.student.dob || 'N/A';
        }

    } catch (e) {
        console.error('Failed to load student dashboard', e);
    }
}
