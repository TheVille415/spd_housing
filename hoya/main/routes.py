"""Import packages from Flask for our routes."""

from flask import Blueprint, render_template, request, redirect, url_for
from hoya import db
from hoya.main.utils import ValuePredictor
from bson.objectid import ObjectId
import random
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


@main.route('/listings', methods=["GET", "POST"])
def listingsQuery():
    """Render search form in listings.html."""
    try:
        if request.method == 'GET':
            return render_template('queryListing.html')
        if request.method == 'POST':
            city = request.form.get('city')
            stateCode = request.form.get('stateCode')
            return redirect(url_for('main.listingsPage', city=city, stateCode=stateCode))
    except (ValueError, TypeError):
        return render_template('500.html'), 500


@main.route("/listings/<string:city>/<string:stateCode>")
def listingsPage(city, stateCode=None):
    """Display listings by location to user."""
    try:
        # Retrieve listings from Hoya database
        listings = list(db.listings.find({"address": {"city": city}}))

        # Retrieve listings from external (realtor) API
        url = os.getenv("API_URL")

        querystring = {
            "city": city,
            "limit": "20",
            "offset": "0",
            "state_code": stateCode,
            "sort": "relevance",
        }

        headers = {
            "x-rapidapi-key": os.getenv("API_KEY"),
            "x-rapidapi-host": os.getenv("API_HOST"),
        }
        response = requests.request(
            "GET", url, headers=headers, params=querystring
        ).json()

        # For each listing in response["properties"] (excluding metadata)
        # append to our listings list
        # given that our API returns inconsistent data, handle cases where keys
        # don't exist

        for prop in response["properties"]:
            sqFootage = None
            if prop.get("lot_size", None) is None:
                sqFootage = prop.get("building_size", {}).get(
                    "size", random.randint(900, 3400)
                )
            if prop.get("building_size", None) is None:
                sqFootage = prop.get("lot_size", {}).get(
                    "size", random.randint(900, 3400)
                )

            listing = {
                "_id": prop.get("property_id", ObjectId()),
                "numBedrooms": prop.get("beds", random.randint(1, 5)),
                "numBathrooms": prop.get("baths", random.randint(1, 5)),
                "sqFootage": sqFootage,
                "price": prop.get("price", random.randint(230000, 800000)),
                "address": {
                    # TODO: instead of None, pass in city, state from req.form
                    "city": prop.get("address", {}).get("city", None),
                    "state": prop.get("address", {}).get("state", None),
                    "zip": prop.get("address", {}).get("postal_code", None),
                },
            }
            listings.append(listing)
        return render_template('listings.html', listings=listings)
    except (KeyError, ValueError):
        # Return custom 404 error page, set status code to 404
        # We use 404 here (rather than 500) because 404 means
        # "resource not found"
        return render_template("404.html"), 404


@main.route("/predict/<listingId>", methods=["GET"])
def predict(listingId):
    """Call ValuePredictor from utils to predict housing price."""
    try:
        # find our listing by the listingId passed through the params
        # parse to dict so that Python can work with it
        listing = dict(db.listings.find_one_or_404({"_id": ObjectId(listingId)}))
        # Access just the square footage value for our prediction model
        sqFootage = listing["sqFootage"]
        # Call ValuePredictor from utils to return our prediction
        result = ValuePredictor(sqFootage)  # sq foot here
        # Parse to a string for display.
        prediction = str(result[0][0])

        # Add price to our database documents
        listing["price"] = prediction

        # Return our index with our prediction passed in to display
        return render_template("predict.html", listing=listing)
    except (ValueError, TypeError):
        # Return custom 500 error page, set status code to 500
        return render_template("500.html"), 500


@main.route("/newListing", methods=["POST"])
def newListing():
    """Add new listing resource to database."""
    try:
        # Create newListing, initialize with user input from form
        newListing = {
            "numBedrooms": request.form.get("numBedrooms"),
            "sqFootage": request.form.get("sqFootage"),
            "numBathrooms": request.form.get("numBathrooms"),
            "price": None,
            "address": {
                "street": request.form.get("address").split(" ")[0],
                "city": request.form.get("address").split(" ")[1],
                "zip": request.form.get("address").split(" ")[2],
            },
        }
        # Call insert_one on listings collection
        # insert newListing
        insertedListing = db.listings.insert_one(newListing)
        # Redirect back to landing page
        # TODO: redirect to listings page
        return redirect(
            url_for("main.predict", listingId=insertedListing.inserted_id)
        )
    except (ValueError, TypeError):
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
    except (ValueError):
        # Return custom 500 error page, set status code to 500
        return render_template("500.html"), 500


@main.route("/deleteListing/<id>", methods=["POST"])
def deleteListing(id):
    """Delete existing listing by id."""
    try:
        # Call delete_one() on listings collection
        db.listings.delete_one({"_id": id})
        return redirect(url_for("main.landingPage"))
    except (ValueError):
        # Return custom 500 error page, set status code to 500
        return render_template("500.html"), 500
