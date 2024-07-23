from uuid import uuid4

from app.db import db
from app.db.models import Component
from app.db.models import Form
from app.db.models import Lizt
from app.db.models import Page
from app.db.models.application_config import Section
from app.db.models.round import Round


def get_form_for_component(component: Component) -> Form:
    page_id = component.page_id
    page = db.session.query(Page).where(Page.page_id == page_id).one_or_none()
    form = db.session.query(Form).where(Form.form_id == page.form_id).one_or_none()
    return form


def get_template_page_by_display_path(display_path: str) -> Page:
    page = (
        db.session.query(Page)
        .where(Page.display_path == display_path)
        .where(Page.is_template == True)  # noqa:E712
        .one_or_none()
    )
    return page


def get_form_by_id(form_id: str) -> Form:
    form = db.session.query(Form).where(Form.form_id == form_id).one_or_none()
    return form


def get_component_by_id(component_id: str) -> Component:
    component = db.session.query(Component).where(Component.component_id == component_id).one_or_none()
    return component


def get_list_by_id(list_id: str) -> Lizt:
    lizt = db.session.query(Lizt).where(Lizt.list_id == list_id).one_or_none()
    return lizt


def _initiate_cloned_component(to_clone: Component, new_page_id=None, new_theme_id=None):
    clone = Component(**to_clone.as_dict())

    clone.component_id = uuid4()
    clone.page_id = new_page_id
    clone.theme_id = new_theme_id
    clone.is_template = False
    clone.source_template_id = to_clone.component_id
    clone.template_name = None
    return clone


def _initiate_cloned_page(to_clone: Page, new_form_id=None):
    clone = Page(**to_clone.as_dict())
    clone.page_id = uuid4()
    clone.form_id = new_form_id
    clone.is_template = False
    clone.source_template_id = to_clone.page_id
    clone.template_name = None
    clone.components = []
    return clone


def _initiate_cloned_form(to_clone: Form, new_section_id: str) -> Form:
    clone = Form(**to_clone.as_dict())
    clone.form_id = uuid4()
    clone.section_id = new_section_id
    clone.is_template = False
    clone.source_template_id = to_clone.form_id
    clone.template_name = None
    clone.pages = []
    return clone


def _initiate_cloned_section(to_clone: Section, new_round_id: str) -> Form:
    clone = Section(**to_clone.as_dict())
    clone.round_id = new_round_id
    clone.section_id = uuid4()
    clone.is_template = False
    clone.source_template_id = to_clone.section_id
    clone.template_name = None
    clone.pages = []
    return clone


def clone_single_section(section_id: str, new_round_id=None) -> Section:
    section_to_clone: Section = db.session.query(Section).where(Section.section_id == section_id).one_or_none()
    clone = _initiate_cloned_section(section_to_clone, new_round_id)

    cloned_forms = []
    cloned_pages = []
    cloned_components = []
    # loop through forms in this section and clone each one
    for form_to_clone in section_to_clone.forms:
        cloned_form = _initiate_cloned_form(form_to_clone, clone.section_id)
        # loop through pages in this section and clone each one
        for page_to_clone in form_to_clone.pages:
            cloned_page = _initiate_cloned_page(page_to_clone, new_form_id=cloned_form.form_id)
            cloned_pages.append(cloned_page)
            # clone the components on this page
            cloned_components.extend(
                _initiate_cloned_components_for_page(page_to_clone.components, cloned_page.page_id)
            )

        cloned_forms.append(cloned_form)

    db.session.add_all([clone, *cloned_forms, *cloned_pages, *cloned_components])
    db.session.commit()

    return clone


def clone_single_form(form_id: str, new_section_id=None) -> Form:
    form_to_clone: Form = db.session.query(Form).where(Form.form_id == form_id).one_or_none()
    clone = _initiate_cloned_form(form_to_clone, new_section_id)

    cloned_pages = []
    cloned_components = []
    for page_to_clone in form_to_clone.pages:

        cloned_page = _initiate_cloned_page(page_to_clone, new_form_id=clone.form_id)
        cloned_pages.append(cloned_page)
        cloned_components.extend(_initiate_cloned_components_for_page(page_to_clone.components, cloned_page.page_id))
    db.session.add_all([clone, *cloned_pages, *cloned_components])
    db.session.commit()

    return clone


def _initiate_cloned_components_for_page(
    components_to_clone: list[Component], new_page_id: str = None, new_theme_id: str = None
):
    cloned_components = []
    for component_to_clone in components_to_clone:

        cloned_component = _initiate_cloned_component(
            component_to_clone, new_page_id=new_page_id, new_theme_id=None
        )  # TODO how should themes work when cloning?
        cloned_components.append(cloned_component)
    return cloned_components


def clone_single_page(page_id: str, new_form_id=None) -> Page:
    page_to_clone: Page = db.session.query(Page).where(Page.page_id == page_id).one_or_none()
    clone = _initiate_cloned_page(page_to_clone, new_form_id)

    cloned_components = _initiate_cloned_components_for_page(page_to_clone.components, new_page_id=clone.page_id)
    db.session.add_all([clone, *cloned_components])
    db.session.commit()

    return clone


def clone_single_component(component_id: str, new_page_id=None, new_theme_id=None) -> Component:
    component_to_clone: Component = (
        db.session.query(Component).where(Component.component_id == component_id).one_or_none()
    )
    clone = _initiate_cloned_component(component_to_clone, new_page_id, new_theme_id)

    db.session.add(clone)
    db.session.commit()

    return clone


# TODO do we need this?
def clone_multiple_components(component_ids: list[str], new_page_id=None, new_theme_id=None) -> list[Component]:
    components_to_clone: list[Component] = (
        db.session.query(Component).filter(Component.component_id.in_(component_ids)).all()
    )
    clones = [
        _initiate_cloned_component(to_clone=to_clone, new_page_id=new_page_id, new_theme_id=new_theme_id)
        for to_clone in components_to_clone
    ]
    db.session.add_all(clones)
    db.session.commit()

    return clones


def clone_single_round(round_id, new_fund_id, new_short_name) -> Round:
    round_to_clone = db.session.query(Round).where(Round.round_id == round_id).one_or_none()
    cloned_round = Round(**round_to_clone.as_dict())
    cloned_round.short_name = new_short_name
    cloned_round.round_id = uuid4()
    cloned_round.fund_id = new_fund_id
    cloned_round.is_template = False
    cloned_round.source_template_id = round_to_clone.round_id
    cloned_round.template_name = None
    cloned_round.sections = []

    db.session.add(cloned_round)
    db.session.commit()

    for section in round_to_clone.sections:
        clone_single_section(section.section_id, cloned_round.round_id)

    return cloned_round
