from flask import Flask, render_template, request
from google.cloud import datastore
import hashlib
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
    print(username + " " + password)
    return render_template("login.html")

@app.route("/register", methods = ["POST"])
def register_data():
    
    username = request.form.get("username")
    password = request.form.get("password")

    user_key = data.key("UserCredential", username)
    user = datastore.Entity(key=user_key)
    user["username"] = username
    user["hashPassword"] = hash_password(password)
    data.put(user)    

    return render_template("home.html")

def hash_password(password):
    """This will give us a hashed password that will be extremlely difficult to 
    reverse.  Creating this as a separate function allows us to perform this
    operation consistently every time we use it."""
    encoded = password.encode("utf-8")
    return hashlib.pbkdf2_hmac("sha256", encoded, 100000)

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
