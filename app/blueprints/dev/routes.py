from flask import Blueprint, redirect, url_for
from app.data.data_access import get_responses, clear_all_responses, get_saved_forms, clear_saved_forms

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

@dev_bp.route("/forms")
def view_forms():
    forms = get_saved_forms()
    return forms


@dev_bp.route("/forms/clear")
def clear_forms():
    clear_saved_forms()
    return redirect(url_for("dev_bp.view_forms"))