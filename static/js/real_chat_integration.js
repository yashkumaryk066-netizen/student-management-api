// ===== REAL AI CHAT INTEGRATION =====
// Complete frontend-to-backend connection

let currentConversationId = null;
let chatHistory = [];

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

// REAL Send Message Function
async function sendMessage() {
    const input = document.getElementById('promptInput');
    const msg = input.value.trim();
    if (!msg) return;

    // Security check (keep existing)
    const restrictedKeywords = ['porn', 'xxx', 'nude', 'sex', 'call girl', 'nsfw', 'hentai'];
    const lowerMsg = msg.toLowerCase();

    if (restrictedKeywords.some(keyword => lowerMsg.includes(keyword))) {
        // Add security alert
        addSecurityAlert(msg);
        input.value = '';
        return;
    }

    // Hide welcome screen
    const welcome = document.getElementById('welcome-screen');
    if (welcome) welcome.style.display = 'none';

    // Add user message to UI
    addMessageToUI('user', msg);

    // Clear input
    input.value = '';
    input.style.height = 'auto';

    // Add typing indicator
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
                message: msg,
                model: localStorage.getItem('selected_ai_model') || 'gemini-2.0-flash',
                system_prompt: getCurrentModePrompt()
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'API Error');
        }

        // Save conversation ID
        if (data.conversation_id) {
            currentConversationId = data.conversation_id;
        }

        // Remove typing indicator
        loadingDiv.remove();

        // Add AI response to UI
        addMessageToUI('ai', data.message.content);

        // Update sidebar if new conversation
        if (data.conversation_title) {
            await loadChatHistory();
        }

        // Play sound
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
function addMessageToUI(role, content) {
    const container = document.getElementById('messages');
    const div = document.createElement('div');

    if (role === 'user') {
        div.className = 'flex justify-end';
        div.innerHTML = `
            <div class="msg-user max-w-3xl p-4 text-white shadow-lg transform transition-all duration-300 translate-y-4 opacity-0 animate-[slideIn_0.3s_forwards]">
                ${escapeHtml(content).replace(/\n/g, '<br>')}
            </div>
        `;
    } else if (role === 'ai') {
        const parsedContent = parseMarkdown(content);
        div.className = 'flex justify-start';
        div.innerHTML = `
            <div class="flex gap-4 max-w-4xl w-full animate-[fadeIn_0.5s_ease-in-out]">
                <div class="w-8 h-8 rounded mt-1 overflow-hidden shadow-lg shadow-cyan-500/20 border border-cyan-500/30">
                    <div class="w-full h-full bg-slate-900 flex items-center justify-center">
                        <i class="fa-solid fa-cube text-cyan-400 text-xs"></i>
                    </div>
                </div>
                <div class="msg-ai p-4 text-slate-300 shadow-lg flex-1 markdown-content">
                    ${parsedContent}
                    <div class="message-tools mt-3 flex flex-wrap gap-2 opacity-0 group-hover:opacity-100 transition">
                        <button onclick="copyMessage(this)" class="text-xs px-2 py-1 bg-white/5 hover:bg-white/10 rounded border border-white/10" title="Copy">
                            <i class="fa-solid fa-copy"></i>
                        </button>
                        <button onclick="regenerateMessage()" class="text-xs px-2 py-1 bg-white/5 hover:bg-white/10 rounded border border-white/10" title="Regenerate">
                            <i class="fa-solid fa-rotate"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    } else if (role === 'error') {
        div.className = 'flex justify-start';
        div.innerHTML = `
            <div class="flex gap-4 max-w-4xl">
                <div class="w-8 h-8 rounded-full bg-red-600 flex items-center justify-center mt-1">
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
            </div>
        </div>
    `;
    container.appendChild(div);
    scrollToBottom();
    return div;
}

// Load chat history (REAL)
async function loadChatHistory() {
    try {
        const response = await fetch('/api/chat/history/', {
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        const data = await response.json();

        if (data.success && data.conversations.length > 0) {
            updateSidebarChats(data.conversations);
        }
    } catch (error) {
        console.error('Load history error:', error);
    }
}

// Update sidebar with real chats
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

// Load specific conversation (REAL)
async function loadConversation(conversationId) {
    try {
        const response = await fetch(`/api/chat/conversation/${conversationId}/`, {
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        const data = await response.json();

        if (data.success) {
            currentConversationId = conversationId;

            // Clear messages
            const container = document.getElementById('messages');
            container.innerHTML = '';

            // Hide welcome
            const welcome = document.getElementById('welcome-screen');
            if (welcome) welcome.style.display = 'none';

            // Load all messages
            data.messages.forEach(msg => {
                addMessageToUI(msg.role, msg.content);
            });

            scrollToBottom();
            showToast('✅ Conversation loaded');
        }
    } catch (error) {
        console.error('Load conversation error:', error);
        showToast('⚠️ Error loading conversation');
    }
}

// Load notifications (REAL)
async function loadNotifications() {
    try {
        const response = await fetch('/api/notifications/', {
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        const data = await response.json();

        if (data.success) {
            updateNotificationBadge(data.unread_count);
            // You can render notifications dropdown here
        }
    } catch (error) {
        console.error('Load notifications error:', error);
    }
}

// Update notification badge
function updateNotificationBadge(count) {
    const badge = document.querySelector('.notification-badge');
    if (badge && count > 0) {
        badge.textContent = count > 9 ? '9+' : count;
        badge.style.display = 'block';
    }
}

// REAL Global Search
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
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });

            const data = await response.json();

            if (data.success) {
                showSearchResults(data.results, query);
            }
        } catch (error) {
            console.error('Search error:', error);
        }
    }, 300);
}

// Show search results
function showSearchResults(results, query) {
    let dropdown = document.getElementById('searchResults');

    if (!dropdown) {
        dropdown = document.createElement('div');
        dropdown.id = 'searchResults';
        dropdown.className = 'absolute top-full left-0 right-0 mt-2 bg-slate-800 border border-white/10 rounded-lg shadow-xl max-h-96 overflow-y-auto z-50';
        document.querySelector('#globalSearch').parentElement.appendChild(dropdown);
    }

    if (results.length === 0) {
        dropdown.innerHTML = '<div class="p-4 text-slate-400 text-sm">No results found</div>';
    } else {
        dropdown.innerHTML = results.map(r => `
            <button onclick="loadConversation(${r.conversation_id})" class="w-full text-left p-4 hover:bg-white/5 transition border-b border-white/5">
                <div class="text-white text-sm font-medium mb-1">${escapeHtml(r.conversation_title)}</div>
                <div class="text-slate-400 text-xs">${highlightMatch(r.content, query)}</div>
                <div class="text-slate-500 text-xs mt-1">${formatDate(r.timestamp)}</div>
            </button>
        `).join('');
    }

    dropdown.style.display = 'block';
}

function hideSearchResults() {
    const dropdown = document.getElementById('searchResults');
    if (dropdown) dropdown.style.display = 'none';
}

// Highlight search match
function highlightMatch(text, query) {
    const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
    return escapeHtml(text.substring(0, 200)).replace(regex, '<mark class="bg-amber-500/30 text-amber-200">$1</mark>');
}

function escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// Get current mode system prompt
function getCurrentModePrompt() {
    const mode = localStorage.getItem('selected_mode') || 'general';

    const prompts = {
        'general': 'You are Y.S.M AI, an advanced AI assistant.',
        'code': 'You are Y.S.M AI in Code Mode. Focus on writing clean, production-ready code with best practices.',
        'study': 'You are Y.S.M AI in Study Mode. Explain concepts clearly with examples and analogies.',
        'design': 'You are Y.S.M AI in Design Mode. Focus on UI/UX design principles and best practices.',
        'business': 'You are Y.S.M AI in Business Mode. Provide strategic business insights and analysis.',
        'debug': 'You are Y.S.M AI in Debug Mode. Analyze code errors systematically and provide fixes.'
    };

    return prompts[mode] || prompts['general'];
}

// Format date helper
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;

    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;

    return date.toLocaleDateString();
}

// Scroll to bottom
function scrollToBottom() {
    const container = document.getElementById('messages');
    container.scrollTop = container.scrollHeight;
}

// Copy message
function copyMessage(button) {
    const messageContent = button.closest('.msg-ai').querySelector('.markdown-content').textContent;
    navigator.clipboard.writeText(messageContent).then(() => {
        showToast('✅ Copied to clipboard');
    });
}

// Regenerate last message
async function regenerateMessage() {
    // Get last user message from chat history
    // Then resend it
    showToast('♻️ Regenerating...');
}

// Auto-load chat history on page load
document.addEventListener('DOMContentLoaded', () => {
    loadChatHistory();
    loadNotifications();

    // Auto-refresh notifications every 30 seconds
    setInterval(loadNotifications, 30000);
});

// Helper function to escape HTML
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Add security alert
function addSecurityAlert(msg) {
    const container = document.getElementById('messages');
    const welcome = document.getElementById('welcome-screen');
    if (welcome) welcome.style.display = 'none';

    // Add user message
    const userDiv = document.createElement('div');
    userDiv.className = 'flex justify-end';
    userDiv.innerHTML = `
        <div class="msg-user max-w-3xl p-4 text-white shadow-lg border border-red-500/30">
            ${escapeHtml(msg).replace(/\n/g, '<br>')}
        </div>
    `;
    container.appendChild(userDiv);

    // Add security alert
    const securityDiv = document.createElement('div');
    securityDiv.className = 'flex justify-start';
    securityDiv.innerHTML = `
        <div class="flex gap-4 max-w-4xl">
            <div class="w-8 h-8 rounded-full bg-red-600 flex items-center justify-center mt-1 animate-pulse">
                <i class="fa-solid fa-shield-halved text-xs text-white"></i>
            </div>
            <div class="msg-ai p-4 text-red-200 bg-red-900/20 border-l-2 border-red-500 shadow-lg shadow-red-900/20">
                <div class="font-bold text-xs uppercase mb-1 flex items-center gap-2">
                    <i class="fa-solid fa-lock"></i> Security Protocol Activated
                </div>
                <div class="text-sm">
                    I cannot process this request. It contains content flagged by <strong>Y.S.M Safety Guidelines</strong> (Adult/Explicit Content).
                    <br><br>
                    <span class="text-xs opacity-70">Event ID: SEC-${Math.floor(Math.random() * 100000)} | Severity: HIGH</span>
                </div>
            </div>
        </div>
    `;
    container.appendChild(securityDiv);
    scrollToBottom();
}
