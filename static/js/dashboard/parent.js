// Parent Dashboard

document.addEventListener('DOMContentLoaded', async () => {
    checkAuth();
    const user = getCurrentUser();
    document.getElementById('userName').textContent = user.fullName || 'Parent';

    await loadParentData();
});

function showSection(id) {
    document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
    document.getElementById(`${id}-section`)?.classList.add('active'); // Basic routing for now

    // For Parent dashboard simplification, we might just put everything in overview or route simple sections
    if (id === 'dashboard') {
        document.getElementById('dashboard-section').classList.add('active');
    }
}

async function loadParentData() {
    try {
        const data = await DashboardAPI.getParentDashboard();

        // Render Children Overview
        const container = document.getElementById('childrenOverviewContainer');
        if (data.children && data.children.length > 0) {
            container.innerHTML = `<div class="stats-grid" style="grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));">
                ${data.children.map(child => `
                    <div class="stat-card" style="display: block;">
                         <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px; border-bottom:1px solid #eee; padding-bottom:10px;">
                             <h3 style="margin:0;">${child.student.name || child.student.first_name}</h3>
                             <span class="badge badge-success">Class ${child.student.grade || 'N/A'}</span>
                         </div>
                         
                         <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px;">
                             <div>
                                 <label class="text-muted" style="font-size:0.8em;">ATTENDANCE</label>
                                 <div style="font-size:1.5em; font-weight:bold; color: var(--primary);">
                                    ${child.attendance.percentage}%
                                 </div>
                             </div>
                             <div>
                                 <label class="text-muted" style="font-size:0.8em;">FEES DUE</label>
                                 <div style="font-size:1.5em; font-weight:bold; color: ${child.payments.due_amount > 0 ? 'red' : 'green'};">
                                    ₹${child.payments.due_amount}
                                 </div>
                             </div>
                         </div>
                         
                         <div style="margin-top: 15px; text-align: center;">
                             <button class="btn btn-secondary btn-sm" style="width:100%;">View Full Report</button>
                         </div>
                    </div>
                `).join('')}
            </div>`;
        } else {
            container.innerHTML = '<div class="alert alert-warning">No children linked to your account. Please contact admin.</div>';
        }

        // Notices
        if (data.notifications) {
            document.getElementById('noticesList').innerHTML = data.notifications.map(n => `
                <div style="padding: 10px; border-bottom: 1px dashed #ccc;">
                    <strong>${n.title || 'Notice'}</strong>
                    <p>${n.message}</p>
                    <small class="text-muted">${new Date(n.created_at).toDateString()}</small>
                </div>
            `).join('');
        }

    } catch (e) {
        console.error(e);
        document.getElementById('childrenOverviewContainer').innerHTML = '<div class="alert alert-danger">Failed to load data. Please try again.</div>';
    }
}
