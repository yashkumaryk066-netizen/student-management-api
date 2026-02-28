/**
 * Module Loader - Lazy Loading for Dashboard Modules
 * SAFE: Adds lazy loading capability without breaking existing code
 * Existing admin.js continues to work as-is
 */

const ModuleLoader = {
    loadedModules: new Set(),
    loadingModules: new Map(),

    /**
     * Dynamically load a JavaScript module
     * @param {string} moduleName - Name of the module to load
     * @param {string} path - Path to the module file
     * @returns {Promise} - Resolves when module is loaded
     */
    async loadModule(moduleName, path) {
        // Check if already loaded
        if (this.loadedModules.has(moduleName)) {
            return Promise.resolve();
        }

        // Check if currently loading
        if (this.loadingModules.has(moduleName)) {
            return this.loadingModules.get(moduleName);
        }

        // Start loading
        const loadPromise = new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = path;
            script.async = true;

            script.onload = () => {
                this.loadedModules.add(moduleName);
                this.loadingModules.delete(moduleName);
                Logger.log(`✅ Module loaded: ${moduleName}`);
                resolve();
            };

            script.onerror = () => {
                this.loadingModules.delete(moduleName);
                Logger.error(`❌ Failed to load module: ${moduleName}`);
                reject(new Error(`Failed to load ${moduleName}`));
            };

            document.head.appendChild(script);
        });

        this.loadingModules.set(moduleName, loadPromise);
        return loadPromise;
    },

    /**
     * Preload modules in the background
     * @param {Array} modules - Array of {name, path} objects
     */
    async preload(modules) {
        const promises = modules.map(({ name, path }) =>
            this.loadModule(name, path).catch(e => Logger.warn(`Preload failed: ${name}`))
        );
        await Promise.allSettled(promises);
    },

    /**
     * Load multiple modules in parallel
     * @param {Array} modules - Array of {name, path} objects
     * @returns {Promise} - Resolves when all modules are loaded
     */
    async loadModules(modules) {
        const promises = modules.map(({ name, path }) => this.loadModule(name, path));
        return Promise.all(promises);
    }
};

// Module registry - map module names to their file paths
const MODULE_REGISTRY = {
    // When we split admin.js, we'll add entries here
    // For now, this is ready for future use without breaking anything

    // Example future modules:
    // 'students': '/static/js/modules/students.js',
    // 'attendance': '/static/js/modules/attendance.js',
    // 'library': '/static/js/modules/library.js',
};

// Make available globally
window.ModuleLoader = ModuleLoader;
window.MODULE_REGISTRY = MODULE_REGISTRY;

// Preload commonly used modules after page load
window.addEventListener('load', () => {
    // Future: Preload essential modules
    // ModuleLoader.preload([
    //     { name: 'students', path: MODULE_REGISTRY.students },
    //     { name: 'attendance', path: MODULE_REGISTRY.attendance }
    // ]);
});
