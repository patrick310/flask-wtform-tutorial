from flask import redirect, render_template, url_for, request, flash
import json
import csv
import os
import os.path
from werkzeug.utils import secure_filename
from flask import send_from_directory, abort, Blueprint
from flask_login import login_required
from dotenv import load_dotenv

load_dotenv()

# DATA_DIRECTORY = os.getenv('DATA_DIRECTORY')
DATA_DIRECTORY = os.environ.get("DATA_DIRECTORY")
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
    # load file and store json data
    original_file = file.replace('.csv', '.json')
    f = open(os.path.join(RESPONSE_DIRECTORY, original_file), 'r')
    responses = json.load(f)
    f.close()
    
    # get dictionary keys for csv header
    key = list(responses.keys())[0]
    keys = list(responses[key].keys())
    
    # open or create csv file
    f = open(os.path.join(RESPONSE_DIRECTORY, file), "w", newline='')
    
    # try writing data to csv file
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
def download_file(path=None):
    # if downloading csv file, update or create csv file
    if '.csv' in path:
        convert_csv(path)

    # try to return file 
    try:
        return send_from_directory(RESPONSE_DIRECTORY, path, as_attachment=True, cache_timeout=0)
        
    # give 404 error if unable to download file
    except FileNotFoundError:
        abort(404)    

# TO DO: Download entire data directory, zip and download        
@admin_bp.route('/download-all', methods = ['GET', 'POST'])
@login_required
def download_all():
    pass


# Delete survey file and data
@admin_bp.route('/delete/<string:name>', methods=["GET", "POST"])
@login_required
def delete_file(key=None, name=None):
    survey = name + '.json'
    if request.method == "POST":
        
        # if user does not want to delete file, redirect to survey home
        if 'Cancel' in request.form:
            return redirect(url_for("survey_bp.survey_home"))
        
        # if user wants to delete file, delete survey and response data
        elif 'Continue' in request.form:
            
            # check to make sure survey file exists, and then delete
            if os.path.exists(os.path.join(SURVEY_DIRECTORY, survey)):
                os.remove(os.path.join(SURVEY_DIRECTORY, survey))
                data = name + '_responses'
                data_json = data + '.json'
                data_csv = data + '.csv'
                
                # check for and remove json results file
                if os.path.exists(os.path.join(RESPONSE_DIRECTORY, data_json)):
                    os.remove(os.path.join(RESPONSE_DIRECTORY, data_json))
                
                # check for and remove csv results file
                if os.path.exists(os.path.join(RESPONSE_DIRECTORY, data_csv)):
                    os.remove(os.path.join(RESPONSE_DIRECTORY, data_csv))
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
        
        # if file selected and is a json file
        elif file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            # if file does not already exist
            if not os.path.isfile(os.path.join(SURVEY_DIRECTORY, filename)):
                # save file to temp folder
                file.save(os.path.join(TEMP_DIRECTORY, filename))
                
                # check if file is json loadable
                try: 
                    f = open(os.path.join(TEMP_DIRECTORY, filename), 'r')
                    survey = json.load(f)
                    f.close()
                    
                    # move file to survey folder
                    if os.path.exists(os.path.join(TEMP_DIRECTORY, filename)):
                        os.replace(os.path.join(TEMP_DIRECTORY, filename), os.path.join(SURVEY_DIRECTORY, filename))
                    
                    # create response file
                    response_file = filename.replace('.json', '')
                    response_file = response_file + '_responses.json'
                    with open(os.path.join(RESPONSE_DIRECTORY, response_file), 'w') as f:
                        f.write('{}')
                    return redirect(url_for("admin_bp.uploaded"))
                except:
                    f.close()
                    
                    # if file was not loadable, delete from temp folder
                    if os.path.exists(os.path.join(TEMP_DIRECTORY, filename)):
                        os.remove(os.path.join(TEMP_DIRECTORY, filename))
                    return redirect(url_for("admin_bp.upload_error"))
                
            # if survey file already exists, redirect to update page
            else:
                file.save(os.path.join(TEMP_DIRECTORY, filename))
                return redirect(url_for("admin_bp.update_file", file=filename))
        else:
            abort(404)
    return render_template(
        "upload.jinja2",
        title="Upload Survey"
    )

# Give user option to update file if file already exists
@admin_bp.route("/update/<string:file>", methods=["GET","POST"])
@login_required
def update_file(file):
    if request.method=="POST":
        
        # if user does not want to update survey, redirect to upload page
        if 'Cancel' in request.form:
            if os.path.exists(os.path.join(TEMP_DIRECTORY, file)):
                os.remove(os.path.join(TEMP_DIRECTORY, file))
            return redirect(url_for("admin_bp.upload_file"))
        
        # if user wants to update survey, move file to survey folder
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

# Get number of responses for a survey
def get_entry_count(file):
    f = open(os.path.join(RESPONSE_DIRECTORY, file))
    responses = json.load(f)
    return len(responses)

# Get date of last response for a survey
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
    
    # default return value if no title key is found
    return "Survey"
             
# Admin survey management homepage
@admin_bp.route("/", methods=["GET", "POST"])
@login_required
def admin():
    surveys = []
    try:
        for file in os.listdir(SURVEY_DIRECTORY):
            responses = file.replace(".json", "_responses.json")
            try:
                surveys.append([file.replace('.json', ''), 
                                get_survey_title(file), 
                                get_entry_count(responses),
                                get_response_date(responses)])
            except OSError or IOError as e:
                print(e)
    except OSError or IOError as e:
        print("No Surveys")
    return render_template(
        "admin.jinja2",
        title="Admin Homepage",
        surveys=surveys,
    )

"""
Success Functions
"""

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

# Error uploading new survey
@admin_bp.route("/upload_error")
def upload_error():
    return render_template(
        "error.jinja2",
        text="File could not be loaded, check format.",
        template="success-template"
    )
