from uuid import uuid4

import pytest

from app.db.models import Component
from app.db.models import ComponentType
from app.db.models import Form
from app.db.models import Fund
from app.db.models import Lizt
from app.db.queries.application import get_component_by_id
from app.db.queries.fund import get_all_funds
from app.question_reuse.generate_assessment_config import build_assessment_config
from app.question_reuse.generate_form import build_form_json


def test_build_form_json(seed_dynamic_data):

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
def test_build_assessment_config(seed_dynamic_data):
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


list_id = uuid4()


@pytest.mark.seed_config(
    {
        "lists": [
            Lizt(
                list_id=list_id,
                name="classifications_list",
                type="string",
                items=[{"text": "Charity", "value": "charity"}, {"text": "Public Limited Company", "value": "plc"}],
            )
        ],
        "components": [
            Component(
                component_id=uuid4(),
                page_id=None,
                title="How is your organisation classified?",
                type=ComponentType.RADIOS_FIELD,
                page_index=1,
                theme_id=None,
                theme_index=6,
                options={"hideTitle": False, "classes": ""},
                runner_component_name="organisation_classification",
                list_id=list_id,
            )
        ],
    }
)
def test_list_relationship(seed_dynamic_data):

    result = get_component_by_id(seed_dynamic_data["components"][0].component_id)
    assert result
    assert result.list_id == list_id
    assert result.lizt
    assert result.lizt.name == "classifications_list"
