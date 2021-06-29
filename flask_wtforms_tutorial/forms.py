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
    
class TextForm(FlaskForm):
    text = StringField("Placeholder")
    
class SelectForm(FlaskForm):
    select = SelectField("Placeholder", choices=[])

class CompleteForm(FlaskForm):
    text_entries = FieldList(FormField(TextForm))
    select_entries = FieldList(FormField(SelectForm))
    submit = SubmitField("Submit")