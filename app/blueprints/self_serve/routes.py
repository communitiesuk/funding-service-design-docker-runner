from flask import Blueprint, render_template
from question_reuse.config.pages_to_reuse import PAGES_TO_REUSE
from question_reuse.config.lookups import LOOKUPS


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
    for page_id in PAGES_TO_REUSE.keys():
        available_pages.append(
            {"id": page_id, "name": LOOKUPS[page_id], "hover_info": {"title": page_id}}
        )
    return render_template("build_form.html", available_pages=available_pages)
