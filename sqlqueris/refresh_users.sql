-- SQLite
DROP TABLE users;
CREATE TABLE users(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    profile_page TEXT,
    profile_pic TEXT NOT NULL,
    hash TEXT NOT NULL
    );