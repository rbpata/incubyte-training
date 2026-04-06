import pytest
from hypothesis import given, strategies as st


@st.composite
def custom_strategy(draw):
    # Generate a random integer between 0 and 100
    random_int = draw(st.integers(min_value=0, max_value=100))
    return random_int


@given(integers=custom_strategy())
def test_hypothesis(integers) -> None:
    assert integers >= 0
