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
        flash("User not found. Please register.")
        return redirect('/register')
    else:
        user = user[0]
        print user
        password = request.form.get("password")
        if password == user.password:
            # start a login session
            session['user_id'] = str(user.user_id)
            flash("Successfully logged in.")
            print "User", user.user_id, "successfully logged in."
            return redirect('/')
        else: 
            flash("Wrong password. Please try again.")
            return redirect("/login")

@app.route("/logout")
# @login_required
def logout():
    print session['user_id'] + "logging out."
    session.clear()
    flash("Successfully logged out.")
    return redirect('/')

# @app.route("/login.json", methods=["POST"])
# def is_user():
#     """ Checks if user exists and opens Flask session. Or something. Not clear yet."""
#     email = request.form.get("email")

    # user = User.query.filter_by(email=email).all()
    # if user == []:
    #     flash("User not found.")
    #     return render_template('/register_form')
    # else:
    #     print "hi"


@app.route("/register", methods=["GET"])
def register_form():
    """ Renders new user registration form. """

    return render_template("register_form.html")


@app.route("/register", methods=["POST"])
def register_process():
    """ Processes registration and sends user to homepage. """
    email = request.form.get("email")
    password = request.form.get("password")
    age = request.form.get("age")
    zipcode = request.form.get("zipcode")

    user = User.query.filter_by(email=email).all()
    if user == []:
        # create user
        new_user = User(email=email, password=password, age=age, zipcode=zipcode)
        db.session.add(new_user)
        db.session.commit()
        print "Added user successfully"
        user = User.query.filter_by(email=email).one()
        session['user_id'] = str(user.user_id)
        flash("Successfully logged in.")
        print "Created user with ID: {}, logged them in".format(user.user_id)
        return redirect('/')
    else:
        flash("User already exists. Please log in.")
        redirect('/login')
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
