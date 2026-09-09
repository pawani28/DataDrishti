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

loginForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = passwordInput.value;

    loginMessage.textContent = "Logging in...";


    try {

        const response = await fetch("http://127.0.0.1:5000/login", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                email: email,
                password: password
            })

        });


        const data = await response.json();


        if (response.ok) {

            loginMessage.textContent = "Login successful!";

            localStorage.setItem("userEmail", email);


            setTimeout(() => {

                window.location.href = "dashboard.html";

            }, 700);


        } else {

            loginMessage.textContent =
                data.message || "Invalid email or password.";

        }


    } catch (error) {

        console.error("Login Error:", error);

        loginMessage.textContent =
            "Unable to connect to server.";

    }

});