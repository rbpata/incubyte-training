from sqlalchemy import select, insert
from core_schema import users, orders, line_items, cookies, engine
from sqlalchemy.exc import IntegrityError


with engine.begin() as connection:
    ins = insert(users).values(
        username="cookiemon2",
        email_address="mon@cookie.com",
        phone="111-111-1111",
        password="password",
    )
    try:
        connection.execute(ins)
    except IntegrityError as e:
        print("Error inserting user: ", e.orig)
