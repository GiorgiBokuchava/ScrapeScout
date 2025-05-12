from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from application.models import User

from application.location import regions, cities_of
from application.category import groups, categories, cats_of


class RegisterForm(FlaskForm):
    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError("This username is taken. Please try a different one.")

    def validate_email_address(self, email_to_check):
        email_address = User.query.filter_by(email_address=email_to_check.data).first()
        if email_address:
            raise ValidationError(
                f"This email address is already registered. Please try a different one."
            )

    username = StringField(
        label="Username", validators=[Length(min=5, max=30), DataRequired()]
    )
    email_address = StringField(
        label="Email Address", validators=[Email(), DataRequired(), Email()]
    )
    password = PasswordField(
        label="Password", validators=[Length(min=5, max=100), DataRequired()]
    )
    confirm_password = PasswordField(
        label="Confirm Password",
        validators=[EqualTo("password"), DataRequired()],
    )
    submit = SubmitField(label="Create Account")


class LoginForm(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    remember = BooleanField(label="Remember Me")
    submit = SubmitField(label="Login")


class JobSearchForm(FlaskForm):
    # Build region list once
    REGION_CHOICES = [(reg.key, reg.display) for reg in regions()]

    # City dropdown will be populated in the view via `cities_of(...)`
    # – leave it empty here or fill with "All cities".
    CITY_CHOICES = [("ALL", "All Cities")]

    GROUP_CHOICES = [("ALL", "All Groups")] + [(g, g) for g in groups()]
    CATEGORY_CHOICES = [(cat.key, cat.display) for cat in categories()]

    SORT_CHOICES = [
        ("date_posted_desc", "Date (Newest First)"),
        ("date_posted_asc", "Date (Oldest First)"),
        ("title_asc", "Title (A-Z)"),
        ("title_desc", "Title (Z-A)"),
        ("company_asc", "Company (A-Z)"),
        ("company_desc", "Company (Z-A)"),
    ]

    regions = SelectField("Region", choices=REGION_CHOICES, default="ALL")
    cities = SelectField("City", choices=CITY_CHOICES, default="ALL")
    groups = SelectField("Group", choices=GROUP_CHOICES, default="ALL")
    categories = SelectField("Category", choices=CATEGORY_CHOICES, default="ALL")
    sort_by = SelectField("Sort By", choices=SORT_CHOICES, default="date_posted_desc")
    keyword = StringField("Keyword")


class ProfileForm(FlaskForm):
    username = StringField(
        label="Username", validators=[Length(min=5, max=30), DataRequired()]
    )
    email = StringField(label="Email Address", validators=[Email(), DataRequired()])
    current_password = PasswordField(
        label="Current Password", validators=[DataRequired()]
    )
    new_password = PasswordField(
        label="New Password", validators=[Length(min=5, max=100)]
    )
    confirm_password = PasswordField(
        label="Confirm New Password", validators=[EqualTo("new_password")]
    )
    submit = SubmitField(label="Save Changes")
