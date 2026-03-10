import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../Day-3"))

from library_system import LibraryItem, Book, Magazine, Member, StudentMember

@pytest.fixture
def member():
    return Member("Ram", 1)

@pytest.fixture
def book():
    return Book("To Kill a Mockingbird", "Harper Lee", 1)


class TestMember:

    def test_member_creation(self, member):
        assert member.name == "Ram"
        assert member.member_id == 1
        assert member.borrowed_items == []

    def test_borrow_item(self, member, book):
        assert member.borrow_item(book) == "Ram has borrowed To Kill a Mockingbird."
        assert book.is_available is False
        assert member.borrowed_items == [book]

    def test_return_item(self, member, book):
        member.borrow_item(book)
        assert member.return_item(book) == "Ram has returned To Kill a Mockingbird."
        assert book.is_available is True
        assert member.borrowed_items == []
