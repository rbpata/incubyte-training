import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../Day-3"))
from library_system import (
    Loan,
    LibraryItem,
    Book,
    Magazine,
    Member,
    StudentMember,
    FacultyMember,
)


@pytest.fixture
def book():
    return Book("To Kill a Mockingbird", "Harper Lee", 1)


@pytest.fixture
def member():
    return StudentMember("Alice", 2)


@pytest.fixture
def loan(book, member):
    return Loan(member, book)


class TestLoan:
    def test_loan_creation(self, loan, book, member):
        assert loan.item == book
        assert loan.member == member
        assert loan.is_active is True

    def test_process(self, loan, book, member):
        assert loan.process() == "Alice has borrowed To Kill a Mockingbird."
        assert book.is_available is False
        assert loan.member.borrowed_items == [book]
