"""
Student Database CRUD Application (Python + PostgreSQL)

This program connects to a PostgreSQL database named "students_db" and
performs the four CRUD operations on the "students" table:

    getAllStudents()                                              -> Read
    addStudent(first_name, last_name, email, enrollment_date)    -> Create
    updateStudentEmail(student_id, new_email)                    -> Update
    deleteStudent(student_id)                                    -> Delete

Run it with:  python src/app.py   (a text menu lets you call each function)
"""

import getpass
import os
import sys
from contextlib import contextmanager
from datetime import date

import psycopg2
from psycopg2 import errors

# ---------------------------------------------------------------------------
# Database connection settings
# ---------------------------------------------------------------------------
# Each value can be overridden with an environment variable. The password is
# never stored in the code: if DB_PASSWORD is not set, the program asks for it
# once when it starts (typing is hidden).
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "students_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
}


@contextmanager
def db_cursor():
    """
    Open a connection, hand back a cursor, then clean up.

    - Commits the transaction if the block finishes normally.
    - Rolls the transaction back if an error occurs, so a failed
      operation never leaves partial changes in the database.
    - Always closes the connection.
    """
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        cur = conn.cursor()
        try:
            yield cur
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# CRUD functions
# ---------------------------------------------------------------------------
def getAllStudents():
    """READ: retrieve every record from the students table and print it."""
    try:
        with db_cursor() as cur:
            cur.execute(
                "SELECT student_id, first_name, last_name, email, enrollment_date "
                "FROM students ORDER BY student_id"
            )
            rows = cur.fetchall()
    except psycopg2.Error as err:
        print(f"Database error while reading students: {err}")
        return []

    if not rows:
        print("The students table is empty.")
        return rows

    # Print the rows as a simple aligned table.
    print(f"{'ID':<5}{'First name':<14}{'Last name':<14}{'Email':<30}{'Enrolled':<12}")
    print("-" * 75)
    for student_id, first, last, email, enrolled in rows:
        print(f"{student_id:<5}{first:<14}{last:<14}{email:<30}{str(enrolled or ''):<12}")
    return rows


def addStudent(first_name, last_name, email, enrollment_date):
    """
    CREATE: insert a new student and return the new student_id.

    enrollment_date is a string in YYYY-MM-DD format (or empty for no date).
    Returns None if the insert fails.
    """
    # Validate the date before touching the database.
    if enrollment_date:
        try:
            enrollment_date = date.fromisoformat(enrollment_date)
        except ValueError:
            print("Invalid date. Please use the format YYYY-MM-DD.")
            return None
    else:
        enrollment_date = None

    try:
        with db_cursor() as cur:
            # %s placeholders let the driver escape values safely.
            cur.execute(
                "INSERT INTO students (first_name, last_name, email, enrollment_date) "
                "VALUES (%s, %s, %s, %s) RETURNING student_id",
                (first_name, last_name, email, enrollment_date),
            )
            new_id = cur.fetchone()[0]
        print(f"Student added with student_id {new_id}.")
        return new_id
    except errors.UniqueViolation:
        print(f"Could not add student: the email '{email}' already exists.")
    except errors.NotNullViolation:
        print("Could not add student: first name, last name and email are required.")
    except psycopg2.Error as err:
        print(f"Database error while adding student: {err}")
    return None


def updateStudentEmail(student_id, new_email):
    """UPDATE: change the email of the student with the given student_id."""
    try:
        with db_cursor() as cur:
            cur.execute(
                "UPDATE students SET email = %s WHERE student_id = %s",
                (new_email, student_id),
            )
            updated = cur.rowcount  # number of rows changed (0 = no such student)
    except errors.UniqueViolation:
        print(f"Could not update: the email '{new_email}' is already used by another student.")
        return False
    except errors.NotNullViolation:
        print("Could not update: the email cannot be empty.")
        return False
    except psycopg2.Error as err:
        print(f"Database error while updating email: {err}")
        return False

    if updated == 0:
        print(f"No student found with student_id {student_id}.")
        return False
    print(f"Email updated for student_id {student_id}.")
    return True


def deleteStudent(student_id):
    """DELETE: remove the student with the given student_id."""
    try:
        with db_cursor() as cur:
            cur.execute("DELETE FROM students WHERE student_id = %s", (student_id,))
            deleted = cur.rowcount  # number of rows removed (0 = no such student)
    except psycopg2.Error as err:
        print(f"Database error while deleting student: {err}")
        return False

    if deleted == 0:
        print(f"No student found with student_id {student_id}.")
        return False
    print(f"Student with student_id {student_id} deleted.")
    return True


# ---------------------------------------------------------------------------
# Text menu (used to demonstrate each function)
# ---------------------------------------------------------------------------
def read_int(prompt):
    """Keep asking until the user types a whole number."""
    while True:
        text = input(prompt).strip()
        try:
            return int(text)
        except ValueError:
            print("Please enter a whole number.")


def print_menu():
    print("\n=== Student Database ===")
    print("1. Show all students")
    print("2. Add a student")
    print("3. Update a student's email")
    print("4. Delete a student")
    print("5. Exit")


def main():
    # Ask for the password once if it was not provided through DB_PASSWORD.
    if DB_CONFIG["password"] is None:
        DB_CONFIG["password"] = getpass.getpass("PostgreSQL password: ")

    # Make sure we can reach the database before showing the menu.
    try:
        psycopg2.connect(**DB_CONFIG).close()
    except psycopg2.OperationalError as err:
        print(f"Could not connect to the database:\n{err}")
        sys.exit(1)

    while True:
        print_menu()
        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            getAllStudents()
        elif choice == "2":
            first = input("First name: ").strip()
            last = input("Last name: ").strip()
            email = input("Email: ").strip()
            enrolled = input("Enrollment date (YYYY-MM-DD, optional): ").strip()
            addStudent(first, last, email, enrolled)
        elif choice == "3":
            student_id = read_int("Student ID: ")
            new_email = input("New email: ").strip()
            updateStudentEmail(student_id, new_email)
        elif choice == "4":
            student_id = read_int("Student ID to delete: ")
            deleteStudent(student_id)
        elif choice == "5":
            print("Goodbye.")
            break
        else:
            print("Invalid option. Please choose 1 to 5.")


if __name__ == "__main__":
    main()
