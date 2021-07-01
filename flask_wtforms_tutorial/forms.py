"""Form object declaration."""
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import (
    DateField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
    FieldList,
    FormField,
)
from wtforms.validators import URL, DataRequired, Email, EqualTo, Length
from wtforms.fields.html5 import EmailField, TelField

    
class TextForm(FlaskForm):
    text = StringField("Placeholder")
    
class SelectForm(FlaskForm):
    select = SelectField("Placeholder", choices=[])
    
class EmailForm(FlaskForm):
    email = EmailField("Placeholder")
    
class PhoneForm(FlaskForm):
    phone = TelField("Placeholder")

class CompleteForm(FlaskForm):
    text_entries = FieldList(FormField(TextForm))
    select_entries = FieldList(FormField(SelectForm))
    email_entries = FieldList(FormField(EmailForm))
    phone_entries = FieldList(FormField(PhoneForm))
    submit = SubmitField("Submit")