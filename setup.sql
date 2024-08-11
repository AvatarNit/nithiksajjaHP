
.open home.db
.mode box



DROP TABLE IF EXISTS feedback;
DROP TABLE IF EXISTS admins;
DROP TABLE IF EXISTS history;
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fName TEXT NOT NULL,
    lName TEXT NOT NULL,
    contact TEXT NOT NULL,
    message TEXT NOT NULL
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
    tableNum INTEGER NOT NULL
);

INSERT INTO feedback VALUES ("Nithik", "Sajja", "3177711201", "This website is great!");
INSERT INTO admins (username, passwords) VALUES ("NITHIK", "704090");
INSERT INTO history (aName, action, tableNum) VALUES ("NITHIK", "Create",1);
