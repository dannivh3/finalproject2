from http.client import NotConnected
import os
from pathlib import Path
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from helpers import login_required, listify, addToString, removeFromString, getPosts, getAllData, getUserData, getFriendsData, stringify, mediaFilter, textFilter
from datetime import datetime


# Create a paths
PARENT = Path(__file__).parent.resolve()
UPLOAD_FOLDER = "static/user_content" 

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

# Some globals
ALLOWED_EXTENSIONS = {'txt', 'png', 'jpg', 'jpeg','mp4'}


# context_processor "https://flask.palletsprojects.com/en/1.1.x/templating/#context-processors"
@app.context_processor
def inject_user():
    try:

        userData = getAllData(db.execute("SELECT * FROM users WHERE id = ?",session['user_id']),db.execute("SELECT * FROM friends WHERE user_id = ?",session['user_id']))
        return dict(userData=userData)
    except:
        return ""

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
    else:
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
        db.execute("UPDATE users SET profile_page = ? WHERE id = ?", (name[:3]+str(userID)), userID)
        db.execute("INSERT INTO friends (friends, friends_pending, user_id) VALUES (?,?,?)", userID, "", userID)
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
    media_content = None

    images_id_list = []
    videos_id_list = []
    stories_id = None

    

    if request.method == "POST":
        
         # IF like button pressed
        if request.form.get("like"):
            print("like:",request.form.get("like"))
            likesTable = db.execute("SELECT * FROM likes WHERE posts_id = ?",request.form.get("like"))
            likes = likesTable[0]["likes"]
            whoLiked = likesTable[0]["who_liked"]
            if whoLiked == None:
                whoLiked = []
            else:
                whoLiked = listify(whoLiked)
            print("whoLiked:",whoLiked)
            print("userID:",userID)
            if str(userID) not in whoLiked:
                if likes == None:
                    likes = 1
                else:
                    likes = int(likes)
                    likes += 1

                whoLiked.append(userID)
                whoLiked = stringify(whoLiked)
                db.execute("UPDATE likes SET likes = ? WHERE posts_id = ?", likes, request.form.get("like"))
                db.execute("UPDATE likes SET who_liked = ? WHERE posts_id = ?",whoLiked, request.form.get("like"))
            else:
                
                likes = int(likes)
                likes += -1

                whoLiked.remove(str(userID))
                whoLiked = stringify(whoLiked)
                db.execute("UPDATE likes SET likes = ? WHERE posts_id = ?", likes, request.form.get("like"))
                db.execute("UPDATE likes SET who_liked = ? WHERE posts_id = ?",whoLiked, request.form.get("like"))
            return redirect("/home")
        if request.form.get("comment"):
            commentText = request.form.get("commentText")
            posts_id = request.form.get("comment")
            time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            db.execute("INSERT INTO comments (user_id, posts_id, datetime, comment) VALUES (?,?,?,?)",userID, int(posts_id), time, commentText)

            return redirect("/home")
        if request.form.get("post_content") == "Post":
            print("Text statement before")
            # Few statements that check if there is something in the form
            if request.form.get("text") != "":
                print(" text before")
                text_content = request.form.get("text")
                print(" text after")
            print("files: ", request.files.getlist("media"))
            if request.files["media"]:
                print(" image before")
                media_content = request.files.getlist("media")
                print(request.files["media"])
                print(" image after")
            
            # If there is nothing in all input fields it will return error
            if media_content == None and text_content == None:
                flash("There is nothing to post","danger")
                return render_template("home.html")
            print("got through nothing content")
            if media_content != None:
                videoType = False
                imageType = False

                for media in media_content:
                    if media.content_type.startswith("image"):
                        imageType = True
                    elif media.content_type.startswith("video"):  
                        videoType = True 

                    if imageType == True and videoType == True:
                        flash("You can either post Video or Images not both","danger")
                        return redirect("/home")
                        

                        
                for media in media_content:
                    if media and allowed_file(media.filename):
                        filename = secure_filename(media.filename)
                        
                        if media.content_type.startswith("image"):
                            
                            purepath = f"{app.config['UPLOAD_FOLDER']}/user_{userID}/images/{filename}"
                            media.save(purepath)

                            # Change type to string to query into database
                            purepath = str(purepath)

                            # Query image into database and get id
                            images_id = db.execute("INSERT INTO images (filename, path, type, user_id) VALUES(?, ?, ?, ?)", filename, purepath, "image", userID)
                            images_id_list.append(images_id)

                        elif media.content_type.startswith("video"):
                
                            # Create a filename, path for the upload and save the video
                    
                            purepath = f"{app.config['UPLOAD_FOLDER']}/user_{userID}/videos/{filename}"
                            media.save(purepath)

                            # Change type to string to query into database
                            purepath = str(purepath)

                            # Query video into video table and get id
                            videos_id = db.execute("INSERT INTO videos (filename, path, type, user_id) VALUES(?, ?, ?, ?)", filename,  purepath, "video", userID)
                            videos_id_list.append(videos_id)
            # If there is any text content
            if text_content:
                print("start of text content")
                # Create a filename and set the path for upload
                filename = secure_filename(f"{text_content[0:20]}.txt")
                purepath = f"{app.config['UPLOAD_FOLDER']}/user_{userID}/stories/{filename}"
                
                # Write text file
                with open(purepath, 'w') as f:
                    f.write(text_content)

                # Change type to string to query into database
                purepath = str(purepath)
                
                # Query content into stories table and get id
                stories_id = db.execute("INSERT INTO stories (filename, path, type, user_id) VALUES (?, ?, ?, ?)", filename, purepath, "story", userID)

            print("got through text content")
            time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            # Update the content columns of the post
            posts_id = db.execute("INSERT INTO posts (datetime, user_id) VALUES (?, ?)",time, userID)
            db.execute("INSERT INTO likes (likes, posts_id) VALUES (?,?)",0,posts_id)
            if images_id_list:
                all_images = stringify(images_id_list)
                db.execute("UPDATE posts SET image_id = ? WHERE id = ?", all_images, posts_id)
            if videos_id_list:
                all_videos = stringify(videos_id_list)
                db.execute("UPDATE posts SET video_id = ? WHERE id = ?", all_videos, posts_id)
            if stories_id:
                db.execute("UPDATE posts SET stories_id = ? WHERE id = ?", stories_id, posts_id)

       

        return redirect("/home")
    
    # If request method is GET
    else:

        # Query the friends table
        friendsRow = db.execute("SELECT * FROM friends WHERE user_id = ?", userID)

        # Get all the friend requests from user and put them in a list        
        pendings = listify(friendsRow[0]["friends_pending"])

        # append all information of each friend request to a list
        notifications = []
        for pending in pendings:
            pendingData = getUserData(db.execute("SELECT * FROM users WHERE id = ?",pending))      
            notifications.append(pendingData)
    
        # Get all posts from user's friends    
        friends = friendsRow[0]["friends"]
        posts = getPosts(friends)

        # return the home template with posts arguement
        return render_template("home.html",posts=posts,notifications=notifications)


@app.route("/search")
@login_required
def search():
    users = db.execute("SELECT * FROM users WHERE name LIKE ?","%" + request.args.get("q") + "%")
    return render_template("search.html", users=users)

@app.route("/profile/<profile_page>/photos", methods=["GET"])
@login_required
def profilePhotos(profile_page):

    profileData = getUserData(db.execute("SELECT * FROM users WHERE profile_page = ?", profile_page))
    allImages = db.execute("SELECT path FROM images WHERE user_id = ?",profileData['userID'])

    images = []
    for img in allImages:
        images.append(img['path'][6:])
    return render_template("photos.html",images=images,profileData=profileData)

@app.route("/profile/<profile_page>/videos", methods=["GET"])
@login_required
def profileVideos(profile_page):

    profileData = getUserData(db.execute("SELECT * FROM users WHERE profile_page = ?", profile_page))
    allVideos = db.execute("SELECT path FROM videos WHERE user_id = ?",profileData['userID'])

    videos = []
    for vid in allVideos:
        videos.append(vid['path'][6:])
    return render_template("videos.html",videos=videos,profileData=profileData)



@app.route("/profile/<profile_page>/settings", methods=["GET","POST"], strict_slashes=False)
@login_required
def settings(profile_page):

    userID = session["user_id"]
    profileData = getUserData(db.execute("SELECT * FROM users WHERE profile_page = ?",profile_page))

    if request.method == "POST":
        print("request type: ",request.form["edit"])
        
        print("beginning of Post")
        if request.form["edit"] == "editPic":
            print("begining og editPic")
            choice = request.form.get("profile")
            print("newProfile: ",choice)
            db.execute("UPDATE users SET profile_pic = ? WHERE id = ?", f"static{choice}", userID)

            return redirect(f"/profile/{profileData['page']}/settings")
        
        elif request.form["edit"] == "editSettings":
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
            if request.form.get("contry_from") != "":
                country_from = request.form.get("contry_from")
                db.execute("UPDATE about SET contry_from = ? WHERE user_id = ?", country_from, userID)

        return redirect(f"/profile/{profileData['page']}/settings")
    else:
        profileFriends = getFriendsData(db.execute("SELECT * FROM friends WHERE user_id = ?", profileData["userID"]))
        userFriends = getFriendsData(db.execute("SELECT * FROM friends WHERE user_id = ?", userID))
        aboutRow = db.execute("SELECT * FROM about WHERE user_id = ?", profileData['userID'])
        imageRow = db.execute("SELECT path FROM images WHERE user_id = ?",profileData['userID'])


        profile_pics = []     
        for img in imageRow:
            print(img)
            profile_pics.append(img["path"][6:])

        about = {
            "pic": profileData["pic"],
            "name": profileData["name"],
            "email": profileData["email"],
            "gender": aboutRow[0]["gender"],
            "birthdate": aboutRow[0]["birthdate"],
            "birthyear": aboutRow[0]["birthyear"],
            "phone": aboutRow[0]["phone"],
            "country_curr": aboutRow[0]["country_curr"],
            "country_from": aboutRow[0]["contry_from"],
            "description": aboutRow[0]["description"]
        }
        
        return render_template("settings.html",about=about,profileData=profileData,profile_pics=profile_pics,profileFriends=profileFriends,userFriends=userFriends)

@app.route("/profile/")
@app.route("/profile/<profile_page>/", methods=["GET","POST"],strict_slashes=False)
@login_required
def userProfile(profile_page):

    # Get vitals
    profileRow = db.execute("SELECT * FROM users WHERE profile_page = ?", profile_page)
    profileID = profileRow[0]["id"]
    userID = session["user_id"]
    userRow = db.execute("SELECT * FROM users WHERE id = ?", userID)
    
    print(profile_page)
    if request.method == "POST":
        if request.form.get("like"):
            print("like:",request.form.get("like"))
            likesTable = db.execute("SELECT * FROM likes WHERE posts_id = ?",request.form.get("like"))
            likes = likesTable[0]["likes"]
            whoLiked = likesTable[0]["who_liked"]
            if whoLiked == None:
                whoLiked = []
            else:
                whoLiked = listify(whoLiked)
            print("whoLiked:",whoLiked)
            print("userID:",userID)
            if str(userID) not in whoLiked:
                if likes == None:
                    likes = 1
                else:
                    likes = int(likes)
                    likes += 1

                whoLiked.append(userID)
                whoLiked = stringify(whoLiked)
                db.execute("UPDATE likes SET likes = ? WHERE posts_id = ?", likes, request.form.get("like"))
                db.execute("UPDATE likes SET who_liked = ? WHERE posts_id = ?",whoLiked, request.form.get("like"))
            else:
                
                likes = int(likes)
                likes += -1

                whoLiked.remove(str(userID))
                whoLiked = stringify(whoLiked)
                db.execute("UPDATE likes SET likes = ? WHERE posts_id = ?", likes, request.form.get("like"))
                db.execute("UPDATE likes SET who_liked = ? WHERE posts_id = ?",whoLiked, request.form.get("like"))
            return redirect(f"/profile/{profile_page}/")
        if request.form.get("comment"):
            commentText = request.form.get("commentText")
            posts_id = request.form.get("comment")
            time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            db.execute("INSERT INTO comments (user_id, posts_id, datetime, comment) VALUES (?,?,?,?)",userID, int(posts_id), time, commentText)

            return redirect(f"/profile/{profile_page}/")
        if request.form['friend_request'] == "Add Friend":

            # Selecting the session user's friends
            userFriendQuery = db.execute("SELECT friends FROM friends WHERE user_id = ?", userID)
            userFriend = addToString(userFriendQuery[0]["friends"],profileID)
            
            # Selecting the profile page user's friends_pending list
            profileFriendPendingQuery = db.execute("SELECT friends_pending FROM friends WHERE user_id = ?", profileID)
            profileFriendPending = addToString(profileFriendPendingQuery[0]["friends_pending"],userID)
            
            # Updating Database
            db.execute("UPDATE friends SET friends_pending = ? WHERE user_id = ?",profileFriendPending,profileID)
            db.execute("UPDATE friends SET friends = ? WHERE user_id = ?",userFriend, userID)

            return redirect(f"/profile/{profile_page}/")

        # If a user clicks on a button of a user that friend requested him
        if request.form['friend_request'] == "Accept Friend Request":

            # Get the id of the profile page owner
            acceptedFriend = db.execute("SELECT id FROM users WHERE profile_page = ?", profile_page)
            acceptedFriend = acceptedFriend[0]["id"]

            # Get the pending friends from user and remove the acceptedFriend
            pendingFriendsQuery = db.execute("SELECT friends_pending FROM friends WHERE user_id = ?",userID)
            newPendingList = removeFromString(pendingFriendsQuery[0]["friends_pending"],acceptedFriend)

            # Update the pending list with the accepted friend removed
            db.execute("UPDATE friends SET friends_pending = ? WHERE user_id = ?", newPendingList, userID)

            # Get friends from user and add acceptedFriend to friends
            newFriendListQuery = db.execute("SELECT friends FROM friends WHERE user_id = ?", userID)
            newFriendList = addToString(newFriendListQuery[0]["friends"],acceptedFriend)

            # Update the friends column of the user
            db.execute("UPDATE friends SET friends = ? WHERE user_id = ?",newFriendList, userID)

            # Reload page
            return redirect(f"/profile/{profile_page}/")
    else:
        
        # Get all information that will be sent to url
        profileData = getAllData(profileRow, db.execute("SELECT * FROM friends WHERE user_id = ?", profileID))
        print(profileData["pic"])
        # Get all posts from profile
        posts = getPosts(str(profileID))

        return render_template("profile.html",profileData=profileData, posts=posts)

