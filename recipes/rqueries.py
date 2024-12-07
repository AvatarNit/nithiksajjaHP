from cs50 import SQL
from werkzeug.security import generate_password_hash, check_password_hash

db = SQL("sqlite:///recipes.db")

# General Functions

def split_list(lst, chunk_size):
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

# Recipes Database

def get_display_info():
    sql = """SELECT name,description,picName FROM recipes"""
    result = db.execute(sql)
    # for i in range(0,10):
    #     result.append(i)
    return split_list(result,4)

def get_categories():
    sql = """SELECT DISTINCT category FROM recipes"""
    result = db.execute(sql)
    return result

def get_classes():
    sql = """SELECT DISTINCT classification FROM recipes"""
    result = db.execute(sql)
    return result

def addRecipe(name, description, picName, instructions, ingredients, videoUrl=None, cookTime=None, servings=None, category=None, classification=None):
    sql = """INSERT INTO recipes (name, description, videoUrl, cookTime, servings, category, classification, ingredients, instructions, picName) VALUES (?,?,?,?,?,?,?,?,?,?)"""
    return db.execute(sql, name, description, videoUrl, cookTime, servings, category, classification, ingredients, instructions, picName)



def filter(filterCategory, filterClass):
    if filterCategory != "Meal Type" and filterClass != "Requirements":
        sql = """SELECT name,description,picName FROM recipes WHERE category=? AND classification=?"""
        result = db.execute(sql,filterCategory,filterClass)
    elif filterCategory!= "Meal Type":
        sql = """SELECT name,description,picName FROM recipes WHERE category=?"""
        result = db.execute(sql,filterCategory)
    elif filterClass!= "Requirements":
        sql = """SELECT name,description,picName FROM recipes WHERE classification=?"""
        result = db.execute(sql,filterClass)
    return split_list(result,4)

def get_recipe_by_name(name):
    sql = """SELECT * FROM recipes WHERE name=?"""
    result = db.execute(sql,name)[0]
    result["ingredients"] = split_ingredients(result["ingredients"])
    result["instructions"] = result["instructions"].split("_")
    return result

def split_ingredients(ingredientsStr):
    ingredientsList = ingredientsStr.split(",")
    ingredients = []
    for ingredient in ingredientsList:
        ingredients.append(ingredient.split("_"))
    return ingredients

# Ingedredient Database
def get_ingredient_image(name):
    sql = """SELECT picLocation FROM ingredients WHERE name=?"""
    return db.execute(sql,name)[0]["picLocation"]


def delete_recipe(name):
    sql = """DELETE FROM recipes WHERE name=?"""
    return db.execute(sql,name)
# Admin Database

def get_admin_info():
    sql = """SELECT * FROM admins"""
    return db.execute(sql)

def login(name, password):
    adminInfo = get_admin_info()
    for i in range(len(adminInfo)):
        if adminInfo[i]["username"] == name and adminInfo[i]["passwords"] == password:
            return True
    return False

def addAccount(name,password):
    sql="""INSERT INTO admins (username, passwords) VALUES (?,?)"""
    return db.execute(sql,name,password)

def get_admin_info_by_id(id):
    sql="""SELECT * FROM admins WHERE id=?"""
    return db.execute(sql,id)[0]

def editAccount(name,password,id):
    sql="""UPDATE admins SET username=?, passwords=? WHERE id=?"""
    return db.execute(sql,name,password,id)

def delete_acc_by_id(id):
    sql="""DELETE FROM admins WHERE id=?"""
    return db.execute(sql,id)

# History Database

def get_history():
    sql="""SELECT * FROM history"""
    return db.execute(sql)

def get_history_by_name(name):
    sql="""SELECT * FROM history WHERE aName=?"""
    return db.execute(sql,name)


def add_history(name,action, msg):
    sql="""INSERT INTO history (aName,action,msg) VALUES (?,?,?)"""
    return db.execute(sql,name,action,msg)