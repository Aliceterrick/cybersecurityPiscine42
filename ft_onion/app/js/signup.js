document.addEventListener('DOMContentLoaded', () => {
    const signForm = document.getElementById('signForm');
    const messageDiv = document.getElementById('message');
    
    function showMessage(msg, className) {
        messageDiv.textContent = msg;
        messageDiv.className = className;
    }
    
    signForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('pseudo').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        
        if (password !== confirmPassword) {
            showMessage('Passwords do not match', 'error');
            return;
        }
        
        const response = await fetch('/api/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
        });
        const result = await response.json();

        if (result.success) {
            showMessage('Account created successfully!', 'success');
            window.location.href = '/';
        } else {
            showMessage(result.message, 'error');
        }
    });
        
});