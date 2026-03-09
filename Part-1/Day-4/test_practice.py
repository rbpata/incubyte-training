import pytest
from practice import Circle, Shape


@pytest.fixture
def shape():
    return Shape("Generic Shape")


@pytest.fixture
def circle():
    return Circle(radius=4)


class Test:
    def test_circle_area(self, circle):
        assert circle.area() == 50.24
        assert circle.area() == 50.24
