import os
import requests
import urllib.parse
from cs50 import SQL

from flask import redirect, render_template, request, session
from functools import wraps


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

def listify(string):
    if len(string) > 1:
        lst = string.split(",")
    elif len(string) == 1:
        lst = [string]
    else:
        lst = []
    return lst

def addToString(oldstring,value):
    lst = listify(oldstring)
    lst.append(str(value))
    newString = ",".join([str(item) for item in lst])
    return newString

def removeFromString(oldstring,remove):
    lst = listify(oldstring)
    lst.remove(str(remove))
    newString = stringify(lst)
    return newString

def stringify(lst):
    newString = ",".join([str(item) for item in lst])
    return newString

def mediaFilter(data):
    return [data[0]['path'][6:]]

def textFilter(data):
    
    with open(data[0]["path"], "r") as f:
        text = f.read()
    type = data[0]["type"]
    return [type,text]


def getAllData(user,friend):
    # Put friends and pending friends of user into list
    friends = listify(friend[0]["friends"])
    pending = listify(friend[0]["friends_pending"])

    # first friend in list is friendlist owner so pop them out
    friends.pop(0)
    
    # Set up profile data to send to route
    data = {
        "userID": user[0]["id"],
        "userIDstr": str(user[0]["id"]),
        "page": user[0]["profile_page"],
        "pic": user[0]["profile_pic"][6:],
        "name": user[0]["name"],
        "friends":friends,
        "pending":pending
    }    

    return data

def getUserData(user):
    data = {
        "userID": user[0]["id"],
        "userIDstr": str(user[0]["id"]),
        "page": user[0]["profile_page"],
        "pic": user[0]["profile_pic"][6:],
        "name": user[0]["name"],
        "email":user[0]["email"]
    }
    print(data)
    return data

def getFriendsData(data):
    # Put friends and pending friends of user into list
    friends = listify(data[0]["friends"])
    pending = listify(data[0]["friends_pending"])

    # first friend in list is friendlist owner so pop them out
    friends.pop(0)
    friendData = {
        "friends": friends,
        "pending": pending
    }
    return friendData

def getPosts(friends):

    db = SQL("sqlite:///finalproject2.db")
    
    # Iterating through all the posts that user can see To gather info
    posts = []

    # Little function to create a query string for getting all the posts from user's friends
    friends = listify(friends)
    foo = "OR user_id = ? " * (len(friends) - 1)
    query = (f"SELECT * FROM posts WHERE user_id = ? {foo}ORDER BY datetime DESC",)
    for friend in friends:
        query = query + (friend,)
    
    
    allPosts = db.execute(*query)
    for post in allPosts:
                
        # Clear these variables otherwise they will bring up wrong data
        postData = {}
        mediaData = []
        mediaType = ""
        textData = ["",""]
        
    
        # Get information of post
        name = db.execute("SELECT name FROM users WHERE id = ?", post["user_id"])
        profile = db.execute("SELECT profile_pic FROM users WHERE id = ?", post["user_id"])
        page = db.execute("SELECT profile_page FROM users WHERE id = ?", post["user_id"])
        likesTable = db.execute("SELECT * FROM likes WHERE posts_id = ?", post["id"])
        likes = likesTable[0]["likes"]
        whoLiked = likesTable[0]["who_liked"]
        comments = []
        allComments = db.execute("SELECT * FROM comments WHERE posts_id = ? ORDER BY datetime ASC", post["id"])

        for comment in allComments:
            commentUser = db.execute("SELECT * FROM users WHERE id = ?" ,comment["user_id"])
            commentUserPic = commentUser[0]["profile_pic"]
            commentUserPage = commentUser[0]["profile_page"]
            commentUserName = commentUser[0]["name"]
            commentText = comment["comment"]
            commentTime = comment["datetime"]
            commentData = {
                "pic": commentUserPic,
                "page": commentUserPage,
                "name": commentUserName,
                "text": commentText,
                "time": commentTime
            }
            comments.append(commentData)

        date = post["datetime"]
        
        # The website will only display eather 1 video or 1 image with or without text
        # These statements will get the media file from the path collumn if there is one
        if post["video_id"] != None:
            all_videos = listify(str(post["video_id"]))
            videoData = []
            for video in all_videos:
                data = mediaFilter(db.execute("SELECT path,type FROM videos WHERE id = ?", video))
                videoData.append(data)
            mediaData = videoData
            mediaType = "video"
        if post["image_id"] != None:
            all_images = listify(str(post["image_id"]))
            imageData = []
            for image in all_images:
                data = mediaFilter(db.execute("SELECT path,type FROM images WHERE id = ?", image))
                imageData.append(data)
            mediaData = imageData
            mediaType = "image"
        # This statement will get the text file if there is one
        if post["stories_id"] != None:
            textData = textFilter(db.execute("SELECT path,type FROM stories WHERE id = ?", post["stories_id"]))
        print("mediaData",mediaData)
        # Set up dict with all the data neccesery
        postData =  {
            "name": name[0]["name"],
            "pic": profile[0]["profile_pic"],
            "page": page[0]["profile_page"],
            "post_id":post["id"],
            "likes": likes,
            "whoLiked":whoLiked,
            "comments":comments,
            "date": date,
            "media": mediaData,
            "mediatype":mediaType,
            "texttype": textData[0],
            "text": textData[1]
        }
        # after each iteration append the data to posts
        print(comments)
        posts.append(postData)
    return posts

    