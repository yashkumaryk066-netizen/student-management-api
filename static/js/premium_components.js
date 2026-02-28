/**
 * ═══════════════════════════════════════════════════════════════
 * PREMIUM UI COMPONENT LIBRARY - Y.S.M EDUCATION
 * Reusable Components for All Modules
 * ═══════════════════════════════════════════════════════════════
 */

// ============================================================
// 1. PREMIUM DATA TABLE COMPONENT
// ============================================================
class PremiumDataTable {
    constructor(config) {
        this.container = config.container;
        this.columns = config.columns;
        this.data = config.data || [];
        this.actions = config.actions || [];
        this.pagination = config.pagination !== false;
        this.pageSize = config.pageSize || 10;
        this.currentPage = 1;
        this.searchable = config.searchable !== false;
        this.exportable = config.exportable !== false;
    }

    render() {
        const container = document.querySelector(this.container);
        if (!container) return;

        container.innerHTML = `
            <div class="premium-table-wrapper" style="background: rgba(255,255,255,0.05); backdrop-filter: blur(20px); border-radius: 16px; padding: 24px; border: 1px solid rgba(255,255,255,0.1);">
                ${this.searchable ? this.renderSearchBar() : ''}
                ${this.exportable ? this.renderToolbar() : ''}
                <div class="table-scroll" style="overflow-x: auto; margin-top: 20px;">
                    <table class="premium-table" style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="border-bottom: 2px solid rgba(59, 130, 246, 0.3);">
                                ${this.columns.map(col => `
                                    <th style="padding: 16px; text-align: left; color: #cbd5e1; font-weight: 600; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px;">
                                        ${col.label}
                                        ${col.sortable ? '<span style="margin-left: 8px; cursor: pointer;">⇅</span>' : ''}
                                    </th>
                                `).join('')}
                                ${this.actions.length ? '<th style="padding: 16px; text-align: right; color: #cbd5e1;">Actions</th>' : ''}
                            </tr>
                        </thead>
                        <tbody id="${this.container.replace('#', '')}_tbody">
                            ${this.renderRows()}
                        </tbody>
                    </table>
                </div>
                ${this.pagination ? this.renderPagination() : ''}
            </div>
        `;

        this.attachEventListeners();
    }

    renderSearchBar() {
        return `
            <div class="table-search" style="margin-bottom: 20px;">
                <input type="text" id="${this.container.replace('#', '')}_search" 
                    placeholder="🔍 Search..." 
                    style="width: 100%; padding: 12px 20px; background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; color: #fff; font-size: 0.95rem;"
                    autocomplete="off">
            </div>
        `;
    }

    renderToolbar() {
        return `
            <div class="table-toolbar" style="display: flex; gap: 12px; margin-bottom: 20px;">
                <button class="glass-button" onclick="window.exportTableData('excel')" style="padding: 10px 20px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; color: #10b981; cursor: pointer; font-weight: 600;">
                    📊 Export Excel
                </button>
                <button class="glass-button" onclick="window.exportTableData('pdf')" style="padding: 10px 20px; background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; color: #ef4444; cursor: pointer; font-weight: 600;">
                    📄 Export PDF
                </button>
            </div>
        `;
    }

    renderRows() {
        const start = (this.currentPage - 1) * this.pageSize;
        const end = start + this.pageSize;
        const pageData = this.data.slice(start, end);

        if (pageData.length === 0) {
            return `
                <tr>
                    <td colspan="${this.columns.length + (this.actions.length ? 1 : 0)}" style="padding: 60px; text-align: center; color: #64748b;">
                        <div style="font-size: 3rem; margin-bottom: 16px; opacity: 0.5;">📭</div>
                        <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 8px;">No Data Found</div>
                        <div style="font-size: 0.9rem;">Try adjusting your search or filters</div>
                    </td>
                </tr>
            `;
        }

        return pageData.map((row, index) => `
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.05); transition: all 0.3s;" 
                onmouseenter="this.style.background='rgba(59, 130, 246, 0.05)'" 
                onmouseleave="this.style.background='transparent'">
                ${this.columns.map(col => `
                    <td style="padding: 16px; color: #e2e8f0; font-size: 0.95rem;">
                        ${this.formatCell(row[col.field], col.format)}
                    </td>
                `).join('')}
                ${this.actions.length ? `
                    <td style="padding: 16px; text-align: right;">
                        <div style="display: flex; gap: 8px; justify-content: flex-end;">
                            ${this.actions.map(action => `
                                <button class="action-btn" onclick="${action.onClick}(${row.id || index})" 
                                    style="padding: 6px 12px; background: ${action.color || 'rgba(59, 130, 246, 0.1)'}; border: 1px solid ${action.borderColor || 'rgba(59, 130, 246, 0.3)'}; border-radius: 6px; color: ${action.textColor || '#3b82f6'}; cursor: pointer; font-size: 0.85rem; font-weight: 600;">
                                    ${action.icon || ''} ${action.label}
                                </button>
                            `).join('')}
                        </div>
                    </td>
                ` : ''}
            </tr>
        `).join('');
    }

    formatCell(value, format) {
        if (!format) return value || '-';

        switch (format) {
            case 'currency':
                return `₹${parseFloat(value || 0).toLocaleString()}`;
            case 'date':
                return new Date(value).toLocaleDateString();
            case 'badge':
                const colors = {
                    active: 'rgba(16, 185, 129, 0.2)',
                    inactive: 'rgba(239, 68, 68, 0.2)',
                    pending: 'rgba(245, 158, 11, 0.2)'
                };
                return `<span style="padding: 4px 12px; border-radius: 12px; background: ${colors[value.toLowerCase()] || colors.pending}; font-size: 0.8rem; font-weight: 600;">${value}</span>`;
            default:
                return value;
        }
    }

    renderPagination() {
        const totalPages = Math.ceil(this.data.length / this.pageSize);

        return `
            <div class="table-pagination" style="display: flex; justify-content: space-between; align-items: center; margin-top: 24px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.1);">
                <div style="color: #94a3b8; font-size: 0.9rem;">
                    Showing ${(this.currentPage - 1) * this.pageSize + 1} to ${Math.min(this.currentPage * this.pageSize, this.data.length)} of ${this.data.length} entries
                </div>
                <div style="display: flex; gap: 8px;">
                    <button onclick="window.tableInstance.prevPage()" ${this.currentPage === 1 ? 'disabled' : ''} 
                        style="padding: 8px 16px; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 8px; color: #3b82f6; cursor: pointer; font-weight: 600;">
                        ← Previous
                    </button>
                    <div style="padding: 8px 16px; background: rgba(59, 130, 246, 0.2); border: 1px solid rgba(59, 130, 246, 0.4); border-radius: 8px; color: #3b82f6; font-weight: 700;">
                        ${this.currentPage} / ${totalPages}
                    </div>
                    <button onclick="window.tableInstance.nextPage()" ${this.currentPage === totalPages ? 'disabled' : ''} 
                        style="padding: 8px 16px; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 8px; color: #3b82f6; cursor: pointer; font-weight: 600;">
                        Next →
                    </button>
                </div>
            </div>
        `;
    }

    attachEventListeners() {
        if (this.searchable) {
            const searchInput = document.getElementById(`${this.container.replace('#', '')}_search`);
            if (searchInput) {
                searchInput.addEventListener('input', (e) => {
                    this.search(e.target.value);
                });
            }
        }
    }

    search(query) {
        // Implement search logic
        console.log('Searching for:', query);
    }

    nextPage() {
        const totalPages = Math.ceil(this.data.length / this.pageSize);
        if (this.currentPage < totalPages) {
            this.currentPage++;
            this.render();
        }
    }

    prevPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.render();
        }
    }

    updateData(newData) {
        this.data = newData;
        this.currentPage = 1;
        this.render();
    }
}

// ============================================================
// 2. PREMIUM MODAL COMPONENT
// ============================================================
class PremiumModal {
    constructor(config) {
        this.id = config.id || 'premiumModal';
        this.title = config.title;
        this.content = config.content;
        this.size = config.size || 'medium'; // small, medium, large
        this.onConfirm = config.onConfirm;
        this.onCancel = config.onCancel;
    }

    show() {
        const sizes = {
            small: '400px',
            medium: '600px',
            large: '900px'
        };

        const modalHTML = `
            <div id="${this.id}" class="premium-modal" style="
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.7);
                backdrop-filter: blur(10px);
                z-index: 10000;
                display: flex;
                align-items: center;
                justify-content: center;
                animation: fadeIn 0.3s ease-out;
            ">
                <div class="modal-content" style="
                    background: rgba(15, 23, 42, 0.95);
                    backdrop-filter: blur(30px);
                    border: 1px solid rgba(59, 130, 246, 0.3);
                    border-radius: 20px;
                    padding: 32px;
                    max-width: ${sizes[this.size]};
                    width: 90%;
                    max-height: 90vh;
                    overflow-y: auto;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
                    animation: slideUp 0.3s ease-out;
                ">
                    <div class="modal-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
                        <h2 style="font-size: 1.8rem; font-weight: 700; color: #e2e8f0; font-family: 'Orbitron', sans-serif;">
                            ${this.title}
                        </h2>
                        <button onclick="window.closeModal('${this.id}')" style="background: none; border: none; color: #94a3b8; font-size: 1.5rem; cursor: pointer; padding: 8px;">
                            ✕
                        </button>
                    </div>
                    <div class="modal-body" style="color: #cbd5e1; line-height: 1.6;">
                        ${this.content}
                    </div>
                    ${this.onConfirm ? `
                        <div class="modal-footer" style="display: flex; gap: 12px; justify-content: flex-end; margin-top: 32px; padding-top: 24px; border-top: 1px solid rgba(255,255,255,0.1);">
                            <button onclick="window.closeModal('${this.id}')" class="glass-button" style="padding: 12px 24px; background: rgba(100, 116, 139, 0.1); border: 1px solid rgba(100, 116, 139, 0.3); border-radius: 8px; color: #94a3b8; cursor: pointer; font-weight: 600;">
                                Cancel
                            </button>
                            <button onclick="window.confirmModal('${this.id}')" class="magnetic-btn" style="padding: 12px 32px; background: linear-gradient(135deg, #3b82f6, #2563eb); border: none; border-radius: 8px; color: white; cursor: pointer; font-weight: 700; box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);">
                                Confirm
                            </button>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Store callbacks
        window[`${this.id}_confirm`] = this.onConfirm;
        window[`${this.id}_cancel`] = this.onCancel;
    }

    hide() {
        const modal = document.getElementById(this.id);
        if (modal) {
            modal.style.animation = 'fadeOut 0.3s ease-out';
            setTimeout(() => modal.remove(), 300);
        }
    }
}

// Global modal functions
window.closeModal = function (id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => modal.remove(), 300);
    }
};

window.confirmModal = function (id) {
    const callback = window[`${id}_confirm`];
    if (callback) callback();
    window.closeModal(id);
};

// ============================================================
// 3. PREMIUM FORM COMPONENT
// ============================================================
class PremiumForm {
    constructor(config) {
        this.container = config.container;
        this.fields = config.fields;
        this.onSubmit = config.onSubmit;
        this.submitLabel = config.submitLabel || 'Submit';
    }

    render() {
        const container = document.querySelector(this.container);
        if (!container) return;

        container.innerHTML = `
            <form class="premium-form" id="${this.container.replace('#', '')}_form" style="display: grid; gap: 20px;">
                ${this.fields.map(field => this.renderField(field)).join('')}
                <button type="submit" class="magnetic-btn" style="padding: 14px 32px; background: linear-gradient(135deg, #3b82f6, #2563eb); border: none; border-radius: 8px; color: white; cursor: pointer; font-weight: 700; font-size: 1rem; margin-top: 12px; box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);">
                    ${this.submitLabel}
                </button>
            </form>
        `;

        this.attachFormListeners();
    }

    renderField(field) {
        const fieldTypes = {
            text: () => `
                <div class="form-field">
                    <label style="display: block; color: #cbd5e1; font-weight: 600; margin-bottom: 8px; font-size: 0.9rem;">
                        ${field.label} ${field.required ? '<span style="color: #ef4444;">*</span>' : ''}
                    </label>
                    <input type="text" name="${field.name}" ${field.required ? 'required' : ''} 
                        placeholder="${field.placeholder || ''}"
                        style="width: 100%; padding: 12px 16px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; color: #fff; font-size: 0.95rem; transition: all 0.3s;"
                        onfocus="this.style.borderColor='#3b82f6'; this.style.boxShadow='0 0 0 3px rgba(59, 130, 246, 0.1)'"
                        onblur="this.style.borderColor='rgba(255,255,255,0.1)'; this.style.boxShadow='none'">
                </div>
            `,
            select: () => `
                <div class="form-field">
                    <label style="display: block; color: #cbd5e1; font-weight: 600; margin-bottom: 8px; font-size: 0.9rem;">
                        ${field.label} ${field.required ? '<span style="color: #ef4444;">*</span>' : ''}
                    </label>
                    <select name="${field.name}" ${field.required ? 'required' : ''}
                        style="width: 100%; padding: 12px 16px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; color: #fff; font-size: 0.95rem;">
                        <option value="">Select ${field.label}</option>
                        ${field.options.map(opt => `<option value="${opt.value}">${opt.label}</option>`).join('')}
                    </select>
                </div>
            `,
            textarea: () => `
                <div class="form-field">
                    <label style="display: block; color: #cbd5e1; font-weight: 600; margin-bottom: 8px; font-size: 0.9rem;">
                        ${field.label} ${field.required ? '<span style="color: #ef4444;">*</span>' : ''}
                    </label>
                    <textarea name="${field.name}" ${field.required ? 'required' : ''} rows="4"
                        placeholder="${field.placeholder || ''}"
                        style="width: 100%; padding: 12px 16px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; color: #fff; font-size: 0.95rem; resize: vertical;"></textarea>
                </div>
            `
        };

        return fieldTypes[field.type]();
    }

    attachFormListeners() {
        const form = document.getElementById(`${this.container.replace('#', '')}_form`);
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                const formData = new FormData(form);
                const data = Object.fromEntries(formData);
                if (this.onSubmit) this.onSubmit(data);
            });
        }
    }
}

// ============================================================
// EXPORT COMPONENTS
// ============================================================
window.PremiumDataTable = PremiumDataTable;
window.PremiumModal = PremiumModal;
window.PremiumForm = PremiumForm;

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    @keyframes fadeOut {
        from { opacity: 1; }
        to { opacity: 0; }
    }
    @keyframes slideUp {
        from { transform: translateY(30px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
`;
document.head.appendChild(style);

console.log('✨ Premium UI Component Library Loaded');
