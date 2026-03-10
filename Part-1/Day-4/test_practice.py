import pytest
from practice import Circle, Shape


@pytest.fixture
def shape():
    return Shape("Generic Shape")


@pytest.fixture
def circle():
    return Circle(radius=4)


class Test:

    @pytest.mark.custom_marker
    def test_circle_area(self, circle):
        assert circle.area() == 50.24
        assert circle.area() == 50.24

    @pytest.mark.parametrize(
        "radius, expected_area",
        [
            (1, 3.14),
            (2, 12.56),
            (3, 28.26),
        ],
    )
    def test_circle_area_parametrized(self, radius, expected_area):
        circle = Circle(radius=radius)
        assert circle.area() == expected_area
