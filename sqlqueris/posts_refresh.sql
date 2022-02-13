-- SQLite
DROP TABLE posts;
CREATE TABLE posts(
    id INTEGER PRIMARY KEY,
    datetime TEXT NOT NULL,
    likes INTEGER,
    comments INTEGER,
    video_id INTEGER,
    image_id INTEGER,
    stories_id INTEGER,
    user_id INTEGER NOT NULL,
        FOREIGN KEY (user_id)
            REFERENCES users(id),
        FOREIGN KEY (stories_id)
            REFERENCES stories(id),
        FOREIGN KEY (image_id)
            REFERENCES images(id),
        FOREIGN KEY (video_id)
            REFERENCES videos(id)
            );