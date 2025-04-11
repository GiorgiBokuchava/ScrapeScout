from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from scrape.models import User


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
    submit = SubmitField(label="Login")
