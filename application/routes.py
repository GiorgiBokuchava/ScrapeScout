from application import app, db
from flask import render_template, request, redirect, url_for, flash, jsonify
from application.forms import RegisterForm, LoginForm, JobSearchForm
from application.models import User, Job, SavedJob
from flask_login import login_user, logout_user
from application.scrape import get_jobs
from application import jobs_ge
from flask_login import current_user, login_required
import re
from html import escape
from datetime import datetime
import json
from flask import make_response
from application.location import LOC_BY_KEY


@app.route("/healthz")
def healthz():
    return "OK", 200


@app.route("/")
@app.route("/home")
def home_page():
    # Get the most recent jobs with default parameters
    recent_jobs = get_jobs(
        searched_location="ALL",
        searched_category="ALL",
        searched_keyword="",
        sort_by="date_posted_desc",
    )[
        :7
    ]  # Get 7 most recent jobs
    return render_template("home.html", recent_jobs=recent_jobs)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(
            username=form.username.data,
            email_address=form.email_address.data,
            password=form.password.data,
        )
        db.session.add(user_to_create)
        db.session.commit()
        flash("Account created successfully!", "success")
        login_user(user_to_create)

        return redirect(url_for("home_page"))

    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f"Error creating account: {err_msg}", category="danger")

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password(form.password.data):
            login_user(attempted_user, remember=form.remember.data)
            flash("Login successful!", "success")
            return redirect(url_for("home_page"))
        else:
            flash("Login failed. Please check your credentials.", "warning")

    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "primary")
    return redirect(url_for("home_page"))


@app.route("/jobs", methods=["GET", "POST"])
def jobs():
    form = JobSearchForm()
    from application.location import regions, LOC_BY_KEY
    from application.category import CATEGORIES, CAT_BY_KEY

    # Get pagination parameters from query string
    page = request.values.get("page", 1, type=int)
    page_size = request.values.get("page_size", 10, type=int)

    # Validate page size
    if page_size not in [10, 20, 30, 50]:
        page_size = 10

    if request.method == "GET":
        return render_template("jobs.html", form=form, page=page, page_size=page_size)

    # Handle POST request
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        # This is an AJAX request, return JSON
        if form.validate_on_submit():
            job_location = form.regions.data
            job_category = form.categories.data
            job_keyword = form.keyword.data
            sort_by = form.sort_by.data

            jobs_list = get_jobs(
                searched_location=job_location,
                searched_category=job_category,
                searched_keyword=job_keyword,
                sort_by=sort_by,
            )

            # Calculate pagination
            total_jobs = len(jobs_list)
            total_pages = (total_jobs + page_size - 1) // page_size
            page = max(1, min(page, total_pages)) if total_pages > 0 else 1

            # Get paginated slice of jobs
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_jobs = jobs_list[start_idx:end_idx]

            jobs_data = []
            for job in paginated_jobs:
                try:
                    location_display = (
                        job.location
                        if job.location and job.location != "All Locations"
                        else (
                            LOC_BY_KEY[job.location_key].display
                            if job.location_key and job.location_key != "ALL"
                            else "All Locations"
                        )
                    )
                    category_display = (
                        CAT_BY_KEY[job.category_key].display
                        if job.category_key and job.category_key != "ALL"
                        else "All Categories"
                    )
                except KeyError:
                    # Fallback to stored values if keys are invalid
                    location_display = job.location
                    category_display = job.category

                # Format date_posted as 'DD MMM, YYYY'
                if hasattr(job.date_posted, "strftime"):
                    date_posted_str = job.date_posted.strftime("%d %b, %Y")
                else:
                    try:
                        dt = datetime.strptime(
                            str(job.date_posted).split()[0], "%Y-%m-%d"
                        )
                        date_posted_str = dt.strftime("%d %b, %Y")
                    except Exception:
                        date_posted_str = str(job.date_posted)

                jobs_data.append(
                    {
                        "title": job.title,
                        "company": job.company,
                        "url": job.url,
                        "date_posted": date_posted_str,
                        "description": job.description,
                        "location_key": job.location_key,
                        "location": location_display,
                        "category_key": job.category_key,
                        "category": category_display,
                    }
                )

            return jsonify(
                {
                    "jobs": jobs_data,
                    "pagination": {
                        "page": page,
                        "page_size": page_size,
                        "total_pages": total_pages,
                        "total_jobs": total_jobs,
                    },
                }
            )
        return jsonify({"jobs": [], "error": form.errors}), 400
    else:
        # This is a regular form submission, render the template
        if form.validate_on_submit():
            job_location = form.regions.data
            job_category = form.categories.data
            job_keyword = form.keyword.data
            sort_by = form.sort_by.data

            jobs_list = get_jobs(
                searched_location=job_location,
                searched_category=job_category,
                searched_keyword=job_keyword,
                sort_by=sort_by,
            )

            # Calculate pagination
            total_jobs = len(jobs_list)
            total_pages = (total_jobs + page_size - 1) // page_size
            page = max(1, min(page, total_pages)) if total_pages > 0 else 1

            # Get paginated slice of jobs
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_jobs = jobs_list[start_idx:end_idx]

            return render_template(
                "jobs.html",
                form=form,
                jobs=paginated_jobs,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
                total_jobs=total_jobs,
            )
        return render_template("jobs.html", form=form, page=page, page_size=page_size)


@app.route("/get_description", methods=["POST"])
def get_description():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "URL is required"}), 400

    def clean_description_text(raw: str) -> str:
        # 1) Split & strip lines
        lines = [line.strip() for line in raw.splitlines()]

        # 2) Collapse into paragraphs
        paragraphs: list[str] = []
        buffer: list[str] = []
        for line in lines:
            if line == "":
                if buffer:
                    paragraphs.append(" ".join(buffer))
                    buffer = []
            else:
                buffer.append(line)
        if buffer:
            paragraphs.append(" ".join(buffer))

        # 3) Auto-link URLs and escape other HTML
        url_pattern = re.compile(r"(https?://[^\s]+)")

        def linkify(text: str) -> str:
            # escape any user content first
            escaped = escape(text)
            # then replace URLs with <a>
            return url_pattern.sub(r'<a href="\1" target="_blank">\1</a>', escaped)

        # 4) Wrap in <p> tags
        html_paragraphs = [f"<p>{linkify(p)}</p>" for p in paragraphs]

        return "\n".join(html_paragraphs)

    try:
        # Look up existing job (by URL)
        job = Job.query.filter_by(url=url).first()

        # Fetch description & email
        description_soup = jobs_ge.extractDescription(url)
        if description_soup == "N/A":
            desc_text = "No description available"
            email = "N/A"
        else:
            raw = description_soup.get_text(separator="\n")
            desc_text = clean_description_text(raw)
            extracted_email = jobs_ge.extractEmail(str(description_soup))
            # More aggressive email cleaning: remove ALL whitespace and newlines
            email = (
                "".join(extracted_email.split()) if extracted_email != "N/A" else "N/A"
            )

        if job:
            # Update existing job
            job.description = desc_text
            job.email = email
            db.session.commit()
        else:
            # Create a new job entry
            job = Job(
                url=url,
                title="N/A",
                company="N/A",
                date_posted="N/A",
                salary="N/A",
                location_key="ALL",
                category_key="ALL",
                location="All Locations",
                category="All Categories",
                description=desc_text,
                email=email,
            )
            db.session.add(job)
            db.session.commit()

        return jsonify({"description": desc_text, "email": email})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/save_job", methods=["POST"])
@login_required
def save_job():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    job = Job.query.filter_by(url=url).first()
    if not job:
        return jsonify({"error": "Job not found"}), 404

    # Check if job is already saved
    existing_save = SavedJob.query.filter_by(
        user_id=current_user.id, job_id=job.id
    ).first()
    if existing_save:
        return jsonify({"success": True, "message": "Job already saved"})

    # Create new SavedJob entry
    saved_job = SavedJob(user_id=current_user.id, job_id=job.id)
    db.session.add(saved_job)
    db.session.commit()

    return jsonify({"success": True})


@app.route("/favorites")
@login_required
def favorites():
    # Get pagination parameters from query string
    page = request.values.get("page", 1, type=int)
    page_size = request.values.get("page_size", 10, type=int)

    # Validate page size
    if page_size not in [10, 20, 30, 50]:
        page_size = 10

    # Get total count of user's favorite jobs using the SavedJob relationship
    total_jobs = SavedJob.query.filter_by(user_id=current_user.id).count()

    # Calculate total pages
    total_pages = (total_jobs + page_size - 1) // page_size

    # Ensure page is within valid range
    page = max(1, min(page, total_pages)) if total_pages > 0 else 1

    # Get paginated jobs using the SavedJob relationship
    saved_jobs = (
        SavedJob.query.filter_by(user_id=current_user.id)
        .order_by(SavedJob.saved_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    # Get the actual Job objects from the SavedJob relationships
    jobs = [saved_job.job for saved_job in saved_jobs]
    # Format date_posted as 'DD MMM, YYYY' for each job
    for job in jobs:
        if hasattr(job.date_posted, "strftime"):
            job.date_posted = job.date_posted.strftime("%d %b, %Y")
        else:
            try:
                dt = datetime.strptime(str(job.date_posted).split()[0], "%Y-%m-%d")
                job.date_posted = dt.strftime("%d %b, %Y")
            except Exception:
                job.date_posted = str(job.date_posted)

    return render_template(
        "favorites.html",
        jobs=jobs,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@app.route("/unsave_job", methods=["POST"])
@login_required
def unsave_job():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    job = Job.query.filter_by(url=url).first()
    if not job:
        return jsonify({"error": "Job not found"}), 404

    # Find and delete the SavedJob entry
    saved_job = SavedJob.query.filter_by(user_id=current_user.id, job_id=job.id).first()
    if saved_job:
        db.session.delete(saved_job)
        db.session.commit()

    return jsonify({"success": True})


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/delete_account")
@login_required
def delete_account():
    # Delete user's data
    SavedJob.query.filter_by(user_id=current_user.id).delete()
    db.session.delete(current_user)
    db.session.commit()
    logout_user()
    flash("Your account has been deleted.", "success")
    return redirect(url_for("home_page"))


@app.route("/export_data")
@login_required
def export_data():
    # Create a dictionary with user's data
    user_data = {
        "username": current_user.username,
        "email": current_user.email_address,
        "saved_jobs": [
            {
                "title": job.job.title,
                "company": job.job.company,
                "url": job.job.url,
                "date_saved": job.date_saved.isoformat(),
            }
            for job in current_user.saved_jobs
        ],
    }

    # Create response with JSON data
    response = make_response(json.dumps(user_data, indent=2))
    response.headers["Content-Type"] = "application/json"
    response.headers["Content-Disposition"] = "attachment; filename=user_data.json"
    return response
