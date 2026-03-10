class LibraryItem:
    total_items = 0

    def __init__(self, title, item_id):
        self._title = title
        self._item_id = item_id
        self._is_available = True
        LibraryItem.total_items += 1

    @property
    def title(self):
        return self._title

    @property
    def item_id(self):
        return self._item_id

    @property
    def is_available(self):
        return self._is_available

    @item_id.setter
    def item_id(self, new_id):
        self._item_id = new_id

    @is_available.setter
    def is_available(self, availability):
        self._is_available = availability

    def checkout(self):
        if self._is_available:
            self._is_available = False
            return f"{self.title} has been checked out."
        else:
            return f"{self.title} is currently unavailable."

    def __str__(self):
        return f"Title: {self.title}, Item ID: {self._item_id}, Available: {self._is_available}"

    def __repr__(self):
        return f"LibraryItem('{self.title}', '{self._item_id}')"

    def __eq__(self, other):
        if isinstance(other, LibraryItem):
            return self._item_id == other._item_id
        return False

    @staticmethod
    def library_info():
        return f"Welcome to the library! We have {LibraryItem.total_items} items."

    @classmethod
    def get_total_items(cls):
        return cls.total_items


class Book(LibraryItem):

    def __init__(self, title, author, item_id):
        super().__init__(title, item_id)
        self.author = author

    def __str__(self):
        return f"Book: {self.title} by {self.author}"


class Magazine(LibraryItem):

    def __init__(self, title, author, item_id):
        super().__init__(title, item_id)
        self.author = author

    def __str__(self):
        return f"Magazine: {self.title} by {self.author}"


class Member:

    def __init__(self, name, member_id):
        self.name = name
        self.member_id = member_id
        self.borrowed_items = []

    def borrow_item(self, item):

        if item.is_available:
            item.checkout()
            self.borrowed_items.append(item)
            return f"{self.name} has borrowed {item.title}."

        return f"{item.title} is currently unavailable."

    def return_item(self, item):

        if item in self.borrowed_items:
            item.is_available = True
            self.borrowed_items.remove(item)
            return f"{self.name} has returned {item.title}."

        return f"{self.name} did not borrow {item.title}."


class StudentMember(Member):

    def max_books(self):
        return 3


class FacultyMember(Member):

    def max_books(self):
        return 5


class Loan:

    def __init__(self, member, item):
        self.member = member
        self.item = item
        self.is_active = True

    def process(self):
        return self.member.borrow_item(self.item)


class Library:

    def __init__(self):
        self.items = []
        self.members = []

    def add_item(self, item):
        self.items.append(item)

    def register_member(self, member):
        self.members.append(member)

    def lend_item(self, member, item):
        loan = Loan(member, item)
        return loan.process()


class LibraryUtils:

    @staticmethod
    def generate_id(prefix, number):
        return f"{prefix}-{number}"


def process_checkout(item):
    item.checkout()


if __name__ == "__main__":

    library = Library()

    book1 = Book("Python Basics", "Guido", "B1")
    book2 = Book("Machine Learning", "Andrew Ng", "B2")

    mag1 = Magazine("Tech Today", "Tech Team", "M1")

    library.add_item(book1)
    library.add_item(book2)
    library.add_item(mag1)

    student = StudentMember("Ram", "S1")
    faculty = FacultyMember("Dr. Smith", "F1")

    library.register_member(student)
    library.register_member(faculty)

    print(library.lend_item(student, book1))
    print(library.lend_item(faculty, mag1))

    print(book1)
    print(student.borrowed_items)

    members = [student, faculty]

    for m in members:
        print(f"{m.name} can borrow {m.max_books()} books")

    print("Total Items:", LibraryItem.get_total_items())

    print("Generated ID:", LibraryUtils.generate_id("BOOK", 10))

    print("Are books equal?", book1 == book2)

    print(LibraryItem.library_info())
