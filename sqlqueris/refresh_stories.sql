-- SQLite
DROP TABLE videos;
CREATE TABLE videos(
    id INTEGER PRIMARY KEY,
    filename TEXT NOT NULL,
    path TEXT NOT NULL,
    type TEXT NOT NULL,
    user_id INTEGER NOT NULL,
        FOREIGN KEY (user_id)
            REFERENCES users(id)
            );