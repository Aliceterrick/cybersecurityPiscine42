document.addEventListener('DOMContentLoaded', () => {
    const logoutBtn = document.getElementById('logout');
    const usersList = document.getElementById('users-list');
    const msgInput = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-button');
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.getElementById('message');

    let currentUser = null;
    let eventSource = null;
    let reconnectAttempts = 0;
    const MAX_RECONNECT_ATTEMPTS = 10;
    let reconnectDelay = 1000;

    function showMessage(msg, className) {
        messageDiv.textContent = msg;
        messageDiv.className = className;
        setTimeout(() => {
            messageDiv.style.display = 'none';
        }, 3000);
    }

    function formatTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    function createMessageElement(message) {
        const isCurrentUser = currentUser && currentUser.id === message.user_id;
        
        const messageElement = document.createElement('div');
        messageElement.className = `message ${isCurrentUser ? 'message-self' : ''}`;
        
        const header = document.createElement('div');
        header.className = 'message-header';
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = message.username.charAt(0).toUpperCase();
        
        const userInfo = document.createElement('div');
        userInfo.className = 'message-user-info';
        
        const username = document.createElement('span');
        username.className = 'message-username';
        username.textContent = message.username;
        
        const timestamp = document.createElement('span');
        timestamp.className = 'message-timestamp';
        timestamp.textContent = formatTime(message.created_at);
        
        userInfo.appendChild(username);
        userInfo.appendChild(timestamp);
        
        header.appendChild(avatar);
        header.appendChild(userInfo);
        
        const content = document.createElement('div');
        content.className = 'message-content';
        content.textContent = message.content;
        
        messageElement.appendChild(header);
        messageElement.appendChild(content);
        
        return messageElement;
    }

    function initSSE() {
        if (eventSource) {
            eventSource.close();
            eventSource = null;
        }

        eventSource = new EventSource('/api/events', {
            withCredentials: true
        });

        reconnectAttempts = 0;
        reconnectDelay = 1000;

        eventSource.onopen = () => {
            showMessage('Chat connected', success);
        } 

        eventSource.addEventListener('newMessage', (event) => {
            try {
                const message = JSON.parse(event.data);
                const messageElement = createMessageElement(message);
                chatMessages.appendChild(messageElement);

                chatMessages.scrollTop = chatMessages.scrollHeight;
            } catch (error) {
                console.error('Error parsing newMessage event: ', error);
            }
        });

        eventSource.addEventListener('connected', (event) => {
            showMessage('Connected to chat', 'success');
            /*  */   /*  */    /*  */      /*  */      /*  */


            /*  */   /*  */    /*  */      /*  */      /*  */
            if (reconnectTimer) {
                clearTimeout(reconnectTimer);
                reconnectTimer = null;
            }
        });

        eventSource.onerror = (error) => {
            console.error('SSE error:', error);
            if (eventSource.readyState === EventSource.CLOSED) {
                console.log('SSE connection closed');
                attemptReconnect();
            }
        };
    }

    async function loadInitialMessages() {
        try {
            const response = await fetch('/api/messages', {
                credentials: 'include'
            });
            
            if (!response.ok) throw new Error('Failed to load messages');
            
            const messages = await response.json();
            messages.forEach(msg => {
                const messageElement = createMessageElement(msg);
                chatMessages.appendChild(messageElement);
            });
            
            chatMessages.scrollTop = chatMessages.scrollHeight;
        } catch (error) {
            console.error('Failed to load messages:', error);
            showMessage('Error loading messages', 'error');
        }
    }

    async function getCurrentUser() {
        try {
            const response = await fetch('/api/auth/status', {
                credentials: 'include'
            });
            
            if (!response.ok) throw new Error('Failed to get user status');
            
            const data = await response.json();
            if (data.authenticated) {
                return data.user;
            }
            return null;
        } catch (error) {
            console.error('Error getting user status:', error);
            return null;
        }
    }

    async function loadOnlineUsers() {
        try {
            const response = await fetch('/api/get_online', {
                method: 'GET',
                headers: {'Content-Type': 'application/json'},
                credentials: 'include'
            });

            if (!response.ok) throw new Error('Failed to fetch online users');

            const result = await response.json();
            usersList.innerHTML = '';

            if (result.online && result.online.rows.length > 0) {
                result.online.rows.forEach(user => {
                    const userElement = document.createElement('a');
                    userElement.href = '#';
                    userElement.textContent = user.username;
                    userElement.className = 'user-link';
                    userElement.dataset.username = user.username;
                    userElement.addEventListener('click', (e) => {
                        e.preventDefault();
                    });
                    usersList.appendChild(userElement);
                });
            } else {
                usersList.textContent = "No users online";
            }
        } catch (error) {
            console.error('Error loading online users:', error);
            usersList.textContent = "Error loading users";
        }
    }

    async function initApp() {
        try {
            currentUser = await getCurrentUser();
            
            if (!currentUser) {
                window.location.href = '/';
                return;
            }

            await loadInitialMessages();
            await loadOnlineUsers();

            initSSE();
        } catch (error) {
            console.error('Application initialization error:', error);
            showMessage('Failed to initialize application', 'error');
        }
    }

    logoutBtn.addEventListener('click', async () => {
        const response = await fetch('/api/logout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json'},
            credentials: 'include'
        });
        const result = await response.json();
        if (result.success) {
            window.location.href = '/';
        } else {
            showMessage(result.message || "Logout failed", 'error');
        }
    });

    sendBtn.addEventListener('click', async () => {
        const content = msgInput.value.trim();
        if (!content || !currentUser) {
            showMessage('Message cannot be empty', 'error');
            return;
        }

        try {
            const response = await fetch('/api/messages', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify ({ content })
            });
            
            if (response.ok)
                msgInput.value = '';
            else {
                const error = await response.json();
                showMessage(error.error ||'Failed to send message', 'error');
            }
        } catch (error) {
            console.error('Message send error:', error);
            showMessage('Network error', 'error');
        }
    });

    initApp();
});

