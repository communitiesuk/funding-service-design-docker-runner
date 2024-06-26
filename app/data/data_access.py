from app.data.not_a_db import COMPONENTS, PAGES, LISTS

saved_responses = []
saved_forms = {}

def save_form(title,form_config):
    saved_forms[title] = form_config


def get_saved_forms():
    return saved_forms

def clear_saved_forms():
    saved_forms = {}
    return

def save_response(form_dict: dict) -> dict:
    saved_responses.append(form_dict)
    return form_dict


def get_responses() -> list:
    return saved_responses


def clear_all_responses():
    responses = []
    return


def get_component_by_name(component_name: str) -> dict:
    return COMPONENTS.get(component_name, None)


def get_all_pages() -> list:
    return PAGES


def get_pages_to_display_in_builder() -> list:
    return [p for p in PAGES if p["show_in_builder"] is True]


def get_page_by_id(id: str) -> dict:
    return next((p for p in PAGES if p["id"] == id), None)


def get_list_by_id(id: str) -> dict:
    return LISTS.get(id, None)
