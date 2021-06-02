"""Routing."""
from flask import current_app as app
from flask import redirect, render_template, url_for, request
import json
import csv
import os
import os.path
from .forms import SignupForm

from flask import Flask, send_file, send_from_directory, abort

DATA_DIRECTORY = os.getenv('DATA_DIRECTORY')
data_file_path = os.path.join(os.path.abspath(__file__), DATA_DIRECTORY, 'data.json')


@app.route("/")
def home():
    """Landing page."""
    return render_template(
        "index.jinja2",
        template="home-template",
        title="Survey Home"
    )


@app.route("/signup", methods=["GET", "POST"])
def signup():
    #logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
    #logging.warning('This will get logged to a file')
    """User sign-up form for giveaway."""
    form = SignupForm()
    if form.validate_on_submit():
        if request.method == 'POST':
            with open(data_file_path) as f:    
                data = json.load(f)
            data.append(request.form.to_dict())
            with open(data_file_path, 'w') as f:
                json.dump(data, f)
        return redirect(url_for("success"))
    return render_template(
        "signup.jinja2",
        form=form,
        template="form-template",
        title="Signup Form"
    )


@app.route("/success", methods=["GET", "POST"])
def success():
    """Generic success page upon form submission."""
    return render_template(
        "success.jinja2",
        template="success-template"
    )

def convert_csv():
    f = open(data_file_path, 'r')
    responses = json.load(f)
    f.close()
    
    keys = list(responses[0].keys())
    
    f = open(data_file_path, "w", newline='')
    
    try:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for data in responses:
            writer.writerow(data)
    except IOError:
        print("I/O error")
    f.close()   
    return 1

@app.route('/get-files/<int:key>/<path:path>',methods = ['GET','POST'])
def get_files(key=None, path=None):

    if key == 123:
        if '.csv' in path:
            convert_csv()
    
        """Download a file."""
        try:
            return send_from_directory(DATA_DIRECTORY, path, as_attachment=True, cache_timeout=0)
        
        except FileNotFoundError:
            abort(404)
    else:
        abort(404)
