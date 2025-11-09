
// paras

// Get form elements
const form = document.getElementById('loginForm');
const loginButton = document.getElementById('loginButton');

// Handle form submission
form.addEventListener('submit', async function (e) {
    e.preventDefault();  // Prevent default form submission
    
    // Get form values
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    console.log(email, password);
    
    // Send data to server
    const response = await fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            email: email, 
            password: password 
        })
    });

    const data = await response.json();
    const errorAlert = document.getElementById('errorAlert');

    if (response.ok) {
        errorAlert.classList.add('d-none');
        window.location.href = '/dashboard';
    } else {
        errorAlert.textContent = data.message || "Login failed. Please check your credentials.";
        errorAlert.classList.remove('d-none');
    }
});

// Function to switch to register page
function switchToRegister() {
    window.location.href = "/register";
}
