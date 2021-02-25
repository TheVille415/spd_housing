"""Import packages from Flask for our routes."""

from flask import Blueprint, render_template, request, redirect, url_for
from hoya import db
from hoya.main.utils import ValuePredictor
from bson.objectid import ObjectId
import requests
import os


main = Blueprint("main", __name__)


@main.route("/")
def landingPage():
    """Return our landing page to the user."""
    # Query all listings from the database and pass to landing page.
    return render_template("landing.html")


@main.route("/contact")
def contactUs():
    """Return contact page."""
    return render_template("contact.html")


@main.route("/about")
def aboutPage():
    """Return about page."""
    return render_template("about.html")


@main.route("/listings")
def listingsPage():
    """Display listings by location to user."""
    try:
        # Retrieve listings from Hoya database
        # TODO: query listings by city based on "search form"
        listings = []
        listings.append(db.listings.find())
        # Retrieve listings from external (realtor) API
        url = os.getenv("API_URL")

        # TODO: make city dynamic based on "search form"
        querystring = {
            "city": "New York City",
            "limit": "50",
            "offset": "0",
            "state_code": "NY",
            "sort": "relevance"
        }

        headers = {
            'x-rapidapi-key': os.getenv("API_KEY"),
            'x-rapidapi-host': os.getenv("API_HOST")
        }
        response = requests.request("GET", url, headers=headers, params=querystring).json()

        # For each listing in response["properties"] (excluding metadata)
        # append to our listings list

        for prop in response["properties"]:
            sqFootage = None
            if prop.get("lot_size", None) is None:
                sqFootage = prop.get("building_size", {}).get("size", None)
            if prop.get("building_size", None) is None:
                sqFootage = prop.get("lot_size", {}).get("size", None)

            listing = {
                "_id": prop.get("property_id", None),
                "numBedrooms": prop.get("beds", None),
                "numBathrooms": prop.get("baths", None),
                "sqFootage": sqFootage,
                "address": {
                    "city": prop.get("address", {}).get("city", None),
                    "state": prop.get("address", {}).get("state", None),
                    "zip": prop.get("address", {}).get("postal_code", None)
                }
            }
            listings.append(listing)
        # TODO: come up with stock "house" icon for FE to show with each listing
        # TODO: pass relevent listing data to FE
        # TODO: check with FE what listings template is called
        return render_template("listings.html", listings=listings)
    except(KeyError):
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
