from flask import redirect, render_template, url_for, request
import json
import os
import os.path
from .forms import CompleteForm
from datetime import datetime
from flask import abort
from flask import Blueprint
from . import build_survey as build

# DATA_DIRECTORY = os.getenv('DATA_DIRECTORY')
DATA_DIRECTORY = "C:/Users/hamilka/Downloads/mbusi_surveys/data/"
SURVEY_DIRECTORY = os.path.join(DATA_DIRECTORY, "surveys/")
RESPONSE_DIRECTORY = os.path.join(DATA_DIRECTORY, "responses/")

# Blueprint configuration
survey_bp = Blueprint(
    'survey_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

# Survey home page
@survey_bp.route('/')
def survey_home():
    surveys = []
    for file in os.listdir(SURVEY_DIRECTORY):
        surveys.append([file.replace('.json', ''), build.get_survey_title(file)])
    return render_template(
        "home.jinja2",
        surveys=surveys,
        title="Surveys"
    )

# Generate survey        
@survey_bp.route('/enter/<string:name>', methods=['GET','POST'])
def create_survey(name=None):
    file = name + '.json'
    if os.path.isfile(os.path.join(SURVEY_DIRECTORY, file)):
        
        form = CompleteForm()
        form.select_entries = build.get_select_entries(file)
        form.text_entries = build.get_text_entries(file)
        form.email_entries = build.get_email_entries(file)
        form.phone_entries = build.get_phone_entries(file)
        # TO DO: Fix multiselect display
        form.multi_entries = build.get_multi_entries(file)
        
        title = build.get_survey_title(file)
        
        # Get total question count
        size = form.select_entries.__len__()
        size = size + form.text_entries.__len__()
        size = size + form.email_entries.__len__()
        size = size + form.phone_entries.__len__()
        size = size + form.multi_entries.__len__()

        # TO DO: Question Priority
        # TO DO: Flag for required response
        
        if form.validate_on_submit():
            if request.method == 'POST':
                with open(RESPONSE_DIRECTORY + name + '_responses.json') as f:    
                    data = json.load(f)
                    
                # add new survey response data and date
                # TO DO: Figure out how to get all multiselect selections
                response = request.form.to_dict()
                #response = request.form.getlist()
                
                for multi_entry in form.multi_entries:
                    values = request.form.getlist(multi_entry.multi.name)
                    response[multi_entry.multi.name] = values
                    
    
                new_key = response.pop('csrf_token')
                data[new_key] = response
                now = datetime.now()
                data[new_key]['date'] = now.strftime("%m/%d/%y")
                
                with open(RESPONSE_DIRECTORY + name + '_responses.json', 'w') as f:
                    json.dump(data, f)
            return redirect(url_for("survey_bp.submitted"))
        
    else:
        abort(404)
    
    return render_template(
        "survey.jinja2",
        form=form,
        name=name,
        title=title,
        size=size
    )       

# Succesful survey submission
@survey_bp.route("/submitted", methods=["GET", "POST"])
def submitted():
    return render_template(
        "success.jinja2",
        text="Your response has been submitted",
        template="success-template"
    )