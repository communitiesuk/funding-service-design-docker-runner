from flask import Blueprint
from app.data.data_access import get_responses

dev_bp = Blueprint(
    "dev_bp",
    __name__,
    url_prefix="/dev",
    template_folder="templates",
)

@dev_bp.route("/responses")
def view_responses():
    responses = get_responses()
    return responses