from schema import engine, User, Cookie, Order, LineItems, sessionmaker
from sqlalchemy import insert, func, select, update, delete


def insert_initial_values():
    session = sessionmaker()
    try:
        session.execute(
            insert(User),
            [
                {
                    "username": "cookiemon2",
                    "email_address": "cookiemon@example.com",
                    "password": "password",
                    "phone": "111-111-1111",
                }
            ],
        )
        session.execute(
            insert(Cookie),
            [
                {
                    "cookie_name": "chocolate chip",
                    "cookie_sku": "CC01",
                    "quantity": 12,
                    "unit_cost": 0.50,
                }
            ],
        )
        session.execute(insert(Order), [{"user_id": 1}])
        session.execute(
            insert(LineItems),
            [
                {
                    "order_id": 1,
                    "cookie_id": 1,
                    "quantity": 2,
                    "extended_cost": 1.00,
                }
            ],
        )
        session.commit()
    except Exception as e:
        print("Error inserting initial values: ", e)
        session.rollback()
    finally:
        session.close()


def fetch_cookies():
    session = sessionmaker()

    try:
        return session.query(Cookie).all()
    except Exception as e:
        print("Error fetching cookies: ", e)
    finally:
        session.close()


if __name__ == "__main__":
    # insert_initial_values()
    print(fetch_cookies())
