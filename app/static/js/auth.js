let isSignUpMode = false;

document.addEventListener('DOMContentLoaded', function() {
    const authForm = document.getElementById('auth-form');
    const toggleLink = document.getElementById('toggle-link');
    const authContainer = document.querySelector('.auth-container');
    const submitBtn = document.getElementById('submit-btn');
    const submitText = document.getElementById('submit-text');
    const loadingSpinner = document.getElementById('loading-spinner');
    const emailField = document.getElementById('email');
    const usernameField = document.getElementById('username');
    const passwordField = document.getElementById('password');
    const passwordToggle = document.getElementById('password-toggle');
    const authTitle = document.getElementById('auth-title');
    const authSubtitle = document.getElementById('auth-subtitle');
    const authFooterText = document.getElementById('auth-footer-text');
    const formOptions = document.getElementById('form-options');
    const toast = document.getElementById('message-toast');
    const toastMessage = document.getElementById('toast-message');

    // Initialize as login mode
    authContainer.classList.add('login-mode');
    emailField.removeAttribute('required');

    // Toggle between login and signup
    toggleLink.addEventListener('click', function(e) {
        e.preventDefault();
        isSignUpMode = !isSignUpMode;
        
        if (isSignUpMode) {
            // Switch to signup mode
            authContainer.classList.remove('login-mode');
            authContainer.classList.add('signup-mode');
            authTitle.textContent = 'Create Account';
            authSubtitle.textContent = 'Sign up to start your fitness journey';
            submitText.textContent = 'Sign Up';
            authFooterText.innerHTML = 'Already have an account? <a href="#" id="toggle-link">Sign In</a>';
            emailField.setAttribute('required', 'required');
            formOptions.style.display = 'none';
        } else {
            // Switch to login mode
            authContainer.classList.remove('signup-mode');
            authContainer.classList.add('login-mode');
            authTitle.textContent = 'Welcome Back';
            authSubtitle.textContent = 'Sign in to continue your fitness journey';
            submitText.textContent = 'Sign In';
            authFooterText.innerHTML = 'Don\'t have an account? <a href="#" id="toggle-link">Sign Up</a>';
            emailField.removeAttribute('required');
            formOptions.style.display = 'flex';
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

        // Prepare data
        const formData = {
            username: usernameField.value.trim(),
            password: passwordField.value
        };

        if (isSignUpMode) {
            formData.email = emailField.value.trim().toLowerCase();
        } else {
            // For login, use username as email (Supabase uses email for login)
            formData.email = usernameField.value.trim().toLowerCase();
        }

        // Show loading state
        setLoadingState(true);

        try {
            const endpoint = isSignUpMode ? '/auth/register' : '/auth/login';
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (response.ok) {
                // Success
                showToast(
                    isSignUpMode ? 'Account created successfully!' : 'Login successful!',
                    'success'
                );
                
                // Store user info
                if (data.user) {
                    sessionStorage.setItem('username', data.user.username || formData.username);
                    sessionStorage.setItem('user_id', data.user.id);
                    sessionStorage.setItem('email', data.user.email);
                }

                // Redirect after short delay
                setTimeout(() => {
                    window.location.href = '/chat';
                }, 1500);
            } else {
                // Error
                showToast(data.error || 'An error occurred. Please try again.', 'error');
                setLoadingState(false);
            }
        } catch (error) {
            console.error('Error:', error);
            showToast('Network error. Please check your connection and try again.', 'error');
            setLoadingState(false);
        }
    });

    // Google login button
    const googleBtn = document.getElementById('google-btn');
    if (googleBtn) {
        googleBtn.addEventListener('click', function() {
            showToast('Google login coming soon!', 'error');
        });
    }

    // Validation functions
    function validateEmail() {
        const email = emailField.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const errorEl = document.getElementById('email-error');

        if (!email) {
            showFieldError('email-error', 'Email is required');
            return false;
        }

        if (!emailRegex.test(email)) {
            showFieldError('email-error', 'Please enter a valid email address');
            return false;
        }

        clearFieldError('email-error');
        return true;
    }

    function validateUsername() {
        const username = usernameField.value.trim();
        const usernameRegex = /^[a-zA-Z0-9_-]{3,}$/;
        const errorEl = document.getElementById('username-error');

        if (!username) {
            showFieldError('username-error', 'Username is required');
            return false;
        }

        if (username.length < 3) {
            showFieldError('username-error', 'Username must be at least 3 characters');
            return false;
        }

        if (!usernameRegex.test(username)) {
            showFieldError('username-error', 'Username can only contain letters, numbers, underscores, and hyphens');
            return false;
        }

        clearFieldError('username-error');
        return true;
    }

    function validatePassword() {
        const password = passwordField.value;
        const errorEl = document.getElementById('password-error');

        if (!password) {
            showFieldError('password-error', 'Password is required');
            return false;
        }

        if (password.length < 6) {
            showFieldError('password-error', 'Password must be at least 6 characters');
            return false;
        }

        clearFieldError('password-error');
        return true;
    }

    function showFieldError(errorId, message) {
        const errorEl = document.getElementById(errorId);
        if (errorEl) {
            errorEl.textContent = message;
        }
    }

    function clearFieldError(errorId) {
        const errorEl = document.getElementById(errorId);
        if (errorEl) {
            errorEl.textContent = '';
        }
    }

    function clearErrors() {
        const errorElements = document.querySelectorAll('.error-text');
        errorElements.forEach(el => {
            el.textContent = '';
        });
    }

    function setLoadingState(loading) {
        if (loading) {
            submitBtn.disabled = true;
            submitText.style.display = 'none';
            loadingSpinner.style.display = 'inline-block';
        } else {
            submitBtn.disabled = false;
            submitText.style.display = 'inline';
            loadingSpinner.style.display = 'none';
        }
    }

    function showToast(message, type = 'success') {
        toastMessage.textContent = message;
        toast.className = `message-toast ${type} show`;
        
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
});
