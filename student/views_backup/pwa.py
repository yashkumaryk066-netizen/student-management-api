from django.http import HttpResponse

def service_worker(request):
    js_content = """
const VERSION = 'v3.0.0';
const CACHE_NAME = `ysm-ai-${VERSION}`;
const RUNTIME_CACHE = `ysm-runtime-${VERSION}`;

// Core assets to cache immediately
const CORE_ASSETS = [
  '/ai-chat/',
  '/static/manifest.json',
  '/static/assets/ysm_icon.png',
  'https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
];

// Install - cache core assets
self.addEventListener('install', event => {
  console.log(`[SW] Installing ${VERSION}`);
  self.skipWaiting(); // Force activation
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(CORE_ASSETS))
      .catch(err => console.log('[SW] Cache install error:', err))
  );
});

// Activate - clean old caches & notify clients
self.addEventListener('activate', event => {
  console.log(`[SW] Activating ${VERSION}`);
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all([
        // Delete old caches
        ...keys.filter(key => key !== CACHE_NAME && key !== RUNTIME_CACHE)
             .map(key => caches.delete(key)),
        // Claim all clients
        self.clients.claim()
      ]);
    }).then(() => {
      // Notify all clients about update
      return self.clients.matchAll().then(clients => {
        clients.forEach(client => {
          client.postMessage({
            type: 'APP_UPDATE',
            version: VERSION,
            message: 'App updated to ' + VERSION
          });
        });
      });
    })
  );
});

// Fetch - Network first for API, Cache first for static
self.addEventListener('fetch', event => {
  const { request } = event;
  
  // Skip non-GET requests
  if (request.method !== 'GET') return;
  
  // For API calls - always try network first
  if (request.url.includes('/api/')) {
    event.respondWith(
      fetch(request)
        .then(response => {
          if (response && response.status === 200) {
            const responseClone = response.clone();
            caches.open(RUNTIME_CACHE).then(cache => {
              cache.put(request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          return caches.match(request).then(cached => {
            if (cached) return cached;
            // Return offline fallback
            return new Response(
              JSON.stringify({ error: 'Offline', cached: false }),
              { headers: { 'Content-Type': 'application/json' } }
            );
          });
        })
    );
    return;
  }
  
  // For static assets - cache first
  event.respondWith(
    caches.match(request)
      .then(cached => {
        if (cached) return cached;
        
        return fetch(request).then(response => {
          if (response && response.status === 200) {
            const responseClone = response.clone();
            caches.open(RUNTIME_CACHE).then(cache => {
              cache.put(request, responseClone);
            });
          }
          return response;
        });
      })
      .catch(err => {
        console.log('[SW] Fetch failed:', request.url);
      })
  );
});

// Background sync for offline messages
self.addEventListener('sync', event => {
  if (event.tag === 'sync-messages') {
    event.waitUntil(syncMessages());
  }
});

async function syncMessages() {
  console.log('[SW] Syncing offline messages...');
}

// Push notifications (future)
self.addEventListener('push', event => {
  const data = event.data ? event.data.json() : {};
  const options = {
    body: data.body || 'New update available',
    icon: '/static/assets/ysm_icon.png',
    badge: '/static/assets/ysm_icon.png',
    vibrate: [200, 100, 200]
  };
  event.waitUntil(
    self.registration.showNotification(data.title || 'Y.S.M AI', options)
  );
});
"""
    return HttpResponse(js_content, content_type="application/javascript")
