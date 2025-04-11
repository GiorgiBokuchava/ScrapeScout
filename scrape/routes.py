from scrape import app, db
from flask import render_template, request, redirect, url_for, flash
from scrape.forms import RegisterForm, LoginForm
from scrape.models import User, Job
from flask_login import login_user, logout_user


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
        login_user(user_to_create)
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
            login_user(attempted_user)
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
