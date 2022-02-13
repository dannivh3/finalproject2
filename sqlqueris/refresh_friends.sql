-- SQLite
DROP TABLE friends;
CREATE TABLE friends(
    id INTEGER PRIMARY KEY,
    friends TEXT NOT NULL,
    friends_pending TEXT,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id)
        REFERENCES users(id)
);