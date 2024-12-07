from flask import Flask, render_template, request, redirect, session, flash
from google.cloud import datastore
from flask.sessions import SessionInterface, SessionMixin
import queries as q
import datetime


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


@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "POST":
        result = q.login(request.form.get("name"),request.form.get("pass"))
        if result:
            flash(f"Welcome {request.form.get('name')}, you are successfully logged in", "success")
            session["admin"] = "T"
            session["name"] = request.form.get('name')
            session["password"] = request.form.get("pass")
            # return session["admin"]
        else:
            flash(f"ERROR: Wrong information provided please try again", "error")
            return redirect("/admin")
    # return q.get_admin_info()
    session["msgCount"] = q.message_count()
    return render_template("index.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "GET":
        return render_template("contact.html")
    elif request.method == "POST":
        fName = str(request.form.get("fName"))
        lName = str(request.form.get("lName"))
        email = str(request.form.get("email"))
        phone = str(request.form.get("phone"))
        message = str(request.form.get("message"))
        
        if not email and not phone:
            flash(f"ERROR: {fName.title()} {lName.title()} did not enter an email or phone number", "error")
            return redirect("/contact")
        
        contact_info = email if email else phone
        if q.sendMessage(fName, lName, contact_info, message, q.get_current_datetime()):
            flash(f"Thank you {fName.title()} {lName.title()} for your message", "success")
        else:
            flash("ERROR: Message wasn't sent", "error")
        return redirect("/contact")

@app.route("/links")
def links():
    return render_template("links.html")

@app.route("/websites")
def website():
    return render_template("websites.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/viewMsg", methods=["GET", "POST"])
def viewMsg():
    if request.method == "POST":
        messages = q.get_messages()
        if request.form.get("action") == "D":
            nameSend = request.form.get("nameSend")
            aName = request.form.get("aName")
            messageId = request.form.get("messageId")
            message = q.get_message_by_id(messageId)
            if (nameSend == message["fName"]) and (aName == session.get("name")):
                if q.delete_message_by_id(messageId):
                    flash(f"Message by {message['fName']} was deleted by {session.get('name')}", "success")
                    q.add_history(session.get("name"),"Delete",f"Message by {message['fName']}")
                else:
                    flash(f"ERROR: Message by {message['fName']} was not deleted", "error")
            else:
                flash(f"ERROR: Message by {message['fName']} was not deleted Wrong Information", "error")
        elif request.form.get("action") == "R":
            for message in messages:
                if message["read"] == 1:
                    if request.form.get(f"check{message['id']}") == "":
                        q.marked_read(message["id"])
                        flash("Marked as Read", "success")
        
    messages = q.get_messages()
    session["msgCount"] = q.message_count()
    return render_template("viewMsg.html", feedback =messages)

@app.route("/deleteMsg/<int:id>")
def deleteMsg(id):
    message = q.get_message_by_id(id)
    return render_template("deleteMsg.html", message=message)

# History Related routes

@app.route("/history")
def history():
    history = q.get_history()
    reHistory = history[::-1]
    return render_template("history.html", history=reHistory)

@app.route("/adminHistory/<int:id>")
def adminHistory(id):
    adminInfo = q.get_admin_info_by_id(id)
    history = q.get_history_by_name(adminInfo["username"])
    return render_template("history.html", history=history)

# Admin Account Related Routes

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/logout")
def logout():
    flash(f"Successfully Logged Out { session.get("name") }", "success")
    session.clear()
    return redirect("/")

@app.route("/addAcc")
def addAcc():
    return render_template("addAcc.html")

@app.route("/viewAcc", methods=["GET","POST"])
def viewAcc():
    if request.method == "POST":
        if request.form.get("action") == "A":
            name = request.form.get("name")
            password = request.form.get("pass")
            if q.addAccount(name,password):
                flash(f"Successfully created account for { name }", "success")
            else:
                flash(f"ERROR: Account for { name } was not created", "error")
                return redirect("/addAcc")
        elif request.form.get("action") == "E":
            name = request.form.get("name")
            password = request.form.get("pass")
            id = request.form.get("id")
            if q.editAccount(name,password,id):
                flash(f"Successfully saved changes for { name }'s account", "success")
            else:
                flash(f"ERROR: Changes for { name }'s account were not saved", "error")
        elif request.form.get("action") == "D":
            accName = request.form.get("accName") + ""
            aName = request.form.get("aName")
            id = request.form.get("id")
            adminInfo = q.get_admin_info_by_id(id)
            if (accName == adminInfo["username"]) and (aName == session.get("name")):
                if q.delete_acc_by_id(id):
                    flash(f"Account {accName} was deleted by {session.get('name')}", "success")
                else:
                    flash(f"ERROR: Account {accName} was not deleted", "error")
            else:
                flash(f"ERROR: Account {accName} was not deleted Wrong Information", "error")

    adminInfo = q.get_admin_info()
    return render_template("viewAcc.html", adminInfo=adminInfo)

@app.route("/editAcc/<int:id>")
def editAcc(id):
    adminInfo = q.get_admin_info_by_id(id)
    return render_template("editAcc.html", adminInfo=adminInfo)

@app.route("/delAcc/<int:id>")
def delAcc(id):
    adminInfo = q.get_admin_info_by_id(id)
    return render_template("delAcc.html", adminInfo=adminInfo)


# @app.route("/test", subdomain="dash")
# def index_dash():
#     return "Subdomain"
#     return render_template("/site1/index.html")

if __name__ == "__main__":
    app.config["SERVER_NAME"] = "nithiksajja.com"
    app.run(debug=True)
