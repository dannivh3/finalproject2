-- SQLite
DROP TABLE about;
CREATE TABLE about(
    id INTEGER PRIMARY KEY,
    gender TEXT,
    birthdate TEXT,
    birthyear TEXT,
    phone TEXT,
    country_curr TEXT,
    contry_from TEXT,
    description TEXT,
    user_id INTEGER NOT NULL,
        FOREIGN KEY (user_id)
            REFERENCES users(id)

            );