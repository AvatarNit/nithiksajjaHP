
.open home.db
.mode box



DROP TABLE IF EXISTS feedback;
DROP TABLE IF EXISTS admins;
DROP TABLE IF EXISTS history;
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fName TEXT NOT NULL,
    lName TEXT NOT NULL,
    contact TEXT NOT NULL,
    message TEXT NOT NULL,
    time TEXT NOT NULL,
    read INTEGER DEFAULT 1
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
    msg INTEGER NOT NULL
);

INSERT INTO feedback VALUES (1,"Nithik", "Sajja", "3177711201", "This website is great!","3:28 PM 05/23/2024",1);
INSERT INTO admins (username, passwords) VALUES ("NITHIK", "704090");
INSERT INTO history (aName, action, msg) VALUES ("NITHIK", "Create",1);
