// Premium Edit Student Modal - Ultra-Level Design
// This file contains the premium modal implementation

// Define globally first to ensure availability
window.showEditStudentModalPremium = function (student) {
    if (typeof DashboardApp !== 'undefined') {
        // Use DashboardApp context if available
        DashboardApp.showEditStudentModalPremiumImpl(student);
    } else {
        // Fallback implementation if DashboardApp is somehow missing (should not happen with correct ordering)
        console.error("DashboardApp missing during modal call");
    }
};

// Also attach to DashboardApp if available (for consistency)
if (typeof DashboardApp !== 'undefined') {
    DashboardApp.showEditStudentModalPremium = window.showEditStudentModalPremium;
}

// The actual implementation (moved from previous assignment)
// We attach it to DashboardApp or window to keep it accessible
(function () {
    const showModal = function (student) {
        // Remove any existing modal first
        const existingModal = document.getElementById('editStudentModal');
        if (existingModal) existingModal.remove();

        // Premium data sanitization and pre-processing
        // Handle age calculation if it's a computed property
        let calculatedAge = student.age;
        if (!calculatedAge && student.dob) {
            const dob = new Date(student.dob);
            const today = new Date();
            calculatedAge = today.getFullYear() - dob.getFullYear();
            const monthDiff = today.getMonth() - dob.getMonth();
            if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dob.getDate())) {
                calculatedAge--;
            }
        }

        const sanitizedStudent = {
            id: student.id,
            name: student.name || '',
            age: calculatedAge || '',
            dob: student.dob || '',
            grade: student.grade !== null && student.grade !== undefined ? student.grade : 0,
            gender: student.gender || 'MALE',
            institution_type: student.institution_type || 'SCHOOL',
            relation: student.relation || '',
            photo: student.photo || null
        };

        // Pre-select logic with proper case handling
        const genderOptions = `
        <option value="MALE" ${sanitizedStudent.gender.toUpperCase() === 'MALE' ? 'selected' : ''}>Male</option>
        <option value="FEMALE" ${sanitizedStudent.gender.toUpperCase() === 'FEMALE' ? 'selected' : ''}>Female</option>
    `;

        const typeOptions = `
        <option value="SCHOOL" ${sanitizedStudent.institution_type === 'SCHOOL' ? 'selected' : ''}>School Student</option>
        <option value="COACHING" ${sanitizedStudent.institution_type === 'COACHING' ? 'selected' : ''}>Coaching Student</option>
        <option value="INSTITUTE" ${sanitizedStudent.institution_type === 'INSTITUTE' ? 'selected' : ''}>Institute/College Student</option>
    `;

        // Ultra-Premium Modal HTML
        const modalHtml = `
        <div class="premium-modal-overlay" id="editStudentModal" onclick="if(event.target === this) DashboardApp.closeEditModal()" style="
            position: fixed; 
            top: 0; 
            left: 0; 
            width: 100%; 
            height: 100%; 
            background: rgba(0, 0, 0, 0.92); 
            backdrop-filter: blur(12px); 
            z-index: 99999; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            animation: fadeIn 0.25s ease;
            padding: 20px;
        ">
            <div class="modal-card" onclick="event.stopPropagation()" style="
                background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); 
                border: 2px solid rgba(99, 102, 241, 0.5); 
                box-shadow: 0 30px 60px -12px rgba(0, 0, 0, 0.9), 0 0 100px rgba(99, 102, 241, 0.2); 
                max-width: 700px; 
                width: 100%; 
                max-height: 95vh; 
                overflow-y: auto; 
                border-radius: 24px; 
                animation: slideUp 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
            ">
                <!-- Header -->
                <div style="
                    padding: 32px 36px; 
                    border-bottom: 2px solid rgba(99, 102, 241, 0.25);
                    background: linear-gradient(135deg, rgba(99, 102, 241, 0.12), rgba(139, 92, 246, 0.08));
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h2 style="
                                margin: 0; 
                                color: white; 
                                font-size: 2rem; 
                                font-weight: 800;
                                display: flex; 
                                align-items: center; 
                                gap: 14px;
                                letter-spacing: -0.5px;
                            ">
                                <span style="font-size: 2.2rem;">✏️</span>
                                Edit Student Details
                            </h2>
                            <p style="
                                margin: 10px 0 0 50px; 
                                color: #94a3b8; 
                                font-size: 1rem;
                            ">Update student information below</p>
                        </div>
                        <button type="button" onclick="DashboardApp.closeEditModal()" style="
                            width: 44px;
                            height: 44px;
                            border-radius: 12px;
                            background: rgba(239, 68, 68, 0.12);
                            border: 2px solid rgba(239, 68, 68, 0.35);
                            color: #ef4444;
                            font-size: 1.8rem;
                            cursor: pointer;
                            transition: all 0.2s ease;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            line-height: 1;
                            font-weight: 300;
                        " onmouseover="this.style.background='rgba(239, 68, 68, 0.25)'; this.style.transform='rotate(90deg) scale(1.1)'" onmouseout="this.style.background='rgba(239, 68, 68, 0.12)'; this.style.transform='rotate(0) scale(1)'">×</button>
                    </div>
                </div>
                
                <!-- Form -->
                <form id="editStudentForm" onsubmit="event.preventDefault(); DashboardApp.handleEditStudentSubmit(event, ${sanitizedStudent.id});" style="padding: 36px;">
                    
                    <!-- Institution Type -->
                    <div class="form-group" style="margin-bottom: 26px;">
                        <label style="
                            display: block; 
                            color: #e2e8f0; 
                            font-weight: 700; 
                            margin-bottom: 12px; 
                            font-size: 1rem;
                            letter-spacing: 0.4px;
                        ">Institution Type</label>
                        <select name="institution_type" id="premiumEditInstitutionType" class="form-input premium-select" required onchange="DashboardApp.toggleStudentFields && DashboardApp.toggleStudentFields(this.value)" style="
                            width: 100%; 
                            padding: 16px 18px; 
                            background: rgba(15, 23, 42, 0.8); 
                            border: 2px solid rgba(99, 102, 241, 0.35); 
                            border-radius: 12px; 
                            color: white; 
                            font-size: 1.05rem;
                            transition: all 0.2s ease;
                            font-weight: 500;
                        ">
                            <!-- Dynamically populated based on plan -->
                        </select>
                        <small id="premiumPlanLockNote" style="color: #94a3b8; font-size: 0.85rem; margin-top: 8px; display: block;"></small>
                    </div>

                    <!-- Full Name -->
                    <div class="form-group" style="margin-bottom: 26px;">
                        <label style="
                            display: block; 
                            color: #e2e8f0; 
                            font-weight: 700; 
                            margin-bottom: 12px; 
                            font-size: 1rem;
                            letter-spacing: 0.4px;
                        ">Full Name *</label>
                        <input type="text" name="name" class="form-input premium-input" required value="${sanitizedStudent.name}" style="
                            width: 100%; 
                            padding: 16px 18px; 
                            background: rgba(15, 23, 42, 0.8); 
                            border: 2px solid rgba(99, 102, 241, 0.35); 
                            border-radius: 12px; 
                            color: white; 
                            font-size: 1.05rem;
                            transition: all 0.2s ease;
                            font-weight: 500;
                        " placeholder="Enter student name">
                    </div>

                    <!-- Age & DOB Row -->
                    <div class="row" style="display: flex; gap: 24px; margin-bottom: 26px;">
                        <div class="form-group" style="flex: 1;">
                            <label style="
                                display: block; 
                                color: #e2e8f0; 
                                font-weight: 700; 
                                margin-bottom: 12px; 
                                font-size: 1rem;
                                letter-spacing: 0.4px;
                            ">Age *</label>
                            <input type="number" name="age" class="form-input premium-input" required value="${sanitizedStudent.age}" min="1" max="100" style="
                                width: 100%; 
                                padding: 16px 18px; 
                                background: rgba(15, 23, 42, 0.8); 
                                border: 2px solid rgba(99, 102, 241, 0.35); 
                                border-radius: 12px; 
                                color: white; 
                                font-size: 1.05rem;
                                transition: all 0.2s ease;
                                font-weight: 500;
                            " placeholder="Age">
                        </div>
                        <div class="form-group" style="flex: 1;">
                            <label style="
                                display: block; 
                                color: #e2e8f0; 
                                font-weight: 700; 
                                margin-bottom: 12px; 
                                font-size: 1rem;
                                letter-spacing: 0.4px;
                            ">Date of Birth *</label>
                            <input type="date" name="dob" class="form-input premium-input" required value="${sanitizedStudent.dob}" style="
                                width: 100%; 
                                padding: 16px 18px; 
                                background: rgba(15, 23, 42, 0.8); 
                                border: 2px solid rgba(99, 102, 241, 0.35); 
                                border-radius: 12px; 
                                color: white; 
                                font-size: 1.05rem;
                                transition: all 0.2s ease;
                                font-weight: 500;
                            ">
                        </div>
                    </div>

                    <!-- Grade & Gender Row -->
                    <div class="row" style="display: flex; gap: 24px; margin-bottom: 26px;">
                        <div class="form-group" style="flex: 1;">
                            <label style="
                                display: block; 
                                color: #e2e8f0; 
                                font-weight: 700; 
                                margin-bottom: 12px; 
                                font-size: 1rem;
                                letter-spacing: 0.4px;
                            ">Class/Grade *</label>
                            <input type="number" name="grade" class="form-input premium-input" required value="${sanitizedStudent.grade}" min="0" max="12" style="
                                width: 100%; 
                                padding: 16px 18px; 
                                background: rgba(15, 23, 42, 0.8); 
                                border: 2px solid rgba(99, 102, 241, 0.35); 
                                border-radius: 12px; 
                                color: white; 
                                font-size: 1.05rem;
                                transition: all 0.2s ease;
                                font-weight: 500;
                            " placeholder="Grade">
                        </div>
                        <div class="form-group" style="flex: 1;">
                            <label style="
                                display: block; 
                                color: #e2e8f0; 
                                font-weight: 700; 
                                margin-bottom: 12px; 
                                font-size: 1rem;
                                letter-spacing: 0.4px;
                            ">Gender *</label>
                            <select name="gender" class="form-input premium-select" required style="
                                width: 100%; 
                                padding: 16px 18px; 
                                background: rgba(15, 23, 42, 0.8); 
                                border: 2px solid rgba(99, 102, 241, 0.35); 
                                border-radius: 12px; 
                                color: white; 
                                font-size: 1.05rem;
                                transition: all 0.2s ease;
                                font-weight: 500;
                            ">
                                ${genderOptions}
                            </select>
                        </div>
                    </div>

                    <!-- Relation -->
                    <div class="form-group" style="margin-bottom: 26px;">
                        <label style="
                            display: block; 
                            color: #e2e8f0; 
                            font-weight: 700; 
                            margin-bottom: 12px; 
                            font-size: 1rem;
                            letter-spacing: 0.4px;
                        ">Parent/Guardian Relation *</label>
                        <input type="text" name="relation" class="form-input premium-input" required value="${sanitizedStudent.relation}" style="
                            width: 100%; 
                            padding: 16px 18px; 
                            background: rgba(15, 23, 42, 0.8); 
                            border: 2px solid rgba(99, 102, 241, 0.35); 
                            border-radius: 12px; 
                            color: white; 
                            font-size: 1.05rem;
                            transition: all 0.2s ease;
                            font-weight: 500;
                        " placeholder="e.g. Father, Mother, Guardian">
                    </div>

                    <!-- Photo Upload -->
                    <div class="form-group" style="margin-bottom: 36px;">
                        <label style="
                            display: block; 
                            color: #e2e8f0; 
                            font-weight: 700; 
                            margin-bottom: 12px; 
                            font-size: 1rem;
                            letter-spacing: 0.4px;
                        ">Update Photo (Optional)</label>
                        <div class="file-upload-wrapper" style="
                            border: 3px dashed rgba(99, 102, 241, 0.45); 
                            padding: 28px; 
                            text-align: center; 
                            border-radius: 16px; 
                            position: relative; 
                            background: rgba(15, 23, 42, 0.5); 
                            transition: all 0.3s ease; 
                            cursor: pointer;
                        " onmouseover="this.style.borderColor='rgba(99, 102, 241, 0.8)'; this.style.background='rgba(99, 102, 241, 0.12)'" onmouseout="this.style.borderColor='rgba(99, 102, 241, 0.45)'; this.style.background='rgba(15, 23, 42, 0.5)'">
                            <input type="file" name="photo" class="form-input" accept="image/*" style="
                                opacity: 0; 
                                position: absolute; 
                                top: 0; 
                                left: 0; 
                                width: 100%; 
                                height: 100%; 
                                cursor: pointer;
                            ">
                            <div style="pointer-events: none;">
                                <span style="font-size: 3rem; display: block; margin-bottom: 12px;">📸</span>
                                <span style="color: #cbd5e1; font-size: 1.1rem; display: block; font-weight: 600;">Click to upload new photo</span>
                                <span style="color: #64748b; font-size: 0.9rem; display: block; margin-top: 8px;">JPG, PNG or GIF (Max 5MB)</span>
                            </div>
                        </div>
                        ${sanitizedStudent.photo ? `<div style="font-size: 0.95rem; color: #10b981; margin-top: 12px; display: flex; align-items: center; gap: 10px; justify-content: center; font-weight: 600;"><span style="font-size: 1.3rem;">✓</span> Current photo exists</div>` : ''}
                    </div>

                    <!-- Action Buttons -->
                    <div class="modal-actions" style="
                        display: flex; 
                        gap: 18px; 
                        justify-content: flex-end; 
                        padding-top: 28px; 
                        border-top: 2px solid rgba(99, 102, 241, 0.25);
                    ">
                        <button type="button" class="btn-cancel" onclick="DashboardApp.closeEditModal()" style="
                            padding: 16px 36px; 
                            background: rgba(239, 68, 68, 0.12); 
                            border: 2px solid rgba(239, 68, 68, 0.45); 
                            color: #fca5a5; 
                            border-radius: 12px; 
                            font-weight: 800; 
                            cursor: pointer; 
                            transition: all 0.2s ease;
                            font-size: 1.05rem;
                            letter-spacing: 0.6px;
                        " onmouseover="this.style.background='rgba(239, 68, 68, 0.25)'; this.style.borderColor='rgba(239, 68, 68, 0.7)'; this.style.color='#ef4444'; this.style.transform='translateY(-3px)'; this.style.boxShadow='0 8px 20px rgba(239, 68, 68, 0.3)'" onmouseout="this.style.background='rgba(239, 68, 68, 0.12)'; this.style.borderColor='rgba(239, 68, 68, 0.45)'; this.style.color='#fca5a5'; this.style.transform='translateY(0)'; this.style.boxShadow='none'">
                            ✕ CANCEL
                        </button>
                        <button type="submit" class="btn-primary" style="
                            padding: 16px 40px; 
                            background: linear-gradient(135deg, #6366f1, #8b5cf6); 
                            border: none; 
                            color: white; 
                            border-radius: 12px; 
                            font-weight: 800; 
                            cursor: pointer; 
                            transition: all 0.2s ease; 
                            box-shadow: 0 8px 24px rgba(99, 102, 241, 0.45);
                            font-size: 1.05rem;
                            letter-spacing: 0.6px;
                        " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 12px 35px rgba(99, 102, 241, 0.65)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 8px 24px rgba(99, 102, 241, 0.45)'">
                            💾 UPDATE CHANGES
                        </button>
                    </div>
                </form>
            </div>
        </div>
    `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);

        // Lock Institution Type based on plan
        const typeSelect = document.getElementById('premiumEditInstitutionType');
        const lockNote = document.getElementById('premiumPlanLockNote');

        if (typeSelect && DashboardApp.currentUser) {
            const userPlan = (DashboardApp.currentUser.institution_type || 'COACHING').toUpperCase();
            const isAdmin = DashboardApp.currentUser.is_superuser;

            const planNames = {
                'COACHING': 'Coaching Student',
                'SCHOOL': 'School Student',
                'INSTITUTE': 'Institute/College Student'
            };

            if (isAdmin) {
                // Super Admins see everything
                typeSelect.innerHTML = `
                    <option value="SCHOOL" ${sanitizedStudent.institution_type === 'SCHOOL' ? 'selected' : ''}>School Student</option>
                    <option value="COACHING" ${sanitizedStudent.institution_type === 'COACHING' ? 'selected' : ''}>Coaching Student</option>
                    <option value="INSTITUTE" ${sanitizedStudent.institution_type === 'INSTITUTE' ? 'selected' : ''}>Institute/College Student</option>
                `;
                if (lockNote) lockNote.textContent = "SuperAdmin: All types unlocked.";
            } else {
                // Regular users locked to their plan
                typeSelect.innerHTML = `<option value="${userPlan}" selected>${planNames[userPlan]}</option>`;
                typeSelect.disabled = true;
                if (lockNote) lockNote.innerHTML = `🛡️ Locked to your <b>${userPlan}</b> subscription.`;

                // Ensure form submit picks up the value even if disabled
                const editForm = document.getElementById('editStudentForm');
                if (editForm) {
                    editForm.addEventListener('submit', () => {
                        typeSelect.disabled = false; // Temporarily enable to let FormData pick it up
                    });
                }
            }
        }

        // Add premium animation styles and spin animation (same as before)
        if (!document.getElementById('editModalAnimations')) {
            const style = document.createElement('style');
            style.id = 'editModalAnimations';
            style.innerHTML = `
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            @keyframes slideUp {
                from { opacity: 0; transform: translateY(50px) scale(0.92); }
                to { opacity: 1; transform: translateY(0) scale(1); }
            }
            @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
            .premium-input:focus, .premium-select:focus {
                outline: none !important;
                border-color: #6366f1 !important;
                box-shadow: 0 0 0 5px rgba(99, 102, 241, 0.2) !important;
                background: rgba(15, 23, 42, 0.95) !important;
            }
            .modal-card::-webkit-scrollbar {
                width: 10px;
            }
            .modal-card::-webkit-scrollbar-track {
                background: rgba(15, 23, 42, 0.6);
                border-radius: 12px;
            }
            .modal-card::-webkit-scrollbar-thumb {
                background: rgba(99, 102, 241, 0.6);
                border-radius: 12px;
            }
            .modal-card::-webkit-scrollbar-thumb:hover {
                background: rgba(99, 102, 241, 0.8);
            }
        `;
            document.head.appendChild(style);
        }

        // Add escape key handler
        const escapeHandler = (e) => {
            if (e.key === 'Escape') {
                DashboardApp.closeEditModal();
            }
        };
        document.addEventListener('keydown', escapeHandler);

        // Store handler for cleanup
        const modal = document.getElementById('editStudentModal');
        if (modal) {
            modal._escapeHandler = escapeHandler;
        }

        // Initialize fields based on current type
        if (typeof DashboardApp.toggleStudentFields === 'function' && typeSelect) {
            DashboardApp.toggleStudentFields(typeSelect.value);
        }
    };

    // Store implementation so we can call it from the global wrapper
    if (typeof DashboardApp !== 'undefined') {
        DashboardApp.showEditStudentModalPremiumImpl = showModal;
    }
    // Also expose simpler one if needed for debugging
    window.showEditStudentModalPremiumImpl = showModal;

    // Direct assignment for backward compatibility/direct calls if DashboardApp is ready
    if (typeof DashboardApp !== 'undefined') {
        DashboardApp.showEditStudentModalPremium = showModal;
        DashboardApp.showEditStudentModal = showModal; // OVERRIDE DEFAULT MODAL
    }

})();


DashboardApp.closeEditModal = function () {
    const modal = document.getElementById('editStudentModal');
    if (modal) {
        // Remove escape key handler
        if (modal._escapeHandler) {
            document.removeEventListener('keydown', modal._escapeHandler);
        }
        // Fade out animation
        modal.style.opacity = '0';
        modal.style.transform = 'scale(0.9)';
        setTimeout(() => {
            if (modal.parentNode) {
                modal.remove();
            }
        }, 250);
    }
};
