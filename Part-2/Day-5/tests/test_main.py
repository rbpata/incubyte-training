# contents of test_append.py
import pytest


# Arrange
@pytest.fixture
def first_entry():
    return "a"


# Arrange
@pytest.fixture
def order():
    return []


# Act
# @pytest.fixture
# def append_first(order, first_entry):
#     return order.append(first_entry)


@pytest.fixture(autouse=True)
def append_first(order, first_entry):
    order.append(first_entry)


def test_string_only(
    order, first_entry
):  # automaticallt receives the order and first_entry fixtures
    # Assert
    assert order == [first_entry]


# function: the default scope, the fixture is destroyed at the end of the test.

# class: the fixture is destroyed during teardown of the last test in the class.

# module: the fixture is destroyed during teardown of the last test in the module.

# package: the fixture is destroyed during teardown of the last test in the package where the fixture is defined, including sub-packages and sub-directories within it.

# session: the fixture is destroyed at the end of the test session.
