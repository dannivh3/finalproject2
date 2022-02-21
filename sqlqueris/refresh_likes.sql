-- SQLite
DROP TABLE likes;
CREATE TABLE likes (
    id INTEGER PRIMARY KEY,
    who_liked TEXT,
    likes INTEGER,
    posts_id INTEGER,
    FOREIGN KEY (posts_id)
        REFERENCES posts(id)
        );
