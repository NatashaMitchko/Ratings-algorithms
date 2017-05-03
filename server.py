"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, jsonify, render_template, redirect, request, flash, session

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "supersecretsecretkey2W00T"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    a = jsonify([1,3])
    return render_template("homepage.html")


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route("/login", methods=["GET"])
def show_login_form():
    """ Render login form. """
    return render_template("/login.html")


@app.route("/login", methods=["POST"])
def login():
    """ Starts new Flask session for existing users. """

    email = request.form.get("email")
    user = User.query.filter_by(email=email).all()

    if user == []:
        flash("User not found.")
        return render_template('/register_form.html')
    else:
        print user


@app.route("/login.json", methods=["POST"])
def is_user():
    """ Checks if user exists and opens Flask session. Or something. Not clear yet."""
    email = request.form.get("email")

    user = User.query.filter_by(email=email).all()
    if user == []:
        flash("User not found.")
        return render_template('/register_form')
    else:
        print "hi"


@app.route("/register", methods=["GET"])
def register_form():
    """ Renders new user registration form. """

    return render_template("register_form.html")


@app.route("/register", methods=["POST"])
def register_process():
    """ Processes registration and sends user to homepage. """
    # Check if users exists (validation)
    # If so log them in (create a session??)
    # If not flash "this account does not exist" and redirect to /register
    return redirect("/")



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)


    
    app.run(port=5000, host='0.0.0.0')
