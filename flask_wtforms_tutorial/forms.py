"""Form object declaration."""
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import (
    DateField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import URL, DataRequired, Email, EqualTo, Length


class SignupForm(FlaskForm):
    """Sign up for a user account."""

    firstName = StringField("First Name", [DataRequired()])
    lastName = StringField("Last Name", [DataRequired()])
    email = StringField(
        "Email",
        [Email(message="Not a valid email address."), DataRequired()]
    )
    confirmEmail = StringField(
        "Verify Email",
        [EqualTo('email', message="Emails must match.")]
    )
    phone = StringField("Phone", [DataRequired()])
    location = SelectField(
        "Location",
        [DataRequired()],
        choices=[
            ("Administraton", "Administraton"),
            ("Assembly 1", "Assembly 1"),
            ("Assembly 2", "Assembly 2"),
            ("Body Shop", "Body Shop"),
            ("Paint Shop", "Paint Shop"),
            ("Bibb County - GSP", "Bibb County - GSP"),
            ("Bibb County - CC USA", "Bibb County - CC USA"),
            ("Bibb County - Battery", "Bibb County - Battery"),
            ("MB ExTra", "MB ExTra"),
        ],
    )
    department = StringField("Department", [DataRequired()])
    e4 = StringField("Supervisor", [DataRequired()])
    shift = SelectField(
        "Shift",
        [DataRequired()],
        choices=[
            ("Admin", "Admin"),
            ("A", "A"),
            ("B", "B"),
        ],
    )
    # recaptcha = RecaptchaField()
    submit = SubmitField("Submit")
