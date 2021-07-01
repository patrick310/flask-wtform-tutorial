"""Routing."""
from flask import current_app as app
from flask import redirect, render_template, url_for, request, flash
import json
import csv
import os
import os.path
import uuid
from werkzeug.utils import secure_filename
from .forms import SelectForm, TextForm, EmailForm, PhoneForm, CompleteForm
from datetime import datetime
from flask import send_from_directory, abort

# DATA_DIRECTORY = os.getenv('DATA_DIRECTORY')
DATA_DIRECTORY = "C:/Users/hamilka/Downloads/flask-wtforms-survey/Data/"
SURVEY_DIRECTORY = os.path.join(DATA_DIRECTORY, "surveys/")
RESPONSE_DIRECTORY = os.path.join(DATA_DIRECTORY, "results/")
TEMP_DIRECTORY = os.path.join(DATA_DIRECTORY, "temp/")

API_KEY = 123

ALLOWED_EXTENSIONS = {'json'}

# Home Page
@app.route('/')
def survey_home():
    surveys = []
    for file in os.listdir(SURVEY_DIRECTORY):
        surveys.append([file.replace('.json', ''), get_survey_title(file)])
    return render_template(
        "home.jinja2",
        surveys=surveys,
        title="Surveys"
    )


"""
Generate Survey
"""
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
            phone_data.append(field["key"])
    return phone_data

# Format phone questions for survey
def get_phone_entries(file):
    phone_data = get_phone_data_from_custom_questions(file)
    all_phone_items = []
    for item in phone_data:
        phone_id = uuid.uuid1()
        phone_entry = PhoneForm()
        phone_entry.phone.label = item
        phone_entry.phone.name = item
        phone_entry.phone.id = phone_id
        all_phone_items.append(phone_entry)
    return all_phone_items

# Get email questions
def get_email_data_from_custom_questions(file):
    type = "email"
    email_data = []
    custom_questions = get_custom_questions(file)
    for field in custom_questions["fields"]:
        if field["type"] == type:
            email_data.append(field["key"])  
    return email_data

# Format email questions for survey
def get_email_entries(file):
    email_data = get_email_data_from_custom_questions(file)
    all_email_items = []
    for item in email_data:
        email_id = uuid.uuid1()
        email_entry = EmailForm()
        email_entry.email.label = item
        email_entry.email.name = item
        email_entry.email.id = email_id
        all_email_items.append(email_entry)
    return all_email_items

# Get text questions
def get_text_data_from_custom_questions(file):
    type = "text"
    text_data = []
    custom_questions = get_custom_questions(file) 
    for field in custom_questions["fields"]:
        if field["type"] == type:
            text_data.append(field["key"])       
    return text_data

# Format text questions for survey
def get_text_entries(file):
    text_data = get_text_data_from_custom_questions(file)
    all_text_items = []
    for item in text_data:
        text_id = uuid.uuid1()
        text_entry = TextForm()
        # TO DO: Finish refactoring code to allow required flag to be set
        # text_entry.text.flags.required = True
        text_entry.text.label = item
        text_entry.text.name = item
        text_entry.text.id = text_id
        all_text_items.append(text_entry)    
    return all_text_items

# Get select questions
def get_select_data_from_custom_questions(file):
    type = "select"
    select_data = []
    custom_questions = get_custom_questions(file)
    for field in custom_questions["fields"]:
        if field["type"] == type:
            select_data.append({field["key"]: field["data_list"]})
    return select_data

# Format select questions for survey
def get_select_entries(file):
    select_data = get_select_data_from_custom_questions(file)
    all_select_items = []
    for select_dict in select_data:
        for k, v in select_dict.items():
            select_id = uuid.uuid1()   # allows for multiple selects
            select_entry = SelectForm()
            select_entry.select.label = k
            select_entry.select.name = k
            select_entry.id = select_id
            select_entry.select.choices = v
            all_select_items.append(select_entry)
    return all_select_items

# Get survey title    
def get_survey_title(file):
    entries = get_custom_questions(file)
    for entry in entries["fields"]:
        if entry["type"] == "title":
            return entry["key"]
    return "Survey"

# Generate survey        
@app.route('/enter/<string:name>', methods=['GET','POST'])
def create_survey(name=None):
    file = name + '.json'
    if os.path.isfile(os.path.join(SURVEY_DIRECTORY, file)):
        
        form = CompleteForm()
        form.select_entries = get_select_entries(file)
        form.text_entries = get_text_entries(file)
        form.email_entries = get_email_entries(file)
        form.phone_entries = get_phone_entries(file)
        
        title = get_survey_title(file)

        # TO DO: Question Priority
        # TO DO: Multiselect Questions
        # TO DO: Flag for required response
        
        if form.validate_on_submit():
            if request.method == 'POST':
                with open(RESPONSE_DIRECTORY + name + '_results.json') as f:    
                    data = json.load(f)
                    
                # add new survey response data and date
                response = request.form.to_dict()
                new_key = response.pop('csrf_token')
                data[new_key] = response
                now = datetime.now()
                data[new_key]['date'] = now.strftime("%m/%d/%y")
                
                with open(RESPONSE_DIRECTORY + name + '_results.json', 'w') as f:
                    json.dump(data, f)
            return redirect(url_for("submitted"))
        
    else:
        abort(404)
    
    return render_template(
        "survey.jinja2",
        form=form,
        name=name,
        title=title
    )    
"""
End Generate Survey
"""     


"""
Download File
"""
# Convert json file to csv
def convert_csv(file):
    original_file = file.replace('.csv', '.json')
    f = open(os.path.join(RESPONSE_DIRECTORY, original_file), 'r')
    responses = json.load(f)
    f.close()
    
    key = list(responses.keys())[0]
    keys = list(responses[key].keys())
    
    f = open(os.path.join(RESPONSE_DIRECTORY, file), "w", newline='')
    
    try:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for k in list(responses.keys()):
            writer.writerow(responses[k])
        """
        for data in responses:
            writer.writerow(data)
        """
    except IOError:
        print("I/O error")
    f.close()   
    return 1

# TO DO: admin homepage, download data for each survey, this route is only a link not directly accessed
# download json or csv file
@app.route('/get-files/<int:key>/<path:path>',methods = ['GET','POST'])
def download_file(key=None, path=None):

    if key == API_KEY:
        if '.csv' in path:
            convert_csv(path)
    
        """Download a file."""
        try:
            return send_from_directory(RESPONSE_DIRECTORY, path, as_attachment=True, cache_timeout=0)
            #redirect(url_for("downloaded"))
            
        except FileNotFoundError:
            abort(404)
    else:
        abort(404)        
"""
End Download File
"""

# TO DO: delete data?
# Delete survey file
@app.route('/delete/<int:key>/<string:name>', methods=["GET", "POST"])
def delete_file(key=None, name=None):
    survey = name + '.json'
    if key == API_KEY:
        if request.method == "POST":
            if 'Cancel' in request.form:
                return redirect(url_for("survey_home"))
            elif 'Continue' in request.form:
                if os.path.exists(os.path.join(SURVEY_DIRECTORY, survey)):
                    os.remove(os.path.join(SURVEY_DIRECTORY, survey))
                    return redirect(url_for("deleted"))
                else:
                    abort(404)

    else:
        abort(404)
    return render_template(
            "delete.jinja2",
            title="Delete Survey",
            file=survey
        )    
        
"""
Upload Survey File
"""
# Check if file type is allowed
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Upload file
# TO DO: Check if new survey is loadable i.e. json is loadable
@app.route('/upload', methods=['GET','POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for("upload_file"))
        elif file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if not os.path.isfile(os.path.join(SURVEY_DIRECTORY, filename)):
                file.save(os.path.join(SURVEY_DIRECTORY, filename))
                results = filename.replace('.json', '')
                results = results + '_results.json'
                # create results file
                with open(os.path.join(RESPONSE_DIRECTORY, results), 'w') as f:
                    f.write('{}')
                return redirect(url_for("uploaded"))
            else:
                # TO DO: if file exists, add line letting admin know file already exists
                file.save(os.path.join(TEMP_DIRECTORY, filename))
                return redirect(url_for("update_file", file=filename))
        else:
            abort(404)
    return render_template(
        "upload.jinja2",
        title="Upload Survey"
    )

@app.route("/update/<string:file>", methods=["GET","POST"])
def update_file(file):
    if request.method=="POST":
        if 'Cancel' in request.form:
            if os.path.exists(os.path.join(TEMP_DIRECTORY, file)):
                os.remove(os.path.join(TEMP_DIRECTORY, file))
            return redirect(url_for("survey_home"))
        elif 'Continue' in request.form:
            # TO DO: Update response file to handle additional fields
            if os.path.exists(os.path.join(TEMP_DIRECTORY, file)):
                os.replace(os.path.join(TEMP_DIRECTORY, file), os.path.join(SURVEY_DIRECTORY, file))
            return redirect(url_for("updated"))
    return render_template(
        "update.jinja2",
        title="Update Survey",
        file=file
    )
"""
End Upload Survey File
"""

def get_entry_count(file):
    f = open(os.path.join(RESPONSE_DIRECTORY, file))
    responses = json.load(f)
    return len(responses)

def get_response_date(file):
    f = open(os.path.join(RESPONSE_DIRECTORY, file))
    responses = json.load(f)
    length = len(responses) 
    keys = list(responses.keys())
    if length > 0:
        return responses[keys[length-1]]['date']
    else:
        return 'N/A'

# TO DO: Figure out basic authorization              
@app.route("/admin", methods=["GET", "POST"])
def admin():
    surveys = []
    for file in os.listdir(SURVEY_DIRECTORY):
        results = file.replace(".json", "_results.json")
        surveys.append([file.replace('.json', ''), 
                        get_survey_title(file), 
                        get_entry_count(results),
                        get_response_date(results)])
    return render_template(
        "admin.jinja2",
        title="Admin Homepage",
        surveys=surveys,
        key=API_KEY
    )


"""
Success Functions
"""
# TO DO: Figure out how to give success page for downloading a file
@app.route("/downloaded")
def downloaded():
    return render_template(
        "success.jinja2",
        text="Your file has been downloaded",
        template="success-template"
    )

# Succesful survey submission
@app.route("/submitted", methods=["GET", "POST"])
def submitted():
    return render_template(
        "success.jinja2",
        text="Your response has been submitted",
        template="success-template"
    )

# Succesful survey upload
@app.route("/uploaded", methods=["GET", "POST"])
def uploaded():
    return render_template(
        "success.jinja2",
        text="Your survey has been uploaded",
        template="success-template"
    )

# Successful survey update
@app.route("/updated", methods=["GET", "POST"])
def updated():
    return render_template(
        "success.jinja2",
        text="Your survey has been updated",
        template="success-template"
    )

# Succesful survey deletion
@app.route("/deleted", methods=["GET", "POST"])
def deleted():
    return render_template(
        "success.jinja2",
        text="Your survey has been deleted",
        template="success-template"
    )
"""
End Success Functions
"""