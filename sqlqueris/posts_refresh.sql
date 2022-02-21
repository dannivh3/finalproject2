-- SQLite
DROP TABLE posts;
CREATE TABLE posts(
    id INTEGER PRIMARY KEY,
    datetime TEXT NOT NULL,
    video_id TEXT,
    image_id TEXT,
    stories_id INTEGER,
    user_id INTEGER NOT NULL,
        FOREIGN KEY (user_id)
            REFERENCES users(id),
        FOREIGN KEY (stories_id)
            REFERENCES stories(id));