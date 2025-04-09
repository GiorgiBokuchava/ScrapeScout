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
});

