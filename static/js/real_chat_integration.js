// ===== REAL AI CHAT INTEGRATION (PREMIUM) =====
// Complete frontend-to-backend connection with Image Support & RAG

let currentConversationId = null;
let chatHistory = [];
let attachedImages = []; // Stores Base64 strings for upload

// Get CSRF token for Django
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadChatHistory();
    loadNotifications();
    setupImageUpload();

    // Auto-refresh notifications every 30 seconds
    setInterval(loadNotifications, 30000);

    // Override Enter key
    const input = document.getElementById('promptInput');
    if (input) {
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
});

// Setup Image Upload
function setupImageUpload() {
    const fileInput = document.getElementById('fileInput');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }
}

function handleFileSelect(event) {
    const files = event.target.files;
    if (files.length === 0) return;

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        if (!file.type.startsWith('image/')) {
            showToast('⚠️ Only images are supported');
            continue;
        }

        if (file.size > 5 * 1024 * 1024) {
            showToast('⚠️ Image too large (Max 5MB)');
            continue;
        }

        const reader = new FileReader();
        reader.onload = function (e) {
            const base64 = e.target.result;
            attachedImages.push(base64);
            showImagePreview(base64, attachedImages.length - 1);
        };
        reader.readAsDataURL(file);
    }
    event.target.value = ''; // Reset input
}

function showImagePreview(base64, index) {
    let container = document.getElementById('image-previews');
    if (!container) {
        container = document.createElement('div');
        container.id = 'image-previews';
        container.className = 'flex gap-2 p-2 absolute bottom-full left-0 w-full bg-slate-900/90 backdrop-blur-sm border-t border-white/10 overflow-x-auto';
        const inputArea = document.querySelector('.input-area-wrapper') || document.getElementById('promptInput').parentElement;
        inputArea.style.position = 'relative';
        inputArea.appendChild(container); // Append to input area wrapper
    }

    const div = document.createElement('div');
    div.className = 'relative group w-16 h-16 rounded-lg overflow-hidden border border-white/20 flex-shrink-0';
    div.innerHTML = `
        <img src="${base64}" class="w-full h-full object-cover">
        <button onclick="removeImage(${index})" class="absolute top-0 right-0 bg-red-500 text-white w-5 h-5 flex items-center justify-center rounded-bl-lg text-xs opacity-0 group-hover:opacity-100 transition">
            <i class="fa-solid fa-times"></i>
        </button>
    `;
    container.appendChild(div);
}

function removeImage(index) {
    attachedImages.splice(index, 1);
    // Re-render previews
    const container = document.getElementById('image-previews');
    if (container) {
        container.innerHTML = '';
        attachedImages.forEach((img, idx) => showImagePreview(img, idx));
        if (attachedImages.length === 0) container.remove();
    }
}

// REAL Send Message Function
async function sendMessage() {
    const input = document.getElementById('promptInput');
    const msg = input.value.trim();

    // Allow sending if there are images, even if text is empty
    if (!msg && attachedImages.length === 0) return;

    // Security check
    const restrictedKeywords = ['porn', 'xxx', 'nude', 'sex', 'call girl', 'nsfw', 'hentai'];
    const lowerMsg = msg.toLowerCase();

    if (restrictedKeywords.some(keyword => lowerMsg.includes(keyword))) {
        addSecurityAlert(msg);
        input.value = '';
        return;
    }

    // Hide welcome
    const welcome = document.getElementById('welcome-screen');
    if (welcome) welcome.style.display = 'none';

    // Add user message to UI
    addMessageToUI('user', msg, attachedImages);

    // Clear input & images
    input.value = '';
    input.style.height = 'auto';
    const tempImages = [...attachedImages]; // Copy for API
    attachedImages = [];
    const previewContainer = document.getElementById('image-previews');
    if (previewContainer) previewContainer.remove();

    // Add loading
    const loadingDiv = addTypingIndicator();

    try {
        // Call REAL API
        const response = await fetch('/api/chat/send/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                conversation_id: currentConversationId,
                message: msg || "Analyze this image", // Default text if only image sent
                model: localStorage.getItem('selected_ai_model') || 'gemini-2.0-flash',
                system_prompt: getCurrentModePrompt(),
                images: tempImages // Send images
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'API Error');
        }

        if (data.conversation_id) {
            currentConversationId = data.conversation_id;
        }

        loadingDiv.remove();
        addMessageToUI('ai', data.message.content);

        if (data.conversation_title) {
            await loadChatHistory();
        }

        sfxReceive.volume = 0.3;
        sfxReceive.play().catch(e => console.log('Audio failed'));

    } catch (error) {
        console.error('Send Error:', error);
        loadingDiv.remove();
        addMessageToUI('error', `⚠️ Error: ${error.message}`);
    }

    scrollToBottom();
}

// Add message to UI
function addMessageToUI(role, content, images = []) {
    const container = document.getElementById('messages');
    const div = document.createElement('div');

    // Image Grids
    let imagesHtml = '';
    if (images.length > 0) {
        imagesHtml = `<div class="flex gap-2 mb-2 flex-wrap">
            ${images.map(img => `<img src="${img}" class="h-32 rounded-lg border border-white/20 shadow-md">`).join('')}
        </div>`;
    }

    if (role === 'user') {
        div.className = 'flex justify-end';
        div.innerHTML = `
            <div class="flex flex-col items-end max-w-3xl">
                ${imagesHtml}
                <div class="msg-user p-4 text-white shadow-lg transform transition-all duration-300 translate-y-4 opacity-0 animate-[slideIn_0.3s_forwards]">
                    ${escapeHtml(content).replace(/\n/g, '<br>')}
                </div>
            </div>
        `;
    } else if (role === 'ai') {
        const parsedContent = parseMarkdown(content);
        div.className = 'flex justify-start';
        div.innerHTML = `
            <div class="flex gap-4 max-w-4xl w-full animate-[fadeIn_0.5s_ease-in-out]">
                <div class="w-8 h-8 rounded mt-1 overflow-hidden shadow-lg shadow-cyan-500/20 border border-cyan-500/30 flex-shrink-0">
                    <div class="w-full h-full bg-slate-900 flex items-center justify-center">
                        <i class="fa-solid fa-cube text-cyan-400 text-xs"></i>
                    </div>
                </div>
                <div class="msg-ai p-4 text-slate-300 shadow-lg flex-1 markdown-content overflow-hidden">
                    ${parsedContent}
                    <div class="message-tools mt-3 flex flex-wrap gap-2 opacity-0 group-hover:opacity-100 transition">
                        <button onclick="copyMessage(this)" class="text-xs px-2 py-1 bg-white/5 hover:bg-white/10 rounded border border-white/10" title="Copy">
                            <i class="fa-solid fa-copy"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    } else if (role === 'error') {
        div.className = 'flex justify-start';
        div.innerHTML = `
            <div class="flex gap-4 max-w-4xl">
                <div class="w-8 h-8 rounded-full bg-red-600 flex items-center justify-center mt-1 flex-shrink-0">
                    <i class="fa-solid fa-exclamation text-xs text-white"></i>
                </div>
                <div class="msg-ai p-4 text-red-200 bg-red-900/20 border-l-2 border-red-500">
                    ${content}
                </div>
            </div>
        `;
    }

    container.appendChild(div);

    // Highlight code blocks
    div.querySelectorAll('pre code').forEach(block => {
        hljs.highlightElement(block);
    });
}

// Add typing indicator
function addTypingIndicator() {
    const container = document.getElementById('messages');
    const div = document.createElement('div');
    div.className = 'flex justify-start typing-indicator';
    div.innerHTML = `
        <div class="flex gap-4 max-w-4xl">
            <div class="w-8 h-8 rounded-full bg-amber-500 flex items-center justify-center mt-1">
                <i class="fa-solid fa-brain text-xs text-white"></i>
            </div>
            <div class="msg-ai p-4 text-slate-300 shadow-none bg-transparent border-none">
                <div class="flex gap-1">
                    <div class="w-2 h-2 bg-amber-500 rounded-full typing-dot"></div>
                    <div class="w-2 h-2 bg-amber-500 rounded-full typing-dot"></div>
                    <div class="w-2 h-2 bg-amber-500 rounded-full typing-dot"></div>
                </div>
                <span class="text-xs text-slate-500 ml-2">Analyzing...</span>
            </div>
        </div>
    `;
    container.appendChild(div);
    scrollToBottom();
    return div;
}

// Load chat history
async function loadChatHistory() {
    try {
        const response = await fetch('/api/chat/history/', {
            headers: { 'X-CSRFToken': getCookie('csrftoken') }
        });
        const data = await response.json();
        if (data.success && data.conversations.length > 0) {
            updateSidebarChats(data.conversations);
        }
    } catch (error) { console.error('Load history error:', error); }
}

// Update sidebar
function updateSidebarChats(conversations) {
    const recentChatsContainer = document.querySelector('.recent-chats-list');
    if (!recentChatsContainer) return;

    recentChatsContainer.innerHTML = conversations.slice(0, 5).map(conv => `
        <button onclick="loadConversation(${conv.id})" class="w-full text-left p-4 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 hover:border-amber-500/30 transition group">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                    <i class="fa-solid fa-message text-purple-400"></i>
                </div>
                <div class="flex-1 min-w-0">
                    <div class="text-white font-medium text-sm truncate group-hover:text-amber-300 transition">
                        ${escapeHtml(conv.title)}
                    </div>
                    <div class="text-xs text-slate-500">${formatDate(conv.updated_at)}</div>
                </div>
                <i class="fa-solid fa-chevron-right text-slate-600 group-hover:text-amber-500 transition text-xs"></i>
            </div>
        </button>
    `).join('');
}

// Load specific conversation
async function loadConversation(conversationId) {
    try {
        const response = await fetch(`/api/chat/conversation/${conversationId}/`, {
            headers: { 'X-CSRFToken': getCookie('csrftoken') }
        });
        const data = await response.json();
        if (data.success) {
            currentConversationId = conversationId;
            const container = document.getElementById('messages');
            container.innerHTML = '';
            document.getElementById('welcome-screen').style.display = 'none';

            data.messages.forEach(msg => {
                addMessageToUI(msg.role, msg.content);
            });
            scrollToBottom();
        }
    } catch (error) { console.error('Load conversation error:', error); }
}

// Load notifications
async function loadNotifications() {
    try {
        const response = await fetch('/api/notifications/', {
            headers: { 'X-CSRFToken': getCookie('csrftoken') }
        });
        const data = await response.json();
        if (data.success) {
            const badge = document.querySelector('.notification-badge');
            if (badge && data.unread_count > 0) {
                badge.textContent = data.unread_count > 9 ? '9+' : data.unread_count;
                badge.style.display = 'block';
            }
        }
    } catch (error) { console.error('Load notifications error:', error); }
}

// Global Search
let searchDebounceTimer;
async function searchGlobal(query) {
    if (!query || query.length < 2) {
        hideSearchResults();
        return;
    }
    clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(async () => {
        try {
            const response = await fetch(`/api/chat/search/?q=${encodeURIComponent(query)}`, {
                headers: { 'X-CSRFToken': getCookie('csrftoken') }
            });
            const data = await response.json();
            if (data.success) showSearchResults(data.results, query);
        } catch (error) { console.error('Search error:', error); }
    }, 300);
}

function showSearchResults(results, query) {
    let dropdown = document.getElementById('searchResults');
    if (!dropdown) {
        dropdown = document.createElement('div');
        dropdown.id = 'searchResults';
        dropdown.className = 'absolute top-full left-0 right-0 mt-2 bg-slate-800 border border-white/10 rounded-lg shadow-xl max-h-96 overflow-y-auto z-50';
        document.querySelector('#globalSearch').parentElement.appendChild(dropdown);
    }
    dropdown.innerHTML = results.length === 0 ? '<div class="p-4 text-slate-400 text-sm">No results found</div>' :
        results.map(r => `
            <button onclick="loadConversation(${r.conversation_id})" class="w-full text-left p-4 hover:bg-white/5 transition border-b border-white/5">
                <div class="text-white text-sm font-medium mb-1">${escapeHtml(r.conversation_title)}</div>
                <div class="text-slate-400 text-xs">${escapeHtml(r.content).substring(0, 50)}...</div>
            </button>
        `).join('');
    dropdown.style.display = 'block';
}

function hideSearchResults() {
    const dropdown = document.getElementById('searchResults');
    if (dropdown) dropdown.style.display = 'none';
}

// Helpers
function formatDate(dateString) { return new Date(dateString).toLocaleDateString(); }
function scrollToBottom() { const c = document.getElementById('messages'); c.scrollTop = c.scrollHeight; }
function escapeHtml(unsafe) {
    return (unsafe || '').replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
function getCurrentModePrompt() { return localStorage.getItem('selected_mode') || 'general'; }
function copyMessage(btn) {
    const text = btn.closest('.msg-ai').textContent;
    navigator.clipboard.writeText(text);
}
function showToast(msg) { alert(msg); } // Simple toast for now
function addSecurityAlert(msg) { addMessageToUI('error', 'Security Policy Violation: Message blocked.'); }
