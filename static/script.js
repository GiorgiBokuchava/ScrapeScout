document.addEventListener("DOMContentLoaded", () => {
    // ---- THEME TOGGLE ----
    const toggle = document.getElementById("dark-mode-toggle");
    const circle = document.querySelector(".button-circle");
    const field_submit = document.querySelector(".field-submit");
    const savedTheme = localStorage.getItem("theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const isDarkTheme = savedTheme === "dark" || (!savedTheme && prefersDark);

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

    // ---- PROFILE DROPDOWN ----
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

    // ---- FLASH RINGS ----
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

    // ---- JOBS UI SETUP ----
    const form = document.getElementById("job-form");
    let currentPage = parseInt(form.dataset.page, 10);
    let currentPageSize = parseInt(form.dataset.pageSize, 10);
    const resultsContainer = document.getElementById("results-container");
    const loadingIndicator = document.getElementById("loading");
    const previewPanel = document.getElementById("preview-panel");
    const closePreviewBtn = previewPanel.querySelector(".close-preview");
    let selectedJob = null;

    // Add overlay div
    const overlay = document.createElement('div');
    overlay.className = 'content-overlay';
    document.body.appendChild(overlay);

    // Add filter summary functionality
    function updateFilterSummary(pagination, formData) {
        const resultsCount = document.getElementById('results-count');
        const activeFilters = document.getElementById('active-filters');

        // Update results count
        resultsCount.innerHTML = `<i class="fa fa-list"></i> ${pagination.total_jobs} jobs found`;

        // Get active filters
        const filters = [];
        const region = formData.get('regions');
        const category = formData.get('categories');
        const keyword = formData.get('keyword');

        if (region !== 'ALL') {
            const regionSelect = document.getElementById('regions');
            const regionText = regionSelect.options[regionSelect.selectedIndex].text;
            filters.push(`<span class="filter-tag"><i class="fa fa-map-marker"></i> ${regionText}</span>`);
        }

        if (category !== 'ALL') {
            const categorySelect = document.getElementById('categories');
            const categoryText = categorySelect.options[categorySelect.selectedIndex].text;
            filters.push(`<span class="filter-tag"><i class="fa fa-folder"></i> ${categoryText}</span>`);
        }

        if (keyword) {
            filters.push(`<span class="filter-tag"><i class="fa fa-search"></i> "${keyword}"</span>`);
        }

        activeFilters.innerHTML = filters.length ? filters.join('') : '';
    }

    function updatePaginationControls(pagination) {
        const paginationControls = document.getElementById('pagination-controls');
        const paginationContainer = document.getElementById('pagination');

        if (pagination.total_pages <= 1) {
            paginationControls.style.display = 'none';
            return;
        }

        paginationControls.style.display = 'flex';
        document.getElementById('page-size').value = pagination.page_size;

        let html = '';
        if (pagination.page > 1) html +=
            `<button class="page-link" onclick="updatePage(${pagination.page - 1})">
          <i class="fa fa-chevron-left"></i> Previous
        </button>`;
        html += `<span class="page-info">Page ${pagination.page} of ${pagination.total_pages}</span>`;
        if (pagination.page < pagination.total_pages) html +=
            `<button class="page-link" onclick="updatePage(${pagination.page + 1})">
          Next <i class="fa fa-chevron-right"></i>
        </button>`;

        paginationContainer.innerHTML = html;
    }

    function renderJobResults(jobs) {
        resultsContainer.innerHTML = "";

        jobs.forEach(job => {
            const jobElement = document.createElement('div');
            jobElement.className = 'job-item';
            jobElement.innerHTML = `
                <h3>${job.title}</h3>
                <div class="job-item-details">
                    <span class="job-item-detail">
                        <i class="fa fa-building"></i>
                        ${job.company}
                    </span>
                    <span class="job-item-detail">
                        <i class="fa fa-map-marker"></i>
                        ${job.location}
                    </span>
                    <span class="job-item-detail">
                        <i class="fa fa-calendar"></i>
                        ${job.date_posted}
                    </span>
                </div>
            `;

            jobElement.addEventListener('click', async () => {
                // Store current job data
                selectedJob = job;
                // Show preview for this job
                showJobPreview(job, jobElement);
            });
            resultsContainer.appendChild(jobElement);
        });
    }

    async function fetchJobDetails(url) {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 second timeout

            const csrfToken = document
                .querySelector('meta[name="csrf-token"]')
                .getAttribute('content');

            const response = await fetch('/get_description', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,       // Flask-WTF default header name
                    'X-CSRF-Token': csrfToken       // Just in case
                },
                body: JSON.stringify({ url }),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                console.error('Bad status:', response.status, await response.text());
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            if (data.error) {
                throw new Error(data.error);
            }

            return {
                description: data.description,
                email: data.email,
                error: null
            };
        } catch (error) {
            console.error('Error fetching job details:', error);
            let errorMessage = 'Failed to load job description. Please try again later.';

            if (error.name === 'AbortError') {
                errorMessage = 'Request timed out. Please try again.';
            }

            return {
                description: null,
                email: null,
                error: errorMessage
            };
        }
    }

    async function showJobPreview(job, jobElement) {
        // Remove selected class from previous selection
        const previousSelected = document.querySelector('.job-item.selected');
        if (previousSelected) {
            previousSelected.classList.remove('selected');
        }

        // Add selected class to current selection
        jobElement.classList.add('selected');

        // Show preview panel and overlay immediately
        const previewPanel = document.getElementById('preview-panel');
        const overlay = document.querySelector('.content-overlay');
        previewPanel.classList.add('show');
        overlay.classList.add('show');

        // Update preview content with initial job data and skeleton loader
        const previewContent = document.querySelector('.preview-content');
        previewContent.innerHTML = `
            <div class="preview-title">
                <h1>${job.title}</h1>
            </div>
            <div class="company">
                <i class="fa fa-building"></i>
                ${job.company}
            </div>
            <div class="metadata">
                <div class="metadata-item">
                    <i class="fa fa-map-marker"></i>
                    ${job.location}
                </div>
                <div class="metadata-item">
                    <i class="fa fa-folder"></i>
                    ${job.category}
                </div>
                <div class="metadata-item">
                    <i class="fa fa-calendar"></i>
                    ${job.date_posted}
                </div>
            </div>
            <div class="actions">
                <a href="${job.url}" target="_blank" class="action-btn primary-btn">
                    <i class="fa fa-external-link"></i>
                    View Job
                </a>
                <button class="action-btn secondary-btn">
                    <i class="fa fa-bookmark"></i>
                    Save Job
                </button>
            </div>
            <div class="description">
                ${showSkeletonLoader()}
            </div>
        `;

        // Set up save button functionality
        setupSaveButton(previewContent, job);

        // Fetch and update description and email
        const { description, email, error } = await fetchJobDetails(job.url);
        const descriptionElement = previewContent.querySelector('.description');

        if (error) {
            descriptionElement.innerHTML = `
                <div class="error-message" style="color: var(--color-error); padding: 1rem;">
                    <i class="fa fa-exclamation-circle"></i>
                    ${error}
                </div>`;
        } else {
            job.description = description;
            job.email = email ? email.replace(/[\s\n\r]+/g, '').trim() : 'N/A';

            const emailHtml = job.email && job.email !== 'N/A' ?
                `<div class="email-item" title="Click to copy email"><i class="fa fa-envelope"></i>${job.email}</div>` : '';

            descriptionElement.innerHTML = emailHtml + (description || 'No description available');

            // Add copy functionality to email item
            const emailItem = descriptionElement.querySelector('.email-item');
            if (emailItem) {
                emailItem.addEventListener('click', async () => {
                    try {
                        await navigator.clipboard.writeText(job.email);
                        const originalContent = emailItem.innerHTML;
                        emailItem.innerHTML = '<i class="fa fa-check"></i> Copied!';
                        emailItem.classList.add('copied');
                        setTimeout(() => {
                            emailItem.innerHTML = originalContent;
                            emailItem.classList.remove('copied');
                        }, 2000);
                    } catch (err) {
                        console.error('Failed to copy email:', err);
                    }
                });
            }
        }
    }

    function setupSaveButton(previewContent, job) {
        const saveBtn = previewContent.querySelector('.secondary-btn');
        saveBtn.addEventListener('click', async () => {
            saveBtn.disabled = true;
            saveBtn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Saving...';

            try {
                const response = await fetch('/save_job', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url: job.url }),
                });

                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }

                saveBtn.innerHTML = '<i class="fa fa-check"></i> Saved';
                saveBtn.style.backgroundColor = 'var(--color-primary)';
                saveBtn.style.color = 'white';
            } catch (err) {
                console.error('Error saving job:', err);
                saveBtn.innerHTML = '<i class="fa fa-exclamation-triangle"></i> Error';
                saveBtn.disabled = false;
            }
        });
    }

    function showSkeletonLoader() {
        return `
            <div class="skeleton-loading">
                <div class="skeleton-text"></div>
                <div class="skeleton-text"></div>
                <div class="skeleton-text"></div>
                <div class="skeleton-text"></div>
                <div class="skeleton-text"></div>
                <div class="skeleton-text"></div>
                <div class="skeleton-text"></div>
                <div class="skeleton-text"></div>
                <div class="skeleton-text"></div>
                <div class="skeleton-text"></div>
            </div>
        `;
    }

    // Close preview panel
    function closePreview() {
        previewPanel.classList.remove('show');
        overlay.classList.remove('show');
        const selectedItem = document.querySelector('.job-item.selected');
        if (selectedItem) {
            selectedItem.classList.remove('selected');
        }
        selectedJob = null;
    }

    if (closePreviewBtn) {
        closePreviewBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            closePreview();
        });
    }

    // Close preview panel when clicking outside
    document.addEventListener('click', (event) => {
        if (previewPanel.classList.contains('show') &&
            !previewPanel.contains(event.target) &&
            !event.target.closest('.job-item')) {
            closePreview();
        }
    });

    // Close preview panel when pressing Escape key
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && previewPanel.classList.contains('show')) {
            closePreview();
        }
    });

    // Navbar hide/show on scroll
    let lastScrollY = 0;
    const navbar = document.querySelector('.nav-container');

    window.addEventListener("scroll", () => {
        let scrollTop = window.scrollY || document.documentElement.scrollTop;

        if (scrollTop > lastScrollY) {
            // Scrolling down
            navbar.style.top = `-${navbar.offsetHeight}px`;
        } else {
            // Scrolling up
            navbar.style.top = "0";
        }

        lastScrollY = scrollTop <= 0 ? 0 : scrollTop; // Fix for Safari
    });

    async function submitSearch() {
        loadingIndicator.style.display = 'block';
        const formData = new FormData(form);
        formData.append('page', currentPage);
        formData.append('page_size', currentPageSize);

        try {
            const res = await fetch('/jobs', {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            const data = await res.json();
            loadingIndicator.style.display = 'none';

            if (data.error) return console.error(data.error);

            renderJobResults(data.jobs);
            updatePaginationControls(data.pagination);
            updateFilterSummary(data.pagination, formData);
        } catch (err) {
            console.error('Fetch error', err);
            loadingIndicator.style.display = 'none';
        }
    }

    // Expose pagination controls
    window.updatePage = page => { currentPage = page; submitSearch(); };
    window.updatePageSize = size => { currentPageSize = parseInt(size, 10); currentPage = 1; submitSearch(); };

    // Event bindings
    form.addEventListener('submit', e => { e.preventDefault(); currentPage = 1; submitSearch(); });
    closePreviewBtn.addEventListener('click', () => {
        previewPanel.classList.remove('show');
        overlay.classList.remove('show');
    });
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