from cs50 import SQL
from datetime import datetime

homeDB = SQL("sqlite:///home.db")

# Feedback Database

def sendMessage(fName, lName, contact, message, time):
    sql = """INSERT INTO feedback (fName, lName, contact, message, time) VALUES (?, ?, ?, ?, ?)"""
    return homeDB.execute(sql, fName, lName, contact, message, time)

def get_current_datetime():
    now = datetime.now()
    formatted_datetime = now.strftime("%I:%M %p %m/%d/%Y").lstrip('0').replace('/0', '/')
    return formatted_datetime

def get_messages():
    sql="""SELECT * FROM feedback ORDER BY id DESC"""
    return homeDB.execute(sql)

def marked_read(id):
    sql="""UPDATE feedback SET read=0 WHERE id=?"""
    return homeDB.execute(sql,id)

def get_message_by_id(id):
    sql="""SELECT * FROM feedback WHERE id=?"""
    return homeDB.execute(sql,id)[0]

def delete_message_by_id(id):
    sql="""DELETE FROM feedback WHERE id=?"""
    return homeDB.execute(sql,id)
def message_count():
    sql="""SELECT COUNT(*) FROM feedback WHERE read=1"""
    return homeDB.execute(sql)[0]["COUNT(*)"]

# Admin Database

def get_admin_info():
    sql = """SELECT * FROM admins"""
    return homeDB.execute(sql)

def login(name, password):
    adminInfo = get_admin_info()
    for i in range(len(adminInfo)):
        if adminInfo[i]["username"] == name and adminInfo[i]["passwords"] == password:
            return True
    return False

def addAccount(name,password):
    sql="""INSERT INTO admins (username, passwords) VALUES (?,?)"""
    return homeDB.execute(sql,name,password)

def get_admin_info_by_id(id):
    sql="""SELECT * FROM admins WHERE id=?"""
    return homeDB.execute(sql,id)[0]

def editAccount(name,password,id):
    sql="""UPDATE admins SET username=?, passwords=? WHERE id=?"""
    return homeDB.execute(sql,name,password,id)

def delete_acc_by_id(id):
    sql="""DELETE FROM admins WHERE id=?"""
    return homeDB.execute(sql,id)

# History Database

def get_history():
    sql="""SELECT * FROM history"""
    return homeDB.execute(sql)

def get_history_by_name(name):
    sql="""SELECT * FROM history WHERE aName=?"""
    return homeDB.execute(sql,name)


def add_history(name,action, msg):
    sql="""INSERT INTO history (aName,action,msg) VALUES (?,?,?)"""
    return homeDB.execute(sql,name,action,msg)
