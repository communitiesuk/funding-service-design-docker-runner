from flask import Blueprint, render_template, request, Response, redirect, current_app,url_for, flash
from app.data.data_access import get_pages_to_display_in_builder, save_response, get_component_by_name, save_form, get_saved_forms
import json
from app.question_reuse.generate_form import build_form_json
import requests, os
from app.all_questions.metadata_utils import generate_print_data_for_sections
from app.question_reuse.generate_all_questions import print_html

FORM_RUNNER_URL = os.getenv("FORM_RUNNER_INTERNAL_HOST", "http://form-runner:3009")
FORM_RUNNER_URL_REDIRECT = "http://localhost:3009"


self_serve_bp = Blueprint(
    "self_serve_bp",
    __name__,
    url_prefix="/",
    template_folder="templates",
)


@self_serve_bp.route("/")
def index():
    return render_template("index.html")


@self_serve_bp.route("/build_form")
def build_form():
    available_pages = []
    pages = get_pages_to_display_in_builder()
    for page in pages:
        questions = [get_component_by_name(c)["title"] for c in page["component_names"]]
        available_pages.append(
            {
                "id": page["id"],
                "display_name": page["builder_display_name"],
                "hover_info": {"title": page["form_display_name"], "questions": questions},
            }
        )
    return render_template("build_form.html", available_pages=available_pages)


@self_serve_bp.route("/download_json", methods=["POST"])
def generate_json():
    form_json = get_form_json()[0]

    return Response(
        response=json.dumps(form_json),
        mimetype="application/json",
        headers={"Content-Disposition": "attachment;filename=form.json"},
    )


def human_to_kebab_case(word: str) -> str | None:
    if word:
        return word.replace(" ", "-").strip().lower()


def get_form_json():
    pages = request.form.getlist("selected_pages")
    title = request.form.get("formName", "My Form")
    title_kebab = human_to_kebab_case(title)
    input_data = {"title": title_kebab, "pages": pages}
    form_json = build_form_json(title=title, input_json=input_data)
    return form_json, title_kebab, title


@self_serve_bp.route("/preview", methods=["POST"])
def preview_form():
    form_json, title_kebab, title = get_form_json()
    form_json["outputs"][0]["outputConfiguration"]["savePerPageUrl"] = "http://fsd-self-serve:8080/save"
    response = requests.post(url=f"{FORM_RUNNER_URL}/publish", json={"id": title_kebab, "configuration": form_json})
    return redirect(f"{FORM_RUNNER_URL_REDIRECT}/{title_kebab}")


@self_serve_bp.route("/save", methods=["PUT"])
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


@self_serve_bp.route("/form_questions", methods=["POST"])
def view_form_questions():
    form_data, title_kebab, title = get_form_json()
    print_data = generate_print_data_for_sections(
        sections=[{"section_title": title, "forms": [{"name": title_kebab, "form_data": form_data}]}], lang="en"
    )
    html = print_html(print_data)
    return render_template("view_questions.html", section_name=title, question_html=html)


@self_serve_bp.route("/save_form", methods=["POST"])
def save_form_config():
    form_data, title_kebab, title = get_form_json()
    save_form(title=title_kebab, form_config=form_data)
    flash(message=f"Form {title} was saved")
    return redirect(url_for("self_serve_bp.index"))


@self_serve_bp.route("build_section")
def build_section():
    saved_forms=get_saved_forms()
    available_forms = []
    for form_id in saved_forms.keys():
        form_config=saved_forms.get(form_id)
        available_forms.append(
            {
                "id": form_id,
                "display_name": form_config["name"],
                "hover_info": {"title": form_config["name"], "pages": ["p1", "p2"]},
            }
        )
    return render_template("build_section.html",available_forms=available_forms)