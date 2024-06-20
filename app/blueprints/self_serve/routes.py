from flask import Blueprint, render_template


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
    pass