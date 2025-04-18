from application import app, db
from flask import render_template, request, redirect, url_for, flash, jsonify
from application.forms import RegisterForm, LoginForm, JobSearchForm
from application.models import User, Job
from flask_login import login_user, logout_user
from application.scrape import get_jobs


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
            password=form.password_field1.data,
        )
        db.session.add(user_to_create)
        db.session.commit()
        flash("Account created successfully!", "success")
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
            flash("Login failed. Please check your credentials.", "danger")

    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("home_page"))


@app.route("/jobs", methods=["GET", "POST"])
def jobs():
    form = JobSearchForm()

    if request.method == "GET":
        return render_template("jobs.html", form=form)

    if form.validate_on_submit():
        job_location = form.locations.data
        job_category = form.categories.data
        job_keyword = form.keyword.data
        # Here you would typically call your scraping function with the provided parameters
        # For example:
        # jobs = scrape_jobs(job_location, job_category, job_keyword)

        jobs_list = get_jobs(
            searched_location=job_location,
            searched_category=job_category,
            searched_keyword=job_keyword,
        )

        # Convert each Job object into a dictionary for JSON serialization
        jobs_data = []
        for job in jobs_list:
            jobs_data.append(
                {
                    "title": job.title,
                    "company": job.company_name,
                    "url": job.job_URL,
                    "posted_time": job.posted_time,
                    "description": job.description,
                }
            )

        return jsonify({"jobs": jobs_data})
    else:
        # You may include form error details for debugging
        return jsonify({"jobs": [], "error": form.errors}), 400
    # return render_template("jobs.html", form=form, jobs=jobs)
