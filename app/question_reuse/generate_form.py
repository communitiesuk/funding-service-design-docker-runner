import copy
import datetime
import json
import os

from app.data.data_access import get_page_by_id, get_component_by_name, get_list_by_id

import click

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
def build_conditions(component_name, component: dict) -> list:
    results = []
    for condition in component["conditions"]:
        json = component["json_snippet"]
        result = {
            "displayName": condition["name"],
            "name": condition["name"],
            "value": {
                "name": condition["name"],
                "conditions": [
                    {
                        "field": {
                            "name": component_name,
                            "type": json["type"],
                            "display": json["title"],
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


def build_page(input_page_name: str) -> dict:
    input_page = get_page_by_id(input_page_name)
    page = copy.deepcopy(BASIC_PAGE_STRUCTURE)
    page.update(
        {
            "path": f"/{input_page_name}",
            "title": input_page["form_display_name"],
        }
    )
    # Having a 'null' controller element breaks the form-json, needs to not be there if blank
    if controller := input_page.get("controller", None):
        page["controller"] = controller
    for component_name in input_page["component_names"]:
        component = copy.deepcopy(get_component_by_name(component_name)["json_snippet"])
        component["name"] = component_name
        conditions = component.get("conditions", None)
        if conditions:
            component.pop("conditions")

        page["components"].append(component)

    return page


# Goes through the set of pages and updates the conditions and next properties to account for branching
def build_navigation(partial_form_json: dict, input_pages: list[str]) -> dict:
    for i in range(0, len(input_pages)):
        if i < len(input_pages) - 1:
            next_path = input_pages[i + 1]
        elif i == len(input_pages) - 1:
            next_path = "summary"
        else:
            next_path = None

        this_path = input_pages[i]
        this_page_in_results = next(p for p in partial_form_json["pages"] if p["path"] == f"/{this_path}")

        has_conditions = False
        for c_name in get_page_by_id(this_path)["component_names"]:
            component = get_component_by_name(c_name)
            if "conditions" in component:

                form_json_conditions = build_conditions(c_name, component)
                has_conditions = True
                partial_form_json["conditions"].extend(form_json_conditions)
                for condition in component["conditions"]:
                    if condition["destination_page"] == "CONTINUE":
                        destination_path = f"/{next_path}"
                    else:
                        destination_path = f"/{condition['destination_page']}"

                    # If this points to a pre-built page flow, add that in now (it won't be in the input)
                    if (
                        destination_path not in [page["path"] for page in partial_form_json["pages"]]
                        and not destination_path == "/summary"
                    ):
                        sub_page = build_page(destination_path[1:])
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


def build_lists(pages: dict) -> dict:
    # Takes in the form builder format json and copies in any lists used in those pages
    lists = []
    for page in pages:
        for component in page["components"]:
            if "list" in component:
                list = copy.deepcopy(get_list_by_id(component["list"]))
                list.update({"name": component["list"], "title": component["title"]})
                lists.append(list)

    return lists


def build_start_page_content_component(content: str, pages) -> dict:
    ask_about='<p class="govuk-body">We will ask you about:</p> <ul>'
    for page in pages:
        ask_about+=f"<li>{page['title']}</li>"
    ask_about += "</ul>"

    result = {
        "name": "start-page-content",
        "options": {},
        "type": "Html",
        "content": f'<p class="govuk-body">{content}</p>{ask_about}',
        "schema": {},
    }
    return result

# title arg is used for title of first page in form
def build_form_json(input_json: dict, form_title: str, form_id: str) -> dict:

    results = copy.deepcopy(BASIC_FORM_STRUCTURE)
    results["name"] = form_title


    for page in input_json["pages"]:
        results["pages"].append(build_page(page))

    start_page = copy.deepcopy(BASIC_PAGE_STRUCTURE)
    start_page.update(
        {
            "title": form_title,
            "path": f"/intro-{form_id}",
            "controller": "./pages/start.js",
            "next": [{"path": f"/{input_json['pages'][0]}"}],
        }
    )
    if intro_content := input_json.get("intro_content"):
        content = build_start_page_content_component(content=intro_content, pages=results["pages"])
        start_page["components"].append(content)

    results["pages"].append(start_page)
    results["startPage"] = start_page["path"]

    results = build_navigation(results, input_json["pages"])

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
