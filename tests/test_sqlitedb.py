import pytest

from wxflow import SQLiteDB


@pytest.fixture(scope="module")
def db():
    # Create an in-memory SQLite database for testing
    db = SQLiteDB(":memory:")
    db.connect()

    # Create a test table
    table_name = "test_table"
    columns = ["id INTEGER PRIMARY KEY", "name TEXT", "age INTEGER"]
    db.create_table(table_name, columns)

    yield db

    # Disconnect from the database
    db.disconnect()


def test_create_table(db):
    # Verify that the test table exists
    assert table_exists(db, "test_table")


def test_add_column(db):
    # Add a new column to the test table
    column_name = "address"
    column_type = "TEXT"
    db.add_column("test_table", column_name, column_type)

    # Verify that the column exists in the test table
    assert column_exists(db, "test_table", column_name)


def test_update_data(db):
    # Insert test data into the table
    values = [1, "Alice", 25, 'Apt 101']
    db.insert_data("test_table", values)

    # Update the age of the record
    new_age = 30
    db.update_data("test_table", "age", new_age, "name", "Alice")

    # Fetch the updated data
    result = db.fetch_data("test_table", condition="name='Alice'")

    # Verify that the age is updated correctly
    assert result[0][2] == new_age


def test_remove_column(db):
    # Removes a column from the test table
    column_name = "address"
    db.remove_column("test_table", column_name)

    # Verify that the column exists in the test table
    assert not column_exists(db, "test_table", column_name)


def test_remove_column_raises_error_when_column_not_exists(db):
    table_name = "test_table"
    column_name = "vacation address"

    with pytest.raises(ValueError, match=f"Column '{column_name}' does not exist in table '{table_name}'"):
        db.remove_column("test_table", column_name)


def test_insert_data(db):
    # Insert test data into the table
    values = [2, "Bob", 35]
    db.insert_data("test_table", values)

    # Fetch all data from the table
    result = db.fetch_data("test_table")

    # Verify that the inserted data is present in the table
    assert len(result) == 2


def test_fetch_data(db):
    # Insert test data into the table
    values = [3, "Charlie", 40]
    db.insert_data("test_table", values)

    # Fetch data from the table
    result = db.fetch_data("test_table", condition="age > 30")

    # Verify that the fetched data meets the condition
    assert len(result) == 2


def test_remove_data(db):
    # Insert test data into the table
    values = [4, "David", 45]
    db.insert_data("test_table", values)

    # Remove a record from the table
    db.remove_data("test_table", "name", "David")

    # Fetch all data from the table
    result = db.fetch_data("test_table")

    # Verify that the removed data is not present in the table
    assert len(result) == 3


# Helper functions

def table_exists(db, table_name):
    query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
    cursor = db.execute_query(query)
    return cursor.fetchone() is not None


def column_exists(db, table_name, column_name):
    query = f"PRAGMA table_info({table_name})"
    cursor = db.execute_query(query)
    columns = [column[1] for column in cursor.fetchall()]
    return column_name in columns
