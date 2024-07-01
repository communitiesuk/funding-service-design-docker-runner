from flask import Blueprint, redirect, url_for, current_app, request
from app.data.data_access import get_responses, clear_all_responses, get_saved_forms, clear_saved_forms, save_response

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


@dev_bp.route("/save", methods=["PUT"])
def save_per_page():
    current_app.logger.info("Saving request")
    request_json = request.get_json(force=True)
    current_app.logger.info(request_json)
    form_dict = {
        "application_id": "",
        "form_name": request_json["name"],
        "question_json": request_json["questions"],
        "is_summary_page_submit": request_json["metadata"].get("isSummaryPageSubmit", False),
    }
    updated_form = save_response(form_dict=form_dict)
    return updated_form, 201