-- SQLite
DROP TABLE comments;
CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    posts_id INTEGER NOT NULL,
    datetime TEXT NOT NULL,
    comment TEXT,
    FOREIGN KEY (user_id)
        REFERENCES users(id),
    FOREIGN KEY (posts_id)
        REFERENCES posts(id)
        );