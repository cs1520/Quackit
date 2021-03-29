from flask import Flask, render_template, request
from google.cloud import datastore
import hashlib
import os
#from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
#db = SQLAlchemy(app)

#class Message(db.model):
#    username = db.Column(db.String(80), unique=True, nullable=False)
#    message = db.Column(db.String(200), unique=False, nullable=False)
#    visibility = db.Column(db.String(10), unique=False, nullable=False)

#    def __msgout__(self):
#        return ("%s: %s" + "visible to: %s"
#                % (self.username, self.message, self.visibility))
data = datastore.Client()

@app.route("/")
def home():
    """Return a simple HTML page."""
    print("Hit the route!")
    return render_template("home.html")


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

    return render_template("home.html")

def hash_password(password, salt):
    """This will give us a hashed password that will be extremlely difficult to 
    reverse.  Creating this as a separate function allows us to perform this
    operation consistently every time we use it."""
    encoded = password.encode("utf-8")
    
    return hashlib.pbkdf2_hmac("sha256", encoded, salt, 100000)

def verify_password(username, password):
        user = data.query(kind = 'UserCredentail')
        user.add_filter('username', '=', username)
        result = user.fetch()

        dataU = result.next()
        dataP = result.next()
        dataS = result.next()

        print("result stuff: U: " + dataU + " P: " + dataP + "S: "  + dataS)

        if(dataU == username):
            login_attempt = hash_password(password, dataS)
            if(login_attempt == dataP + dataS):
                return True #I don't know what to return

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

#@app.route("/message_form", methods = ["GET", "POST"])
#def message_form():
#    msg = request.form.get["message"]
#    visible = request.form.get["visibility"]
#    return(msg, visible)
