from flask import redirect, render_template, url_for, request, flash
import json
import csv
import os
import os.path
from werkzeug.utils import secure_filename
from flask import send_from_directory, abort, Blueprint
from flask_login import login_required

# DATA_DIRECTORY = os.getenv('DATA_DIRECTORY')
DATA_DIRECTORY = "C:/Users/hamilka/Downloads/mbusi_surveys/data/"
SURVEY_DIRECTORY = os.path.join(DATA_DIRECTORY, "surveys/")
RESPONSE_DIRECTORY = os.path.join(DATA_DIRECTORY, "responses/")
TEMP_DIRECTORY = os.path.join(DATA_DIRECTORY, "temp/")

ALLOWED_EXTENSIONS = {'json'}

# Blueprint Configuration
admin_bp = Blueprint(
    'admin_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

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
            
    except IOError:
        print("I/O error")
    f.close()   
    return 1

# download json or csv file
@admin_bp.route('/get-files/<path:path>',methods = ['GET','POST'])
@login_required
def download_file(key=None, path=None):
    if '.csv' in path:
        convert_csv(path)

    try:
        return send_from_directory(RESPONSE_DIRECTORY, path, as_attachment=True, cache_timeout=0)
        #redirect(url_for("downloaded"))
        
    except FileNotFoundError:
        abort(404)        


# TO DO: delete data?
# Delete survey file
@admin_bp.route('/delete/<string:name>', methods=["GET", "POST"])
@login_required
def delete_file(key=None, name=None):
    survey = name + '.json'
    if request.method == "POST":
        if 'Cancel' in request.form:
            return redirect(url_for("survey_bp.survey_home"))
        elif 'Continue' in request.form:
            if os.path.exists(os.path.join(SURVEY_DIRECTORY, survey)):
                os.remove(os.path.join(SURVEY_DIRECTORY, survey))
                return redirect(url_for("admin_bp.deleted"))
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
@admin_bp.route('/upload', methods=['GET','POST'])
@login_required
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
            return redirect(url_for("admin_bp.upload_file"))
        elif file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if not os.path.isfile(os.path.join(SURVEY_DIRECTORY, filename)):
                file.save(os.path.join(SURVEY_DIRECTORY, filename))
                responses = filename.replace('.json', '')
                responses = responses + '_responses.json'
                # create response file
                with open(os.path.join(RESPONSE_DIRECTORY, responses), 'w') as f:
                    f.write('{}')
                return redirect(url_for("admin_bp.uploaded"))
            else:
                # TO DO: if file exists, add line letting admin know file already exists
                file.save(os.path.join(TEMP_DIRECTORY, filename))
                return redirect(url_for("admin_bp.update_file", file=filename))
        else:
            abort(404)
    return render_template(
        "upload.jinja2",
        title="Upload Survey"
    )

@admin_bp.route("/update/<string:file>", methods=["GET","POST"])
@login_required
def update_file(file):
    if request.method=="POST":
        if 'Cancel' in request.form:
            if os.path.exists(os.path.join(TEMP_DIRECTORY, file)):
                os.remove(os.path.join(TEMP_DIRECTORY, file))
            return redirect(url_for("admin_bp.upload_file"))
        elif 'Continue' in request.form:
            # TO DO: Update response file to handle additional fields? If saving to sqlite, will need to be handled during CSV conversion only
            if os.path.exists(os.path.join(TEMP_DIRECTORY, file)):
                os.replace(os.path.join(TEMP_DIRECTORY, file), os.path.join(SURVEY_DIRECTORY, file))
            return redirect(url_for("admin_bp.updated"))
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

# Get data from file
def get_custom_questions(file):
    path = os.path.join(SURVEY_DIRECTORY, file)
    with open(path, "r") as f:
        data = json.load(f)
    return data

# Get survey title    
def get_survey_title(file):
    entries = get_custom_questions(file)
    for entry in entries["fields"]:
        if entry["type"] == "title":
            return entry["key"]
    return "Survey"
             
@admin_bp.route("/", methods=["GET", "POST"])
@login_required
def admin():
    surveys = []
    for file in os.listdir(SURVEY_DIRECTORY):
        responses = file.replace(".json", "_responses.json")
        surveys.append([file.replace('.json', ''), 
                        get_survey_title(file), 
                        get_entry_count(responses),
                        get_response_date(responses)])
    return render_template(
        "admin.jinja2",
        title="Admin Homepage",
        surveys=surveys,
    )

"""
Success Functions
"""
# TO DO: Figure out how to give success page for downloading a file
@admin_bp.route("/downloaded")
def downloaded():
    return render_template(
        "success.jinja2",
        text="Your file has been downloaded",
        template="success-template"
    )

# Succesful survey upload
@admin_bp.route("/uploaded", methods=["GET", "POST"])
def uploaded():
    return render_template(
        "success.jinja2",
        text="Your survey has been uploaded",
        template="success-template"
    )

# Successful survey update
@admin_bp.route("/updated", methods=["GET", "POST"])
def updated():
    return render_template(
        "success.jinja2",
        text="Your survey has been updated",
        template="success-template"
    )

# Succesful survey deletion
@admin_bp.route("/deleted", methods=["GET", "POST"])
def deleted():
    return render_template(
        "success.jinja2",
        text="Your survey has been deleted",
        template="success-template"
    )
"""
End Success Functions
"""