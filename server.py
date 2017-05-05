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

    return render_template("homepage.html")


@app.route('/movies')
def display_movie_list():
    """Show a list of all the movies in the database"""

    movies = Movie.query.order_by(Movie.movie_title).all()
    return render_template("movie_list.html", movies=movies)


@app.route('/movies/<movie_id>')
def display_movie_details(movie_id):
    """Displaying details for a specific movie by movie id"""

    movie = Movie.query.get(movie_id)
    ratings = movie.ratings

    scores = []
    for rating in ratings:
        scores.append(rating.score)

    number_of_ratings = len(scores)
    average_score = sum(scores) / (len(scores))

    return render_template("movie_details.html", movie=movie, average_score=average_score,
                            number_of_ratings=number_of_ratings)


@app.route('/update_rating.json', methods=["POST"])
def add_update_rating():
    """Adding or updating a rating from movie details page"""

    rating = int(request.form['user_rating'])
    print rating
    user_id = session['user_id']
    print user_id
    movie_id = request.form['movie_id']
    print movie_id
    current_rating = Rating.query.filter((Rating.user_id==user_id) & (Rating.movie_id==movie_id)).first()

    if current_rating:
        current_rating.score = rating
        db.session.commit()
    else:
        new_rating = Rating(movie_id=movie_id, user_id=user_id, score=rating)
        print new_rating
        db.session.add(new_rating)
        db.session.commit()


    return jsonify({})



@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route("/users/<user_id>")
def show_user_profile(user_id):
    """Shows users profile by user ID"""

    user = User.query.get(user_id)
    user_ratings = user.ratings
    movie_titles = {}
    for rating in user_ratings:
        movie_titles[rating.movie_id] = rating.movie.movie_title

    print user_ratings
    return render_template("user_profile.html", user=user, user_ratings=user_ratings,
                                                movie_titles=movie_titles)


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
            return redirect('/users/{}'.format(user.user_id))
        else:
            flash("Wrong password. Please try again.")
            return redirect("/login")


@app.route("/logout")
def logout():
    """Clears user session"""

    print session['user_id'] + "logging out."
    session.clear()
    flash("Successfully logged out.")
    return redirect('/')


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
