import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from src.greeting_service import GreetingService


scenarios("../features/greeting.feature")


@given(parsers.parse('a user named "{name}"'), target_fixture="user")
def user(name):
    return {"name": name}


@when("the greeting service greets the user", target_fixture="greeting_result")
def greet_user(user):
    service = GreetingService()
    return service.greet(user["name"])


@then(parsers.parse('the result should be "{expected}"'))
def result(greeting_result, expected):
    assert greeting_result == expected
