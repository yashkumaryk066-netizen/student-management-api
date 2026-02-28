/**
 * ═══════════════════════════════════════════════════════════════
 * GENERIC MODULE FACTORY - Rapid Module Development
 * Creates consistent modules with minimal code
 * ═══════════════════════════════════════════════════════════════
 */

class GenericModuleFactory {
    static create(config) {
        return new class {
            constructor() {
                this.config = config;
                this.data = [];
                this.table = null;
            }

            async init() {
                console.log(`📦 Initializing ${this.config.name} Module...`);
                await this.loadData();
                this.renderModule();
            }

            async loadData() {
                try {
                    if (this.config.apiEndpoint) {
                        const res = await fetch(this.config.apiEndpoint, {
                            headers: { 'Authorization': 'Bearer ' + localStorage.getItem('authToken') }
                        });
                        this.data = await res.json();
                    } else {
                        // Mock data for modules without API
                        this.data = this.config.mockData || [];
                    }
                    console.log(`✅ Loaded ${this.data.length} records`);
                } catch (error) {
                    console.error(`❌ Failed to load ${this.config.name}:`, error);
                    this.data = [];
                }
            }

            renderModule() {
                const container = document.getElementById('dashboardView');
                if (!container) return;

                container.innerHTML = `
                    <div class="module-container" style="animation: fadeIn 0.4s ease-out;">
                        <!-- Header -->
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 32px;">
                            <div>
                                <h1 class="page-title" style="font-family: 'Orbitron', sans-serif; font-size: 2.5rem; background: ${this.config.gradient || 'linear-gradient(135deg, #667eea, #764ba2)'}; -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 8px;">
                                    ${this.config.name} ${this.config.icon || '📊'}
                                </h1>
                                <p style="color: #94a3b8; font-size: 1.05rem;">${this.config.description || 'Manage your records'}</p>
                            </div>
                            ${this.renderHeaderActions()}
                        </div>

                        <!-- Stats Cards -->
                        ${this.config.stats ? this.renderStatsCards() : ''}

                        <!-- Data Table -->
                        <div id="${this.config.id}TableContainer"></div>
                    </div>
                `;

                this.renderTable();
            }

            renderHeaderActions() {
                if (!this.config.actions) return '';

                return `
                    <div style="display: flex; gap: 12px;">
                        ${this.config.actions.map(action => `
                            <button onclick="${action.onClick}" class="${action.class || 'magnetic-btn'}" 
                                style="padding: 12px 24px; background: ${action.bg || 'linear-gradient(135deg, #10b981, #059669)'}; border: none; border-radius: 8px; color: white; cursor: pointer; font-weight: 700; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);">
                                ${action.icon || '➕'} ${action.label}
                            </button>
                        `).join('')}
                    </div>
                `;
            }

            renderStatsCards() {
                if (!this.config.stats) return '';

                return `
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 32px;">
                        ${this.config.stats.map(stat => {
                    const value = typeof stat.value === 'function' ? stat.value(this.data) : stat.value;
                    return `
                                <div class="stat-card-premium premium-card-3d" style="position: relative;">
                                    <div class="stat-icon" style="background: ${stat.gradient || 'linear-gradient(135deg, #667eea, #764ba2)'}; width: 50px; height: 50px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; margin-bottom: 16px;">
                                        ${stat.icon}
                                    </div>
                                    <div class="stat-value" style="font-size: 2.5rem; font-weight: 900; color: ${stat.color || '#667eea'}; margin-bottom: 4px;">
                                        ${value}
                                    </div>
                                    <div class="stat-label" style="color: #cbd5e1; font-size: 0.9rem;">${stat.label}</div>
                                </div>
                            `;
                }).join('')}
                    </div>
                `;
            }

            renderTable() {
                this.table = new PremiumDataTable({
                    container: `#${this.config.id}TableContainer`,
                    columns: this.config.columns,
                    data: this.data,
                    actions: this.config.tableActions || [],
                    pagination: true,
                    searchable: true,
                    exportable: true
                });

                this.table.render();
                window[`${this.config.id}Table`] = this.table;
            }

            async refresh() {
                await this.loadData();
                if (this.table) {
                    this.table.updateData(this.data);
                }
            }
        };
    }
}

// Export
window.GenericModuleFactory = GenericModuleFactory;

console.log('🏭 Generic Module Factory Loaded');
