import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../Day-3"))

from library_system import LibraryItem, Book, Magazine, Member, StudentMember


@pytest.fixture
def library_item():
    return LibraryItem("The Great Gatsby", 1)


class TestLibraryItem:

    def test_library_item_creation(self, library_item):
        item = library_item
        assert item.title == "The Great Gatsby"
        assert item._item_id == 1
        assert item.is_available is True

    def test_checkout(self, library_item):
        item = library_item
        assert item.checkout() == "The Great Gatsby has been checked out."
        assert item.is_available is False

    def test_equality(self, library_item):
        item1 = library_item
        item2 = LibraryItem("The Great Gatsby", 1)
        item3 = LibraryItem("1984", 2)
        assert item1 == item2
        assert item1 != item3
        
    def test_library_info(self):
        LibraryItem.total_items = 5
        assert LibraryItem.library_info() == "Welcome to the library! We have 5 items."
    
    def test_get_total_items(self):
        LibraryItem.total_items = 10
        assert LibraryItem.get_total_items() == 10
        
