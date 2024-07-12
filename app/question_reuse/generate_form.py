import copy
import json
import os

import click

from app.db.models import Component
from app.db.models import Form
from app.db.models import Page
from app.db.queries.application import get_list_by_id
from app.db.queries.application import get_template_page_by_display_path

BASIC_FORM_STRUCTURE = {
    "metadata": {},
    "startPage": None,
    "backLinkText": "Go back to application overview",
    "pages": [],
    "lists": [],
    "conditions": [],
    "fees": [],
    "sections": [],
    "outputs": [
        {
            "name": "update-form",
            "title": "Update form in application store",
            "type": "savePerPage",
            "outputConfiguration": {"savePerPageUrl": True},
        }
    ],
    "skipSummary": False,
    "name": "",
}

BASIC_PAGE_STRUCTURE = {
    "path": None,
    "title": None,
    "components": [],
    "next": [],
    "options": {},
}


SUMMARY_PAGE = {
    "path": "/summary",
    "title": "Check your answers",
    "components": [],
    "next": [],
    "section": "uLwBuz",
    "controller": "./pages/summary.js",
}


# Takes in a simple set of conditions and builds them into the form runner format
def build_conditions(component: Component) -> list:
    results = []
    for condition in component.conditions:
        result = {
            "displayName": condition["name"],
            "name": condition["name"],
            "value": {
                "name": condition["name"],
                "conditions": [
                    {
                        "field": {
                            "name": component.runner_component_name,
                            "type": component.type.value,
                            "display": component.title,
                        },
                        "operator": condition["operator"],
                        "value": {
                            "type": "Value",
                            "value": condition["value"],
                            "display": condition["value"],
                        },
                    }
                ],
            },
        }
        results.append(result)

    return results


def build_component(component: Component) -> dict:
    built_component = {
        "options": component.options or {},
        "type": component.type.value,
        "title": component.title,
        "hint": component.hint_text or "",
        "schema": {},
        "name": component.runner_component_name,
        "metadata": {"fund_builder_id": str(component.component_id)},
    }
    if component.lizt:
        built_component.update({"list": component.lizt.name})
        built_component["metadata"].update({"fund_builder_list_id": str(component.list_id)})
    return built_component


def build_page(page: Page = None, page_display_path: str = None) -> dict:
    if not page:
        page = get_template_page_by_display_path(page_display_path)
    built_page = copy.deepcopy(BASIC_PAGE_STRUCTURE)
    built_page.update(
        {
            "path": f"/{page.display_path}",
            "title": page.name_in_apply["en"],
        }
    )
    # Having a 'null' controller element breaks the form-json, needs to not be there if blank
    # if controller := input_page.get("controller", None):
    #     page["controller"] = controller
    for component in page.components:
        built_component = build_component(component)

        built_page["components"].append(built_component)

    return built_page


# Goes through the set of pages and updates the conditions and next properties to account for branching
def build_navigation(partial_form_json: dict, input_pages: list[Page]) -> dict:
    # TODO order by index not order in list
    for i in range(0, len(input_pages)):
        if i < len(input_pages) - 1:
            next_path = input_pages[i + 1].display_path
        elif i == len(input_pages) - 1:
            next_path = "summary"
        else:
            next_path = None

        this_page = input_pages[i]
        this_page_in_results = next(p for p in partial_form_json["pages"] if p["path"] == f"/{this_page.display_path}")

        has_conditions = False

        for component in this_page.components:
            if not component.conditions:
                continue
            form_json_conditions = build_conditions(component)
            has_conditions = True
            partial_form_json["conditions"].extend(form_json_conditions)

            for condition in component.conditions:
                if condition["destination_page_path"] == "CONTINUE":
                    destination_path = f"/{next_path}"
                else:
                    destination_path = f"/{condition['destination_page_path']}"

                # If this points to a pre-built page flow, add that in now (it won't be in the input)
                if (
                    destination_path not in [page["path"] for page in partial_form_json["pages"]]
                    and not destination_path == "/summary"
                ):
                    sub_page = build_page(page_display_path=destination_path[1:])
                    if not sub_page.get("next", None):
                        sub_page["next"] = [{"path": f"/{next_path}"}]

                    partial_form_json["pages"].append(sub_page)

                this_page_in_results["next"].append(
                    {
                        "path": destination_path,
                        "condition": condition["name"],
                    }
                )

        # If there were no conditions and we just continue to the next page
        if not has_conditions:
            this_page_in_results["next"].append({"path": f"/{next_path}"})

    return partial_form_json


def build_lists(pages: list[dict]) -> list:
    # Takes in the form builder format json and copies in any lists used in those pages
    lists = []
    for page in pages:
        for component in page["components"]:
            if component.get("list"):
                list_from_db = get_list_by_id(component["metadata"]["fund_builder_list_id"])
                list = {"type": list_from_db.type, "items": list_from_db.items, "name": list_from_db.name}
                lists.append(list)

    return lists


def build_start_page_content_component(content: str, pages) -> dict:
    ask_about = '<p class="govuk-body">We will ask you about:</p> <ul>'
    for page in pages:
        ask_about += f"<li>{page['title']}</li>"
    ask_about += "</ul>"

    result = {
        "name": "start-page-content",
        "options": {},
        "type": "Html",
        "content": f'<p class="govuk-body">{content}</p>{ask_about}',
        "schema": {},
    }
    return result


def human_to_kebab_case(word: str) -> str | None:
    if word:
        return word.replace(" ", "-").strip().lower()


def build_form_json(form: Form) -> dict:

    results = copy.deepcopy(BASIC_FORM_STRUCTURE)
    results["name"] = form.name_in_apply["en"]

    for page in form.pages:
        results["pages"].append(build_page(page=page))

    start_page = copy.deepcopy(BASIC_PAGE_STRUCTURE)
    start_page.update(
        {
            "title": form.name_in_apply["en"],
            "path": f"/intro-{human_to_kebab_case(form.name_in_apply['en'])}",
            "controller": "./pages/start.js",
            "next": [{"path": f"/{form.pages[0].display_path}"}],
        }
    )
    intro_content = build_start_page_content_component(content=None, pages=results["pages"])
    start_page["components"].append(intro_content)

    results["pages"].append(start_page)
    results["startPage"] = start_page["path"]

    results = build_navigation(results, form.pages)

    results["lists"] = build_lists(results["pages"])

    results["pages"].append(SUMMARY_PAGE)

    return results


@click.command()
@click.option(
    "--input_folder",
    default="./question_reuse/test_data/in/",
    help="Input configuration",
    prompt=True,
)
@click.option(
    "--input_file",
    default="org-info_basic_name_address.json",
    help="Input configuration",
    prompt=True,
)
@click.option(
    "--output_folder",
    default="../digital-form-builder/runner/dist/server/forms/",
    help="Output destination",
    prompt=True,
)
@click.option(
    "--output_file",
    default="single_name_address.json",
    help="Output destination",
    prompt=True,
)
def generate_form_json(input_folder, input_file, output_folder, output_file):
    with open(os.path.join(input_folder, input_file), "r") as f:
        input_data = json.load(f)

    form_json = build_form_json(input_data)

    with open(os.path.join(output_folder, output_file), "w") as f:
        json.dump(form_json, f)


if __name__ == "__main__":
    generate_form_json()
