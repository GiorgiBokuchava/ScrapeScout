from application import app, db
from flask import render_template, request, redirect, url_for, flash, jsonify
from application.forms import RegisterForm, LoginForm, JobSearchForm
from application.models import User, Job
from flask_login import login_user, logout_user
from application.scrape import get_jobs


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

    if request.method == "GET":
        return render_template("jobs.html", form=form)

    if form.validate_on_submit():
        job_location = form.locations.data
        job_category = form.categories.data
        job_keyword = form.keyword.data

        jobs_list = get_jobs(
            searched_location=job_location,
            searched_category=job_category,
            searched_keyword=job_keyword,
        )

        # Convert each Job object into a dictionary and add new Job objects to the database
        jobs_data = []
        for job in jobs_list:
            jobs_data.append(
                {
                    "title": job.title,
                    "company": job.company,
                    "url": job.url,
                    "date_posted": job.date_posted,
                    "description": job.description,
                }
            )

            new_job = Job(
                title=job.title,
                company=job.company,
                description=job.description,
                url=job.url,
                date_posted=job.date_posted,
            )
            db.session.add(new_job)
        db.session.commit()

        return jsonify({"jobs": jobs_data})
    else:
        return jsonify({"jobs": [], "error": form.errors}), 400
