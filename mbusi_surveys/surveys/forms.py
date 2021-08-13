"""Form object declaration."""
from flask_wtf import FlaskForm
from wtforms import (
    SelectField,
    StringField,
    SubmitField,
    FieldList,
    FormField,
    SelectMultipleField,
    widgets
)
from wtforms.fields.html5 import EmailField, TelField

    
class TextForm(FlaskForm):
    text = StringField("Placeholder")
    priority = 0
    
class SelectForm(FlaskForm):
    select = SelectField("Placeholder", choices=[])
    priority = 0

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()
 
class MultiForm(FlaskForm):
    multi = MultiCheckboxField("Placeholder", choices=[])
    priority = 0
   
class EmailForm(FlaskForm):
    email = EmailField("Placeholder")
    priority = 0
    
class PhoneForm(FlaskForm):
    phone = TelField("Placeholder")
    priority = 0

class CompleteForm(FlaskForm):
    text_entries = FieldList(FormField(TextForm))
    select_entries = FieldList(FormField(SelectForm))
    multi_entries = FieldList(FormField(MultiForm))
    email_entries = FieldList(FormField(EmailForm))
    phone_entries = FieldList(FormField(PhoneForm))
    submit = SubmitField("Submit")