from flask import Flask, render_template, request, redirect, session, flash, jsonify
from google.cloud import datastore
from flask.sessions import SessionInterface, SessionMixin
import rqueries as rq
import datetime
import os

# Custom session interface for Google Datastore
class DatastoreSession(dict, SessionMixin):
    def __init__(self, initial=None, sid=None):
        super().__init__(initial or {})
        self.sid = sid
        self.modified = False


class DatastoreSessionInterface(SessionInterface):
    def __init__(self, client=None, kind='Session'):
        self.client = client or datastore.Client()
        self.kind = kind

    def generate_sid(self):
        from uuid import uuid4
        return str(uuid4())

    def get_session(self, sid):
        # Fetch the session from Google Datastore
        key = self.client.key(self.kind, sid)
        entity = self.client.get(key)
        if entity:
            return DatastoreSession(initial=dict(entity), sid=sid)
        return None

    def save_session(self, app, session, response):
        if not session:
            # Delete session from Datastore if it's empty
            key = self.client.key(self.kind, session.sid)
            self.client.delete(key)
            return

        # Save the session in Google Datastore
        entity = datastore.Entity(key=self.client.key(self.kind, session.sid))
        for key, value in session.items():
            if key == "_flashes" and isinstance(value, list):
                # Convert list of tuples to a list of strings for storage
                entity[key] = [f"{category}:{message}" for category, message in value]
            elif isinstance(value, tuple):
                # Convert tuple to string
                entity[key] = str(value)
            elif isinstance(value, list):
                # Convert lists with tuples (except `_flashes`) to a compatible format
                if any(isinstance(item, tuple) for item in value):
                    entity[key] = [str(item) for item in value]
                else:
                    entity[key] = value
            else:
                entity[key] = value

        entity['modified'] = datetime.datetime.utcnow()
        self.client.put(entity)


    def open_session(self, app, request):
        sid = request.cookies.get(app.config["SESSION_COOKIE_NAME"])
        if not sid:
            sid = self.generate_sid()
            return DatastoreSession(sid=sid)

        session = self.get_session(sid)
        if session:
            # Convert `_flashes` back to tuples
            if "_flashes" in session:
                session["_flashes"] = [
                    tuple(flash.split(":", 1)) for flash in session["_flashes"]
                ]
            return session

        return DatastoreSession(sid=sid)

app = Flask(__name__)
app.secret_key = "704090s4N"

# Set up Google Datastore as the session backend
datastore_client = datastore.Client()
app.session_interface = DatastoreSessionInterface(client=datastore_client)


# Configure Session
app.config["SERVER_NAME"] = "nithiksajja.com"
app.config["SESSION_TYPE"] = 'filesystem'
UPLOAD_FOLDER = 'static/food'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# General Routes

@app.route("/",subdomain="recipes", methods=["GET","POST"])
def index():
    if request.method == "POST":
        result = rq.login(request.form.get("name"),request.form.get("pass"))
        if result:
            flash(f"Welcome {request.form.get('name')}, you are successfully logged in", "success")
            session["admin"] = "T"
            session["name"] = request.form.get('name')
            session["password"] = request.form.get("pass")
        else:
            flash(f"ERROR: Wrong information provided please try again", "error")
            return redirect("/admin")
    displayInfo = rq.get_display_info()
    return render_template("index.html", displayInfo=displayInfo)

# Recipe Related Routes

@app.route("/viewRecipes",subdomain="recipes", methods=["GET", "POST"])
def viewRecipes():
    if request.method == "POST":
        filterCategory = request.form.get('category', "Meal Type")
        filterClass = request.form.get("class", "Requirements")
        displayInfo = rq.filter(filterCategory, filterClass)
    else:
        displayInfo = rq.get_display_info()
        print(displayInfo)
    categories = rq.get_categories()
    return render_template("viewRecipes.html", displayInfo=displayInfo, categories=categories)

@app.route("/addRecipe",subdomain="recipes", methods=["GET", "POST"])
def addRecipe():
    if request.method == "GET":
        return render_template("addRecipe.html")
    elif request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        videoUrl = request.form.get("videoUrl", None)
        cookTime = request.form.get("cookTime", None)
        servings = request.form.get("servings", None)
        category = request.form.get("category", None)
        classification = request.form.get("classification", None)
        instructions=""
        ingredients=""
        for i in range(1,100):
            if request.form.get(f"instructions-{i}", False):
                instructions = instructions + f"_{i}. " + request.form.get(f"instructions-{i}")
            else:
                break
        for i in range(1,100):
            if request.form.get(f"ingredientsName-{i}", False):
                ingredients = f"{ingredients},{request.form.get('ingredientsNum-' + str(i))}_{request.form.get('ingredientsMeasure-' + str(i))}_{request.form.get('ingredientsName-' + str(i))}"
            else:
                break
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            picName = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(picName)

            if rq.addRecipe(name, description, picName, instructions, ingredients, videoUrl, cookTime, servings, category, classification):
                flash(f"Successfully added {name} to the database", "success")
                return redirect("/")


@app.route("/viewRecipe/<name>",subdomain="recipes")
def viewRecipe(name):
    recipe = rq.get_recipe_by_name(name)
    current_recipe = session.get('currentRecipe')
    for i in range(0, len(recipe["ingredients"])):
        recipe["ingredients"][i].append(rq.get_ingredient_image(recipe["ingredients"][i][-1]))
        recipe["ingredients"][i].insert(0, recipe["ingredients"][i][-2].replace(" ", "_"))
    # return recipe
    return render_template("viewRecipe.html", recipe=recipe, current_recipe=current_recipe)

@app.route('/toggle_favorite',subdomain="recipes", methods=['POST'])
def toggle_favorite():
    data = request.json
    recipe_name = data.get('recipe_name')
    if session.get('currentRecipe') == recipe_name:
        session['currentRecipe'] = None
    else:
        session['currentRecipe'] = recipe_name
    return jsonify(status='success')


@app.route("/deleteRecipe/<name>",subdomain="recipes", methods=['POST', "GET"])
def deleteRecipe(name):
    if request.method == "POST":
        if session.get('name') == request.form.get('adminName') and name == request.form.get('recipeName'):
            if rq.delete_recipe(name):
                flash(f"Successfully deleted {name} from the database", "success")
                return redirect("/viewRecipes")
            else:
                flash(f"ERROR: Failed to delete {name} from the database", "error")
                return redirect("/viewRecipes")
        else:
            flash(f"ERROR: You are not authorized to delete this recipe", "error")
            return redirect("/viewRecipes")
    else:
        return render_template("deleteRecipe.html", name=name)

# History Related routes

@app.route("/history",subdomain="recipes")
def history():
    history = rq.get_history()
    reHistory = history[::-1]
    return render_template("history.html", history=reHistory)

@app.route("/adminHistory/<int:id>",subdomain="recipes")
def adminHistory(id):
    adminInfo = rq.get_admin_info_by_id(id)
    history = rq.get_history_by_name(adminInfo["username"])
    return render_template("history.html", history=history)

# Admin Account Related Routes

@app.route("/admin",subdomain="recipes")
def admin():
    return render_template("admin.html")

@app.route("/logout",subdomain="recipes")
def logout():
    name=session.get("name")
    session.clear()
    flash(f"Successfully Logged Out { name }", "success")
    return redirect("/")

@app.route("/addAcc",subdomain="recipes")
def addAcc():
    return render_template("addAcc.html")

@app.route("/viewAcc",subdomain="recipes", methods=["GET","POST"])
def viewAcc():
    if request.method == "POST":
        if request.form.get("action") == "A":
            name = request.form.get("name")
            password = request.form.get("pass")
            if rq.addAccount(name,password):
                flash(f"Successfully created account for { name }", "success")
            else:
                flash(f"ERROR: Account for { name } was not created", "error")
                return redirect("/addAcc")
        elif request.form.get("action") == "E":
            name = request.form.get("name")
            password = request.form.get("pass")
            id = request.form.get("id")
            if rq.editAccount(name,password,id):
                flash(f"Successfully saved changes for { name }'s account", "success")
            else:
                flash(f"ERROR: Changes for { name }'s account were not saved", "error")
        elif request.form.get("action") == "D":
            accName = request.form.get("accName") + ""
            aName = request.form.get("aName")
            id = request.form.get("id")
            adminInfo = rq.get_admin_info_by_id(id)
            if (accName == adminInfo["username"]) and (aName == session.get("name")):
                if rq.delete_acc_by_id(id):
                    flash(f"Account {accName} was deleted by {session.get('name')}", "success")
                else:
                    flash(f"ERROR: Account {accName} was not deleted", "error")
            else:
                flash(f"ERROR: Account {accName} was not deleted Wrong Information", "error")

    adminInfo = rq.get_admin_info()
    return render_template("viewAcc.html", adminInfo=adminInfo)

@app.route("/editAcc/<int:id>",subdomain="recipes")
def editAcc(id):
    adminInfo = rq.get_admin_info_by_id(id)
    return render_template("editAcc.html", adminInfo=adminInfo)

@app.route("/delAcc/<int:id>",subdomain="recipes")
def delAcc(id):
    adminInfo = rq.get_admin_info_by_id(id)
    return render_template("delAcc.html", adminInfo=adminInfo)


# Conversions

@app.route("/convert",subdomain="recipes")
def convert():
    return render_template("convert.html")