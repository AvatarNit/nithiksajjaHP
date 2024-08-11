from flask import Flask, render_template, request, redirect, session, flash
from flask_session import Session
import queries as q

app = Flask(__name__)
# app = Flask(__name__, subdomain_matching=True)
app.secret_key = "secretcode1234"

# Configure Session
app.config["SESSION_PERMENANT"] = False
app.config["SESSION_TYPE"] = 'filesystem'
Session(app)


@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "POST":
        result = q.login(request.form.get("name"),request.form.get("pass"))
        if result:
            flash(f"Welcome {request.form.get('name')}, you are successfully logged in", "success")
            session["admin"] = "T"
            session["name"] = request.form.get('name')
            session["password"] = request.form.get("pass")
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
        fName = request.form.get("fName")
        lName = request.form.get("lName")
        email = request.form.get("email")
        phone = request.form.get("phone")
        message = request.form.get("message")
        
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
    name=session.get("name")
    session.clear()
    flash(f"Successfully Logged Out { name }", "success")
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

# if __name__ == "__main__":
#     app.config["SERVER_NAME"] = "nithiksajja.com"
#     app.run(host="0.0.0.0", port=80, debug=True)