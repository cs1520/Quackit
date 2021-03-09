from flask import Flask, render_template, request
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


@app.route("/")
def home():
    """Return a simple HTML page."""
    print("Hit the route!")
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)

#@app.route("/message_form", methods = ["GET", "POST"])
#def message_form():
#    msg = request.form.get["message"]
#    visible = request.form.get["visibility"]
#    return(msg, visible)
