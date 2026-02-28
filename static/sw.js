const CACHE_NAME = 'sovereign-erp-v5.4.6'; // Incremented version
const ASSETS_TO_CACHE = [
    '/',
    '/static/css/dashboard.css',
    '/static/js/admin.js',
    '/static/img/ysm_logo.png'
];

// Force update on version change
self.addEventListener('install', (event) => {
    self.skipWaiting();
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return Promise.allSettled(
                ASSETS_TO_CACHE.map(url =>
                    fetch(url).then(response => {
                        if (response.ok) return cache.put(url, response);
                        throw new Error(`Failed to fetch ${url}`);
                    })
                )
            ).then(results => {
                const failed = results.filter(r => r.status === 'rejected');
                if (failed.length > 0) {
                    console.warn('⚠️ SW: Some assets failed to cache:', failed.map(f => f.reason));
                }
            });
        })
    );
});

// Clear old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.map((key) => {
                    if (key !== CACHE_NAME) return caches.delete(key);
                })
            );
        })
    );
});

// NETWORK FIRST STRATEGY: Always try network, fallback to cache
self.addEventListener('fetch', (event) => {
    event.respondWith(
        fetch(event.request).catch(() => {
            return caches.match(event.request);
        })
    );
});
