# application/models.py

from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import func
from application import db, bcrypt, login_manager
from pytz import utc  # renamed to avoid clashing with datetime.timezone


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    email_address = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(60), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(utc))

    # relationships (the target classes are defined _below_)
    saved_jobs = db.relationship("SavedJob", back_populates="user", lazy=True)
    viewed_jobs = db.relationship("ViewedJob", back_populates="user", lazy=True)

    # user preferences
    theme = db.Column(db.String(10), default="system")  # light, dark, system
    font_size = db.Column(db.Integer, default=14)
    default_location = db.Column(db.String(50))
    jobs_per_page = db.Column(db.Integer, default=20)
    sort_order = db.Column(db.String(10), default="newest")  # newest, oldest, relevance

    profile_visible = db.Column(db.Boolean, default=True)
    activity_visible = db.Column(db.Boolean, default=True)
    data_collection_enabled = db.Column(db.Boolean, default=True)

    @property
    def password(self):
        raise AttributeError("Password is write‐only")

    @password.setter
    def password(self, plain_text):
        self.password_hash = bcrypt.generate_password_hash(plain_text).decode("utf-8")

    def check_password(self, attempted):
        return bcrypt.check_password_hash(self.password_hash, attempted)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email_address,
            "created_at": self.created_at.isoformat(),
            "preferences": {
                "theme": self.theme,
                "font_size": self.font_size,
                "default_location": self.default_location,
                "jobs_per_page": self.jobs_per_page,
                "sort_order": self.sort_order,
            },
        }


class Job(db.Model):
    __tablename__ = "job"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, default="N/A")
    location = db.Column(db.String(100), nullable=False, default="N/A")
    category = db.Column(db.String(100), nullable=False, default="N/A")
    location_key = db.Column(db.String(50), nullable=False, index=True, default="ALL")
    category_key = db.Column(db.String(50), nullable=False, index=True, default="ALL")
    company = db.Column(db.String(100), nullable=False, default="N/A")
    description = db.Column(db.Text, nullable=False, default="N/A")
    url = db.Column(db.String(200), nullable=False, default="N/A", unique=True)
    date_posted = db.Column(db.String(20), nullable=False, default="N/A")
    salary = db.Column(db.String(50), nullable=False, default="N/A")
    email = db.Column(db.String(100), nullable=False, default="N/A")
    date_populated = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(utc),
    )

    # backrefs from SavedJob / ViewedJob if you need them:
    saved_by = db.relationship("SavedJob", back_populates="job", lazy=True)
    viewed_by = db.relationship("ViewedJob", back_populates="job", lazy=True)

    def __repr__(self):
        return f"<Job {self.title!r}>"


class SavedJob(db.Model):
    __tablename__ = "saved_job"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("job.id"), nullable=False)
    saved_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(utc)
    )

    user = db.relationship("User", back_populates="saved_jobs")
    job = db.relationship("Job", back_populates="saved_by")

    def __repr__(self):
        return f"<SavedJob user={self.user_id} job={self.job_id}>"


class ViewedJob(db.Model):
    __tablename__ = "viewed_job"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("job.id"), nullable=False)
    viewed_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(utc)
    )

    user = db.relationship("User", back_populates="viewed_jobs")
    job = db.relationship("Job", back_populates="viewed_by")

    def __repr__(self):
        return f"<ViewedJob user={self.user_id} job={self.job_id}>"
