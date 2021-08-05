import json
import os
import os.path
import uuid
from .forms import SelectForm, MultiForm, TextForm, EmailForm, PhoneForm
from dotenv import load_dotenv

load_dotenv()

# DATA_DIRECTORY = os.getenv('DATA_DIRECTORY')
# DATA_DIRECTORY = "C:/Users/hamilka/Downloads/mbusi_surveys/data/"
DATA_DIRECTORY = os.environ.get("DATA_DIRECTORY")
SURVEY_DIRECTORY = os.path.join(DATA_DIRECTORY, "surveys/")

# Get data from file
def get_custom_questions(file):
    path = os.path.join(SURVEY_DIRECTORY, file)
    with open(path, "r") as f:
        data = json.load(f)
    return data

# Get phone questions
def get_phone_data_from_custom_questions(file):
    type = "phone"
    phone_data = []
    custom_questions = get_custom_questions(file)
    for field in custom_questions["fields"]:
        if field["type"] == type:
            phone_data.append({"key": field["key"],
                               "priority": field["priority"],
                               "required": field["required"]})
    return phone_data

# Format phone questions for survey
def get_phone_entries(file):
    phone_data = get_phone_data_from_custom_questions(file)
    all_phone_items = []
    for item in phone_data:
        phone_id = uuid.uuid1()
        phone_entry = PhoneForm()
        phone_entry.phone.label = item["key"]
        phone_entry.phone.name = item["key"]
        phone_entry.phone.id = phone_id
        phone_entry.priority = item["priority"]
        if item["required"] == "True":
            phone_entry.phone.flags.required = True
        all_phone_items.append(phone_entry)
    all_phone_items = sorted(all_phone_items, key=lambda k: k.priority, reverse=True) 
    return all_phone_items

# Get email questions
def get_email_data_from_custom_questions(file):
    type = "email"
    email_data = []
    custom_questions = get_custom_questions(file)
    for field in custom_questions["fields"]:
        if field["type"] == type:
            email_data.append({"key": field["key"],
                               "priority": field["priority"],
                               "required": field["required"]})  
    return email_data

# Format email questions for survey
def get_email_entries(file):
    email_data = get_email_data_from_custom_questions(file)
    all_email_items = []
    for item in email_data:
        email_id = uuid.uuid1()
        email_entry = EmailForm()
        email_entry.email.label = item["key"]
        email_entry.email.name = item["key"]
        email_entry.email.id = email_id
        email_entry.priority = item["priority"]
        if item["required"] == "True":
            email_entry.email.flags.required = True
        all_email_items.append(email_entry)
    all_email_items = sorted(all_email_items, key=lambda k: k.priority, reverse=True) 
    return all_email_items

# Get text questions
def get_text_data_from_custom_questions(file):
    type = "text"
    text_data = []
    custom_questions = get_custom_questions(file) 
    for field in custom_questions["fields"]:
        if field["type"] == type:
            text_data.append({"key": field["key"],
                              "priority": field["priority"],
                              "required": field["required"]})
    return text_data

# Format text questions for survey
def get_text_entries(file):
    text_data = get_text_data_from_custom_questions(file)
    all_text_items = []
    for item in text_data:
        text_id = uuid.uuid1()
        text_entry = TextForm()
        text_entry.text.label = item["key"]
        text_entry.text.name = item["key"]
        text_entry.text.id = text_id
        text_entry.priority = item["priority"]
        if item["required"] == "True":
            text_entry.text.flags.required = True
        all_text_items.append(text_entry)
    all_text_items = sorted(all_text_items, key=lambda k: k.priority, reverse=True) 
    return all_text_items

# Get multiselect questions
def get_multi_data_from_custom_questions(file):
    type = "checkbox"
    multi_data = []
    custom_questions = get_custom_questions(file)
    for field in custom_questions["fields"]:
        if field["type"] == type:
            multi_data.append({"key": field["key"], 
                               "data_list": field["data_list"],
                               "priority": field["priority"],
                               "required": field["required"]})
    return multi_data

# Format multiselect questions for survey
def get_multi_entries(file):
    multi_data = get_multi_data_from_custom_questions(file)
    all_multi_items = []
    for multi_dict in multi_data:
        multi_id = uuid.uuid1()
        multi_entry = MultiForm()
        multi_entry.multi.label = multi_dict["key"]
        multi_entry.multi.name = multi_dict["key"]
        multi_entry.id = multi_id
        multi_entry.multi.choices = multi_dict["data_list"]
        multi_entry.priority = multi_dict["priority"]
        if multi_dict["required"] == "True":
            multi_entry.multi.flags.required = True
        all_multi_items.append(multi_entry)
    all_multi_items = sorted(all_multi_items, key=lambda k: k.priority, reverse=True) 
    return all_multi_items

# Get select questions
def get_select_data_from_custom_questions(file):
    type = "select"
    select_data = []
    custom_questions = get_custom_questions(file)
    for field in custom_questions["fields"]:
        if field["type"] == type:
            select_data.append({"key": field["key"],
                                "data_list": field["data_list"], 
                                "priority": field["priority"], 
                                "required": field["required"]})
    return select_data

# Format select questions for survey
def get_select_entries(file):
    select_data = get_select_data_from_custom_questions(file)
    all_select_items = []
    for select_dict in select_data:
        select_id = uuid.uuid1()   # allows for multiple selects
        select_entry = SelectForm()
        select_entry.select.label = select_dict["key"]
        select_entry.select.name = select_dict["key"]
        select_entry.id = select_id
        select_entry.select.choices = select_dict["data_list"]
        select_entry.priority = select_dict["priority"]
        if select_dict["required"] == "True":
            select_entry.select.flags.required = True
        all_select_items.append(select_entry)
    all_select_items = sorted(all_select_items, key=lambda k: k.priority, reverse=True) 
    return all_select_items

# Get survey title    
def get_survey_title(file):
    entries = get_custom_questions(file)
    for entry in entries["fields"]:
        if entry["type"] == "title":
            return entry["key"]
    return "Survey"