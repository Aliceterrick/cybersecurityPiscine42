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
    console.log('here0');
    const result = await response.json();
    console.log('here');
    if (result.success) {
        console.log('here&');
        window.location.href = '/home';
    } else {
        console.log('here2');
        showMessage(result.message, 'error');
    }
    console.log('here3');
    });
});