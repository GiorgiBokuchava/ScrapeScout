// static/script.js

// ---- Helper Functions ----

// Fetch job description & email from server
async function fetchJobDetails(url) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000);
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    try {
        const res = await fetch('/get_description', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-CSRF-Token': csrfToken
            },
            body: JSON.stringify({ url }),
            signal: controller.signal
        });
        clearTimeout(timeoutId);

        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        if (data.error) throw new Error(data.error);
        return data;
    } catch (err) {
        clearTimeout(timeoutId);
        console.error('Error fetching job details:', err);
        throw err;
    }
}

// A simple skeleton loader markup
function showSkeletonLoader() {
    return `
      <div class="skeleton-loading">
        <div class="skeleton-text"></div>
        <div class="skeleton-text"></div>
        <div class="skeleton-text"></div>
        <div class="skeleton-text"></div>
        <div class="skeleton-text"></div>
      </div>
    `;
}

// ---- UI Initializers ----

function initThemeToggle() {
    const toggle = document.getElementById("dark-mode-toggle");
    const circle = document.querySelector(".button-circle");
    const fieldSubmit = document.querySelector(".field-submit");
    const saved = localStorage.getItem("theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const isDark = saved === "dark" || (!saved && prefersDark);

    if (toggle) {
        toggle.checked = isDark;
        toggle.addEventListener("change", () => {
            const theme = toggle.checked ? "dark" : "light";
            document.documentElement.setAttribute("data-theme", theme);
            localStorage.setItem("theme", theme);
        });
    }

    if (circle && fieldSubmit) {
        document.body.addEventListener("mousemove", e => {
            circle.style.left = `${e.pageX - fieldSubmit.offsetLeft - 15}px`;
            circle.style.top = `${e.pageY - fieldSubmit.offsetTop - 15}px`;
        });
    }
}

function initFlashTimers() {
    document.querySelectorAll('.flash-message').forEach(flash => {
        const ring = flash.querySelector('.progress-ring');
        if (!ring) return;
        const D = 3000, I = 10, steps = D / I, dec = 360 / steps;
        let angle = 360, timer;

        function update() {
            angle -= dec;
            if (angle <= 0) {
                clearInterval(timer);
                flash.style.display = 'none';
            }
            ring.style.setProperty('--angle', angle + 'deg');
        }
        timer = setInterval(update, I);

        flash.addEventListener('mouseenter', () => clearInterval(timer));
        flash.addEventListener('mouseleave', () => { angle = 360; timer = setInterval(update, I); });
    });
}

function initProfileDropdown() {
    const btn = document.getElementById('profile-btn');
    const menu = document.getElementById('dropdown-menu');
    if (!btn || !menu) return;

    btn.addEventListener('click', e => {
        e.stopPropagation();
        menu.classList.toggle('show');
    });
    document.addEventListener('click', () => menu.classList.remove('show'));
    document.addEventListener('keydown', e => { if (e.key === 'Escape') menu.classList.remove('show'); });
}

function initNavbarScroll() {
    let lastY = 0;
    const nav = document.querySelector('.nav-container');
    window.addEventListener('scroll', () => {
        const y = window.scrollY;
        nav.style.top = y > lastY ? `-${nav.offsetHeight}px` : '0';
        lastY = Math.max(0, y);
    });
}

// ---- Jobs Page UI ----

function initJobsUI() {
    const form = document.getElementById("job-form");
    const results = document.getElementById("results-container");
    const loading = document.getElementById("loading");
    const preview = document.getElementById("preview-panel");
    const closeBtn = preview.querySelector(".close-preview");
    const overlay = document.createElement('div');
    overlay.className = 'content-overlay';
    document.body.appendChild(overlay);

    let page = parseInt(form.dataset.page, 20);
    let pageSize = parseInt(form.dataset.pageSize, 20);
    let selectedJob = null;

    function updateFilters(pagination, formData) {
        document.getElementById('results-count').innerHTML =
            `<i class="fa fa-list"></i> ${pagination.total_jobs} jobs found`;
        const tags = [];
        if (formData.get('regions') !== 'ALL') {
            const sel = form.elements.regions;
            tags.push(`<span class="filter-tag"><i class="fa fa-map-marker"></i> ${sel.selectedOptions[0].text}</span>`);
        }
        if (formData.get('categories') !== 'ALL') {
            const sel = form.elements.categories;
            tags.push(`<span class="filter-tag"><i class="fa fa-folder"></i> ${sel.selectedOptions[0].text}</span>`);
        }
        if (formData.get('keyword')) {
            tags.push(`<span class="filter-tag"><i class="fa fa-search"></i> "${formData.get('keyword')}"</span>`);
        }
        document.getElementById('active-filters').innerHTML = tags.join('');
    }

    function updatePagination(pagination) {
        const container = document.getElementById('pagination');
        const controls = document.getElementById('pagination-controls');
        if (pagination.total_pages <= 1) {
            controls.style.display = 'none';
            return;
        }
        controls.style.display = 'flex';
        document.getElementById('page-size').value = pagination.page_size;
        let html = '';
        if (pagination.page > 1) {
            html += `<button class="page-link" onclick="updatePage(${pagination.page - 1})">
                   <i class="fa fa-chevron-left"></i> Prev
                 </button>`;
        }
        html += `<span class="page-info">Page ${pagination.page} of ${pagination.total_pages}</span>`;
        if (pagination.page < pagination.total_pages) {
            html += `<button class="page-link" onclick="updatePage(${pagination.page + 1})">
                   Next <i class="fa fa-chevron-right"></i>
                 </button>`;
        }
        container.innerHTML = html;
    }

    function renderResults(jobs) {
        results.innerHTML = '';
        jobs.forEach(job => {
            const el = document.createElement('div');
            el.className = 'job-item';
            el.dataset.url = job.url;
            el.dataset.description = job.description;
            el.dataset.category = job.category;
            el.innerHTML = `
          <h3>${job.title}</h3>
          <div class="job-item-details">
            <span class="job-item-detail"><i class="fa fa-building"></i> ${job.company}</span>
            <span class="job-item-detail"><i class="fa fa-map-marker"></i> ${job.location}</span>
            <span class="job-item-detail"><i class="fa fa-calendar"></i> ${job.date_posted}</span>
          </div>
        `;
            el.addEventListener('click', () => showPreview(job, el));
            results.appendChild(el);
        });
    }

    async function submitSearch() {
        loading.style.display = 'block';
        const fd = new FormData(form);
        fd.append('page', page);
        fd.append('page_size', pageSize);

        try {
            const res = await fetch('/jobs', {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                body: fd
            });
            const data = await res.json();
            loading.style.display = 'none';
            renderResults(data.jobs);
            updatePagination(data.pagination);
            updateFilters(data.pagination, fd);
        } catch (err) {
            console.error('Search error', err);
            loading.style.display = 'none';
        }
    }

    function closePreview() {
        preview.classList.remove('show');
        overlay.classList.remove('show');
        document.querySelector('.job-item.selected')?.classList.remove('selected');
        selectedJob = null;
    }

    async function showPreview(job, el) {
        document.querySelector('.job-item.selected')?.classList.remove('selected');
        el.classList.add('selected');
        selectedJob = job;

        // Show basic info immediately
        const basicInfo = `
            <div class="preview-title"><h1>${job.title}</h1></div>
            <div class="company"><i class="fa fa-building"></i> ${job.company}</div>
            <div class="metadata">
                <div class="metadata-item"><i class="fa fa-map-marker"></i> ${job.location}</div>
                <div class="metadata-item"><i class="fa fa-folder"></i> ${job.category}</div>
                <div class="metadata-item"><i class="fa fa-calendar"></i> ${job.date_posted}</div>
            </div>
            <div class="actions">
                <a href="${job.url}" target="_blank" class="action-btn primary-btn">
                    <i class="fa fa-external-link"></i> View Job
                </a>
                <button class="action-btn secondary-btn save-btn">
                    <i class="fa fa-bookmark"></i> ${job.favorite ? 'Unsave Job' : 'Save Job'}
                </button>
            </div>
            <div class="description">
                ${showSkeletonLoader()}
            </div>
        `;
        preview.querySelector('.preview-content').innerHTML = basicInfo;
        preview.classList.add('show');
        overlay.classList.add('show');

        try {
            const data = await fetchJobDetails(job.url);
            const desc = preview.querySelector('.description');
            desc.innerHTML = data.description;

            // Email copy if present
            if (data.email && data.email !== 'N/A') {
                const emailEl = document.createElement('div');
                emailEl.className = 'email-item';
                emailEl.title = 'Click to copy email';
                emailEl.innerHTML = `<i class="fa fa-envelope"></i> ${data.email}`;
                emailEl.addEventListener('click', async () => {
                    await navigator.clipboard.writeText(data.email);
                    const orig = emailEl.innerHTML;
                    emailEl.innerHTML = '<i class="fa fa-check"></i> Copied!';
                    setTimeout(() => emailEl.innerHTML = orig, 2000);
                });
                desc.prepend(emailEl);
            }

            // Save/Unsave button
            const btn = preview.querySelector('.save-btn');
            btn.addEventListener('click', async () => {
                btn.disabled = true;
                btn.innerHTML = `<i class="fa fa-spinner fa-spin"></i> ${job.favorite ? 'Unsaving' : 'Saving'}...`;
                const url = job.url;
                const endpoint = job.favorite ? '/unsave_job' : '/save_job';
                const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
                try {
                    const resp = await fetch(endpoint, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken,
                            'X-CSRF-Token': csrfToken
                        },
                        body: JSON.stringify({ url })
                    });
                    if (!resp.ok) throw new Error('Network error');
                    job.favorite = !job.favorite;
                    btn.innerHTML = `<i class="fa fa-bookmark"></i> ${job.favorite ? 'Unsave Job' : 'Save Job'}`;
                    btn.disabled = false;
                } catch (err) {
                    console.error(err);
                    btn.innerHTML = `<i class="fa fa-exclamation-triangle"></i> Error`;
                }
            });
        } catch (err) {
            preview.querySelector('.description').innerHTML = `
                <div class="error-message">
                    <i class="fa fa-exclamation-circle"></i>
                    <p>Unable to load description.</p>
                </div>
            `;
        }
    }

    // Expose pagination control functions to global scope
    window.updatePage = p => { page = p; submitSearch(); };
    window.updatePageSize = s => { pageSize = +s; page = 1; submitSearch(); };

    // Event bindings
    form.addEventListener('submit', e => { e.preventDefault(); page = 1; submitSearch(); });
    closeBtn.addEventListener('click', e => { e.stopPropagation(); closePreview(); });
    document.addEventListener('click', e => {
        if (preview.classList.contains('show') &&
            !preview.contains(e.target) &&
            !e.target.closest('.job-item')) {
            closePreview();
        }
    });
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape' && preview.classList.contains('show')) {
            closePreview();
        }
    });
}

// ---- Favorites Page UI ----

function initFavoritesUI() {
    const preview = document.getElementById("preview-panel");
    if (!preview) return;
    const closeBtn = preview.querySelector(".close-preview");
    const overlay = document.createElement("div");
    overlay.className = "content-overlay";
    document.body.appendChild(overlay);

    document.querySelectorAll(".job-item").forEach(el => {
        el.addEventListener("click", async () => {
            document.querySelectorAll(".job-item").forEach(i => i.classList.remove("selected"));
            el.classList.add("selected");

            const job = {
                url: el.dataset.url,
                title: el.querySelector("h3").textContent,
                company: el.querySelector(".job-item-detail:nth-child(1)").textContent.trim(),
                location: el.querySelector(".job-item-detail:nth-child(2)").textContent.trim(),
                date_posted: el.querySelector(".job-item-detail:nth-child(3)").textContent.trim()
            };

            // Show basic info immediately
            const basicInfo = `
                <div class="preview-title"><h1>${job.title}</h1></div>
                <div class="company"><i class="fa fa-building"></i> ${job.company}</div>
                <div class="metadata">
                    <div class="metadata-item"><i class="fa fa-map-marker"></i> ${job.location}</div>
                    <div class="metadata-item"><i class="fa fa-calendar"></i> ${job.date_posted}</div>
                </div>
                <div class="actions">
                    <a href="${job.url}" target="_blank" class="action-btn primary-btn">
                        <i class="fa fa-external-link"></i> View Job
                    </a>
                    <button class="action-btn secondary-btn unsave-btn">
                        <i class="fa fa-bookmark"></i> Unsave Job
                    </button>
                </div>
                <div class="description">
                    ${showSkeletonLoader()}
                </div>
            `;
            preview.querySelector(".preview-content").innerHTML = basicInfo;
            preview.classList.add("show");
            overlay.classList.add("show");

            try {
                const data = await fetchJobDetails(job.url);
                const desc = preview.querySelector('.description');
                desc.innerHTML = data.description;

                // Add email box if present
                if (data.email && data.email !== 'N/A') {
                    const emailEl = document.createElement('div');
                    emailEl.className = 'email-item';
                    emailEl.title = 'Click to copy email';
                    emailEl.innerHTML = `<i class="fa fa-envelope"></i> ${data.email}`;
                    emailEl.addEventListener('click', async () => {
                        await navigator.clipboard.writeText(data.email);
                        const orig = emailEl.innerHTML;
                        emailEl.innerHTML = '<i class="fa fa-check"></i> Copied!';
                        setTimeout(() => emailEl.innerHTML = orig, 2000);
                    });
                    desc.prepend(emailEl);
                }

                // Setup unsave
                preview.querySelector(".unsave-btn").addEventListener("click", async () => {
                    const btn = preview.querySelector(".unsave-btn");
                    btn.disabled = true;
                    btn.innerHTML = `<i class="fa fa-spinner fa-spin"></i> Unsaving...`;
                    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
                    try {
                        const res = await fetch('/unsave_job', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': csrfToken,
                                'X-CSRF-Token': csrfToken
                            },
                            body: JSON.stringify({ url: job.url })
                        });
                        if (!res.ok) throw new Error('Network error');
                        document.querySelector(`.job-item[data-url="${job.url}"]`).remove();
                        closeBtn.click();
                    } catch (err) {
                        console.error(err);
                        btn.innerHTML = `<i class="fa fa-exclamation-triangle"></i> Error`;
                        btn.disabled = false;
                    }
                });
            } catch (err) {
                preview.querySelector('.description').innerHTML = `
                    <div class="error-message">
                        <i class="fa fa-exclamation-circle"></i>
                        <p>Unable to load details.</p>
                    </div>
                `;
            }
        });
    });

    function closeFavPreview() {
        preview.classList.remove("show");
        overlay.classList.remove("show");
        document.querySelector(".job-item.selected")?.classList.remove("selected");
    }
    closeBtn.addEventListener("click", closeFavPreview);
    document.addEventListener('click', e => {
        if (preview.classList.contains('show') &&
            !preview.contains(e.target) &&
            !e.target.closest('.job-item')) {
            closeFavPreview();
        }
    });
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape' && preview.classList.contains('show')) {
            closeFavPreview();
        }
    });
}

// ---- Initialize All ----

document.addEventListener("DOMContentLoaded", () => {
    initThemeToggle();
    initFlashTimers();
    initProfileDropdown();
    initNavbarScroll();

    if (document.getElementById("job-form")) {
        initJobsUI();
    }
    if (window.location.pathname === "/favorites") {
        initFavoritesUI();
    }
});
