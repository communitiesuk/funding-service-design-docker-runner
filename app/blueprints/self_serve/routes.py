from flask import Blueprint, render_template, request, Response, redirect, current_app, url_for, flash
from app.blueprints.self_serve.forms.question_form import QuestionForm
from app.blueprints.self_serve.forms.page_form import PageForm
from app.data.data_access import (
    get_pages_to_display_in_builder,
    get_all_components,
    save_response,
    get_component_by_name,
    save_form,
    save_page,
    get_saved_forms,
    save_question,
)
import json
from app.question_reuse.generate_form import build_form_json
import requests, os
from app.all_questions.metadata_utils import generate_print_data_for_sections
from app.question_reuse.generate_all_questions import print_html

FORM_RUNNER_URL = os.getenv("FORM_RUNNER_INTERNAL_HOST", "http://form-runner:3009")
FORM_RUNNER_URL_REDIRECT = os.getenv("FORM_RUNNER_EXTERNAL_HOST", "http://localhost:3009")


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
        questions = [
            x["json_snippet"]["title"] if (x := get_component_by_name(comp_name)) else comp_name
            for comp_name in page["component_names"]
        ]
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
    form_json = generate_form_config_from_request()["form_json"]

    return Response(
        response=json.dumps(form_json),
        mimetype="application/json",
        headers={"Content-Disposition": "attachment;filename=form.json"},
    )


def human_to_kebab_case(word: str) -> str | None:
    if word:
        return word.replace(" ", "-").strip().lower()


def generate_form_config_from_request():
    pages = request.form.getlist("selected_pages")
    title = request.form.get("formName", "My Form")
    intro_content = request.form.get("startPageContent")
    form_id = human_to_kebab_case(title)
    input_data = {"title": form_id, "pages": pages, "intro_content": intro_content}
    form_json = build_form_json(form_title=title, input_json=input_data, form_id=form_id)
    return {"form_json": form_json, "form_id": form_id, "title": title}


@self_serve_bp.route("/preview", methods=["POST"])
def preview_form():
    form_config = generate_form_config_from_request()
    form_config["form_json"]["outputs"][0]["outputConfiguration"]["savePerPageUrl"] = "http://fsd-self-serve:8080/dev/save"
    response = requests.post(
        url=f"{FORM_RUNNER_URL}/publish", json={"id": form_config["form_id"], "configuration": form_config["form_json"]}
    )
    return redirect(f"{FORM_RUNNER_URL_REDIRECT}/{form_config['form_id']}")


@self_serve_bp.route("/form_questions", methods=["POST"])
def view_form_questions():
    form_config = generate_form_config_from_request()
    print_data = generate_print_data_for_sections(
        sections=[
            {
                "section_title": form_config["title"],
                "forms": [{"name": form_config["form_id"], "form_data": form_config["form_json"]}],
            }
        ],
        lang="en",
    )
    html = print_html(print_data)
    return render_template("view_questions.html", section_name=form_config["title"], question_html=html)


@self_serve_bp.route("/save_form", methods=["POST"])
def save_form_config():
    form_config = generate_form_config_from_request()
    save_form(title=form_config["form_id"], form_config=form_config["form_json"])
    flash(message=f"Form {form_config['title']} was saved")
    return redirect(url_for("self_serve_bp.index"))


@self_serve_bp.route("build_section")
def build_section():
    pass


#     saved_forms = get_saved_forms()
#     available_forms = []
#     for form_id in saved_forms.keys():
#         form_config = saved_forms.get(form_id)
#         available_forms.append(
#             {
#                 "id": form_id,
#                 "display_name": form_config["name"],
#                 "hover_info": {"title": form_config["name"], "pages": ["p1", "p2"]},
#             }
#         )
#     return render_template("build_section.html", available_forms=available_forms)


@self_serve_bp.route("/add_question", methods=["GET", "POST"])
def add_question():
    form = QuestionForm()
    question = form.as_dict()
    if form.validate_on_submit():
        save_question(question)
        flash(message=f"Question '{question['title']}' was saved")
        return redirect(url_for("self_serve_bp.index"))
    return render_template("add_question.html", form=form)


@self_serve_bp.route("/build_page", methods=["GET", "POST"])
def build_page():
    form = PageForm()
    if form.validate_on_submit():
        new_page = {
            "id": form.id.data,
            "builder_display_name": form.builder_display_name.data,
            "form_display_name": form.form_display_name.data,
            "component_names": form.selected_components.data,
            "show_in_builder": True,
        }
        save_page(new_page)
        flash(message=f"Page '{form.builder_display_name.data}' was saved")
        return redirect(url_for("self_serve_bp.index"))
    components = get_all_components()
    available_questions = [
        {
            "id": c["id"],
            "display_name": c["builder_display_name"] or c["id"],
            "hover_info": {"title": c["json_snippet"]["title"]},
        }
        for c in components
    ]
    return render_template("build_page.html", form=form, available_questions=available_questions)
