document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.getElementById("dark-mode-toggle");
    const circle = document.querySelector(".button-circle");
    const field_submit = document.querySelector(".field-submit");
    const savedTheme = localStorage.getItem("theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const isDarkTheme = savedTheme === "dark" || (!savedTheme && prefersDark);

    // Set the toggle switch state
    if (toggle) {
        toggle.checked = isDarkTheme;
    }

    // Toggle theme on checkbox change
    toggle.addEventListener("change", () => {
        if (toggle.checked) {
            document.documentElement.setAttribute("data-theme", "dark");
            localStorage.setItem("theme", "dark");
        } else {
            document.documentElement.setAttribute("data-theme", "light");
            localStorage.setItem("theme", "light");
        }
    });

    // Circle animation
    if (circle && field_submit) {
        document.body.addEventListener("mousemove", (e) => {
            const circleLeft = e.pageX - field_submit.offsetLeft - 15;
            const circleTop = e.pageY - field_submit.offsetTop - 15;
            circle.style.left = `${circleLeft}px`;
            circle.style.top = `${circleTop}px`;
        });
    }

    const dropdownBtn = document.getElementById('profile-btn');
    const dropdownMenu = document.getElementById('dropdown-menu');

    // Toggle dropdown menu on button click
    dropdownBtn.addEventListener('click', (event) => {
        event.stopPropagation(); // Prevent the click from bubbling up to the document
        dropdownMenu.classList.toggle('show');
    });

    // Close the dropdown if clicked outside
    document.addEventListener('click', (event) => {
        // Check if the click target is not inside the dropdown menu or button
        if (!dropdownMenu.contains(event.target) && !dropdownBtn.contains(event.target)) {
            dropdownMenu.classList.remove('show');
        }
    });

    // Optional: Close the dropdown when pressing the Escape key
    document.addEventListener('keydown', (event) => {
        if (event.key === "Escape") {
            dropdownMenu.classList.remove('show');
        }
    });
});

