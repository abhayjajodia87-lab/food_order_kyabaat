// Get the registration form
const form = document.getElementById('registerForm');

// This function runs when the form is submitted
form.addEventListener('submit', async function(event) {
    // Stop the form from submitting normally
    event.preventDefault();
    
    // Get all the values from the form
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    // Check if passwords match
    if (password !== confirmPassword) {
        alert('Passwords do not match!');
        return;
    }
    
    // Send the data to the server
    const response = await fetch('/signup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: name,
            email: email,
            password: password
        })
    });
    
    const data = await response.json();
    alert('Registration successful!');
        // Go to login page
        window.location.href = '/login';

    console.log('Server response:', response, response.ok);
    
});