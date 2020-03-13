# Inititalization
from app import app
from flask import render_template, request, redirect, flash, send_from_directory, abort
import csv
import os

uploads_path        = os.path.abspath("app/static/uploads")
results             = []     # -> list, containing the whole csv file
fieldnames          = []     # -> list, containing the whole csv file except of headers
headers             = []     # -> list, containing only headers
entry_data          = []     # -> list, containing the costum entry
old_data            = []     # -> list, containing the entry before getting edited
new_data            = []     # -> list, containing the new content of the entry to be edited
global_csv_path     = ""     # -> string to save the csv_path
global_csv_filename = ""     # -> string to save the csv_filename
valid               = True   # -> boolean for the validation
add_check           = False  # -> boolean to check the add-entry-forms
edit_check          = False  # -> boolean to check the edit-entry-forms


# Functions
def valid_file(filename):
    """ A function to ensure that the uploaded file is a valid csv file. """

    valid = True

    if "." not in filename:
        valid = False
    elif filename == "":
        valid = False
    elif not filename.endswith(".csv"):
        valid = False
    
    return valid

def append_to_csv(inserts, filename):
    """ A method to append a user-generated entry to the csv file. """

    with open(filename, "a") as appending_file:
        csvwriter = csv.writer(appending_file, delimiter=";")
        csvwriter.writerow(inserts)

def entry_in_file(entry, filename):
    """ A function to ensure that the entry to be edited is in the csv file. """

    in_file = False

    with open(filename, "r") as file_search:
        file_reader = csv.reader(file_search, delimiter=";")

        for line in file_reader:
            if entry in file_reader:
                in_file = True
    
    return in_file


# Routes
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload-csv", methods=["GET", "POST"])
def upload_csv():

    # Globals
    global uploads_path
    global fieldnames
    global entry_data
    global old_data
    global new_data
    global add_check
    global edit_check
    global global_csv_path
    global global_csv_filename
    global valid

    # If a CSV file gets uploaded
    if request.method == "POST" and request.files:

        csv_file            = request.files["csv_file"]
        global_csv_filename = csv_file.filename

        # validation check
        if not valid_file(csv_file.filename):
            return redirect(request.url)
            
        else:
            
            csv_file_path   = os.path.join(uploads_path, csv_file.filename)
            global_csv_path = csv_file_path

            # Upload
            csv_file.save(csv_file_path)

            # CSV Processing
            with open(global_csv_path, "r") as uploaded_csv:
                csv_reader = csv.DictReader(uploaded_csv, delimiter=";")

                for row in csv_reader:
                    results.append(dict(row))

                fieldnames = [key for key in results[0].keys()]

                # Headers Outsourcing
                for header in results[0].keys():
                    headers.append(header)

                return redirect(request.url)

    # Entry Upload and Edit
    elif request.method == "POST":

        for header in headers:
            if header in request.form:
                add_check = True
                break
            if ("old-" + header) in request.form or \
               ("new-" + header) in request.form:
                edit_check = True
                break

        # If a custom entry gets uploaded
        if add_check == True:
            for header in headers:
                entry_data.append(request.form[header])

            append_to_csv(entry_data, global_csv_path)
            entry_data.clear()

            # CSV Updating
            with open(global_csv_path, "r") as uploaded_csv:
                csv_reader = csv.DictReader(uploaded_csv, delimiter=";")

                for row in csv_reader:
                    results.append(dict(row))

                fieldnames = [key for key in results[0].keys()]
            
        # If an entry gets edited
        if edit_check == True:
            for header in headers:
                old_data.append(request.form.get(("old-" + header)))
                new_data.append(request.form.get(("new-" + header)))


            if entry_in_file(old_data, global_csv_path):
                print("Is There!")
                # To be continued...

        # If the CSV file gets downloaded
        if request.form.get("download"):
            try:
                return send_from_directory(uploads_path,
                                           global_csv_filename,
                                           as_attachment=True)
            except FileNotFoundError:
                abort(404)


        return redirect(request.url)

    return render_template("upload-csv.html",
                            results             =             results, 
                            fieldnames          =          fieldnames, 
                            len                 =                 len, 
                            headers             =             headers,  
                            global_csv_filename = global_csv_filename,
                            valid               =               valid)