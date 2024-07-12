from uuid import uuid4

import pytest
from flask_migrate import upgrade
from sqlalchemy import text

from app.app import create_app
from app.db.models import Component
from app.db.models import ComponentType
from app.db.models import Form
from app.db.models import Fund
from app.db.models import Lizt
from app.db.queries.application import get_component_by_id
from app.db.queries.fund import get_all_funds
from app.question_reuse.generate_assessment_config import build_assessment_config
from app.question_reuse.generate_form import build_form_json
from tasks.test_data import insert_test_data

url_base = "postgresql://postgres:password@fsd-self-serve-db:5432/fund_builder"  # pragma: allowlist secret


@pytest.fixture(scope="session")
def app():
    app = create_app(config={"SQLALCHEMY_DATABASE_URI": f"{url_base}_unit_test"})
    yield app


@pytest.fixture(scope="function")
def flask_test_client():
    with create_app(
        config={"SQLALCHEMY_DATABASE_URI": f"{url_base}_unit_test"}  # pragma: allowlist secret
    ).app_context() as app_context:
        upgrade()
        with app_context.app.test_client() as test_client:
            yield test_client


@pytest.fixture(scope="session")
def _db(app, request):
    """
    Fixture to supply tests with direct access to the database
    """

    yield app.extensions["sqlalchemy"]


@pytest.fixture(scope="function")
def sort_out_test_data(_db, flask_test_client):
    _db.session.execute(
        text("TRUNCATE TABLE fund, round, section,form, page, component, theme, subcriteria, criteria, lizt CASCADE;")
    )
    _db.session.commit()
    insert_test_data(_db)


def test_build_form_json(sort_out_test_data):

    f: Fund = get_all_funds()[0]
    form: Form = f.rounds[0].sections[0].forms[0]

    result = build_form_json(form=form)
    assert result
    assert len(result["pages"]) == 6
    exp_start_path = "/intro-about-your-organisation"
    exp_second_path = "/organisation-name"
    assert result["startPage"] == exp_start_path
    intro_page = next((p for p in result["pages"] if p["path"] == exp_start_path), None)
    assert intro_page
    assert intro_page["next"][0]["path"] == exp_second_path

    org_name_page = next((p for p in result["pages"] if p["path"] == exp_second_path), None)
    assert org_name_page
    assert len(org_name_page["next"]) == 2

    alt_names_page = next((p for p in result["pages"] if p["path"] == "/organisation-alternative-names"), None)
    assert alt_names_page
    assert alt_names_page["next"][0]["path"] == "/organisation-address"

    address_page = next((p for p in result["pages"] if p["path"] == "/organisation-address"), None)
    assert address_page
    assert address_page["next"][0]["path"] == "/organisation-classification"

    assert (
        next((p for p in result["pages"] if p["path"] == "/organisation-classification"), None)["next"][0]["path"]
        == "/summary"
    )

    summary = next((p for p in result["pages"] if p["path"] == "/summary"), None)
    assert summary


# TODO this fails with components from a template (branching logic)
def test_build_assessment_config(sort_out_test_data):
    f: Fund = get_all_funds()[0]
    criteria = f.rounds[0].criteria[0]
    result = build_assessment_config(criteria_list=[criteria])
    assert result
    first_unscored = result["unscored_sections"][0]
    assert first_unscored
    assert first_unscored["name"] == "Unscored"
    assert len(first_unscored["subcriteria"]) == 1
    assert len(first_unscored["subcriteria"][0]["themes"]) == 2
    assert len(first_unscored["subcriteria"][0]["themes"][0]["answers"]) == 4
    assert len(first_unscored["subcriteria"][0]["themes"][1]["answers"]) == 3


def test_list_relationship(_db, flask_test_client):

    lizt: Lizt = Lizt(
        list_id=uuid4(),
        name="classifications_list",
        type="string",
        items=[{"text": "Charity", "value": "charity"}, {"text": "Public Limited Company", "value": "plc"}],
    )
    component: Component = Component(
        component_id=uuid4(),
        page_id=None,
        title="How is your organisation classified?",
        type=ComponentType.RADIOS_FIELD,
        page_index=1,
        theme_id=None,
        theme_index=6,
        options={"hideTitle": False, "classes": ""},
        runner_component_name="organisation_classification",
        list_id=lizt.list_id,
    )
    _db.session.bulk_save_objects([lizt, component])
    _db.session.commit()

    result = get_component_by_id(component.component_id)
    assert result
    assert result.list_id == lizt.list_id
    assert result.lizt
    assert result.lizt.name == "classifications_list"
