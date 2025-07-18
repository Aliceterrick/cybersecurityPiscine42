async function checkAuth () {
    const response = await fetch('/api/auth/status', {
        credentials: 'include'
    });
    const data = await response.json();

    if (!data.authenticated) {
        redirectToLogin();
    }
}

function redirectToLogin() {
    window.location.href = '/';
}

document.addEventListener('DOMContentLoaded', () => {
    const protectedPages = ['/home'];
    if (protectedPages.some(page => window.location.pathname.endsWith(page))) {
        checkAuth();
    }
});