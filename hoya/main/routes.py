"""Import packages from Flask for our routes."""

from flask import Blueprint, render_template, request, redirect, url_for
from hoya import db
from hoya.main.utils import ValuePredictor
from bson.objectid import ObjectId
import requests
import os

# from bson.objectid import ObjectId

# This is weird flask syntax that intializes our blueprint
# You'll notice our routes below look like:
# main.route('/') instead of what you're used to (app.route('/'))
# We're basically just sectioning off related routes from our app,
# which will help us preserve readability and maintainability as we scale.
main = Blueprint("main", __name__)


@main.route("/")
def landingPage():
    """Return our landing page to the user."""
    # Query all listings from the database and pass to landing page.
    # TODO: FE is creating a listings page. We'll render that template, instead
    # with this data
    try:
        listings = db.listings.find()
        # Add API call code here to show more listings
        return render_template("index.html", listings=listings)
    except(404):
        # Return custom 404 error page, set status code to 404
        # We use 404 here (rather than 500) because 404 means
        # "resource not found"
        return render_template("404.html"), 404


@main.route("/predict/<ObjectId:listingId>", methods=["GET"])
def result(listingId):
    """Call ValuePredictor from utils to predict housing price."""
    try:
        # find our listing by the listingId passed through the params
        # parse to dict so that Python can work with it
        listing = dict(db.listings.find_one_or_404({"_id": listingId}))
        # Access just the square footage value for our prediction model
        sqFootage = listing["sqFootage"]
        # Call ValuePredictor from utils to return our prediction
        result = ValuePredictor(sqFootage)  # sq foot here
        # Parse to a string for display.
        prediction = str(result)
        # Return our index with our prediction passed in to display
        # TODO: FE team is working on where to display this.
        # Update accordingly.
        return render_template("index.html", prediction=prediction)
    except(ValueError, TypeError):
        # Return custom 500 error page, set status code to 500
        return render_template("500.html"), 500


# TODO: move listing routes to their own blueprint


@main.route("/newListing", methods=["POST"])
def newListing():
    """Add new listing resource to database."""
    try:
        # Create newListing, initialize with user input from form
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
        # Call insert_one on listings collection
        # insert newListing
        db.listings.insert_one(newListing)
        # Remove print statements after testing
        print(f"Inserted successfully! {newListing}")
        # Redirect back to landing page
        # TODO: redirect to listings page
        return redirect(url_for("main.landingPage"))
    except(ValueError, TypeError):
        # Return custom 500 error page, set status code to 500
        return render_template("500.html"), 500


@main.route("/updateListing/<id>", methods=["POST"])
def updateListing(id):
    """Update existing listing."""
    # In the future it would be nice if we could display the listing
    # details by id, and show the updated one after the user changes it
    try:
        # Call update_one() on listings collection with
        # user input
        updatedListing = db.listings.update_one(
            {"_id": id},
            {
                "$set": {
                    "numBedrooms": request.form.get("numBedrooms"),
                    "sqFootage": request.form.get("sqFootage"),
                    "numBathrooms": request.form.get("numBathrooms"),
                    "address": {
                        "street": request.form.get("street"),
                        "city": request.form.get("city"),
                        "zip": request.form.get("zip"),
                    },
                }
            },
        )
        # Once update completed, redirect user to landing page.
        return redirect(url_for("main.landingPage"))
    except(ValueError):
        # Return custom 500 error page, set status code to 500
        return render_template("500.html"), 500


@main.route("/deleteListing/<id>", methods=["POST"])
def deleteListing(id):
    """Delete existing listing by id."""
    try:
        # Call delete_one() on listings collection
        db.listings.delete_one({"_id": id})
        return redirect(url_for("main.landingPage"))
    except(ValueError):
        # Return custom 500 error page, set status code to 500
        return render_template("500.html"), 500
