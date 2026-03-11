# context manager control the setupa and clean up the resources


class Database:

    def __init__(self, database_name):
        self.databse_name = database_name
        self.connection = None

    def __enter__(self):
        print("Connection to the database..")
        self.connection = True
        return self

    def __exit__(self, exc_type, exc, tb):
        print("closing the database..")
        self.connection = False
        if exc_type:
            print("DB ERROR : ", exc)
            return False
        return True

    def execute(self, query):
        print("executed the query..", query)


with Database("temp") as db:
    db.execute("select * from employee")


# with the decorator

from contextlib import contextmanager


@contextmanager
def database(database_name):
    print("connecting to the database")
    connection = True

    try:
        yield connection

    finally:
        connection = False
        print("closing the database")


import os


@contextmanager
def safe_write(filepath):
    f = open(filepath, mode="+a")
    try:
        yield f
        f.close()
        print("file saved currectly..")

    except Exception as e:
        f.close()
        os.remove(filepath)
        print("failed to close the file")
        raise


with safe_write(
    "/Users/ram_pata/Incubyte/incubyte-training/Part-1/Day-5/text.txt"
) as f:
    f.write("writing in the text file.")
