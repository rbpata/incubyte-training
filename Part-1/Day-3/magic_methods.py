class Book:
    def __init__(self):
        self.title = "The Great Gatsby"
        self.author = "F. Scott Fitzgerald"
    def __str__(self):
        return f"Title: {self.title}, Author: {self.author}"
    def __repr__(self):
        return f"Book(title='{self.title}', author='{self.author}')"
    def __len__(self):
        return len(self.title)
    def __eq__(self, other):
        if isinstance(other, Book):
            return self.title == other.title and self.author == other.author
        return False
    
    @property
    def book_info(self):
        return f"{self.title} by {self.author}"
    
    @book_info.setter
    def book_info(self, info):
        title, author = info.split(" by ")
        self.title = title
        self.author = author

book1 = Book()
book2 = Book()
print(book1)
print(repr(book1))
print(len(book1))
print(book1 == book2)


book3 = Book()
book3.book_info = "To Kill a Mockingbird by Harper Lee"
print(book3)