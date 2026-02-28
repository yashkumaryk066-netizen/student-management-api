/**
 * Performance Monitor
 * Tracks page load time, API calls, and user interactions
 * SAFE: Only monitors, doesn't change any functionality
 */

const PerformanceMonitor = {
    metrics: {
        pageLoad: null,
        apiCalls: [],
        moduleLoads: [],
        errors: []
    },

    init() {
        this.trackPageLoad();
        this.trackApiCalls();
        this.trackErrors();

        // Log summary after page is fully loaded
        window.addEventListener('load', () => {
            setTimeout(() => this.logSummary(), 2000);
        });
    },

    trackPageLoad() {
        if (window.performance) {
            const perfData = window.performance.timing;
            const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
            const connectTime = perfData.responseEnd - perfData.requestStart;
            const renderTime = perfData.domComplete - perfData.domLoading;

            this.metrics.pageLoad = {
                total: pageLoadTime,
                connect: connectTime,
                render: renderTime,
                domReady: perfData.domContentLoadedEventEnd - perfData.navigationStart
            };
        }
    },

    trackApiCall(url, duration, success = true) {
        this.metrics.apiCalls.push({
            url,
            duration,
            success,
            timestamp: Date.now()
        });
    },

    trackModuleLoad(moduleName, duration) {
        this.metrics.moduleLoads.push({
            module: moduleName,
            duration,
            timestamp: Date.now()
        });
    },

    trackErrors() {
        window.addEventListener('error', (event) => {
            this.metrics.errors.push({
                message: event.message,
                source: event.filename,
                line: event.lineno,
                timestamp: Date.now()
            });
        });
    },

    logSummary() {
        if (!Logger.isDevelopment) return;

        console.group('📊 Performance Report');

        // Page Load
        if (this.metrics.pageLoad) {
            console.log('⏱️  Page Load Time:', this.metrics.pageLoad.total + 'ms');
            console.log('   - Connection:', this.metrics.pageLoad.connect + 'ms');
            console.log('   - DOM Ready:', this.metrics.pageLoad.domReady + 'ms');
            console.log('   - Render:', this.metrics.pageLoad.render + 'ms');
        }

        // API Calls
        if (this.metrics.apiCalls.length > 0) {
            const avgApiTime = this.metrics.apiCalls.reduce((sum, call) => sum + call.duration, 0) / this.metrics.apiCalls.length;
            const failedCalls = this.metrics.apiCalls.filter(c => !c.success).length;

            console.log(`\n🌐 API Calls: ${this.metrics.apiCalls.length} total`);
            console.log('   - Average time:', Math.round(avgApiTime) + 'ms');
            console.log('   - Failed:', failedCalls);
        }

        // Errors
        if (this.metrics.errors.length > 0) {
            console.log(`\n❌ Errors: ${this.metrics.errors.length}`);
            this.metrics.errors.forEach(err => {
                console.log(`   - ${err.message} (${err.source}:${err.line})`);
            });
        }

        console.groupEnd();
    },

    // Get report for sending to analytics
    getReport() {
        return {
            ...this.metrics,
            userAgent: navigator.userAgent,
            timestamp: Date.now()
        };
    }
};

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => PerformanceMonitor.init());
} else {
    PerformanceMonitor.init();
}

// Make available globally
window.PerformanceMonitor = PerformanceMonitor;
