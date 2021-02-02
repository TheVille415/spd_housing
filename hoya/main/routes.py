"""Import packages from Flask for our routes."""
from flask import Blueprint, render_template

# This is weird flask syntax that intializes our blueprint
# You'll notice our routes below look like:
# main.route('/') instead of what you're used to (app.route('/'))
# We're basically just sectioning off related routes from our app,
# which will help us preserve readability and maintainability as we scale.
main = Blueprint("main", __name__)


@main.route("/")
def landingPage():
    """Return our landing page to the user."""
    # Right now, index.html is an empty file that tells us our server is running

    test_listing =db.listings.insert_one({'name':"flower"})

    return render_template("index.html")
