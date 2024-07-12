import json
import os

import requests
from flask import Blueprint
from flask import Response
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from app.all_questions.metadata_utils import generate_print_data_for_sections
from app.blueprints.self_serve.data.data_access import get_all_components
from app.blueprints.self_serve.data.data_access import get_component_by_name
from app.blueprints.self_serve.data.data_access import get_pages_to_display_in_builder
from app.blueprints.self_serve.data.data_access import get_saved_forms
from app.blueprints.self_serve.data.data_access import save_form
from app.blueprints.self_serve.data.data_access import save_page
from app.blueprints.self_serve.data.data_access import save_question
from app.blueprints.self_serve.data.data_access import save_section
from app.blueprints.self_serve.forms.form_form import FormForm
from app.blueprints.self_serve.forms.page_form import PageForm
from app.blueprints.self_serve.forms.question_form import QuestionForm
from app.blueprints.self_serve.forms.section_form import SectionForm
from app.question_reuse.generate_all_questions import print_html
from app.question_reuse.generate_form import build_form_json

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


@self_serve_bp.route("/build_form", methods=["GET", "POST"])
def build_form():
    form = FormForm()
    if form.validate_on_submit():
        new_form = {
            "builder_display_name": form.builder_display_name.data,
            "start_page_guidance": form.start_page_guidance.data,
            "form_display_name": form.form_title.data,
            "id": human_to_kebab_case(form.form_title.data),
            "pages": form.selected_pages.data,
        }
        save_form(new_form)
        flash(message=f'Form {new_form["form_display_name"]} was saved')
        return redirect(url_for("self_serve_bp.index"))

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
    return render_template("build_form.html", available_pages=available_pages, form=form)


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
    title = request.form.get("form_title", "My Form")
    intro_content = request.form.get("startPageContent")
    form_id = human_to_kebab_case(title)
    input_data = {"title": form_id, "pages": pages, "intro_content": intro_content}
    form_json = build_form_json(form_title=title, input_json=input_data, form_id=form_id)
    return {"form_json": form_json, "form_id": form_id, "title": title}


@self_serve_bp.route("/preview", methods=["POST"])
def preview_form():
    form_config = generate_form_config_from_request()
    form_config["form_json"]["outputs"][0]["outputConfiguration"][
        "savePerPageUrl"
    ] = "http://fsd-self-serve:8080/dev/save"
    requests.post(
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


@self_serve_bp.route("build_section", methods=["GET", "POST"])
def build_section():
    form = SectionForm()
    if form.validate_on_submit():
        save_section(form.as_dict())
        flash(message=f"Section '{form['builder_display_name'].data}' was saved")
        return redirect(url_for("self_serve_bp.index"))

    saved_forms = get_saved_forms()
    available_forms = []
    for f in saved_forms:
        available_forms.append(
            {
                "id": f["id"],
                "display_name": f["builder_display_name"],
                "hover_info": {"title": f["builder_display_name"], "pages": f["pages"]},
            }
        )
    return render_template("build_section.html", available_forms=available_forms, form=form)


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


@self_serve_bp.route("/section_questions", methods=["POST"])
def view_section_questions():
    # form_config = generate_form_config_from_request()
    # print_data = generate_print_data_for_sections(
    #     sections=[
    #         {
    #             "section_title": form_config["title"],
    #             "forms": [{"name": form_config["form_id"], "form_data": form_config["form_json"]}],
    #         }
    #     ],
    #     lang="en",
    # )
    # html = print_html(print_data)
    # return render_template("view_questions.html", section_name=form_config["title"], question_html=html)
    pass
