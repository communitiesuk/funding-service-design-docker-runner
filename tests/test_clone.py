from uuid import uuid4

import pytest

from app.db.models import Component
from app.db.models import ComponentType
from app.db.models import Page
from app.db.queries.application import _initiate_cloned_component
from app.db.queries.application import _initiate_cloned_page
from app.db.queries.application import clone_multiple_components
from app.db.queries.application import clone_single_component
from app.db.queries.application import clone_single_page


@pytest.fixture
def mock_new_uuid(mocker):
    new_id = uuid4()
    mocker.patch("app.db.queries.application.uuid4", return_value=new_id)
    yield new_id


# =====================================================================================================================
# These functions mock the _initiate_cloned_XXX functions and don't use the db
# =====================================================================================================================


def test_initiate_cloned_page(mock_new_uuid):
    clone: Page = Page(
        page_id="old-id",
        name_in_apply_json={"en": "test page 1"},
        form_id="old-form-id",
        is_template=True,
        template_name="Template Page",
        display_path="template-page",
    )
    result: Page = _initiate_cloned_page(to_clone=clone, new_form_id="new-form")
    assert result
    assert result.page_id == mock_new_uuid

    # Check other bits are the same
    assert result.name_in_apply_json == clone.name_in_apply_json
    assert result.display_path == clone.display_path

    # check template settings
    assert result.is_template is False
    assert result.source_template_id == "old-id"
    assert result.template_name is None

    assert result.form_id == "new-form"


def test_initiate_cloned_component(mock_new_uuid):
    clone: Component = Component(
        component_id="old-id",
        page_id="pre-clone",
        title="Template qustion 1?",
        type=ComponentType.TEXT_FIELD,
        template_name="Template Component",
        is_template=True,
        page_index=1,
        theme_id="pre-clone",
        theme_index=2,
        options={"hideTitle": False, "classes": "test-class"},
        runner_component_name="template_question_name",
        conditions={"a": "b"},
    )
    result = _initiate_cloned_component(clone, "page-123", "theme-234")

    assert result

    # Check new ID
    assert result.component_id == mock_new_uuid

    # Check other bits are the same
    assert result.title == clone.title
    assert result.type == clone.type
    assert result.options == clone.options
    assert result.conditions == clone.conditions

    # check template settings
    assert result.is_template is False
    assert result.source_template_id == "old-id"
    assert result.template_name is None

    assert result.page_id == "page-123"
    assert result.theme_id == "theme-234"


# =====================================================================================================================
# These functions mock the clone_XXX functions and DO use the db
# =====================================================================================================================


def test_clone_single_component(flask_test_client, _db):
    template_component: Component = Component(
        component_id=uuid4(),
        page_id=None,
        title="Template qustion 1?",
        type=ComponentType.YES_NO_FIELD,
        page_index=1,
        theme_id=None,
        theme_index=2,
        options={"hideTitle": False, "classes": "test-class"},
        runner_component_name="template_question_name",
    )

    old_id = template_component.component_id

    _db.session.bulk_save_objects([template_component])
    _db.session.commit()

    assert _db.session.get(Component, old_id)

    result = clone_single_component(template_component.component_id)
    assert result
    new_id = result.component_id

    # check can retrieve new component
    assert _db.session.get(Component, new_id)

    # Check new ID
    assert result.component_id != template_component.component_id

    # Check other bits are the same
    assert result.title == template_component.title
    assert result.type == template_component.type
    assert result.options == template_component.options
    assert result.conditions is None

    # check template settings
    assert result.is_template is False
    assert result.source_template_id == template_component.component_id

    # check can retrieve old component
    assert _db.session.get(Component, old_id)


page_id = uuid4()


@pytest.mark.seed_config(
    {
        "components": [
            Component(
                component_id=uuid4(),
                page_id=None,
                title="Template qustion 1?",
                type=ComponentType.YES_NO_FIELD,
                page_index=1,
                theme_id=None,
                theme_index=2,
                options={"hideTitle": False, "classes": "test-class"},
                runner_component_name="template_question_name_1",
                is_template=True,
            ),
            Component(
                component_id=uuid4(),
                page_id=None,
                title="Template qustion 2?",
                type=ComponentType.YES_NO_FIELD,
                page_index=1,
                theme_id=None,
                theme_index=2,
                options={"hideTitle": False, "classes": "test-class"},
                runner_component_name="template_question_name_2",
                is_template=True,
            ),
            Component(
                component_id=uuid4(),
                page_id=None,
                title="Template qustion 3?",
                type=ComponentType.YES_NO_FIELD,
                page_index=1,
                theme_id=None,
                theme_index=2,
                options={"hideTitle": False, "classes": "test-class"},
                runner_component_name="template_question_name_3",
                is_template=True,
            ),
        ],
    }
)
def test_clone_multiple_components(seed_dynamic_data, _db):
    existing_components = seed_dynamic_data["components"]

    results = clone_multiple_components(
        component_ids=[c.component_id for c in existing_components],
        new_page_id=None,
        new_theme_id=None,
    )
    assert results
    assert len(results) == 3

    # Check new component exists in db
    from_db = _db.session.query(Component).filter(Component.component_id.in_([c.component_id for c in results])).all()
    assert from_db
    assert len(from_db) == 3

    # Check the old ones exist
    from_db = (
        _db.session.query(Component)
        .filter(Component.component_id.in_([c.component_id for c in existing_components]))
        .all()
    )
    assert from_db
    assert len(from_db) == 3


@pytest.mark.seed_config(
    {
        "pages": [
            Page(
                page_id=uuid4(),
                form_id=None,
                display_path="testing-clones-no-components",
                is_template=True,
                name_in_apply_json={"en": "Clone testing"},
                form_index=0,
            )
        ]
    }
)
def test_clone_page_no_components(seed_dynamic_data, _db):

    old_id = seed_dynamic_data["pages"][0].page_id

    # check initial page exists
    initial_page_from_db = _db.session.query(Page).where(Page.page_id == old_id).one_or_none()
    assert initial_page_from_db

    result = clone_single_page(page_id=old_id, new_form_id=None)
    assert result
    new_id = result.page_id

    # check new page exists
    new_page_from_db = _db.session.query(Page).where(Page.page_id == new_id).one_or_none()
    assert new_page_from_db

    # check old page still exists
    old_page_from_db = _db.session.query(Page).where(Page.page_id == old_id).one_or_none()
    assert old_page_from_db


page_id = uuid4()


@pytest.mark.seed_config(
    {
        "pages": [
            Page(
                page_id=page_id,
                form_id=None,
                display_path="testing-clones-with-components",
                is_template=True,
                name_in_apply_json={"en": "Clone testing"},
                form_index=0,
            )
        ],
        "components": [
            Component(
                component_id=uuid4(),
                page_id=page_id,
                title="Template qustion 1?",
                type=ComponentType.YES_NO_FIELD,
                page_index=1,
                theme_id=None,
                theme_index=2,
                options={"hideTitle": False, "classes": "test-class"},
                runner_component_name="template_question_name_1",
                is_template=True,
            ),
            Component(
                component_id=uuid4(),
                page_id=page_id,
                title="Template qustion 2?",
                type=ComponentType.YES_NO_FIELD,
                page_index=1,
                theme_id=None,
                theme_index=2,
                options={"hideTitle": False, "classes": "test-class"},
                runner_component_name="template_question_name_2",
                is_template=True,
            ),
            Component(
                component_id=uuid4(),
                page_id=page_id,
                title="Template qustion 3?",
                type=ComponentType.YES_NO_FIELD,
                page_index=1,
                theme_id=None,
                theme_index=2,
                options={"hideTitle": False, "classes": "test-class"},
                runner_component_name="template_question_name_3",
                is_template=True,
            ),
        ],
    }
)
def test_clone_page_with_components(seed_dynamic_data, _db):

    old_page_id = seed_dynamic_data["pages"][0].page_id
    old_component_ids = [str(c.component_id) for c in seed_dynamic_data["components"]]

    # check initial page exists
    initial_page_from_db = _db.session.query(Page).where(Page.page_id == old_page_id).one_or_none()
    assert initial_page_from_db

    result = clone_single_page(page_id=old_page_id, new_form_id=None)
    assert result
    new_id = result.page_id

    # check new page exists
    new_page_from_db = _db.session.query(Page).where(Page.page_id == new_id).one_or_none()
    assert new_page_from_db
    # check components have also been cloned
    assert len(new_page_from_db.components) == 3
    for component in new_page_from_db.components:
        assert str(component.component_id) not in old_component_ids

    # check old page still exists
    old_page_from_db = _db.session.query(Page).where(Page.page_id == old_page_id).one_or_none()
    assert old_page_from_db
    # check old page still has references to original components
    assert len(old_page_from_db.components) == 3
    for component in old_page_from_db.components:
        assert str(component.component_id) in old_component_ids
