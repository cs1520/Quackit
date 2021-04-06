from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from google.cloud import datastore
from datetime import datetime
import hashlib
import os

app = Flask(__name__)
app.secret_key = b"20072012f35b38f51c782e21b478395891bb6be23a61d70a"
data = datastore.Client()

@app.route("/")
def home():
    """Return a simple HTML page."""
    print("Hit the route!")
    return render_template("index.html")


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
        return render_template("login.html")


@app.route("/groups")
def groupnav():
    return render_template("group-nav.html")


@app.route("/groups/<group>")
def grouppage(group):
    return render_template("group-page.html", name=group)



@app.route("/groupdata/<title>", methods = ["GET"])
def group(title):

    gd = data.query(kind="Group")
    if title != "NULL":
        gd.add_filter("Title","=",title)
    groupData = gd.fetch()

    x = [{"title": i["Title"], "primary": i["PrimColor"], "secondary": i["SecColor"], "image": i["Banner"]} for i in groupData]
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
    data.put(group)

    return jsonify(group)

@app.route("/groups/<group>/messagecreate", methods = ["POST"])
def messagecreate(group):
    messageM = request.form.get("message")
    messageU = get_user()
    
    group_key = data.key("Group", group)
    message_key = data.key("Message",messageM)
    message = datastore.Entity(key=message_key)
    message["Text"] = messageM
    message["User"] = messageU
    message["CreationTime"] = datetime.now()
    message["group_key"] = group_key
    data.put(message)

    print(message["Text"])

    return jsonify({"Text": message["Text"], "User": message["User"], "CreationTime": message["CreationTime"]})

@app.route("/groupdata/<group>/messages", methods = ["GET"])
def show_messages(group):
    group_key = data.key("Group", group)

    msg = data.query(kind="Message")
    msg.add_filter("group_key","=",group_key)
    msg.order = "creation_time"
    messages = msg.fetch()
    output = [{"Message":x["Message"], "User":x["User"], "CreationTime": x["CreationTime"]} for x in messages]

    print(output)

    return jsonify(output)


@app.route("/register", methods = ["POST"])
def register_data():
    
    username = request.form.get("username")
    password = request.form.get("password")

    user_key = data.key("UserCredential", username)
    user = datastore.Entity(key=user_key)
    user["username"] = username
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode("utf-8")
    user["salt"] = salt
    #user["hashPassword"] = hash_password(password, salt)
    user["hashPassword"] = password
    data.put(user)    

    return render_template("index.html")

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

        print(userData[0]["U"])
        print(userData[0]["P"])
        print(userData[0]["S"])

        userSalt = str(userData[0]["S"])
        print(userSalt)

        if(userData[0]["U"] == username):
            print("Username Match!")
            #login_attempt = hash_password(password, userData[0]["S"])
            login_attempt = password
            #if(login_attempt == userData[0]["P"] + userData[0]["S"]):
            if(login_attempt == userData[0]["P"]):
                print("Password Match!")
                session["user"] = username
                return True #I don't know what to return
            else:
                print("Password Mismatch!")
                return None

        else:
            return None


@app.route("/register", methods = ["GET"])
def register():
    print("Register Page")
    return render_template("register.html")

@app.route("/profile/")
def profile():
    
    user = get_user()
    if user == None:
            return redirect("/login")
    else:
        #url_for('profile', user)
        return render_template("profile.html", name=user)

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

