from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from google.cloud import datastore
from datetime import datetime, timedelta
import itertools
import hashlib
import os
#import json

app = Flask(__name__)
app.secret_key = b"20072012f35b38f51c782e21b478395891bb6be23a61d70a"
data = datastore.Client()

@app.route("/")
def home():
    """Return a simple HTML page."""
    #print("Hit the route!")

    if(get_user() == None):
        return render_template("login.html")
    else:
        return render_template("index.html")

@app.route("/home/info", methods = ["GET"])
def home_info():

    ug = data.query(kind="UserGroups")
    ug.add_filter("User","=",get_user())
    groups = ug.fetch()   

    followed = []

    for i in groups:
        fm = data.query(kind="Message")
        fm.add_filter("GroupTitle","=",i["Group"])
        fm.order = ["-CreationTime"]
        firstMessage = fm.fetch(limit=1)
        for x in firstMessage:
            first = x["Text"]

        groupM = [{"group": i["Group"],"text": first}]
        followed.append(groupM[0])
    
    return jsonify(followed) 

@app.route("/home/recommended", methods = ["GET"])
def home_recommended():
    usergd = data.query(kind="UserGroups")
    usergd.add_filter("User","=",get_user())
    userGroupData = usergd.fetch()

    allgd = data.query(kind="Group")
    allGroupData = allgd.fetch()

    followed = []
    not_followed = []

    for i in userGroupData:
        followed.append(i["Group"])

    for i in allGroupData:
        f = 0
        for j in range(len(followed)):
            if(i["Title"]==followed[j]):
                f=1
        if(f==0):
            groupNF = [{"group": i["Title"]}]
            not_followed.append(groupNF[0])

    return jsonify(not_followed)


@app.route("/login", methods = ["GET"])
def login():
    
    return render_template("login.html") 

@app.route("/login", methods = ["POST"])
def login_data():
    
    username = request.form.get("username")
    password = request.form.get("password")
    #print(username + " " + password)

    if(verify_password(username, password)):
        print(username + " has logged in successfully")
        return redirect("/")
    else:
        print("Login failed")
        return render_template("login.html", failed = 1)


@app.route("/groups")
def groupnav():
    return render_template("group-nav.html")


@app.route("/groups/<group>", methods = ["GET"])
def grouppage(group):

    ug = data.query(kind="UserGroups")
    ug.add_filter("User","=",get_user())
    groups = ug.fetch()

    follow = False

    for i in groups:
        if i["Group"] == group:
            follow = True

    return render_template("group-page.html", name=group, user=get_user(), follow = follow)



@app.route("/groupdata/<title>", methods = ["GET"])
def group(title):

    gd = data.query(kind="Group")
    if title != "NULL":
        gd.add_filter("Title","=",title)
    groupData = gd.fetch()

 
    x = [{"title": i["Title"], "primary": i["PrimColor"], "secondary": i["SecColor"], "image": i["Banner"], "owner":i["Owner"], "about": i["About"], "rules": i["Rules"]} for i in groupData]

    return jsonify(x)

@app.route("/groupdata/nav", methods = ["GET"])
def groupdatanav():

    gd = data.query(kind="Group")
    groupData = gd.fetch()

 
    x = [{"title": i["Title"], "primary": i["PrimColor"], "secondary": i["SecColor"]} for i in groupData]

    return jsonify(x)

@app.route("/groupcreate", methods = ["POST"])
def groupcreate():
    groupT = request.form.get("title")
    groupB = request.form.get("banner")
    groupP = request.form.get("primary")
    groupS = request.form.get("secondary")

    group_key = data.key("Group", groupT)
    group = datastore.Entity(key=group_key)
    group["Title"] = groupT
    group["Banner"] = groupB
    group["PrimColor"] = groupP
    group["SecColor"] = groupS
    group["Owner"] = get_user()
    group["About"] = ""
    group["Rules"] = ""
    data.put(group)

    return jsonify(group)


@app.route("/groups/<group>/updatedetails", methods = ["POST"])
def groupupdate(group):
    ty = request.form.get("type")
    dat = request.form.get("data")

    group_key = data.key("Group",group)
    g = data.get(key=group_key)
    if ty == 'about':
        g["About"] = dat
    else:
        g["Rules"] = dat
    
    data.put(g)

    return jsonify(g)


@app.route("/groups/<group>/messagecreate", methods = ["POST"])
def messagecreate(group):
    messageM = request.form.get("message")
    messageU = get_user()
    
    message_key = data.key("Message")
    message = datastore.Entity(key=message_key)
    message["Text"] = messageM
    message["User"] = messageU
    message["CreationTime"] = datetime.now()
    message["GroupTitle"] = group
    data.put(message)

    print(message["Text"])

    return jsonify(message)

@app.route("/messagedelete/<int:messageid>", methods = ["POST"])
def delete_messages(messageid):
    message_key = data.key("Message",messageid)
    data.delete(message_key)    

    return 'deleted'


@app.route("/groupdata/<group>/messages", methods = ["GET"])
def show_messages(group):
    
    GroupTitle = group
    msg = data.query(kind="Message")
    msg.add_filter("GroupTitle","=",GroupTitle)
    msg.order = ["-CreationTime"]
    messages = msg.fetch()
    output = [{"id" : x.id, "text":x["Text"], "user":x["User"], "creationtime": x["CreationTime"], "grouptitle": x["GroupTitle"]} for x in messages]

    return jsonify(output)

@app.route("/groups/<group>/follow", methods= ["POST"])
def follow_group(group):
    
    key = data.key("UserGroups")
    UG = datastore.Entity(key = key)
    UG["Group"] = group
    UG["User"] = get_user()
    data.put(UG)

    return jsonify(UG)

@app.route("/groups/<group>/unfollow", methods= ["POST"])
def unfollow_group(group):
    
    ug = data.query(kind="UserGroups")
    ug.add_filter("User","=",get_user())
    ug.add_filter("Group","=",group)
    group = ug.fetch(limit=1)

    output = [{"id":i.id} for i in group]

    key = data.key("UserGroups", output[0]["id"])

    data.delete(key)
    
    return 'deleted'   


@app.route("/register", methods = ["POST"])
def register_data():
    
    username = request.form.get("username")
    password = request.form.get("password")

    if(username_Auth(username)):
        user_key = data.key("UserCredential", username)
        user = datastore.Entity(key=user_key)
        user["username"] = username
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode("utf-8")
        user["salt"] = salt
        user["hashPassword"] = hash_password(password, salt)
        # user["hashPassword"] = password

        userData_key = data.key("UserDetails", username)
        userData = datastore.Entity(key=userData_key)
        userData["username"] = username
        userData["profile picture"] = "https://i.imgur.com/wqO3i23.jpg" # hardcoded default profile picture

        data.put(user)
        data.put(userData)
        session["user"] = username
        return render_template("index.html")
    else:
        return render_template("register.html", taken=1)

def username_Auth(nUsername):
    users = data.query(kind = 'UserCredential')
    result = users.fetch()

    usersNames = [{"U": i["username"]} for i in result]

    for i in usersNames:
        if(i["U"] == nUsername):
            return False

    return True



def hash_password(password, salt):
    """This will give us a hashed password that will be extremlely difficult to 
    reverse.  Creating this as a separate function allows us to perform this
    operation consistently every time we use it."""
    encoded = password.encode("utf-8")
    
    return hashlib.pbkdf2_hmac("sha256", encoded, salt, 100000)

def verify_password(username, password):
        user = data.query(kind = 'UserCredential')
        user.add_filter('username', '=', username)
        result = user.fetch()

        if(result == None):
            print("result is null")
            return False

        userData = [{"U": i["username"], "P": i["hashPassword"], "S": i["salt"]} for i in result]

        #print(userData[0]["U"])
        #print(userData[0]["P"])
        #print(userData[0]["S"])

        #userSalt = str(userData[0]["S"])
        #print(userSalt)

        if(userData[0]["U"] == username):
            print("Username Match!")
            login_attempt = hash_password(password, userData[0]["S"])
            #login_attempt = password
            #if(login_attempt == userData[0]["P"] + userData[0]["S"]):
            if(login_attempt == userData[0]["P"]):
                print("Password Match!")
                session["user"] = username
                return True #I don't know what to return
            else:
                #print("Password Mismatch!")
                return None

        else:
            return None


@app.route("/register", methods = ["GET"])
def register():
    usernameQuery = data.query(kind = 'UserCredential')
    #usernameQuery.add_filter('username', '=', 'Cam')    #to limit size for bugfixing
    result = usernameQuery.fetch()
    x = [{"uName": i["username"]} for i in result]
    #x = json.dumps(x)
    jsonify(x)

    return render_template("register.html", names = x)

@app.route("/profile/")
def profile():
    
    user = get_user()
    if user == None:
            return redirect("/login")
    else:
        profilepicQuery = data.query(kind = 'UserDetails')
        profilepicQuery.add_filter('username', '=', user)    #to limit size for bugfixing
        result = profilepicQuery.fetch()
        x = [{"profilepic": i["profile picture"]} for i in result]
        userpic = x[0]["profilepic"]
        #userpic = "https://wallpapercave.com/wp/wp6489846.png"
        return render_template("profile.html", name=user, pic = userpic)
@app.route("/changeData", methods = ["GET"])
def changeData():
    return render_template("changeData.html")

@app.route("/changeData", methods = ["POST"])
def updateData():
    currUser = get_user()
    nPassword = request.form.get("newPassword")

    user_key = data.key("UserCredential", currUser)
    user = datastore.Entity(key=user_key)
    user["username"] = currUser
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode("utf-8")
    user["salt"] = salt
    user["hashPassword"] = hash_password(nPassword, salt)
    data.put(user)
    return render_template("changeData.html", success = 1)

@app.route("/imageUpload", methods = ["GET"])
def imageUpload():
    return render_template("image-upload.html")

@app.route("/imageUpload", methods = ["POST"])
def imageUploadData():
    newPic = request.form.get("newPicture")
    username = get_user()

    if(username == None):
        render_template("login.html")

    userData_key = data.key("UserDetails", username)
    userData = datastore.Entity(key=userData_key)
    userData["username"] = username
    userData["profile picture"] = newPic
    data.put(userData)
    return redirect("/profile")

"""@app.route("/profile/<user>")
def profile_user(user):
    username = get_user()
    return render_template("profile.html", name=username)"""
    

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

def get_user():
    """If our session has an identified user (i.e., a user is signed in), then
    return that username."""
    return session.get("user", None)    

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)

