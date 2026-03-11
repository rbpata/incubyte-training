def counter():
    count = 0
    while True:
        yield count
        count += 1


for i in counter():
    print(i)
    if i >= 5:
        break


def read_file(file_path):
    with open(file_path) as f:
        for line in f:
            yield line.strip()


for line in read_file(
    "/Users/ram_pata/Incubyte/incubyte-training/Part-1/Day-5/text.txt"
):
    print(line)


books = [
    {"title": "Dune", "pages": 688, "available": True},
    {"title": "1984", "pages": 328, "available": True},
    {"title": "Sapiens", "pages": 443, "available": False},
    {"title": "Atomic", "pages": 320, "available": True},
]


def only_available(books):
    for book in books:
        if book["available"] == True:
            yield book


def under_pages(books, limit):
    for book in books:
        if book["pages"] > limit:
            yield book


def format_title(books):
    for i in books:
        yield f"{i['title']} ({i['pages']})"


pipeline = format_title(under_pages(only_available(books), 400))
for book in pipeline:
    print(book)

# generator expression
squares = (x**2 for x in range(10))
print(next(squares))
print(next(squares))
print(next(squares))


