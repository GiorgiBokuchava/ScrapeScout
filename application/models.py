from application import db, bcrypt, login_manager
from flask_login import UserMixin
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, func
from pytz import timezone


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email_address = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    favorites = db.relationship("Job", backref="owner_user", lazy=True)

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode(
            "utf-8"
        )

    def check_password(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    title = db.Column(db.String(100), nullable=False, default="N/A")
    location = db.Column(db.String(100), nullable=False, default="N/A")
    category = db.Column(db.String(100), nullable=False, default="N/A")
    company = db.Column(db.String(100), nullable=False, default="N/A")
    description = db.Column(db.Text, nullable=False, default="N/A")
    url = db.Column(db.String(200), nullable=False, default="N/A")
    date_posted = db.Column(db.String(20), nullable=False, default="N/A")
    salary = db.Column(db.String(50), nullable=False, default="N/A")
    email = db.Column(db.String(100), nullable=False, default="N/A")
    favorite = db.Column(db.Boolean, default=False)
    owner_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    date_populated = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone("Asia/Tbilisi")),
    )

    def __repr__(self):
        return f"<Job {self.title}>"
