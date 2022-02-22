# finalproject2
#### Video Demo: https://youtu.be/VhaNJvn2W9g
#### Description: 
A social media platform made for families, This is first version of the website. 
you will be able to post both video content and images, like and comment on those posts.
Each user has it's own profile page which you can edit your settings and profilepicture,
each profile has its own photo album and video album.
You can add friends and see their content on the public feed.

#### app.py:
This is the main application that ties everything together, 
I made the website with the flask library and linked pages together with the routing decoration.

#### helpers.py:
This file has all the functions that were to messy to write in the main app.py. It is beautifully written though.
It includes a lot of functions that help with the querying in the database. some querys have a comma seporated list and i needed a function
to easily get and query them into the database. 
- listify()
> It is a function that takes 1 arguement (a comma seporated string) and returns a list
- stringify()
> Function that takes a list as an arguement and returns a comma seporated list
- removeFromString()
> removes the argument out of the string
- addToString()
> adds the argument to the string
- login_required()
> Function i got from the flask docs which checks if user is logged in
- mediaFilter, textFilter
> filters the media data to a more readable data
- getUserData, getFriendsData, getAllData
> gets all the neccisary data to send to the url
- getPosts
> Get all posts visably to the user

#### finalProject2.db
The database storing all the data

#### Templates dir
I made the templates with jinja2 and flask, 
I made it by using bootsrap 5 

#### static Dir
- styles.css
> Here are my custom made styles to make the webpage pretty
> I also did my best to make the webpage useable in mobile
- script.js
> Few function's to make the page more dynamic. 
- user_content dir
> All the uploaded media goes into special made folders in the user_content
- web_img dir
> couple of images for the page

#### sqlquerys
This is a folder of all saved querys to make it easier to refresh the database
