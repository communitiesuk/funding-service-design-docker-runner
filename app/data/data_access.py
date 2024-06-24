from app.data.not_a_db import COMPONENTS, PAGES


def get_component_by_name(component_name: str) -> dict:
    return COMPONENTS.get(component_name, None)


def get_all_pages() -> list:
    return PAGES


def get_pages_to_display_in_builder() -> list:
    return [p for p in PAGES if p["show_in_builder"] is True]
