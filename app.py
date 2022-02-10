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
        profile_pic = "static/web_img/empty_profile.png"
        # insert into database & Get user id
        userID = db.execute("INSERT INTO users (name, email, profile_pic, hash) VALUES (?, ?, ?, ?)", name, email, profile_pic, hash)
        db.execute("INSERT INTO friend_list (user_id) VALUES (?)", userID)
        db.execute("INSERT INTO about (user_id) VALUES (?)", userID)

        # Create a user dir
        path = f"static/user_content/user_{userID}"
        Path(path).mkdir(parents=True)
        path_img = path + "/images"
        path_vid = path + "/videos"
        path_sto = path + "/stories"
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
            print(request.files["image"])
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
        if video_content and allowed_file(video_content.filename):
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

        # Update the content columns of the post
        posts_id = db.execute("INSERT INTO posts (datetime, user_id) VALUES (?, ?)",time, userID)
        if images_id:
            db.execute("UPDATE posts SET image_id = ? WHERE id = ?", images_id, posts_id)
        if videos_id:
            db.execute("UPDATE posts SET video_id = ? WHERE id = ?", videos_id, posts_id)
        if stories_id:
            db.execute("UPDATE posts SET stories_id = ? WHERE id = ?", stories_id, posts_id)


        return redirect("/home")
    
    # If request method is GET
    else:
        # Get posts that session user can see
        allPosts = db.execute("SELECT * FROM posts WHERE user_id = ? ORDER BY datetime DESC", userID)

        # Setting the list where all post data will be kept
        posts = []
        
        # Iterating through all the posts that user can see To gather info
        for post in allPosts:
            
            # Clear these variables otherwise they will bring up wrong data
            postData = {}
            mediaPath = None
            mediaType = None
           
            # Name of poster
            name = db.execute("SELECT name FROM users WHERE id = ?", post["user_id"])
            profile = db.execute("SELECT profile_pic FROM users WHERE id = ?", post["user_id"])
            # Likes and comments of post
            likes = post["likes"]
            comments = post["comments"]
            # Date of post
            date = post["datetime"]
            
            # The website will only display eather 1 video or 1 image with or without text
            # These statements will get the media file from the path collumn if there is one
            
            if post["video_id"] != None:
                mediaPath = db.execute("SELECT path FROM videos WHERE id = ?", post["video_id"])
                mediaType = db.execute("SELECT type FROM videos WHERE id = ?", post["video_id"])
                mediaType = mediaType[0]["type"]
                mediaPath = mediaPath[0]["path"]
            if post["image_id"] != None:
                mediaPath = db.execute("SELECT path FROM images WHERE id = ?", post["image_id"])
                mediaType = db.execute("SELECT type FROM images WHERE id = ?", post["image_id"])
                mediaType = mediaType[0]["type"]
                mediaPath = mediaPath[0]["path"]

            # This statement will get the text file if there is one
            if post["stories_id"] != None:
                storyPath = db.execute("SELECT path FROM stories WHERE id = ?", post["stories_id"])
                with open(storyPath[0]["path"], "r") as f:
                    text = f.read()
                textType = db.execute("SELECT type FROM stories WHERE id = ?", post["stories_id"])
            else:
                text = ""
                textType = [""]

            # Set up dict with all the data neccesery
            postData =  {
                            "name": name[0]["name"],
                            "profile": profile[0]["profile_pic"],
                            "likes": likes,
                            "comments": comments,
                            "date": date,
                            "path": mediaPath,
                            "text": text,
                            "type": mediaType,
                            "texttype": textType
                        }
            # after each iteration append the data to posts
            posts.append(postData)
            
        # return the home template with posts arguement
        return render_template("home.html",posts=posts)


@app.route("/profile", methods=["GET"])
@login_required
def profile():

    userID = session["user_id"]
    row = db.execute("SELECT * FROM users WHERE id = ?", userID)
    profileData = {
        "profile_pic": row[0]["profile_pic"],
        "name": row[0]["name"]
    }
    
    allPosts = db.execute(f"SELECT * FROM posts WHERE user_id = ? ORDER BY datetime DESC", userID)


    # Setting the list where all post data will be kept
    posts = []
    
    # Iterating through all the posts that user can see To gather info
    for post in allPosts:
                
                # Clear these variables otherwise they will bring up wrong data
                postData = {}
                mediaPath = None
                mediaType = None
            
                # Name of poster
                name = db.execute("SELECT name FROM users WHERE id = ?", post["user_id"])
                profile = db.execute("SELECT profile_pic FROM users WHERE id = ?", post["user_id"])
                # Likes and comments of post
                likes = post["likes"]
                comments = post["comments"]
                # Date of post
                date = post["datetime"]
                
                # The website will only display eather 1 video or 1 image with or without text
                # These statements will get the media file from the path collumn if there is one
                
                if post["video_id"] != None:
                    mediaPath = db.execute("SELECT path FROM videos WHERE id = ?", post["video_id"])
                    mediaType = db.execute("SELECT type FROM videos WHERE id = ?", post["video_id"])
                    mediaType = mediaType[0]["type"]
                    mediaPath = mediaPath[0]["path"]
                if post["image_id"] != None:
                    mediaPath = db.execute("SELECT path FROM images WHERE id = ?", post["image_id"])
                    mediaType = db.execute("SELECT type FROM images WHERE id = ?", post["image_id"])
                    mediaType = mediaType[0]["type"]
                    mediaPath = mediaPath[0]["path"]

                # This statement will get the text file if there is one
                if post["stories_id"] != None:
                    storyPath = db.execute("SELECT path FROM stories WHERE id = ?", post["stories_id"])
                    with open(storyPath[0]["path"], "r") as f:
                        text = f.read()
                    textType = db.execute("SELECT type FROM stories WHERE id = ?", post["stories_id"])
                else:
                    text = ""
                    textType = [""]

                # Set up dict with all the data neccesery
                postData =  {
                                "name": name[0]["name"],
                                "profile": profile[0]["profile_pic"],
                                "likes": likes,
                                "comments": comments,
                                "date": date,
                                "path": mediaPath,
                                "text": text,
                                "type": mediaType,
                                "texttype": textType
                            }
                # after each iteration append the data to posts
                posts.append(postData)
    return render_template("profile.html",profileData=profileData, posts=posts)

@app.route("/photos", methods=["GET"])
@login_required
def profilePhotos():

    userID = session["user_id"]
    row = db.execute("SELECT * FROM users WHERE id = ?", userID)
    profileData = {
        "profile_pic": row[0]["profile_pic"],
        "name": row[0]["name"]
    }
    allImages = db.execute("SELECT path FROM images WHERE user_id = ?",userID)
    images = []
    for img in allImages:
        images.append(img)
        print(img)
    print(images)
    for i in images:
        print(i['path'])


    return render_template("profilephotos.html",images=images,profileData=profileData)

@app.route("/videos", methods=["GET"])
@login_required
def profileVideos():

    userID = session["user_id"]
    row = db.execute("SELECT * FROM users WHERE id = ?", userID)
    profileData = {
        "profile_pic": row[0]["profile_pic"],
        "name": row[0]["name"]
    }
    allVideos = db.execute("SELECT path FROM videos WHERE user_id = ?",userID)
    videos = []
    for vid in allVideos:
        videos.append(vid)
        
    
    


    return render_template("profilevideos.html",videos=videos,profileData=profileData)

@app.route("/about", methods=["GET","POST"])
@login_required
def profileAbout():

    userID = session["user_id"]

    if request.method == "POST":

        
        choice = request.form.get("profile")

        db.execute("UPDATE users SET profile_pic = ? WHERE id = ?", choice, userID)

        return redirect("/about")

        


    else:
        
        userRow = db.execute("SELECT * FROM users WHERE id = ?", userID)
        aboutRow = db.execute("SELECT * FROM about WHERE user_id = ?", userID)
        imageRow = db.execute("SELECT path FROM images WHERE user_id = ?",userID)
        profile_pics = []
        
        
        for img in imageRow:
            print(img)
            profile_pics.append(img["path"])
         
        about = {
            "profile_pic": userRow[0]["profile_pic"],
            "name": userRow[0]["name"],
            "email": userRow[0]["email"],
            "gender": aboutRow[0]["gender"],
            "birthdate": aboutRow[0]["birthdate"],
            "birthyear": aboutRow[0]["birthyear"],
            "phone": aboutRow[0]["phone"],
            "country_curr": aboutRow[0]["country_curr"],
            "country_from": aboutRow[0]["country_from"],
            "description": aboutRow[0]["description"]
        }
        profileData = {
            "profile_pic": userRow[0]["profile_pic"],
            "name": userRow[0]["name"]
        }
        return render_template("profileabout.html",about=about,profileData=profileData, profile_pics=profile_pics)

@app.route("/settings", methods=["GET","POST"])
@login_required
def settings():
    userID = session["user_id"]
    
    if request.method == "POST":
        print("request type: ",request.form["edit"])
        
        print("beginning of Post")
        if request.form["edit"] == "editPic":
            print("begining og editPic")
            choice = request.form.get("profile")

            db.execute("UPDATE users SET profile_pic = ? WHERE id = ?", choice, userID)

            return redirect("/about")
        
        elif request.form["edit"] == "editSettings":
            print("begining og editPic")
            if request.form.get("name") != "":
                name = request.form.get("name")
                db.execute("UPDATE users SET name = ? WHERE id = ?", name, userID)
            if request.form.get("gender") != "":
                gender = request.form.get("gender")
                db.execute("UPDATE about SET gender = ? WHERE user_id = ?", gender, userID)
            if request.form.get("birthdate") != "":
                birthdate = request.form.get("birthdate")
                db.execute("UPDATE about SET birthdate = ? WHERE user_id = ?", birthdate, userID)
            if request.form.get("birthyear") != "":
                birthyear = request.form.get("birthyear")
                db.execute("UPDATE about SET birthyear = ? WHERE user_id = ?", int(birthyear), userID)
            if request.form.get("phone") != "":
                phone = request.form.get("phone")
                db.execute("UPDATE about SET phone = ? WHERE user_id = ?", phone, userID)
            if request.form.get("email") != "":
                email = request.form.get("email")
                db.execute("UPDATE users SET email = ? WHERE id = ?", email, userID)
            if request.form.get("country_curr") != "":
                country_curr = request.form.get("country_curr")
                db.execute("UPDATE about SET country_curr = ? WHERE user_id = ?", country_curr, userID)
            if request.form.get("country_from") != "":
                country_from = request.form.get("country_from")
                db.execute("UPDATE about SET country_from = ? WHERE user_id = ?", country_from, userID)

        return redirect("/about")
    else:
        userRow = db.execute("SELECT * FROM users WHERE id = ?", userID)
        aboutRow = db.execute("SELECT * FROM about WHERE user_id = ?", userID)
        imageRow = db.execute("SELECT path FROM images WHERE user_id = ?",userID)

        profile_pics = []     
        for img in imageRow:
            print(img)
            profile_pics.append(img["path"])

        about = {
            "profile_pic": userRow[0]["profile_pic"],
            "name": userRow[0]["name"],
            "email": userRow[0]["email"],
            "gender": aboutRow[0]["gender"],
            "birthdate": aboutRow[0]["birthdate"],
            "birthyear": aboutRow[0]["birthyear"],
            "phone": aboutRow[0]["phone"],
            "country_curr": aboutRow[0]["country_curr"],
            "country_from": aboutRow[0]["country_from"],
            "description": aboutRow[0]["description"]
        }
        profileData = {
            "profile_pic": userRow[0]["profile_pic"],
            "name": userRow[0]["name"]
        }
        return render_template("settings.html",about=about,profileData=profileData,profile_pics=profile_pics)