document.addEventListener('DOMContentLoaded', () => {
    const logForm = document.getElementById('logForm');
    const messageDiv = document.getElementById('message');

    function showMessage(msg, className) {
        messageDiv.textContent = msg;
        messageDiv.className = className;
    }
    
    logForm.addEventListener('submit', async (e) => { 
        e.preventDefault();
        
        const pseudo = document.getElementById('pseudo').value;
        const password = document.getElementById('password').value;

        const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json'},
        body: JSON.stringify({pseudo, password})
        });
        const result = await response.json();
        if (result.success) {
            window.location.href = '/home';
        } else {
            showMessage(result.message, 'error');
        }
    });
});