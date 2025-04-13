from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from application.models import User


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
    password_field1 = PasswordField(
        label="Password", validators=[Length(min=5, max=100), DataRequired()]
    )
    password_field2 = PasswordField(
        label="Confirm Password",
        validators=[EqualTo("password_field1"), DataRequired()],
    )
    submit = SubmitField(label="Create Account")


class LoginForm(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    remember = BooleanField(label="Remember Me")
    submit = SubmitField(label="Login")


class JobSearchForm(FlaskForm):
    locations = SelectField(
        label="Job Location",
        choices=[
            ("All", "All"),
            ("Tbilisi", "Tbilisi"),
            ("Abkhazia", "Abkhazia"),
            ("Adjara", "Adjara"),
            ("Guria", "Guria"),
            ("Imereti", "Imereti"),
            ("Kakheti", "Kakheti"),
            ("Mtskheta-Mtianeti", "Mtskheta-Mtianeti"),
            ("Ratcha-Letchkhumi, qv. Svaneti", "Ratcha-Letchkhumi, qv. Svaneti"),
            ("Samegrelo-Zemo Svaneti", "Samegrelo-Zemo Svaneti"),
            ("Samtskhe-Javakheti", "Samtskhe-Javakheti"),
            ("Kvemo-Kartli", "Kvemo-Kartli"),
            ("Shida-Kartli", "Shida-Kartli"),
            ("Abroad", "Abroad"),
            ("Remote", "Remote"),
        ],
        validators=[DataRequired()],
        default="All",
    )

    categories = SelectField(
        label="Job Category",
        choices=[
            ("Any", "Any"),
            ("Administration/Management", "Administration/Management"),
            ("Finances/Statistics", "Finances/Statistics"),
            ("Sales", "Sales"),
            ("PR/Marketing", "PR/Marketing"),
            ("General Technical Personnel", "General Technical Personnel"),
            ("Logistics/Transport/Distribution", "Logistics/Transport/Distribution"),
            ("Building/Renovation", "Building/Renovation"),
            ("Cleaning", "Cleaning"),
            ("Security", "Security"),
            ("IT/Programming", "IT/Programming"),
            ("Media/Publishing", "Media/Publishing"),
            ("Education", "Education"),
            ("Law", "Law"),
            ("Medicine/Pharmacy", "Medicine/Pharmacy"),
            ("Beauty/Fashion", "Beauty/Fashion"),
            ("Food", "Food"),
            ("Other", "Other"),
        ],
        validators=[DataRequired()],
        default="Any",
    )

    keyword = StringField(label="Keyword")
