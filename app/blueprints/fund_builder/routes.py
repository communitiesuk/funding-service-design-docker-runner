import json
import os
from datetime import datetime
from random import randint

import requests
from flask import Blueprint
from flask import Response
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from app.all_questions.metadata_utils import generate_print_data_for_sections
from app.blueprints.fund_builder.forms.fund import FundForm
from app.blueprints.fund_builder.forms.round import RoundForm
from app.db.models.fund import Fund
from app.db.models.round import Round
from app.db.queries.application import get_form_by_id
from app.db.queries.fund import add_fund
from app.db.queries.fund import get_all_funds
from app.db.queries.fund import get_fund_by_id
from app.db.queries.round import add_round
from app.db.queries.round import get_round_by_id
from app.question_reuse.generate_all_questions import print_html
from app.question_reuse.generate_form import build_form_json

# Blueprint for routes used by v1 of FAB - using the DB
build_fund_bp = Blueprint(
    "build_fund_bp",
    __name__,
    url_prefix="/",
    template_folder="templates",
)
# TODO get these from config
FUND_BUILDER_HOST = "fab:8080"
FORM_RUNNER_URL = os.getenv("FORM_RUNNER_INTERNAL_HOST", "http://form-runner:3009")
FORM_RUNNER_URL_REDIRECT = os.getenv("FORM_RUNNER_EXTERNAL_HOST", "http://localhost:3009")


def all_funds_as_govuk_select_items(all_funds: list) -> list:
    """
    Reformats a list of funds into a list of display/value items that can be passed to a govUk select macro
    in the html
    """
    return [{"text": f"{f.short_name} - {f.name_json['en']}", "value": str(f.fund_id)} for f in all_funds]


@build_fund_bp.route("/fund/view", methods=["GET", "POST"])
def view_fund():
    """
    Renders a template providing a drop down list of funds. If a fund is selected, renders its config info
    """
    params = {"all_funds": all_funds_as_govuk_select_items(get_all_funds())}
    if request.method == "POST":
        fund_id = request.form.get("fund_id")
        fund = get_fund_by_id(fund_id)
        params["fund"] = fund

    return render_template("view_fund_config.html", **params)


@build_fund_bp.route("/fund/round/<round_id>/application_config")
def view_app_config(round_id):
    """
    Renders a template displaying application configuration info for the chosen round
    """
    round = get_round_by_id(round_id)
    fund = get_fund_by_id(round.fund_id)
    return render_template("view_application_config.html", round=round, fund=fund)


@build_fund_bp.route("/fund/round/<round_id>/assessment_config")
def view_assess_config(round_id):
    """
    Renders a template displaying assessment configuration info for the chosen round
    """
    round = get_round_by_id(round_id)
    fund = get_fund_by_id(round.fund_id)
    return render_template("view_assessment_config.html", round=round, fund=fund)


@build_fund_bp.route("/fund", methods=["GET", "POST"])
def fund():
    """
    Renders a template to allow a user to add a fund, when saved validates the form data and saves to DB
    """
    form: FundForm = FundForm()
    if form.validate_on_submit():
        add_fund(
            Fund(
                name_json={"en": form.name_en.data},
                title_json={"en": form.title_en.data},
                description_json={"en": form.description_en.data},
                welsh_available=form.welsh_available.data,
                short_name=form.short_name.data,
                audit_info={"user": "dummy_user", "timestamp": datetime.now().isoformat(), "action": "create"},
            )
        )
        flash(f"Saved fund {form.name_en.data}")
        return redirect(url_for("self_serve_bp.index"))

    return render_template("fund.html", form=form)


@build_fund_bp.route("/round", methods=["GET", "POST"])
def round():
    """
    Renders a template to select a fund and add a round to that fund. If saved, validates the round form data
    and saves to DB
    """
    all_funds = get_all_funds()
    form: RoundForm = RoundForm()
    if form.validate_on_submit():
        add_round(
            Round(
                fund_id=form.fund_id.data,
                audit_info={"user": "dummy_user", "timestamp": datetime.now().isoformat(), "action": "create"},
                title_json={"en": form.title_en.data},
                short_name=form.short_name.data,
                opens=form.opens.data,
                deadline=form.deadline.data,
                assessment_start=form.assessment_start.data,
                reminder_date=form.reminder_date.data,
                assessment_deadline=form.assessment_deadline.data,
                prospectus_link=form.prospectus_link.data,
                privacy_notice_link=form.privacy_notice_link.data,
            )
        )

        flash(f"Saved round {form.title_en.data}")
        return redirect(url_for("self_serve_bp.index"))

    return render_template(
        "round.html",
        form=form,
        all_funds=all_funds_as_govuk_select_items(all_funds),
    )


@build_fund_bp.route("/preview/<form_id>", methods=["GET"])
def preview_form(form_id):
    """
    Generates the form json for a chosen form, does not persist this, but publishes it to the form runner using the
    'runner_publish_name' of that form. Returns a redirect to that form in the form-runner
    """
    form = get_form_by_id(form_id)
    form_json = build_form_json(form)

    # Update the savePerPageUrl to point at the dev route to save responses
    form_json["outputs"][0]["outputConfiguration"]["savePerPageUrl"] = f"http://{FUND_BUILDER_HOST}/dev/save"
    try:
        publish_response = requests.post(
            url=f"{FORM_RUNNER_URL}/publish", json={"id": form.runner_publish_name, "configuration": form_json}
        )
        if not str(publish_response.status_code).startswith("2"):
            return "Error during form publish", 500
    except Exception as e:
        return f"unable to publish form: {str(e)}", 500
    return redirect(f"{FORM_RUNNER_URL_REDIRECT}/{form.runner_publish_name}")


@build_fund_bp.route("/download/<form_id>", methods=["GET"])
def download_form_json(form_id):
    """
    Generates form json for the selected form and returns it as a file download
    """
    form = get_form_by_id(form_id)
    form_json = build_form_json(form)

    # TODO what should we set this to?
    form_json["outputs"][0]["outputConfiguration"]["savePerPageUrl"] = "http://localhost:5000/dev/save"
    return Response(
        response=json.dumps(form_json),
        mimetype="application/json",
        headers={"Content-Disposition": f"attachment;filename=form-{randint(0,999)}.json"},
    )


@build_fund_bp.route("/fund/round/<round_id>/all_questions", methods=["GET"])
def view_all_questions(round_id):
    """
    Generates the form data for all sections in the selected round, then uses that to generate the 'All Questions'
    data for that round and returns that to render in a template.
    """
    round = get_round_by_id(round_id)
    fund = get_fund_by_id(round.fund_id)
    sections_in_round = round.sections
    section_data = []
    for section in sections_in_round:
        forms = [{"name": form.runner_publish_name, "form_data": build_form_json(form)} for form in section.forms]
        section_data.append({"section_title": section.name_in_apply["en"], "forms": forms})

    print_data = generate_print_data_for_sections(
        section_data,
        lang="en",
    )
    html = print_html(print_data)
    return render_template("view_questions.html", round=round, fund=fund, question_html=html)
