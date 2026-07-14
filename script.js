// ===============================
// DataDrishti AI - script.js
// ===============================

// Navbar Shadow
window.addEventListener("scroll", () => {

    const nav = document.querySelector("nav");

    if (window.scrollY > 50) {

        nav.style.background = "rgba(15,23,42,0.95)";
        nav.style.boxShadow = "0 8px 25px rgba(0,0,0,0.3)";

    } else {

        nav.style.background = "rgba(255,255,255,0.05)";
        nav.style.boxShadow = "none";

    }

});


// ===============================
// Smooth Scroll
// ===============================

document.querySelectorAll('a[href^="#"]').forEach(anchor => {

    anchor.addEventListener("click", function (e) {

        e.preventDefault();

        const target = document.querySelector(this.getAttribute("href"));

        if (target) {

            target.scrollIntoView({

                behavior: "smooth"

            });

        }

    });

});


// ===============================
// Reveal Animation
// ===============================

const revealElements = document.querySelectorAll(".feature-box, .glass-card");

function reveal() {

    revealElements.forEach(el => {

        const top = el.getBoundingClientRect().top;

        const windowHeight = window.innerHeight;

        if (top < windowHeight - 100) {

            el.style.opacity = "1";
            el.style.transform = "translateY(0)";

        }

    });

}

window.addEventListener("scroll", reveal);
reveal();


// ===============================
// Counter Animation
// ===============================

const counters = document.querySelectorAll(".card span");

counters.forEach(counter => {

    const text = counter.innerText;

    const number = parseInt(text.replace(/[^0-9]/g, ""));

    if (!isNaN(number)) {

        let count = 0;

        const speed = Math.ceil(number / 60);

        const update = () => {

            count += speed;

            if (count >= number) {

                counter.innerText = text;

            } else {

                counter.innerText = count;

                requestAnimationFrame(update);

            }

        };

        update();

    }

});


// ===============================
// Button Ripple Effect
// ===============================

document.querySelectorAll(".primary-btn, .secondary-btn").forEach(btn => {

    btn.addEventListener("click", function (e) {

        const ripple = document.createElement("span");

        ripple.classList.add("ripple");

        const rect = this.getBoundingClientRect();

        ripple.style.left = (e.clientX - rect.left) + "px";
        ripple.style.top = (e.clientY - rect.top) + "px";

        this.appendChild(ripple);

        setTimeout(() => {

            ripple.remove();

        }, 600);

    });

});


// ===============================
// Typing Effect
// ===============================

const title = document.querySelector(".hero-left h1 span");

const words = [
    "AI Data Analyst",
    "Business Intelligence",
    "Smart Insights",
    "Data Visualization"
];

let wordIndex = 0;
let charIndex = 0;
let deleting = false;

function typeEffect() {

    if (!title) return;

    const current = words[wordIndex];

    if (!deleting) {

        title.textContent = current.substring(0, charIndex++);

        if (charIndex > current.length) {

            deleting = true;

            setTimeout(typeEffect, 1200);

            return;

        }

    } else {

        title.textContent = current.substring(0, charIndex--);

        if (charIndex < 0) {

            deleting = false;

            wordIndex = (wordIndex + 1) % words.length;

        }

    }

    setTimeout(typeEffect, deleting ? 60 : 120);

}

typeEffect();


// ===============================
// Glass Card Tilt
// ===============================

const glass = document.querySelector(".glass-card");

if (glass) {

    glass.addEventListener("mousemove", (e) => {

        const rect = glass.getBoundingClientRect();

        const x = e.clientX - rect.left;

        const y = e.clientY - rect.top;

        const rotateY = ((x / rect.width) - 0.5) * 15;

        const rotateX = ((y / rect.height) - 0.5) * -15;

        glass.style.transform =
            `rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;

    });

    glass.addEventListener("mouseleave", () => {

        glass.style.transform =
            "rotateX(0deg) rotateY(0deg)";

    });

}