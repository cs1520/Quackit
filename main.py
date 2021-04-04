from flask import Flask, render_template, request, jsonify
from google.cloud import datastore
import hashlib
import os

app = Flask(__name__)

data = datastore.Client()

@app.route("/")
def home():
    """Return a simple HTML page."""
    print("Hit the route!")
    return render_template("index.html")


@app.route("/login", methods = ["GET"])
def login():
    
    print("Login page")
    return render_template("login.html")

@app.route("/login", methods = ["POST"])
def login_data():
    
    username = request.form.get("username")
    password = request.form.get("password")
    #print(username + " " + password)

    if(verify_password(username, password)):
        print(username + " has logged in successfully")
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
    gd.add_filter("Title","=",title)
    groupData = gd.fetch()

    x = [{"title": i["Title"], "primary": i["PrimColor"], "secondary": i["SecColor"], "image": i["Image"]} for i in groupData]
    return jsonify(x)
    


@app.route("/register", methods = ["POST"])
def register_data():
    
    username = request.form.get("username")
    password = request.form.get("password")

    user_key = data.key("UserCredential", username)
    user = datastore.Entity(key=user_key)
    user["username"] = username
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode("utf-8")
    user["salt"] = salt
    user["hashPassword"] = hash_password(password, salt)
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
            login_attempt = hash_password(password, userData[0]["S"])
            if(login_attempt == userData[0]["P"] + userData[0]["S"]):
                print("Password Match!")
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

@app.route("/profile", methods = ["GET"])
def profile():
    
    print("Profile page")
    return render_template("profile.html")

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)

