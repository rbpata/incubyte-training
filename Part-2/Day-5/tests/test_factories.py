import pytest


# @pytest.fixture
# def make_custom_record():

#     def _make_custom_record(name, value):
#         return {"name": name, "value": value}

#     return _make_custom_record


# def test_custom_record(make_custom_record):
#     record = make_custom_record("ram", "test_value")
#     assert record == {"name": "ram", "value": "test_value"}


@pytest.fixture
def make_customer_record():
    created_records = []

    def _make_customer_record(name):
        record = {"name": name}
        created_records.append(record)
        return record

    yield _make_customer_record

    for record in created_records:
        record.clear()  # Simulate cleanup of records


def test_customer_records(make_customer_record):
    customer_1 = make_customer_record("Lisa")
    customer_2 = make_customer_record("Mike")
    customer_3 = make_customer_record("Meredith")
