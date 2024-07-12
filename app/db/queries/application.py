from app.db import db
from app.db.models import Component
from app.db.models import Form
from app.db.models import Lizt
from app.db.models import Page


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
