# SCHOOL MANAGEMENT SYSTEM SW 26
# Kenzhemurat Damira CS1
# Entry point — run this file to start the application

from config import DB_CONFIG
from database import DatabaseManager
from auth import AuthService
from modules import create_tables, insert_test_data, Admin, Teacher, Student


def main():
    # Main entry point of the application
    # Connects to MySQL, creates tables, inserts sample data,
    # authenticates users and launches role-based menus

    # Step 1: connect to MySQL database
    db = DatabaseManager(DB_CONFIG)
    if not db.connect():
        print("Could not connect to database. Exiting.")
        return

    # Step 2: create tables if they don't exist yet
    create_tables(db.connection)

    # Step 3: fill tables with sample data
    insert_test_data(db.connection)

    print("=" * 45)
    print("   SCHOOL MANAGEMENT SYSTEM")
    print("=" * 45)

    # Step 4: login loop — keeps running until user exits (R9, O1)
    while True:
        role, user_id, course_id = AuthService.login()

        # If login failed 3 times — close the program
        if role is None:
            print("Program closed.")
            break

        print(f"\nWelcome! Logged in as: {role.upper()}")

        # Step 5: launch correct menu based on role (O6 — access levels)
        match role:
            case "admin":
                Admin(db).show_menu()               # full access
            case "teacher":
                Teacher(db, course_id).show_menu()  # own course only
            case "student":
                Student(db, user_id).show_menu()    # own data only

    # Step 6: close the database connection
    db.close()


if __name__ == "__main__":
    main()
