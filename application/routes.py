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


@app.route("/healthz")
def healthz():
    return "OK", 200


@app.route("/")
@app.route("/home")
def home_page():
    return render_template("home.html")


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

            jobs_data.append(
                {
                    "title": job.title,
                    "company": job.company,
                    "url": job.url,
                    "date_posted": job.date_posted,
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


@app.route("/profile")
@login_required
def profile():
    # Get user statistics
    saved_jobs_count = len(current_user.saved_jobs)
    viewed_jobs_count = len(current_user.viewed_jobs)
    days_active = (datetime.now() - current_user.created_at).days

    return render_template(
        "profile.html",
        saved_jobs_count=saved_jobs_count,
        viewed_jobs_count=viewed_jobs_count,
        days_active=days_active,
    )


@app.route("/settings")
@login_required
def settings():
    # Get current user preferences
    current_theme = current_user.theme or "system"
    current_font_size = current_user.font_size or 14
    current_location = current_user.default_location
    jobs_per_page = current_user.jobs_per_page or 20
    sort_order = current_user.sort_order or "newest"
    profile_visible = current_user.profile_visible
    activity_visible = current_user.activity_visible
    data_collection_enabled = current_user.data_collection_enabled

    # Get available locations
    locations = Location.query.all()

    return render_template(
        "settings.html",
        current_theme=current_theme,
        current_font_size=current_font_size,
        locations=locations,
        current_location=current_location,
        jobs_per_page=jobs_per_page,
        sort_order=sort_order,
        profile_visible=profile_visible,
        activity_visible=activity_visible,
        data_collection_enabled=data_collection_enabled,
    )


@app.route("/update_appearance", methods=["POST"])
@login_required
def update_appearance():
    theme = request.form.get("theme")
    font_size = int(request.form.get("font_size"))

    current_user.theme = theme
    current_user.font_size = font_size
    db.session.commit()

    flash("Appearance settings updated successfully!", "success")
    return redirect(url_for("settings"))


@app.route("/update_search_preferences", methods=["POST"])
@login_required
def update_search_preferences():
    default_location = request.form.get("default_location")
    jobs_per_page = int(request.form.get("jobs_per_page"))
    sort_order = request.form.get("sort_order")

    current_user.default_location = default_location
    current_user.jobs_per_page = jobs_per_page
    current_user.sort_order = sort_order
    db.session.commit()

    flash("Search preferences updated successfully!", "success")
    return redirect(url_for("settings"))


@app.route("/update_privacy", methods=["POST"])
@login_required
def update_privacy():
    profile_visible = "profile_visibility" in request.form
    activity_visible = "activity_visibility" in request.form
    data_collection = "data_collection" in request.form

    current_user.profile_visible = profile_visible
    current_user.activity_visible = activity_visible
    current_user.data_collection_enabled = data_collection
    db.session.commit()

    flash("Privacy settings updated successfully!", "success")
    return redirect(url_for("settings"))


@app.route("/delete_account")
@login_required
def delete_account():
    # Delete user's data
    SavedJob.query.filter_by(user_id=current_user.id).delete()
    ViewedJob.query.filter_by(user_id=current_user.id).delete()

    # Delete the user
    db.session.delete(current_user)
    db.session.commit()

    logout_user()
    flash("Your account has been deleted successfully.", "success")
    return redirect(url_for("home_page"))


@app.route("/export_data")
@login_required
def export_data():
    # Create a dictionary with user's data
    user_data = {
        "username": current_user.username,
        "email": current_user.email_address,
        "created_at": current_user.created_at.isoformat(),
        "saved_jobs": [job.to_dict() for job in current_user.saved_jobs],
        "viewed_jobs": [job.to_dict() for job in current_user.viewed_jobs],
        "preferences": {
            "theme": current_user.theme,
            "font_size": current_user.font_size,
            "default_location": current_user.default_location,
            "jobs_per_page": current_user.jobs_per_page,
            "sort_order": current_user.sort_order,
        },
    }

    # Convert to JSON
    json_data = json.dumps(user_data, indent=2)

    # Create response with JSON file
    response = make_response(json_data)
    response.headers["Content-Type"] = "application/json"
    response.headers["Content-Disposition"] = (
        f"attachment; filename=scrapescout_data_{current_user.username}.json"
    )

    return response
