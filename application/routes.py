from application import app, db
from flask import render_template, request, redirect, url_for, flash, jsonify
from application.forms import RegisterForm, LoginForm, JobSearchForm
from application.models import User, Job
from flask_login import login_user, logout_user
from application.scrape import get_jobs
from application import jobs_ge
from flask_login import current_user, login_required
import re
from html import escape


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

    if request.method == "GET":
        return render_template("jobs.html", form=form)

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

        jobs_data = []
        for job in jobs_list:
            try:
                location_display = (
                    LOC_BY_KEY[job.location_key].display
                    if job.location_key and job.location_key != "ALL"
                    else "All Locations"
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

        return jsonify({"jobs": jobs_data})

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

    # Mark as favorite and record owner
    job.favorite = True
    job.owner_user_id = current_user.id
    db.session.commit()

    return jsonify({"success": True})


@app.route("/favorites")
@login_required
def favorites():
    jobs = Job.query.filter_by(owner_user_id=current_user.id, favorite=True).all()
    return render_template("favorites.html", jobs=jobs)


@app.route("/unsave_job", methods=["POST"])
@login_required
def unsave_job():
    url = request.get_json().get("url")
    job = Job.query.filter_by(url=url, owner_user_id=current_user.id).first_or_404()
    job.favorite = False
    job.owner_user_id = None
    db.session.commit()
    return jsonify({"success": True})
