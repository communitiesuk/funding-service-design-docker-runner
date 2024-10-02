from uuid import uuid4

from sqlalchemy import delete

from app.db import db
from app.db.models import Component
from app.db.models import Form
from app.db.models import Lizt
from app.db.models import Page
from app.db.models import Section
from app.db.models.round import Round
from app.db.queries.round import get_round_by_id


def get_all_template_sections() -> list[Section]:
    return db.session.query(Section).where(Section.is_template == True).all()  # noqa:E712


def get_section_by_id(section_id) -> Section:
    s = db.session.query(Section).where(Section.section_id == section_id).one_or_none()
    return s


def get_all_template_forms() -> list[Form]:
    return db.session.query(Form).where(Form.is_template == True).all()  # noqa:E712


def get_form_for_component(component: Component) -> Form:
    page_id = component.page_id
    page = db.session.query(Page).where(Page.page_id == page_id).one_or_none()
    form = db.session.query(Form).where(Form.form_id == page.form_id).one_or_none()
    return form


def get_form_by_id(form_id: str) -> Form:
    form = db.session.query(Form).where(Form.form_id == form_id).one_or_none()
    return form


def get_form_by_template_name(template_name: str) -> Form:
    form = db.session.query(Form).where(Form.template_name == template_name).one_or_none()
    return form


def get_component_by_id(component_id: str) -> Component:
    component = db.session.query(Component).where(Component.component_id == component_id).one_or_none()
    return component


def get_list_by_id(list_id: str) -> Lizt:
    lizt = db.session.query(Lizt).where(Lizt.list_id == list_id).one_or_none()
    return lizt


def get_list_by_name(list_name: str) -> Lizt:
    lizt = db.session.query(Lizt).filter_by(name=list_name).first()
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


def _initiate_cloned_form(to_clone: Form, new_section_id: str, section_index=0) -> Form:
    clone = Form(**to_clone.as_dict())
    clone.form_id = uuid4()
    clone.section_id = new_section_id
    clone.is_template = False
    clone.source_template_id = to_clone.form_id
    clone.template_name = None
    clone.pages = []
    clone.section_index = section_index
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
        cloned_form = _initiate_cloned_form(form_to_clone, clone.section_id, section_index=form_to_clone.section_index)
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
    cloned_pages = _fix_cloned_default_pages(cloned_pages)
    db.session.commit()

    return clone


def _fix_cloned_default_pages(cloned_pages: list[Page]):
    # Go through each page
    # Get the page ID of the default next page (this will be a template page)
    # Find the cloned page that was created from that template
    # Get that cloned page's ID
    # Update this default_next_page to point to the cloned page

    for clone in cloned_pages:
        if clone.default_next_page_id:
            template_id = clone.default_next_page_id
            concrete_next_page = next(p for p in cloned_pages if p.source_template_id == template_id)
            clone.default_next_page_id = concrete_next_page.page_id

    return cloned_pages


def clone_single_form(form_id: str, new_section_id=None, section_index=0) -> Form:
    form_to_clone: Form = db.session.query(Form).where(Form.form_id == form_id).one_or_none()
    clone = _initiate_cloned_form(form_to_clone, new_section_id, section_index=section_index)

    cloned_pages = []
    cloned_components = []
    for page_to_clone in form_to_clone.pages:

        cloned_page = _initiate_cloned_page(page_to_clone, new_form_id=clone.form_id)
        cloned_pages.append(cloned_page)
        cloned_components.extend(_initiate_cloned_components_for_page(page_to_clone.components, cloned_page.page_id))
    db.session.add_all([clone, *cloned_pages, *cloned_components])
    cloned_pages = _fix_cloned_default_pages(cloned_pages)
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
    cloned_round.fund_id = new_fund_id
    cloned_round.short_name = new_short_name
    cloned_round.round_id = uuid4()
    cloned_round.is_template = False
    cloned_round.source_template_id = round_to_clone.round_id
    cloned_round.template_name = None
    cloned_round.sections = []

    db.session.add(cloned_round)
    db.session.commit()

    for section in round_to_clone.sections:
        clone_single_section(section.section_id, cloned_round.round_id)

    return cloned_round


# CRUD operations for Section, Form, Page, and Component
# CRUD SECTION
def insert_new_section(new_section_config):
    """
    Inserts a section object based on the provided configuration.

    Parameters:
        new_section_config (dict): A dictionary containing the configuration for the new section.
            new_section_config keys:
                - round_id (str): The ID of the round to which the section belongs.
                - name_in_apply_json (dict): The name of the section as it will be in the Application
                JSON (support multiple languages/keys).
                - template_name (str): The name of the template.
                - is_template (bool): A flag indicating whether the section is a template.
                - source_template_id (str): The ID of the source template.
                - audit_info (dict): Audit information for the section.
                - index (int): The index of the section.
            Returns:
                Section: The newly created section object.
    """
    section = Section(
        section_id=uuid4(),
        round_id=new_section_config.get("round_id", None),
        name_in_apply_json=new_section_config.get("name_in_apply_json"),
        template_name=new_section_config.get("template_name", None),
        is_template=new_section_config.get("is_template", False),
        source_template_id=new_section_config.get("source_template_id", None),
        audit_info=new_section_config.get("audit_info", {}),
        index=new_section_config.get("index"),
    )
    db.session.add(section)
    db.session.commit()
    return section


def update_section(section_id, new_section_config):
    section = db.session.query(Section).where(Section.section_id == section_id).one_or_none()
    if section:
        # Define a list of allowed keys to update
        allowed_keys = ["round_id", "name_in_apply_json", "template_name", "is_template", "audit_info", "index"]

        for key, value in new_section_config.items():
            # Update the section if the key is allowed
            if key in allowed_keys:
                setattr(section, key, value)

        db.session.commit()
    return section


def delete_section_from_round(round_id, section_id, cascade: bool = False):
    """Removes a section from the application config for a round. Uses `reorder()` on the
    round to update numbering so if there are 3 sections in a round numbered as follows:
    - 1 Round A
    - 2 Round B
    - 3 Round C

    And then round B is deleted, you get
    - 1 Round A
    - 2 Round C

    Args:
        round_id (UUID): ID of the round to remove the section from
        section_id (UUID): ID of the section to remove
        cascade (bool, optional): Whether to cascade delete forms within this section. Defaults to False.
    """
    delete_section(section_id=section_id, cascade=cascade)
    round = get_round_by_id(id=round_id)
    round.sections.reorder()
    db.session.commit()


def delete_section(section_id, cascade: bool = False):
    """Removes a section from the database. If cascade=True, will also cascade the delete
    to all forms within this section, and on down the hierarchy. This DOES NOT update
    numbering of any other sections in the round. If you want this, use
    `.delete_section_from_round()` instead.

    Args:
        section_id (_type_): section ID to delete
        cascade (bool, optional): Whether to cascade the delete down the hierarchy. Defaults to False.

    """
    section = db.session.query(Section).where(Section.section_id == section_id).one_or_none()
    if cascade:
        _delete_all_components_in_pages(page_ids=[page.page_id for form in section.forms for page in form.pages])
        _delete_all_pages_in_forms(form_ids=[f.form_id for f in section.forms])
        _delete_all_forms_in_sections(section_ids=[section_id])
    db.session.delete(section)
    db.session.commit()
    return section


# CRUD FORM
def insert_new_form(new_form_config):
    """
    Inserts a form object based on the provided configuration.

    Parameters:
        new_form_config (dict): A dictionary containing the configuration for the new form.
            new_form_config keys:
                - section_id (str): The ID of the section to which the form belongs.
                - name_in_apply_json (dict): The name of the form as it will be in the Application
                JSON (support multiple languages/keys).
                - is_template (bool): A flag indicating whether the form is a template.
                - template_name (str): The name of the template.
                - source_template_id (str): The ID of the source template.
                - audit_info (dict): Audit information for the form.
                - section_index (int): The index of the form within the section.
                - runner_publish_name (bool): The path of the form in the form runner (kebab case).
    Returns:
        Form: The newly created form object.
    """

    form = Form(
        form_id=uuid4(),
        section_id=new_form_config.get("section_id", None),
        name_in_apply_json=new_form_config.get("name_in_apply_json"),
        is_template=new_form_config.get("is_template", False),
        template_name=new_form_config.get("template_name", None),
        source_template_id=new_form_config.get("source_template_id", None),
        audit_info=new_form_config.get("audit_info", {}),
        section_index=new_form_config.get("section_index"),
        runner_publish_name=new_form_config.get("runner_publish_name", None),
    )
    db.session.add(form)
    db.session.commit()
    return form


def update_form(form_id, new_form_config):
    form = db.session.query(Form).where(Form.form_id == form_id).one_or_none()
    if form:
        # Define a list of allowed keys to update
        allowed_keys = [
            "section_id",
            "name_in_apply_json",
            "template_name",
            "is_template",
            "audit_info",
            "section_index",
            "runner_publish_name",
        ]

        # Iterate over the new_form_config dictionary
        for key, value in new_form_config.items():
            # Update the form if the key is allowed
            if key in allowed_keys:
                setattr(form, key, value)

        db.session.commit()
    return form


def _delete_all_forms_in_sections(section_ids: list):
    stmt = delete(Form).filter(Form.section_id.in_(section_ids))
    db.session.execute(stmt)
    db.session.commit()


def delete_form_from_section(section_id, form_id, cascade: bool = False):
    """Deletes a form from a section and renumbers all remaining forms accordingly. If cascade==True,
    cascades the delete to pages and then components within this form

    So for example if you have 3 sections:
    - 1 Section A
    - 2 Section B
    - 3 Section C
    Then delete section B, they are renumbered as:
    - 1 Section A
    - 2 Section C

    Args:
        section_id (_type_): Section ID to remove the form from
        form_id (_type_): Form ID of the form to remove
        cascade (bool, optional): Whether to cascade the delete down the hierarchy. Defaults to False.
    """
    delete_form(form_id=form_id, cascade=cascade)
    section = get_section_by_id(section_id=section_id)
    section.forms.reorder()
    db.session.commit()


def delete_form(form_id, cascade: bool = False):
    """Deletes a form. If cascade==True, cascades this delete down through the hierarchy to
    pages within this form and then components on those pages. It DOES NOT update the section_index
    property of remaining forms. If you want this functionality, call #delete_form_from_section() instead.

    Args:
        form_id (UUID): ID of the form to delete
        cascade (bool, optional): Whether to cascade the delete down the hierarchy. Defaults to False.

    """
    form = db.session.query(Form).where(Form.form_id == form_id).one_or_none()
    if cascade:
        _delete_all_components_in_pages(page_ids=[p.page_id for p in form.pages])
        _delete_all_pages_in_forms(form_ids=[form_id])
    db.session.delete(form)
    db.session.commit()
    return form


# CRUD PAGE
def insert_new_page(new_page_config):
    """
    Inserts a page object based on the provided configuration.

    Parameters:
        new_page_config (dict): A dictionary containing the configuration for the new page.
            new_page_config keys:
                - form_id (str): The ID of the form to which the page belongs.
                - name_in_apply_json (str): The name of the page as it will be in the Application JSON.
                - template_name (str): The name of the template.
                - is_template (bool): A flag indicating whether the page is a template.
                - source_template_id (str): The ID of the source template.
                - audit_info (dict): Audit information for the page.
                - form_index (int): The index of the page within the form.
                - display_path (str): The form runner display path of the page (kebab case).
                - controller (str): The form runner controller path for the page (e.g. './pages/summary.js').
                Returns:
            Page: The newly created page object.
    """
    page = Page(
        page_id=uuid4(),
        form_id=new_page_config.get("form_id", None),
        name_in_apply_json=new_page_config.get("name_in_apply_json"),
        template_name=new_page_config.get("template_name", None),
        is_template=new_page_config.get("is_template", False),
        source_template_id=new_page_config.get("source_template_id", None),
        audit_info=new_page_config.get("audit_info", {}),
        form_index=new_page_config.get("form_index"),
        display_path=new_page_config.get("display_path"),
        controller=new_page_config.get("controller", None),
    )
    db.session.add(page)
    db.session.commit()
    return page


def update_page(page_id, new_page_config):
    page = db.session.query(Page).where(Page.page_id == page_id).one_or_none()
    if page:
        # Define a list of allowed keys to update
        allowed_keys = [
            "form_id",
            "name_in_apply_json",
            "template_name",
            "is_template",
            "audit_info",
            "form_index",
            "display_path",
            "controller",
        ]

        for key, value in new_page_config.items():
            # Update the page if the key is allowed
            if key in allowed_keys:
                setattr(page, key, value)

        db.session.commit()
    return page


def _delete_all_pages_in_forms(form_ids: list):
    stmt = delete(Page).filter(Page.form_id.in_(form_ids))
    db.session.execute(stmt)
    db.session.commit()


def delete_page(page_id, cascade: bool = False):
    page = db.session.query(Page).where(Page.page_id == page_id).one_or_none()
    if cascade:
        _delete_all_components_in_pages(page_ids=[page_id])
    db.session.delete(page)
    db.session.commit()
    return page


# CRUD COMPONENT
def insert_new_component(new_component_config: dict):
    """
    Inserts a component object based on the provided configuration.

    Parameters:
        new_component_config (dict): A dictionary containing the configuration for the new component.
            new_component_config keys:
                - page_id (str): The ID of the page to which the component belongs.
                - theme_id (str): The ID of the theme to which the component belongs.
                - title (str): The title of the component.
                - hint_text (str): The hint text for the component.
                - options (dict): The options such as classes, prefix etc
                - type (str): The type of the component.
                - template_name (str): The name of the template.
                - is_template (bool): A flag indicating whether the component is a template.
                - source_template_id (str): The ID of the source template.
                - audit_info (dict): Audit information for the component.
                - page_index (int): The index of the component within the page.
                - theme_index (int): The index of the component within the theme.
                - conditions (dict): The conditions such as potential routes based on the
                components value (can specify page path).
                - runner_component_name (str): The name of the runner component.
                - list_id (str): The ID of the list to which the component belongs.
            Returns:
                Component: The newly created component object.
    """
    # Instantiate the Component object with the provided and default values
    component = Component(
        component_id=uuid4(),
        page_id=new_component_config.get("page_id", None),
        theme_id=new_component_config.get("theme_id", None),
        title=new_component_config.get("title"),
        hint_text=new_component_config.get("hint_text"),
        options=new_component_config.get("options", {}),
        type=new_component_config.get("type"),
        is_template=new_component_config.get("is_template", False),
        template_name=new_component_config.get("template_name", None),
        source_template_id=new_component_config.get("source_template_id", None),
        audit_info=new_component_config.get("audit_info", {}),
        page_index=new_component_config.get("page_index"),
        theme_index=new_component_config.get("theme_index"),
        conditions=new_component_config.get("conditions", []),
        runner_component_name=new_component_config.get("runner_component_name"),
        list_id=new_component_config.get("list_id", None),
    )

    # Add the component to the session and commit
    db.session.add(component)
    db.session.commit()

    # Return the created component object or its ID based on your requirements
    return component


def update_component(component_id, new_component_config):
    component = db.session.query(Component).where(Component.component_id == component_id).one_or_none()
    if component:
        # Define a list of allowed keys to update to prevent updating unintended fields
        allowed_keys = [
            "page_id",
            "theme_id",
            "title",
            "hint_text",
            "options",
            "type",
            "template_name",
            "is_template",
            "audit_info",
            "page_index",
            "theme_index",
            "conditions",
            "runner_component_name",
            "list_id",
        ]

        for key, value in new_component_config.items():
            # Update the component if the key is allowed
            if key in allowed_keys:
                setattr(component, key, value)

        db.session.commit()
    return component


def delete_component(component_id):
    component = db.session.query(Component).where(Component.component_id == component_id).one_or_none()
    db.session.delete(component)
    db.session.commit()
    return component


def _delete_all_components_in_pages(page_ids):
    stmt = delete(Component).filter(Component.page_id.in_(page_ids))
    db.session.execute(stmt)
    db.session.commit()


# Section and form reordering


def swap_elements_in_list(containing_list: list, index_a: int, index_b: int) -> list:
    """Swaps the elements at the specified indices in the supplied list.
    If either index is outside the valid range, returns the list unchanged.

    Args:
        containing_list (list): List containing the elements to swap
        index_a (int): List index (0-based) of the first element to swap
        index_b (int): List index (0-based) of the second element to swap

    Returns:
        list: The updated list
    """
    if 0 <= index_a < len(containing_list) and 0 <= index_b < len(containing_list):
        containing_list[index_a], containing_list[index_b] = containing_list[index_b], containing_list[index_a]
    return containing_list


def move_section_down(round_id, section_index_to_move_down: int):
    """Moves a section one place down in the ordered list of sections in a round.
    In this case down means visually down, so the index number will increase by 1.

    Element | Section.index | Index in list
        A   |   1           |   0
        B   |   2           |   1
        C   |   3           |   2

    Then move B down, which results in C moving up

    Element | Section.index | Index in list
        A   |   1           |   0
        C   |   2           |   1
        B   |   3           |   2

    Args:
        round_id (UUID): Round ID to move this section within
        section_index_to_move_down (int): Current Section.index value of the section to move
    """
    round: Round = get_round_by_id(round_id)
    list_index_to_move_down = section_index_to_move_down - 1  # Need the 0-based index inside the list
    round.sections = swap_elements_in_list(round.sections, list_index_to_move_down, list_index_to_move_down + 1)
    db.session.commit()


def move_section_up(round_id, section_index_to_move_up: int):
    """Moves a section one place up in the ordered list of sections in a round.
    In this case up means visually up, so the index number will decrease by 1.


    Element | Section.index | Index in list
        A   |   1           |   0
        B   |   2           |   1
        C   |   3           |   2

    Then move B up, which results in A moving down

    Element | Section.index | Index in list
        B   |   1           |   0
        A   |   2           |   1
        C   |   3           |   2

    Args:
        round_id (UUID): Round ID to move this section within
        section_index_to_move_up (int): Current Section.index value of the section to move
    """

    round: Round = get_round_by_id(round_id)
    list_index_to_move_up = section_index_to_move_up - 1  # Need the 0-based index inside the list
    round.sections = swap_elements_in_list(round.sections, list_index_to_move_up, list_index_to_move_up - 1)

    db.session.commit()


def move_form_down(section_id, form_index_to_move_down: int):
    """Moves a form one place down in the ordered list of forms in a section.
    In this case down means visually down, so the index number will increase by 1.

    Element | Form.section_index    | Index in list
        A   |   1                   |   0
        B   |   2                   |   1
        C   |   3                   |   2

    Then move B down, which results in C moving up

    Element | Form.section_index    | Index in list
        A   |   1                   |   0
        C   |   2                   |   1
        B   |   3                   |   2

    Args:
        section_id (UUID): Section ID to move this form within
        form_index_to_move_down (int): Current Form.section_index value of the form to move
    """
    section: Section = get_section_by_id(section_id)
    list_index_to_move_down = form_index_to_move_down - 1  # Need the 0-based index inside the list

    section.forms = swap_elements_in_list(section.forms, list_index_to_move_down, list_index_to_move_down + 1)
    db.session.commit()


def move_form_up(section_id, form_index_to_move_up: int):
    """Moves a form one place up in the ordered list of forms in a section.
    In this case up means visually up, so the index number will decrease by 1.


    Element | Form.section_index    | Index in list
        A   |   1                   |   0
        B   |   2                   |   1
        C   |   3                   |   2

    Then move B up, which results in A moving down

    Element | Form.section_index    | Index in list
        B   |   1                   |   0
        A   |   2                   |   1
        C   |   3                   |   2

    Args:
        section_id (UUID): Section ID to move this form within
        form_index_to_move_up (int): Current Form.section_index value of the form to up
    """

    section: Section = get_section_by_id(section_id)
    list_index_to_move_up = form_index_to_move_up - 1  # Need the 0-based index inside the list

    section.forms = swap_elements_in_list(section.forms, list_index_to_move_up, list_index_to_move_up - 1)
    db.session.commit()


def insert_list(list_config: dict, do_commit: bool = True) -> Lizt:
    new_list = Lizt(
        is_template=True,
        name=list_config.get("name"),
        title=list_config.get("title"),
        type=list_config.get("type"),
        items=list_config.get("items"),
    )
    try:
        db.session.add(new_list)
    except Exception as e:
        print(e)
        raise e
    if do_commit:
        db.session.commit()
    db.session.flush()  # flush to get the list id
    return new_list
