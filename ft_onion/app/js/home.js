document.addEventListener('DOMContentLoaded', () => {
    const logoutBtn = document.getElementById('logout');
    const usersList = document.getElementById('users-list');
    const chatMsgs = document.getElementById('chat-messages');
    const msgInput = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-button');


    async function loadOnlineUsers() {
        const response = await fetch ('/api/get_online', {
            method: 'GET',
            headers: {'Content-Type': 'application/json'},
        });
        if (!response.ok)
            showMessage('failed to fetch online users', 'error');
        else {
            const result = await response.json();
            usersList.innerHTML = '';
            if (result.online && result.online.rows.length > 0) {
                result.online.rows.forEach(user => {
                    const userElement = document.createElement('a');
                    userElement.href = '#';
                    userElement.textContent = user.username;
                    userElement.className = 'user-link';
                    userElement.dataset.username = user.username;
                    usersList.appendChild(userElement);
                });
            } else 
                usersList.textContent = "No connected user";
        }
    }

    logoutBtn.addEventListener('click', async () => {
        const response = await fetch('/api/logout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json'},
        credentials: 'include'
        });
        const result = await response.json();
        if (result.success)
            window.location.href = '/';
        else
            showMessage(result.message || "Logout failed", 'error')
    });



    async function loadMessages() {
        try {
            const response = await fetch('/api/messages', {
                credentials: 'include'
            });
            const messages = await response.json();
            renderMessages(messages);
        } catch (error) {
            console.error('Failed to load messages:', error);
        }
    }

    function renderMessages(messages) {
        chatMsgs.innerHTML = '';
        
        messages.forEach(msg => {
            const messageElement = document.createElement('div');
            messageElement.className = 'message';

            const curUser = JSON.parse(localStorage.getItem('user'));
            const isCurUser = curUser && curUser.username === msg.username;
            if (isCurUser)
                messageElement.classList.add('message-self');
            
            const header = document.createElement('div');
            header.innerHTML = `<strong>${msg.username}</strong> 
                                <span>${new Date(msg.created_at).toLocaleTimeString()}</span>`;
            
            const content = document.createElement('div');
            content.className = 'message-content';
            content.textContent = msg.content;
            
            messageElement.appendChild(header);
            messageElement.appendChild(content);
            chatMsgs.appendChild(messageElement);
        });
        
        chatMsgs.scrollTop = chatMsgs.scrollHeight;
    }

    async function sendMessage() {
        const content = msgInput.value.trim();
        if (!content) return;
        
        try {
            const response = await fetch('/api/messages', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ content })
            });
            
            if (response.ok) {
                msgInput.value = '';
                loadMessages();
            } else {
                const error = await response.json();
                showMessage(error.error || 'Failed to send message', 'error');
            }
        } catch (error) {
            console.error('Message send error:', error);
            showMessage('Network error', 'error');
        }
    }
    
    sendBtn.addEventListener('click', sendMessage);
    msgInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
    
    loadOnlineUsers();
    loadMessages();
    setInterval(loadMessages, 5000);
});