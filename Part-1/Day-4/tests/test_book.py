import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../Day-3"))

from library_system import LibraryItem, Book, Magazine, Member, StudentMember


@pytest.fixture
def book():
    return Book("To Kill a Mockingbird", "Harper Lee", 1)


class TestBook:

    def test_book_creation(self, book):
        book = book
        assert book.title == "To Kill a Mockingbird"
        assert book.author == "Harper Lee"
        assert book._item_id == 1
        assert book.is_available is True

    def test_book_str(self, book):
        book = book
        assert str(book) == "Book: To Kill a Mockingbird by Harper Lee"
