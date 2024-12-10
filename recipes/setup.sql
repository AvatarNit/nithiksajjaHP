
DROP TABLE IF EXISTS recipes;
DROP TABLE IF EXISTS admins;
DROP TABLE IF EXISTS history;
DROP TABLE IF EXISTS ingredients;

CREATE TABLE IF NOT EXISTS recipes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    picName TEXT NOT NULL,
    videoUrl TEXT,
    ingredients TEXT NOT NULL,
    instructions TEXT NOT NULL,
    cookTime INTEGER,
    servings INTEGER,
    category TEXT,
    classification TEXT,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    passwords TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aName TEXT NOT NULL,
    action TEXT NOT NULL,
    recipeNum INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    picLocation TEXT NOT NULL
);

INSERT INTO recipes (name,picName,videoUrl,ingredients,instructions,cookTime,servings,category,classification, description) VALUES ("Lemon Rice", "/static/food/lemon rice.png", "https://www.youtube.com/embed/DVoTi4mve2U?si=dUAFAX9vKypsOGXX", "1_Cup_Peanuts,5_Chilies,8_Curry Leaves,1_tsp_Jeera,1_tsp_Chana Dal,1_tsp_Mustard Seeds,1_tsp_Urad Dal,1_tsp_Turmeric,Lemon Extract,Salt,2_Cup_Cooked Rice", "1. Break up the rice._2. Heat oil in a pan._3. Fry peanuts until golden._4. Add Chana Dal, Jeera, Mustard Seeds, and Urad Dal. Mix._5. Add Curry Leaves and Chilies. Mix._6. Add turmeric. Mix._7. Add rice. Mix well on low heat._8. Add lemon extract and salt to taste._9. Enjoy!",15,2,"Breakfast","Veg", "Lemon Rice is a South Indian rice dish with lemon and spices");
INSERT INTO admins (username, passwords) VALUES ("NITHIK", "704090");
INSERT INTO history (aName, action, recipeNum) VALUES ("NITHIK", "Create",1);
INSERT INTO ingredients (name,picLocation) VALUES ("Chana Dal", "/static/ingredients/chana_dal.png");
INSERT INTO ingredients (name,picLocation) VALUES ("Chilies", "/static/ingredients/chilies.png");
INSERT INTO ingredients (name,picLocation) VALUES ("Cooked Rice", "/static/ingredients/cooked_rice.png");
INSERT INTO ingredients (name,picLocation) VALUES ("Curry Leaves", "/static/ingredients/curry_leaves.png");
INSERT INTO ingredients (name,picLocation) VALUES ("Jeera", "/static/ingredients/jeera.png");
INSERT INTO ingredients (name,picLocation) VALUES ("Lemon Extract", "/static/ingredients/lemon_extract.png");
INSERT INTO ingredients (name,picLocation) VALUES ("Mustard Seeds", "/static/ingredients/mustard_seeds.png");
INSERT INTO ingredients (name,picLocation) VALUES ("Peanuts", "/static/ingredients/peanuts.png");
INSERT INTO ingredients (name,picLocation) VALUES ("Salt", "/static/ingredients/salt.png");
INSERT INTO ingredients (name,picLocation) VALUES ("Turmeric", "/static/ingredients/turmeric.png");
INSERT INTO ingredients (name,picLocation) VALUES ("Urad Dal", "/static/ingredients/urad_dal.png");