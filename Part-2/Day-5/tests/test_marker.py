import pytest


@pytest.fixture
def fixt(request):
    data = request.node.get_closest_marker("my_marker")
    if data is None:
        pytest.skip("No marker found")
    return data.args[0]


@pytest.mark.my_marker("Hello, World!")
def test_marker(fixt):
    assert fixt == "Hello, World!"
