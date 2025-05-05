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
    }

    // Submit button circle animation
    if (circle && field_submit) {
        document.body.addEventListener("mousemove", (e) => {
            const circleLeft = e.pageX - field_submit.offsetLeft - 15;
            const circleTop = e.pageY - field_submit.offsetTop - 15;
            circle.style.left = `${circleLeft}px`;
            circle.style.top = `${circleTop}px`;
        });
    }

    // Dropdown menu for profile button
    const profileBtn = document.getElementById('profile-btn');
    const dropdownMenu = document.getElementById('dropdown-menu');

    if (profileBtn && dropdownMenu) {
        // Toggle dropdown menu on button click
        profileBtn.addEventListener('click', (event) => {
            event.stopPropagation(); // Prevent the click from bubbling up to the document
            dropdownMenu.classList.toggle('show');
        });

        // Close the dropdown if clicked outside
        document.addEventListener('click', (event) => {
            // Check if the click target is not inside the dropdown menu or button
            if (!dropdownMenu.contains(event.target) && !profileBtn.contains(event.target)) {
                dropdownMenu.classList.remove('show');
            }
        });

        // Optional: Close the dropdown when pressing the Escape key
        document.addEventListener('keydown', (event) => {
            if (event.key === "Escape") {
                dropdownMenu.classList.remove('show');
            }
        });
    }

    // Progress ring for flash messages
    const flashMessages = document.querySelectorAll('.flash-message');

    flashMessages.forEach((flash) => {
        // Look for the progress ring inside the flash message
        const progressRing = flash.querySelector('.progress-ring');
        if (!progressRing) {
            console.log("Progress ring not found for a flash message.");
            return;
        }

        // Timer settings per flash message
        const totalDuration = 3000; // duration in ms
        const intervalTime = 10; // update interval in ms
        const steps = totalDuration / intervalTime;
        const decrement = 360 / steps;
        let angle = 360;
        let timer;

        function updateRing() {
            angle -= decrement;
            if (angle <= 0) {
                angle = 0;
                clearInterval(timer);
                flash.style.display = 'none';
            }
            progressRing.style.setProperty('--angle', angle + 'deg');
        }

        function startTimer() {
            clearInterval(timer);
            timer = setInterval(updateRing, intervalTime);
        }

        // Start timer for this flash message
        startTimer();

        // Pause the timer on hover
        flash.addEventListener('mouseenter', function () {
            clearInterval(timer);
            angle = 365; // Reset slightly above full to ensure display update
            updateRing();
        });

        // Resume the timer when the mouse leaves
        flash.addEventListener('mouseleave', function () {
            startTimer();
        });
    });

    // Load scraped jobs
    const jobForm = document.getElementById("job-form");
    if (jobForm) {
        // Handle search submission
        document.getElementById("job-form").addEventListener("submit", async function (event) {
            event.preventDefault(); // Prevent a full page reload

            // Show the loading indicator
            document.getElementById("loading").style.display = "block";
            document.getElementById("results-container").innerHTML = "";

            // Gather form data, including the hidden CSRF token
            const formData = new FormData(event.target);

            try {
                // Send a POST request to /jobs with the form data
                const response = await fetch("/jobs", {
                    method: "POST",
                    body: formData
                });

                // Parse the JSON response
                const data = await response.json();
                console.log("Response data:", data);

                // Hide the loader
                document.getElementById("loading").style.display = "none";

                // Build the HTML
                if (data.jobs && data.jobs.length > 0) {
                    let html = "<h2>Showing up to 10 Jobs:</h2><ul>";
                    data.jobs.forEach(job => {
                        html += `
          <li style="margin: 15px 0;">
            <h3>${job.title}</h3>
            <p>Company: ${job.company}</p>
            <p>Posted: ${job.posted_time}</p>
            <p>Email: ${job.email}</p>
            <p>Description: ${job.description.slice(0, 100)}...</p>
            <a href="${job.url}" target="_blank">View Listing</a>
          </li>
        `;
                        console.log(job);
                    });
                    html += "</ul>";
                    document.getElementById("results-container").innerHTML = html;
                } else if (data.error) {
                    // If there's an error, show it (like a missing CSRF token)
                    document.getElementById("results-container").innerHTML =
                        `<p>Error: ${JSON.stringify(data.error)}</p>`;
                } else {
                    // No jobs found
                    document.getElementById("results-container").innerHTML = "<p>No jobs found. Try adjusting your search.</p>";
                }

            } catch (err) {
                console.error("Error or Exception in fetch:", err);
                document.getElementById("loading").style.display = "none";
                document.getElementById("results-container").innerHTML =
                    "<p>Something went wrong. Check console for details.</p>";
            }
        });
    }
});


console.log(`                                                                                
                             ./%@@@@@@@@@@@@@@%*                                
                       @@@@@@@@@@@@@@@@@(@@@@@@@@@@@@@*                         
                  *@@@@@@#  %@@@@    @@@(    @@@@  ,&@@@@@&                     
               %@@@@@     *@@@(      @@@(      @@@@     ,@@@@@.                 
            *@@@@#       @@@@        @@@(        @@@(       @@@@@               
          %@@@@         @@@@         @@@(         @@@#         @@@@             
        #@@@@@@%,      @@@%          @@@(          @@@#      /&@@@@@@           
       @@@@  (@@@@@@@@@@@@(,.        @@@(        .,(@@@@@@@@@@@@*  @@@@         
     ,@@@.          .*@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*.          %@@@        
    (@@@             @@@*            @@@(            .   %           .@@@       
   ,@@@              @@@             @@@(          *@@@@@@@           /@@@      
   @@@,             (@@&             @@@(     #@@@@@@@@@@@@@           @@@&     
  (@@@              @@@.                .&@@@@@@@@@@@@@@@@@@@           @@@     
  @@@#              @@@            /@@@@@@@@@@@@@@@@@@@@@@@@@(          @@@     
  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@  @@@@@@@@@@@@@@@@@@@@@@@@@@  @@@@@@@@@@@#    
  @@@*,,,,,,,,,,,,,,@@@              @@@@@@@@@@@@@@@@@@@@@@@@@&         @@@/    
  @@@&              @@@                @@@@@@@@@@@@@@@@@@@@@@@@         @@@     
  .@@@              @@@(             @  %@@@@@@@@@@@@@@@@@@@@@@        *@@@     
   @@@@             (@@@             @@@  @@@@@@@@@@@@@@@@@@@@@,       @@@      
    @@@#             @@@             @@@,   @@@@@@@@@@@@@@@@@@@/      @@@#      
     @@@%            @@@@    *#&&@@@@@@@@@@@  .@@@@@@@@@@@@@@@@,     @@@%       
      @@@@      .(@@@@@@@@@@@@@@@@@@&@@@&@@@@@&  &@@@@@@@@@@@@@    .@@@*        
       *@@@@@@@@@@@@,  @@@           @@@(           @@@@@@@@/  / .@@@@          
         &@@@%         ,@@@          @@@(         .@  %(  *@@@@@@  @.           
           &@@@@        .@@@         @@@(        /@@@   @@@@@@@@@@              
             .@@@@@.      @@@&       @@@(       @@@@     @@@@@@@@@@#            
                .@@@@@@    #@@@#     @@@(     @@@@    (@  @@@@@@@@@@@           
                    *@@@@@@@%%@@@@,  @@@(  /@@@@(@@@@@@@&  @@@@@@@@@@@          
                          &@@@@@@@@@@@@@@@@@@@@@@@@/        @@@@@@@@@@@*        
                                      ...                    %@@@@@@@@@@&       
                                                              (@@@@@@@@@@@      
                                                               ,@@@@@   @@@     
                                                                 @@@@@@@@@      
                                                                  .%@@#.        
                                                                                
`)