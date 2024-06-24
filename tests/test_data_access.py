from app.data.data_access import (
    get_all_pages,
    get_component_by_name,
    get_pages_to_display_in_builder,
)
import pytest


@pytest.mark.parametrize(
    "all_pages,exp_length",
    [
        (
            [
                {"id": "1", "show_in_builder": True},
                {"id": "1", "show_in_builder": True},
                {"id": "1", "show_in_builder": False},
            ],
            3,
        ),
        (
            [
                {"id": "1", "show_in_builder": True},
                {"id": "1", "show_in_builder": True},
            ],
            2,
        ),
        (
            [
                {"id": "1", "show_in_builder": False},
                {"id": "1", "show_in_builder": False},
            ],
            2,
        ),
        ([], 0),
    ],
)
def test_get_all_pages(mocker, all_pages, exp_length):
    mocker.patch(
        "app.data.data_access.PAGES",
        all_pages,
    )
    results = get_all_pages()
    assert len(results) == exp_length


@pytest.mark.parametrize(
    "all_pages,exp_length",
    [
        (
            [
                {"id": "1", "show_in_builder": True},
                {"id": "1", "show_in_builder": True},
                {"id": "1", "show_in_builder": False},
            ],
            2,
        ),
        (
            [
                {"id": "1", "show_in_builder": True},
                {"id": "1", "show_in_builder": True},
            ],
            2,
        ),
        (
            [
                {"id": "1", "show_in_builder": False},
                {"id": "1", "show_in_builder": False},
            ],
            0,
        ),
        ([], 0),
    ],
)
def test_get_all_pages_for_builder(mocker, all_pages, exp_length):
    mocker.patch(
        "app.data.data_access.PAGES",
        all_pages,
    )
    results = get_pages_to_display_in_builder()
    assert len(results) == exp_length


TEST_COMPONENTS = {"name1": {}, "name2": {}}


@pytest.mark.parametrize(
    "all_components, name, exp_result",
    [
        ({}, "anything", None),
        (TEST_COMPONENTS, "name1", {}),
        (TEST_COMPONENTS, "not_in_list", None),
    ],
)
def test_get_components_by_name(mocker, all_components, name, exp_result):
    results = get_component_by_name(name)
