from core_schema import engine, cookies, users, orders, line_items
from sqlalchemy import insert, func, select, update, delete


def seed_initial_data():
    try:
        with engine.begin() as connection:
            # Clear child tables first, then parent tables.
            connection.execute(delete(line_items))
            connection.execute(delete(orders))
            connection.execute(delete(users))
            connection.execute(delete(cookies))

            cookie_rows = [
                {
                    "cookie_id": 1,
                    "cookie_name": "chocolate chip",
                    "cookie_recipe_url": "http://somewhere.com/choc_chip.html",
                    "cookie_sku": "CC01",
                    "quantity": 12,
                    "unit_cost": 0.50,
                },
                {
                    "cookie_id": 2,
                    "cookie_name": "dark chocolate chip",
                    "cookie_recipe_url": "http://somewhere.com/dark_choc_chip.html",
                    "cookie_sku": "CC02",
                    "quantity": 8,
                    "unit_cost": 0.75,
                },
                {
                    "cookie_id": 3,
                    "cookie_name": "white chocolate chip",
                    "cookie_recipe_url": "http://somewhere.com/white_choc_chip.html",
                    "cookie_sku": "CC03",
                    "quantity": 10,
                    "unit_cost": 0.80,
                },
                {
                    "cookie_id": 4,
                    "cookie_name": "peanut butter",
                    "cookie_recipe_url": "http://somewhere.com/peanut_butter.html",
                    "cookie_sku": "PB01",
                    "quantity": 24,
                    "unit_cost": 0.25,
                },
                {
                    "cookie_id": 5,
                    "cookie_name": "oatmeal raisin",
                    "cookie_recipe_url": "http://somewhere.com/oatmeal_raisin.html",
                    "cookie_sku": "OR01",
                    "quantity": 100,
                    "unit_cost": 0.50,
                },
            ]

            user_rows = [
                {
                    "user_id": 1,
                    "customer_number": 1001,
                    "username": "cookiemon",
                    "email_address": "cook@bakedgoods.com",
                    "phone": "111-222-3333",
                    "password": "secret123",
                },
                {
                    "user_id": 2,
                    "customer_number": 1002,
                    "username": "baker01",
                    "email_address": "baker01@bakedgoods.com",
                    "phone": "222-333-4444",
                    "password": "secret123",
                },
                {
                    "user_id": 3,
                    "customer_number": 1003,
                    "username": "sweettooth",
                    "email_address": "sweettooth@bakedgoods.com",
                    "phone": "333-444-5555",
                    "password": "secret123",
                },
            ]

            order_rows = [
                {"order_id": 1, "user_id": 1},
                {"order_id": 2, "user_id": 1},
                {"order_id": 3, "user_id": 2},
                {"order_id": 4, "user_id": 3},
            ]

            line_item_rows = [
                {
                    "line_items_id": 1,
                    "order_id": 1,
                    "cookie_id": 1,
                    "quantity": 2,
                    "extended_cost": 1.00,
                },
                {
                    "line_items_id": 2,
                    "order_id": 1,
                    "cookie_id": 4,
                    "quantity": 4,
                    "extended_cost": 1.00,
                },
                {
                    "line_items_id": 3,
                    "order_id": 2,
                    "cookie_id": 3,
                    "quantity": 3,
                    "extended_cost": 2.40,
                },
                {
                    "line_items_id": 4,
                    "order_id": 3,
                    "cookie_id": 5,
                    "quantity": 5,
                    "extended_cost": 2.50,
                },
                {
                    "line_items_id": 5,
                    "order_id": 4,
                    "cookie_id": 2,
                    "quantity": 6,
                    "extended_cost": 4.50,
                },
            ]

            connection.execute(insert(cookies), cookie_rows)
            connection.execute(insert(users), user_rows)
            connection.execute(insert(orders), order_rows)
            connection.execute(insert(line_items), line_item_rows)

            print(
                "Initial bulk data inserted into cookies, users, orders, and line_items"
            )
    except Exception as e:
        print(f"Error seeding initial data: {e}")


def initialize_data():
    try:
        with engine.begin() as connection:
            connection.execute(
                insert(users),
                [{"username": "cookiemon", "email_address": "cook@bakedgoods.com"}],
            )
            connection.execute(insert(orders), [{"user_id": 1}])
            connection.commit()
    except Exception as e:
        print(f"Error initializing data: {e}")
        return


def insert_cookie():
    try:
        with engine.begin() as connection:
            invetory_list = [
                {
                    "cookie_name": "chocolate chip",
                    "cookie_recipe_url": "http://somewhere.com/choc_chip.html",
                    "cookie_sku": "CC01",
                    "quantity": 12,
                    "unit_cost": 0.50,
                },
                {
                    "cookie_name": "dark chocolate chip",
                    "cookie_recipe_url": "http://somewhere.com/dark_choc_chip.html",
                    "cookie_sku": "CC02",
                    "quantity": 1,
                    "unit_cost": 0.75,
                },
                {
                    "cookie_name": "white chocolate chip",
                    "cookie_recipe_url": "http://somewhere.com/white_choc_chip.html",
                    "cookie_sku": "CC03",
                    "quantity": 1,
                    "unit_cost": 0.75,
                },
                {
                    "cookie_name": "peanut butter",
                    "cookie_recipe_url": "http://somewhere.com/peanut_butter.html",
                    "cookie_sku": "PB01",
                    "quantity": 24,
                    "unit_cost": 0.25,
                },
                {
                    "cookie_name": "oatmeal raisin",
                    "cookie_recipe_url": "http://somewhere.com/oatmeal_raisin.html",
                    "cookie_sku": "OR01",
                    "quantity": 100,
                    "unit_cost": 0.50,
                },
            ]
            connection.execute(insert(cookies), invetory_list)
            connection.commit()

    except Exception as e:
        print(f"Error inserting data: {e}")
        return

    try:
        with engine.begin() as connection:
            connection.execute(
                insert(orders),
                [
                    {"user_id": 1},
                    {"user_id": 2},
                    {"user_id": 3},
                ],
            )
            connection.commit()

    except Exception as e:
        print(f"Error inserting data: {e}")
        return


def select_cookies():
    try:
        with engine.connect() as connection:
            select_stmt = cookies.select()
            # select_stmt = select_stmt.order_by(cookies.c.cookie_name.desc())
            select_stmt = select_stmt.limit(2)
            result = connection.execute(select_stmt)
            for row in result:
                print(row)

    except Exception as e:
        print(f"Error selecting data: {e}")


def count_cookies():
    try:
        with engine.connect() as connection:
            s = select(func.count(cookies.c.cookie_id).label("inventory_count"))
            result = connection.execute(s).first()
            print(f"Total number of cookies in inventory: {result.inventory_count}")

    except Exception as e:
        print(f"Error counting cookies: {e}")


def filter_cookies():
    try:
        with engine.connect() as connection:
            s = select(cookies).where(cookies.c.cookie_name == "oatmeal raisin")
            result = connection.execute(s)
            for row in result:
                print(row)

    except Exception as e:
        print(f"Error filtering cookies: {e}")


def trucate_cookies():
    try:
        with engine.begin() as connection:
            connection.execute(cookies.delete())
            connection.commit()

    except Exception as e:
        print(f"Error truncating cookies: {e}")


def update_cookies():
    try:
        with engine.begin() as connection:
            u = (
                update(cookies)
                .where(cookies.c.cookie_name == "oatmeal raisin")
                .values(quantity=100)
            )
            connection.execute(u)
            connection.commit()

    except Exception as e:
        print(f"Error updating cookies: {e}")


def delete_cookies():
    try:
        with engine.begin() as connection:
            d = delete(cookies).where(cookies.c.cookie_name == "oatmeal raisin")
            connection.execute(d)
            connection.commit()

    except Exception as e:
        print(f"Error deleting cookies: {e}")


def orders_by_user():
    try:
        with engine.connect() as connection:
            s = (
                select(users.c.username, orders.c.order_id)
                .outerjoin(orders)
                .where(users.c.user_id == orders.c.user_id)
                .order_by(users.c.username)
            )
            result = connection.execute(s)
            for row in result:
                print(row)

    except Exception as e:
        print(f"Error selecting data: {e}")


def get_orders_by_customer(cust_name):
    with engine.connect() as connection:
        columns = [
            orders.c.order_id,
            users.c.username,
            users.c.phone,
            cookies.c.cookie_name,
            line_items.c.quantity,
            line_items.c.extended_cost,
        ]
        cust_order = (
            select(*columns)
            .join(users)
            .join(line_items)
            .join(cookies)
            .where(users.c.username == cust_name)
        )
        result = connection.execute(cust_order)
        return result.fetchall()

#raw query
# stmt = select([users]).where(text("username='cookiemon'"))
# print(connection.execute(stmt).fetchall())


if __name__ == "__main__":
    # seed_initial_data()
    # trucate_cookies()
    # insert_cookie()
    # select_cookies()
    # count_cookies()
    # filter_cookies()
    # # update_cookies()
    # filter_cookies()
    # delete_cookies()
    # filter_cookies()

    # seed_initial_data()
    # orders_by_user()
    print(get_orders_by_customer("cookiemon"))
