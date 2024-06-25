from app.blueprints.self_serve.routes import human_to_kebab_case

import pytest

@pytest.mark.parametrize("input, exp_output", [
    ("", None),
    ("hello world", "hello-world"),
    ("Hi There Everyone", "hi-there-everyone")

])
def test_human_to_kebab(input, exp_output):
    result = human_to_kebab_case(input)
    assert result == exp_output