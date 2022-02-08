from http.client import NotConnected
import os
from pathlib import Path
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from helpers import login_required
from datetime import datetime

# Create a paths
PARENT = Path(__file__).parent.resolve()
UPLOAD_FOLDER = "static/user_content" 

# Some globals
ALLOWED_EXTENSIONS = {'txt', 'png', 'jpg', 'jpeg','mp4'}

# Configure application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1000 * 1000

# Ensure templates are auto-reloaded
app.config["TEMPLATE_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finalproject2.db")



# Function to check if a file is allowed
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# The Landing page
@app.route("/", methods=["GET","POST"])
def index():
    # Clear users session
    session.clear()

    if request.method == "POST":
        
        email = request.form.get("email")
        row = db.execute("SELECT * FROM users WHERE email = ?", email)
        
        # If either password or email incorrect then flash message
        if len(row) != 1 or not check_password_hash(row[0]["hash"], request.form.get("password")): 
            flash("Incorrect email or/and password","danger")
            return render_template("index.html")

        # if bot email and password correct    
        elif len(row) == 1 and check_password_hash(row[0]["hash"], request.form.get("password")):
            # Remember user
            session["user_id"] = row[0]["id"]

            flash("You successfully logged in", "success")
            return redirect("/home")
        
        # Just in case something else goes wrong
        flash("Something went wrong, Try again","warning")
        return render_template("index.html")

    return render_template("index.html")

# Register page
@app.route("/register", methods=["GET", "POST"])
def register():

    # If submitting a form
    if request.method == "POST":

        # Initialise error message
        error = False

        # if name field is empty
        if request.form.get("name") == "":
            flash("The name field is empty","danger")
            error = True
        # if email is empty
        if request.form.get("email") == "":
            flash("The email field is empty","danger")
            error = True
        # if password fields are empty
        if request.form.get("password") == "" or request.form.get("rpassword") == "":
            flash("The password field is empty","danger")
            error = True
        # if password is less than 8
        if len(request.form.get("password")) < 8:
            flash("The password is less that 8 characters","danger")
            error = True
        # check if passwords are the same
        if request.form.get("password") != request.form.get("rpassword"):
            flash("The passwords do not match","danger")
            error = True
        # Query database for existing user
        row = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))

        # Check if email already in database
        if len(row) != 0:
            flash("The email is already registered","danger")
            error = True
        # Check if terms is checked
        if request.form.get("terms") != "terms":
            flash("The Terms of agreement is not checked","danger")
            error = True

        # if any errors
        if error == True:
            return render_template("register.html")

        # Get all the data from forms
        name = request.form.get("name")
        email = request.form.get("email")
        hash = generate_password_hash(request.form.get("password"))

        # insert into database
        db.execute("INSERT INTO users (name, email, hash) VALUES (?, ?, ?)", name, email, hash)

        # Get user id
        userID = db.execute("SELECT id FROM users WHERE email = ?", email)
        userID = userID[0]["id"]

        # Create a user dir
        path = f"finalproject2/static/user_content/user_{userID}"
        Path(path).mkdir(parents=True)
        path_img = path / "images"
        path_vid = path / "videos"
        path_sto = path / "stories"
        Path(path_img).mkdir(parents=True)
        Path(path_vid).mkdir(parents=True)
        Path(path_sto).mkdir(parents=True)

        # Go to login page
        flash("Sucessfully Registered an account", "success")
        return render_template("index.html")

    else:
        return render_template("register.html")

@app.route("/home", methods=["GET", "POST"])
@login_required
def home():

    userID = session["user_id"]

    # Need to set content to null
    text_content = None
    image_content = None
    video_content = None

    images_id = None
    videos_id = None
    stories_id = None


    if request.method == "POST":
        print("Text statement before")
        # Few statements that check if there is something in the form
        if request.form.get("text") != "":
            print(" text before")
            text_content = request.form.get("text")
            print(" text after")
        print("image statement before")
        if request.files["image"]:
            print(" image before")
            image_content = request.files["image"]
            print(" image after")
        print("video statement before")
        if request.files["video"]:
            print(" video before")
            video_content = request.files["video"]
            print(" video after")
        print("after something in form")

        # If there is nothing in all input fields it will return error
        if image_content == None and video_content == None and text_content == None:
            flash("There is nothing to post","danger")
            return render_template("home.html")
        if image_content != None and video_content != None:
            flash("You cant post both videos and images","danger")
            return render_template("home.html")
        print("got through nothing content")
        print(image_content)
        # if there is something in the image input field
        if image_content and allowed_file(image_content.filename):
            
            print("start of image content")
            # Create a filename, path for the upload and save the image
            filename = secure_filename(image_content.filename)
           
            purepath = f"{app.config['UPLOAD_FOLDER']}/user_{userID}/images/{filename}"
            image_content.save(purepath)

            # Change type to string to query into database
            purepath = str(purepath)

            print("filename: ",filename, type(filename))
            print("purepath: ",purepath, type(purepath))

            # Query image into database and get id
            images_id = db.execute("INSERT INTO images (filename, path, type, user_id) VALUES(?, ?, ?, ?)", filename, purepath, "image", userID)
            

            
        print("got through image content")
        # if there is something in the video input field
        if video_content and allowed_file(video_content):
            print("start of video content")
            # Create a filename, path for the upload and save the video
            filename = secure_filename(video_content.filename)
            purepath = f"{app.config['UPLOAD_FOLDER']}/user_{userID}/videos/{filename}"
            video_content.save(purepath)

            # Change type to string to query into database
            purepath = str(purepath)

             # Query video into video table and get id
            videos_id = db.execute("INSERT INTO videos (filename, path, type, user_id) VALUES(?, ?, ?, ?)", filename,  purepath, "video", userID)
        
        print("got through video content")
        # If there is any text content
        if text_content:
            print("start of text content")
            # Create a filename and set the path for upload
            filename = secure_filename(f"{text_content[0:20]}.txt")
            purepath = f"{app.config['UPLOAD_FOLDER']}/user_{userID}/stories/{filename}"
            
            # Write text file
            with open(purepath, 'x') as f:
                f.write(text_content)

            # Change type to string to query into database
            purepath = str(purepath)
            
            # Query content into stories table and get id
            stories_id = db.execute("INSERT INTO stories (filename, path, type, user_id) VALUES (?, ?, ?, ?)", filename, purepath, "story", userID)

        print("got through text content")
        time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")


        posts_id = db.execute("INSERT INTO posts (datetime, user_id) VALUES (?, ?)",time, userID)
        if images_id:
            db.execute("UPDATE posts SET image_id = ? WHERE id = ?", images_id, posts_id)
        if videos_id:
            db.execute("UPDATE posts SET video_id = ? WHERE id = ?", videos_id, posts_id)
        if stories_id:
            db.execute("UPDATE posts SET stories_id = ? WHERE id = ?", stories_id, posts_id)


        return render_template("home.html")
    
    else:
        allPosts = db.execute("SELECT * FROM posts WHERE user_id = ?", userID)
        posts = []
        for post in allPosts:

            name = db.execute("SELECT name FROM users WHERE id = ?", post["user_id"])
            likes = post["likes"]
            
            date = post["datetime"]
            
            print(post)
            if post["video_id"]:
                mediaPath = db.execute("SELECT path FROM videos WHERE id = ?", post["video_id"])
                mediaType = db.execute("SELECT type FROM videos WHERE id = ?", post["video_id"])
            if post["image_id"]:
                mediaPath = db.execute("SELECT path FROM images WHERE id = ?", post["image_id"])
                mediaType = db.execute("SELECT type FROM images WHERE id = ?", post["image_id"])
            if post["stories_id"]:
                storyPath = db.execute("SELECT path FROM stories WHERE id = ?", post["stories_id"])
                print(storyPath)
                with open(storyPath[0]["path"], "r") as f:
                    text = f.read()
                textType = ("SELECT type FROM type WHERE id = ?", post["stories_id"])
            else:
                text = ""
                textType = ""
            postData =  {
                            "name": name[0]["name"],
                            "likes": likes,
                            "date": date,
                            "path": mediaPath[0]["path"],
                            "text": text,
                            "type": mediaType[0]["type"],
                            "texttype": textType
                        }
            posts.append(postData)
            
            
        return render_template("home.html",posts=posts)