"""Import packages from Flask for our routes."""
from flask import Blueprint, render_template, request, redirect, url_for
from hoya import db

# This is weird flask syntax that intializes our blueprint
# You'll notice our routes below look like:
# main.route('/') instead of what you're used to (app.route('/'))
# We're basically just sectioning off related routes from our app,
# which will help us preserve readability and maintainability as we scale.
main = Blueprint("main", __name__)


@main.route("/")
def landingPage():
    """Return our landing page to the user."""
    # Right now, index.html is an empty file that tells
    # us our server is running
    listings = db.listings.find()
    print(list(listings))
    return render_template("index.html")


# TODO: move listing routes to their own blueprint


@main.route("/newListing", methods=["POST"])
def newListing():
    """Add new listing resource to database."""
    newListing = {
        "numBedrooms": request.form.get("numBedrooms"),
        "sqFootage": request.form.get("sqFootage"),
        "numBathrooms": request.form.get("numBathrooms"),
        "address": {
            "street": request.form.get("street"),
            "city": request.form.get("city"),
            "zip": request.form.get("zip"),
        },
    }
    db.listings.insert_one(newListing)
    return redirect(url_for("main.newListing"))
