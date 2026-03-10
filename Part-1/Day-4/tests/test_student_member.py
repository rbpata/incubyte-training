import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../Day-3"))
from library_system import LibraryItem, Book, Magazine, Member, StudentMember


class TestStudentMember:

    def test_student_member_max_borrow_limit(self):
        student_member = StudentMember("Alice", 2)
        assert student_member.max_books() == 3
