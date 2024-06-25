from app.data.data_access import (
    get_all_pages,
    get_list_by_id,
    get_component_by_name,
    get_pages_to_display_in_builder,
    get_page_by_id,
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


TEST_COMPONENTS = {"name1": {"a": "b"}, "name2": {}}


@pytest.mark.parametrize(
    "all_components, name, exp_result",
    [
        ({}, "anything", None),
        (TEST_COMPONENTS, "name1", {"a": "b"}),
        (TEST_COMPONENTS, "not_in_list", None),
    ],
)
def test_get_components_by_name(mocker, all_components, name, exp_result):
    mocker.patch("app.data.data_access.COMPONENTS", all_components)
    results = get_component_by_name(name)
    assert results == exp_result


mock_pages = [
    {"id": "1", "show_in_builder": True},
    {"id": "2", "show_in_builder": True},
    {"id": "3", "show_in_builder": False},
]


@pytest.mark.parametrize("all_pages,id,exp_result", [(mock_pages, "2", {"id": "2", "show_in_builder": True})])
def test_get_page_by_id(mocker, all_pages, id, exp_result):
    mocker.patch("app.data.data_access.PAGES", all_pages)
    result = get_page_by_id(id)
    assert result == exp_result


mock_lists = {"list1": {"items": []}, "list2": {"items": []}}


@pytest.mark.parametrize(
    "all_lists, list_id, exp_result", [(mock_lists, "list1", mock_lists["list1"]), (mock_lists, "badid", None)]
)
def test_get_list_by_id(mocker, all_lists, list_id, exp_result):
    mocker.patch("app.data.data_access.LISTS", all_lists)
    result = get_list_by_id(list_id)
    assert result == exp_result