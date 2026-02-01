let isSignUpMode = false;

document.addEventListener('DOMContentLoaded', function() {
    const authForm = document.getElementById('auth-form');
    const toggleLink = document.getElementById('toggle-link');
    const toggleText = document.getElementById('toggle-text');
    const submitBtn = document.getElementById('submit-btn');
    const emailField = document.getElementById('email');
    const authPanel = document.querySelector('.auth-panel');
    const errorMessage = document.getElementById('error-message');

    // Toggle between login and signup
    toggleLink.addEventListener('click', function(e) {
        e.preventDefault();
        isSignUpMode = !isSignUpMode;
        
        if (isSignUpMode) {
            authPanel.classList.remove('login-mode');
            authPanel.classList.add('signup-mode');
            toggleText.innerHTML = 'Already have an account? <a href="#" id="toggle-link">Sign in</a>';
            submitBtn.textContent = 'Sign Up';
            emailField.required = true;
        } else {
            authPanel.classList.remove('signup-mode');
            authPanel.classList.add('login-mode');
            toggleText.innerHTML = 'Don\'t have an account, <a href="#" id="toggle-link">Sign up</a>';
            submitBtn.textContent = 'Sign In';
            emailField.required = false;
        }
        
        // Re-attach event listener to new toggle link
        document.getElementById('toggle-link').addEventListener('click', arguments.callee);
        errorMessage.classList.remove('show');
    });

    // Initialize as login mode
    authPanel.classList.add('login-mode');
    // Set initial state - email not required in login mode
    emailField.required = false;

    // Form submission
    authForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        errorMessage.classList.remove('show');

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const email = document.getElementById('email').value;

        // Validate required fields
        if (!username || !password) {
            showError('Username and password are required');
            return;
        }

        if (isSignUpMode && !email) {
            showError('Please enter your email');
            return;
        }

        try {
            const endpoint = isSignUpMode ? '/auth/register' : '/auth/login';
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: username,
                    password: password,
                    email: email
                })
            });

            const data = await response.json();

            if (response.ok) {
                // Store username in sessionStorage for chat page
                sessionStorage.setItem('username', username);
                // Redirect to chat page
                window.location.href = '/chat';
            } else {
                showError(data.error || 'An error occurred');
            }
        } catch (error) {
            showError('Network error. Please try again.');
            console.error('Error:', error);
        }
    });

    // Google login button
    document.getElementById('google-btn').addEventListener('click', function() {
        showError('Google login not yet implemented');
    });

    // Phone signup button
    document.getElementById('phone-btn').addEventListener('click', function() {
        showError('Phone signup not yet implemented');
    });

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.add('show');
    }
});

