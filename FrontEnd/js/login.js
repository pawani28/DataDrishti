const loginForm = document.getElementById("loginForm");
const loginMessage = document.getElementById("loginMessage");

const passwordInput = document.getElementById("password");
const togglePassword = document.getElementById("togglePassword");


// Show / Hide Password

togglePassword.addEventListener("click", function () {

    if (passwordInput.type === "password") {

        passwordInput.type = "text";

        togglePassword.classList.remove("fa-eye");
        togglePassword.classList.add("fa-eye-slash");

    } else {

        passwordInput.type = "password";

        togglePassword.classList.remove("fa-eye-slash");
        togglePassword.classList.add("fa-eye");

    }

});


// Login Form
// NOTE: the Flask backend has no authentication route yet, so this is a front-end
// only sign-in (it just remembers the email and opens the dashboard).
// When a real /api/login endpoint exists, call it here instead.

loginForm.addEventListener("submit", function (event) {

    event.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = passwordInput.value;

    if (!email || !password) {
        loginMessage.textContent = "Please enter your email and password.";
        return;
    }

    localStorage.setItem("userEmail", email);

    loginMessage.textContent = "Login successful!";

    setTimeout(() => {
        window.location.href = "dashboard.html";
    }, 500);

});
