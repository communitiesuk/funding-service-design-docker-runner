from flask import Blueprint, redirect, url_for
from app.data.data_access import get_responses, clear_all_responses

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


@dev_bp.route("/responses/clear")
def clear_responses():
    clear_all_responses()
    return redirect(url_for("dev_bp.view_responses"))