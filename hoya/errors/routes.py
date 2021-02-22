"""Handle errors to provide positive user experience."""
from flask import Blueprint, render_template

errors = Blueprint("errors", __name__)


@errors.errorhandler(404)
def show404(err):
    """Show 404 page."""
    print(err)
    return render_template("404.html")


@errors.errorhandler(500)
def show500(err):
    print(err)
    return render_template("500.html")
