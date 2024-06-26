from flask import Blueprint, render_template, request, Response, redirect, url_for, current_app
from app.data.data_access import get_pages_to_display_in_builder, save_response, get_component_by_name
import json
from app.question_reuse.generate_form import build_form_json
import requests, os


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
                "hover_info": {"title": page["form_display_name"], "questions":questions},
            }
        )
    return render_template("build_form.html", available_pages=available_pages)


@self_serve_bp.route("/download_json", methods=["POST"])
def generate_json():
    pages = request.form.getlist("selected_pages")
    title = request.form.get("formName")
    input_data = {"title": title, "pages": pages}
    form_json = build_form_json(input_data)

    return Response(
        response=json.dumps(form_json),
        mimetype="application/json",
        headers={"Content-Disposition": "attachment;filename=form.json"},
    )


def human_to_kebab_case(word: str) -> str | None:
    if word:
        return word.replace(" ", "-").strip().lower()


@self_serve_bp.route("/preview", methods=["POST"])
def preview_form():
    pages = request.form.getlist("selected_pages")
    title = request.form.get("formName", "My Form")
    title_kebab = human_to_kebab_case(title)
    input_data = {"title": title_kebab, "pages": pages}
    form_json = build_form_json(title=title, input_json=input_data)
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




    # rehydrate_payload = format_runner_payload(
    #     form_data=None, application_id="test-123", returnUrl="", form_name=title_kebab
    # )
    # rehydration_token = get_token(title_kebab, rehydrate_payload)

    # return redirect(location=f"{FORM_RUNNER_URL_REDIRECT}/session/{rehydration_token}")



# def get_token(form_name, rehydrate_payload):
#     res = requests.post(
#         f"{FORM_RUNNER_URL}/session/{form_name}",
#         json=rehydrate_payload,
#     )
#     if res.status_code == 201:
#         token_json = res.json()
#         return token_json["token"]
#     else:
#         raise Exception("Unexpected response POSTing form token" f" response code {res.status_code}")


# def format_runner_payload(
#     form_data,
#     application_id,
#     returnUrl,
#     form_name,
# ):

#     formatted_data = {}
#     callback_url = "http://fsd-self-serve:8080/"

#     formatted_data["options"] = {
#         "callbackUrl": callback_url,
#         "customText": {"nextSteps": "Form Submitted"},
#         "returnUrl": returnUrl,
#         "markAsCompleteComponent": False,
#     }
#     # formatted_data["questions"] = extract_subset_of_data_from_application(
#     #     form_data, "questions"
#     # )
#     formatted_data["metadata"] = {}
#     formatted_data["metadata"]["application_id"] = application_id
#     formatted_data["metadata"]["form_session_identifier"] = application_id
#     formatted_data["metadata"]["form_name"] = form_name
#     return formatted_data
