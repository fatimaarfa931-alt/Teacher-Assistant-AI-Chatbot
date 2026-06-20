// script.js - Chat Logic, Voice, and History

document.addEventListener('DOMContentLoaded', () => {
    const messageInput = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');
    const chatArea = document.getElementById('chat-area');
    const micBtn = document.getElementById('mic-btn');
    const sidebar = document.getElementById('sidebar');
    const toggleSidebarBtn = document.getElementById('toggle-sidebar-btn');
    const closeSidebarBtn = document.getElementById('close-sidebar-btn');
    const historyList = document.getElementById('history-list');

    let currentChatId = Date.now().toString();
    let chats = JSON.parse(localStorage.getItem('teacherChats')) || {};

    // Load History
    function loadHistorySidebar() {
        // Keep the title
        historyList.innerHTML = '<p class="history-title">Recent Chats</p>';
        const sortedChatIds = Object.keys(chats).sort((a, b) => b - a);
        
        sortedChatIds.forEach(id => {
            const chat = chats[id];
            const title = chat.title || 'New Chat';
            const item = document.createElement('div');
            item.className = 'history-item';
            item.innerHTML = `<i class="fa-regular fa-message"></i> ${title}`;
            item.onclick = () => loadChat(id);
            historyList.appendChild(item);
        });
    }

    function loadChat(id) {
        currentChatId = id;
        chatArea.innerHTML = '';
        const chat = chats[id];
        chat.messages.forEach(msg => {
            appendMessage(msg.sender, msg.text, false);
        });
        if (window.innerWidth <= 768) {
            sidebar.classList.remove('open');
        }
    }

    function saveMessageToHistory(sender, text) {
        if (!chats[currentChatId]) {
            chats[currentChatId] = {
                title: sender === 'user' ? text.substring(0, 30) + (text.length > 30 ? '...' : '') : 'New Chat',
                messages: []
            };
        }
        chats[currentChatId].messages.push({ sender, text });
        localStorage.setItem('teacherChats', JSON.stringify(chats));
        loadHistorySidebar();
    }

    // Initialize sidebar
    loadHistorySidebar();

    // Sidebar Toggle for Mobile
    toggleSidebarBtn.addEventListener('click', () => {
        sidebar.classList.add('open');
    });
    closeSidebarBtn.addEventListener('click', () => {
        sidebar.classList.remove('open');
    });

    // Auto-resize textarea
    messageInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
        if(this.value.trim() !== "") {
            sendBtn.style.color = "var(--text-main)";
        } else {
            sendBtn.style.color = "var(--text-muted)";
        }
    });

    // Send Message on Enter (Shift+Enter for new line)
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    sendBtn.addEventListener('click', sendMessage);

    // Make sendAction available globally for HTML onclick attributes
    window.sendAction = function(actionText, autoSend = true) {
        messageInput.value = actionText;
        messageInput.style.height = 'auto';
        messageInput.style.height = (messageInput.scrollHeight) + 'px';
        if (autoSend) {
            sendMessage();
        } else {
            messageInput.focus();
            sendBtn.style.color = "var(--text-main)";
        }
    }

    window.startNewChat = function() {
        currentChatId = Date.now().toString();
        chatArea.innerHTML = `
            <div class="message bot-message">
                <div class="avatar bot-avatar"><i class="fa-solid fa-graduation-cap"></i></div>
                <div class="message-content">
                    <p>Assalamu Alaikum! Welcome to your Islamiyat Teacher Assistant. 🕌</p>
                    <p>New chat started. Ask one Islamiyat question at a time, and I will answer it clearly for class 1 to 12.</p>
                </div>
            </div>
        `;
        if (window.innerWidth <= 768) {
            sidebar.classList.remove('open');
        }
    }

    async function sendMessage() {
        const text = messageInput.value.trim();
        if (!text) return;

        // Clear input
        messageInput.value = '';
        messageInput.style.height = 'auto';
        sendBtn.style.color = "var(--text-muted)";

        // Append User Message
        appendMessage('user', text, true);

        // Show typing indicator or skeleton
        const typingId = appendTypingIndicator();

        try {
            // Send to Backend
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: text })
            });

            const data = await response.json();
            
            // Remove typing indicator
            document.getElementById(typingId).remove();
            
            // Append Bot Message
            appendMessage('bot', data.response, true);

        } catch (error) {
            document.getElementById(typingId).remove();
            appendMessage('bot', '**Error:** Could not connect to the server.', false);
            console.error(error);
        }
    }

    function appendMessage(sender, text, saveToHistory = false) {
        if (saveToHistory) {
            saveMessageToHistory(sender, text);
        }

        const msgDiv = document.createElement('div');
        msgDiv.classList.add('message');
        msgDiv.classList.add(sender === 'user' ? 'user-message' : 'bot-message');

        const avatarDiv = document.createElement('div');
        avatarDiv.classList.add('avatar');
        avatarDiv.classList.add(sender === 'user' ? 'user-avatar' : 'bot-avatar');
        avatarDiv.innerHTML = sender === 'user' ? '<i class="fa-solid fa-user"></i>' : '<i class="fa-solid fa-graduation-cap"></i>';

        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');
        
        // Parse markdown if marked is available
        if (typeof marked !== 'undefined') {
            contentDiv.innerHTML = marked.parse(text);
        } else {
            contentDiv.textContent = text;
        }

        msgDiv.appendChild(avatarDiv);
        msgDiv.appendChild(contentDiv);
        
        chatArea.appendChild(msgDiv);
        chatArea.scrollTop = chatArea.scrollHeight;
    }

    function appendTypingIndicator() {
        const id = 'typing-' + Date.now();
        const msgDiv = document.createElement('div');
        msgDiv.id = id;
        msgDiv.classList.add('message', 'bot-message');

        msgDiv.innerHTML = `
            <div class="avatar bot-avatar"><i class="fa-solid fa-graduation-cap"></i></div>
            <div class="message-content">
                <p>Thinking...</p>
            </div>
        `;
        
        chatArea.appendChild(msgDiv);
        chatArea.scrollTop = chatArea.scrollHeight;
        return id;
    }

    // Voice Input via Web Speech API
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onstart = function() {
            micBtn.classList.add('recording');
        };

        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            messageInput.value = transcript;
            messageInput.style.height = 'auto';
            messageInput.style.height = (messageInput.scrollHeight) + 'px';
            sendBtn.style.color = "var(--text-main)";
            // Automatically send after voice dictation completes
            sendMessage();
        };

        recognition.onerror = function(event) {
            console.error("Speech recognition error", event.error);
            micBtn.classList.remove('recording');
        };

        recognition.onend = function() {
            micBtn.classList.remove('recording');
        };

        micBtn.addEventListener('click', () => {
            if (micBtn.classList.contains('recording')) {
                recognition.stop();
            } else {
                recognition.start();
            }
        });
    } else {
        micBtn.style.display = 'none'; // Hide if not supported
        console.warn("Speech Recognition API not supported in this browser.");
    }
});
