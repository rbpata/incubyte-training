import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../Day-3"))
from library_system import FacultyMember


class TestFacultyMember:

    def test_faculty_member_max_borrow_limit(self):
        faculty_member = FacultyMember("Dr. Smith", 5)
        assert faculty_member.max_books() == 5
