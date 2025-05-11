document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('job-form');
    let currentPage = parseInt(form.dataset.page, 10);
    let currentPageSize = parseInt(form.dataset.pageSize, 10);
    const resultsContainer = document.getElementById('results-container');
    const loadingIndicator = document.getElementById('loading');
    const previewPanel = document.getElementById('preview-panel');
    const closePreviewBtn = previewPanel.querySelector('.close-preview');

    // Overlay for preview
    const overlay = document.createElement('div');
    overlay.className = 'content-overlay';
    document.body.appendChild(overlay);

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

    function updateActiveFilters() {
        const formData = new FormData(form);
        const activeFilters = document.getElementById('active-filters');
        const tags = [];

        if (formData.get('regions') !== 'ALL') {
            const sel = form.querySelector('[name="regions"]');
            tags.push(`<span class="filter-tag"><i class="fa fa-map-marker"></i> ${sel.selectedOptions[0].text}</span>`);
        }
        if (formData.get('categories') !== 'ALL') {
            const sel = form.querySelector('[name="categories"]');
            tags.push(`<span class="filter-tag"><i class="fa fa-folder"></i> ${sel.selectedOptions[0].text}</span>`);
        }
        if (formData.get('keyword')) {
            tags.push(`<span class="filter-tag"><i class="fa fa-search"></i> "${formData.get('keyword')}"</span>`);
        }

        activeFilters.innerHTML = tags.join('');
    }

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
            updateActiveFilters();
            document.getElementById('results-count').innerHTML = `<i class="fa fa-list"></i> ${data.pagination.total_jobs} jobs found`;
        } catch (err) {
            console.error('Fetch error', err);
            loadingIndicator.style.display = 'none';
        }
    }

    function renderJobResults(jobs) {
        resultsContainer.innerHTML = '';
        jobs.forEach(job => {
            const el = document.createElement('div');
            el.className = 'job-item';
            el.dataset.url = job.url;
            el.dataset.description = job.description;
            el.innerHTML = `
          <h3>${job.title}</h3>
          <div class="job-item-details">
            <span class="job-item-detail"><i class="fa fa-building"></i> ${job.company}</span>
            <span class="job-item-detail"><i class="fa fa-map-marker"></i> ${job.location}</span>
            <span class="job-item-detail"><i class="fa fa-calendar"></i> ${job.date_posted}</span>
          </div>
        `;
            resultsContainer.appendChild(el);
        });
    }

    function showJobPreview(jobItem) {
        document.querySelector('.job-item.selected')?.classList.remove('selected');
        jobItem.classList.add('selected');

        const previewContent = previewPanel.querySelector('.preview-content');
        previewContent.innerHTML = `
        <h1>${jobItem.querySelector('h3').textContent}</h1>
        <div class="metadata">${jobItem.querySelector('.job-item-details').innerHTML}</div>
        <div class="description">${jobItem.dataset.description}</div>
        <a href="${jobItem.dataset.url}" target="_blank" class="action-btn primary-btn">
          <i class="fa fa-external-link"></i> View Job
        </a>
      `;

        previewPanel.classList.add('show');
        overlay.classList.add('show');
    }

    // Expose pagination controls
    window.updatePage = page => { currentPage = page; submitSearch(); };
    window.updatePageSize = size => { currentPageSize = parseInt(size, 10); currentPage = 1; submitSearch(); };

    // Event bindings
    form.addEventListener('submit', e => { e.preventDefault(); currentPage = 1; submitSearch(); });
    resultsContainer.addEventListener('click', e => {
        const job = e.target.closest('.job-item');
        if (job) showJobPreview(job);
    });
    closePreviewBtn.addEventListener('click', () => {
        previewPanel.classList.remove('show');
        overlay.classList.remove('show');
    });
});
