/* SERVICE WORKER KILL SWITCH */
/* This service worker effectively disables itself and clears caches to ensure fresh content. */

const CACHE_NAME = 'ysm-ai-v2';

self.addEventListener('install', (event) => {
    // Force this worker to activate immediately, skipping the 'waiting' state
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    // Claim any clients immediately, so they are controlled by this new worker
    event.waitUntil(
        clients.claim().then(() => {
            // Delete all caches to ensure old content is gone
            caches.keys().then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        console.log('Deleting cache:', cacheName);
                        return caches.delete(cacheName);
                    })
                );
            });
        })
    );
});

self.addEventListener('fetch', (event) => {
    // Bypassing cache completely - network only
    // This ensures we never serve stale content
    event.respondWith(
        fetch(event.request).catch(() => {
            // Optional: fallback if offline (not needed for this specific fix)
        })
    );
});
