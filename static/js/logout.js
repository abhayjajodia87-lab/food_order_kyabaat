// pabisa


// Simple logout function for beginners
function logout() {
    // Send a request to the server to end the session
    fetch('/logout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.ok) {
            // If logout successful, redirect to login page
            window.location.href = '/login';
        }
    });
}