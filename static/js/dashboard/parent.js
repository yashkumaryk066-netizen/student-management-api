const safeText = v => (v === null || v === undefined) ? 'N/A' : String(v);

document.addEventListener('DOMContentLoaded', async () => {
    await AuthEngine.checkAuth();
    const user = AuthEngine.currentUser();
    if (user.role !== 'parent') {
        return location.href = '/login/';
    }

    await loadParentData();
});

async function loadParentData() {
    try {
        const data = await DashboardAPI.getParentDashboard();

        // 1. Parent Name
        setText('parentName', data.parent_name || 'Parent');

        // 2. Children Cards
        renderChildren(data.children || []);

        // 3. Notifications
        renderNotifications(data.notifications || []);

    } catch (e) {
        console.error(e);
        showToast('Failed to load parent dashboard', 'error');
    }
}

function renderChildren(children) {
    const container = document.getElementById('childrenContainer');
    if (!children || !children.length) {
        container.innerHTML = '<div class="kpi-card" style="text-align: center; color: #94a3b8;">No children linked to this account.</div>';
        return;
    }

    container.innerHTML = children.map(c => `
        <div class="kpi-card" style="margin-bottom: 20px; border-left: 4px solid #3b82f6; background: #1e293b;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div style="display: flex; gap: 15px; align-items: center;">
                    <div style="width: 60px; height: 60px; background: #3b82f6; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; overflow: hidden; border: 2px solid rgba(255,255,255,0.1);">
                        ${c.photo ? `<img src="${c.photo}" style="width: 100%; height: 100%; object-fit: cover;">` : '🎓'}
                    </div>
                    <div>
                        <h3 style="color: white; margin: 0; font-size: 1.2rem; font-weight: 700;">${c.name}</h3>
                        <p style="color: #94a3b8; font-size: 0.85rem; margin: 2px 0;">Class ${c.grade} • ID: ${c.id}</p>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="color: #10b981; font-weight: 800; font-size: 1.4rem;">${c.attendance}%</div>
                    <div style="color: #64748b; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">Attendance</div>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-top: 25px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.05);">
                <div style="background: rgba(255,255,255,0.02); padding: 12px; border-radius: 8px;">
                    <label style="color: #64748b; font-size: 0.65rem; text-transform: uppercase; font-weight: 700; display: block; margin-bottom: 5px;">Latest Result</label>
                    <div style="color: #60a5fa; font-size: 0.9rem; font-weight: 600;">${c.latest_result}</div>
                </div>
                <div style="background: rgba(255,255,255,0.02); padding: 12px; border-radius: 8px;">
                    <label style="color: #64748b; font-size: 0.65rem; text-transform: uppercase; font-weight: 700; display: block; margin-bottom: 5px;">Homework</label>
                    <div style="color: #f59e0b; font-size: 0.9rem; font-weight: 600;">${c.pending_homework} Pending</div>
                </div>
                <div style="background: rgba(255,255,255,0.02); padding: 12px; border-radius: 8px;">
                    <label style="color: #64748b; font-size: 0.65rem; text-transform: uppercase; font-weight: 700; display: block; margin-bottom: 5px;">Fee Status</label>
                    <div style="color: ${c.total_due > 0 ? '#f87171' : '#10b981'}; font-size: 0.9rem; font-weight: 600;">₹${c.total_due} Due</div>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 10px;">
                <div style="background: rgba(139, 92, 246, 0.05); padding: 10px; border-radius: 8px; border: 1px solid rgba(139, 92, 246, 0.1);">
                    <label style="color: #a78bfa; font-size: 0.65rem; text-transform: uppercase; font-weight: 700; display: block;">Live Classes</label>
                    <div style="color: white; font-size: 0.85rem; font-weight: 600;">${c.upcoming_live_classes} Upcoming</div>
                </div>
                <div style="background: rgba(59, 130, 246, 0.05); padding: 10px; border-radius: 8px; border: 1px solid rgba(59, 130, 246, 0.1);">
                    <label style="color: #60a5fa; font-size: 0.65rem; text-transform: uppercase; font-weight: 700; display: block;">Diary Tasks</label>
                    <div style="color: white; font-size: 0.85rem; font-weight: 600;">${c.active_diary_tasks} Active</div>
                </div>
            </div>

            <div style="display: flex; gap: 12px; margin-top: 20px;">
                <button onclick="applyLeave(${c.id}, '${c.name}')" style="flex: 1; background: rgba(59, 130, 246, 0.1); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.2); padding: 10px; border-radius: 8px; font-size: 0.85rem; font-weight: 600; cursor: pointer; transition: 0.3s; display: flex; align-items: center; justify-content: center; gap: 6px;">
                    <span>📝</span> Apply Leave
                </button>
                <button onclick="showFees(${c.id})" style="flex: 1; background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.2); padding: 10px; border-radius: 8px; font-size: 0.85rem; font-weight: 600; cursor: pointer; transition: 0.3s; display: flex; align-items: center; justify-content: center; gap: 6px;">
                    <span>💳</span> Pay Fees
                </button>
            </div>
        </div>
    `).join('');
}

function renderNotifications(notices) {
    const list = document.getElementById('notificationList');
    if (!notices || !notices.length) {
        list.innerHTML = '<p style="color: #64748b; font-size: 0.85rem;">No new family notifications.</p>';
        return;
    }

    list.innerHTML = notices.map(n => `
        <div style="background: rgba(255,255,255,0.03); padding: 15px; border-radius: 10px; border-left: 4px solid #6366f1; margin-bottom: 12px;">
            <div style="color: white; font-weight: 700; font-size: 0.95rem;">${n.title}</div>
            <div style="color: #94a3b8; font-size: 0.85rem; margin: 6px 0; line-height: 1.4;">${n.message}</div>
            <div style="color: #64748b; font-size: 0.75rem; font-weight: 500;">${new Date(n.date).toLocaleDateString()}</div>
        </div>
    `).join('');
}

function applyLeave(studentId, name) {
    document.getElementById('leaveStudentId').value = studentId;
    document.getElementById('leaveStudentName').textContent = `Requesting leave for ${name}`;
    document.getElementById('leaveModal').style.display = 'flex';
}

function closeLeaveModal() {
    document.getElementById('leaveModal').style.display = 'none';
}

document.getElementById('leaveForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const studentId = document.getElementById('leaveStudentId').value;
    const type = document.getElementById('leaveType').value;
    const start = document.getElementById('leaveStart').value;
    const end = document.getElementById('leaveEnd').value;
    const reason = document.getElementById('leaveReason').value;

    if (!start || !end || !reason) return showToast('Please fill all fields', 'warning');

    try {
        await apiCall('/api/leave-requests/', {
            method: 'POST',
            body: JSON.stringify({
                student: studentId,
                leave_type: type,
                start_date: start,
                end_date: end,
                reason: reason
            })
        });
        showToast(`Leave request submitted.`, 'success');
        closeLeaveModal();
    } catch (err) {
        showToast('Submission failed.', 'error');
    }
});

function showFees(studentId) {
    showToast('Redirecting to Payment Portal...', 'info');
}

function setText(id, val) {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
}

function logout() {
    AuthEngine.logout();
}
