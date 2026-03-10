import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../Day-3"))

from library_system import LibraryItem, Book, Magazine, Member, StudentMember


@pytest.fixture
def magazine():
    return Magazine("National Geographic", "National Geographic Society", 1)


class TestMagazine:

    def test_magazine_creation(self, magazine):
        magazine = magazine
        assert magazine.title == "National Geographic"
        assert magazine.author == "National Geographic Society"
        assert magazine._item_id == 1
        assert magazine.is_available is True

    def test_magazine_str(self, magazine):
        magazine = magazine
        assert (
            str(magazine)
            == "Magazine: National Geographic by National Geographic Society"
        )
