# modules.py
# Contains: Person, StudentPerson, TeacherPerson, TablePrinter,
#           create_tables, insert_test_data, Admin, Teacher, Student

import mysql.connector
from mysql.connector import Error
from validators import InputValidator
from config import DB_CONFIG

try:
    from rich.console import Console
    from rich.table import Table
    from rich import print as rprint
    console = Console(force_terminal=True)
except ImportError:
    Console = None
    Table = None
    rprint = print
    console = None


# ── OOP CLASSES ──────────────────────────────────────────────────────────────
# Parent class used for inheritance
# Common attributes stored here to reduce code duplication
# Protected variables demonstrate encapsulation

class Person:
    # Base class representing a person in the school system
    # Every person in the system has these 4 fields

    def __init__(self, first_name, last_name, email, phone_number):
        # Encapsulated attributes with underscore — private access
        self._first_name = first_name
        self._last_name = last_name
        self._email = email
        self._phone_number = phone_number

    # Getter methods to safely access encapsulated attributes
    @property
    def first_name(self):
        return self._first_name

    @property
    def last_name(self):
        return self._last_name

    @property
    def email(self):
        return self._email

    @property
    def phone_number(self):
        return self._phone_number

    def full_name(self):
        # Return full name as one string
        return f"{self._first_name} {self._last_name}"

    def __str__(self):
        return f"{self.full_name()} ({self._email})"


class StudentPerson(Person):
    # StudentPerson inherits from Person
    # Additional student-specific attributes added here
    # This demonstrates inheritance and code reuse

    def __init__(self, first_name, last_name, email, phone_number,
                 date_of_birth, gender, address):
        # Call parent constructor — inherits base attributes
        super().__init__(first_name, last_name, email, phone_number)
        self._date_of_birth = date_of_birth
        self._gender = gender
        self._address = address

    @property
    def date_of_birth(self):
        return self._date_of_birth

    @property
    def gender(self):
        return self._gender

    @property
    def address(self):
        return self._address


class TeacherPerson(Person):
    # TeacherPerson inherits from Person
    # Stores teacher-specific information such as department

    def __init__(self, first_name, last_name, email, phone_number, department):
        # Call parent constructor — inherits base attributes
        super().__init__(first_name, last_name, email, phone_number)
        self._department = department

    @property
    def department(self):
        return self._department


# ── TABLE PRINTER ─────────────────────────────────────────────────────────────

class TablePrinter:
    # Displays database records in formatted tables using the rich library
    # Improves readability and user experience

    def __init__(self):
        # Use rich Console if available, otherwise fall back to plain text
        self.console = Console(force_terminal=True) if Console else None

    def print_table(self, title, columns, rows):
        # Print data as a formatted table with title and column headers
        if not rows:
            print("No records found.")
            return

        if self.console and Table:
            # Rich formatted table output
            table = Table(title=title)
            for column in columns:
                table.add_column(column, overflow="fold", no_wrap=False)
            for row in rows:
                table.add_row(*[str(value) for value in row])
            self.console.print(table)
        else:
            # Plain text fallback if rich is not installed
            print(f"\n--- {title} ---")
            print(" | ".join(columns))
            print("-" * 80)
            for row in rows:
                print(" | ".join(str(value) for value in row))


# ── DATA SETUP ────────────────────────────────────────────────────────────────

def create_tables(connection):
    # Creates all relational database tables used in the system
    # Primary keys, foreign keys and constraints maintain data integrity
    try:
        cursor = connection.cursor()

        # 1. Teachers table — must be created before courses
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teachers (
                teacher_id   INT          AUTO_INCREMENT PRIMARY KEY,
                first_name   VARCHAR(50)  NOT NULL,
                last_name    VARCHAR(50)  NOT NULL,
                email        VARCHAR(100) NOT NULL UNIQUE,
                phone_number VARCHAR(20)  NOT NULL,
                department   VARCHAR(100) NOT NULL,
                created_at   DATE         NOT NULL DEFAULT (CURRENT_DATE)
            )
        """)

        # 2. Students table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id    INT          AUTO_INCREMENT PRIMARY KEY,
                first_name    VARCHAR(50)  NOT NULL,
                last_name     VARCHAR(50)  NOT NULL,
                date_of_birth DATE         NOT NULL,
                gender        VARCHAR(10)  NOT NULL
                              CHECK (gender IN ('Male','Female','Other')),
                email         VARCHAR(100) NOT NULL UNIQUE,
                phone_number  VARCHAR(20)  NOT NULL,
                address       VARCHAR(255) NOT NULL,
                created_at    DATE         NOT NULL DEFAULT (CURRENT_DATE)
            )
        """)

        # 3. Courses table — linked to teachers via foreign key
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                course_id      INT          AUTO_INCREMENT PRIMARY KEY,
                course_name    VARCHAR(100) NOT NULL,
                course_code    VARCHAR(20)  NOT NULL UNIQUE,
                teacher_id     INT          NOT NULL,
                course_credits INT          NOT NULL
                               CHECK (course_credits BETWEEN 1 AND 10),
                CONSTRAINT fk_course_teacher
                    FOREIGN KEY (teacher_id)
                    REFERENCES teachers(teacher_id)
                    ON UPDATE CASCADE ON DELETE RESTRICT
            )
        """)

        # 4. Registrations table — links students to courses
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS registrations (
                registration_id   INT  AUTO_INCREMENT PRIMARY KEY,
                student_id        INT  NOT NULL,
                course_id         INT  NOT NULL,
                registration_date DATE NOT NULL DEFAULT (CURRENT_DATE),
                CONSTRAINT fk_reg_student
                    FOREIGN KEY (student_id) REFERENCES students(student_id)
                    ON UPDATE CASCADE ON DELETE CASCADE,
                CONSTRAINT fk_reg_course
                    FOREIGN KEY (course_id) REFERENCES courses(course_id)
                    ON UPDATE CASCADE ON DELETE CASCADE,
                UNIQUE KEY uq_student_course (student_id, course_id)
            )
        """)

        # 5. Attendance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                attendance_id   INT         AUTO_INCREMENT PRIMARY KEY,
                student_id      INT         NOT NULL,
                course_id       INT         NOT NULL,
                attendance_date DATE        NOT NULL DEFAULT (CURRENT_DATE),
                status          VARCHAR(20) NOT NULL
                                CHECK (status IN ('Present','Absent','Late')),
                CONSTRAINT fk_att_student
                    FOREIGN KEY (student_id) REFERENCES students(student_id)
                    ON UPDATE CASCADE ON DELETE CASCADE,
                CONSTRAINT fk_att_course
                    FOREIGN KEY (course_id) REFERENCES courses(course_id)
                    ON UPDATE CASCADE ON DELETE CASCADE
            )
        """)

        # 6. Grades table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grades (
                grade_id    INT        AUTO_INCREMENT PRIMARY KEY,
                student_id  INT        NOT NULL,
                course_id   INT        NOT NULL,
                grade_value VARCHAR(5) NOT NULL
                            CHECK (grade_value IN ('A','B','C','D','F')),
                grade_date  DATE       NOT NULL DEFAULT (CURRENT_DATE),
                CONSTRAINT fk_grade_student
                    FOREIGN KEY (student_id) REFERENCES students(student_id)
                    ON UPDATE CASCADE ON DELETE CASCADE,
                CONSTRAINT fk_grade_course
                    FOREIGN KEY (course_id) REFERENCES courses(course_id)
                    ON UPDATE CASCADE ON DELETE CASCADE
            )
        """)

        connection.commit()
        print("Tables created successfully.")
        cursor.close()

    except Error as err:
        print(f"Error creating tables: {err}")


def insert_test_data(connection):
    # Inserts sample school data into the database
    # INSERT IGNORE prevents duplicate records on re-run
    try:
        cursor = connection.cursor()

        # 1. Insert 5 teachers
        cursor.executemany("""
            INSERT IGNORE INTO teachers
                (teacher_id, first_name, last_name, email, phone_number, department)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, [
            (1, 'Dana',     'Sarsen',     'dana.sarsen@school.kz',        '+77011112233', 'Mathematics'),
            (2, 'Timur',    'Omarov',     'timur.omarov@school.kz',       '+77022223344', 'History'),
            (3, 'Aliya',    'Nurgalieva', 'aliya.nurgalieva@school.kz',   '+77033334455', 'English'),
            (4, 'Erlan',    'Kassymov',   'erlan.kassymov@school.kz',     '+77044445566', 'Physics'),
            (5, 'Saltanat', 'Akhmetova',  'saltanat.akhmetova@school.kz', '+77055556677', 'Biology'),
        ])

        # 2. Insert 10 students
        cursor.executemany("""
            INSERT IGNORE INTO students
                (student_id, first_name, last_name, date_of_birth,
                 gender, email, phone_number, address)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, [
            (1,  'Amina',   'Kovaleva',   '2008-03-15', 'Female', 'amina.kovaleva@school.kz',    '+77011110001', 'Almaty, Abay 10'),
            (2,  'Dias',    'Nurlan',     '2007-07-22', 'Male',   'dias.nurlan@school.kz',       '+77011110002', 'Almaty, Dostyk 5'),
            (3,  'Arman',   'Zhaksylyk',  '2008-01-10', 'Male',   'arman.zhaksylyk@school.kz',   '+77011110003', 'Astana, Kerey 3'),
            (4,  'Sofia',   'Petrova',    '2007-11-30', 'Female', 'sofia.petrova@school.kz',     '+77011110004', 'Astana, Mangilik 7'),
            (5,  'Miras',   'Aitbay',     '2008-05-18', 'Male',   'miras.aitbay@school.kz',      '+77011110005', 'Almaty, Seifullin 12'),
            (6,  'Alina',   'Sadykova',   '2007-09-04', 'Female', 'alina.sadykova@school.kz',    '+77011110006', 'Almaty, Furmanov 8'),
            (7,  'Ruslan',  'Imanov',     '2008-02-27', 'Male',   'ruslan.imanov@school.kz',     '+77011110007', 'Astana, Beibitshilik 2'),
            (8,  'Leila',   'Karimova',   '2007-12-05', 'Female', 'leila.karimova@school.kz',    '+77011110008', 'Almaty, Tole Bi 15'),
            (9,  'Sanzhar', 'Mukhanov',   '2008-06-14', 'Male',   'sanzhar.mukhanov@school.kz',  '+77011110009', 'Astana, Kabanbay 4'),
            (10, 'Kamila',  'Aubakirova', '2007-08-20', 'Female', 'kamila.aubakirova@school.kz', '+77011110010', 'Almaty, Al-Farabi 9'),
        ])

        # 3. Insert 5 courses
        cursor.executemany("""
            INSERT IGNORE INTO courses
                (course_id, course_name, course_code, teacher_id, course_credits)
            VALUES (%s, %s, %s, %s, %s)
        """, [
            (1, 'Mathematics', 'MATH101', 1, 5),
            (2, 'History',     'HIST101', 2, 3),
            (3, 'English',     'ENGL101', 3, 4),
            (4, 'Physics',     'PHYS101', 4, 4),
            (5, 'Biology',     'BIOL101', 5, 3),
        ])

        # 4. Insert registrations
        cursor.executemany("""
            INSERT IGNORE INTO registrations
                (registration_id, student_id, course_id, registration_date)
            VALUES (%s, %s, %s, %s)
        """, [
            (1,  1, 1, '2026-01-10'), (2,  1, 3, '2026-01-10'),
            (3,  2, 1, '2026-01-10'), (4,  2, 2, '2026-01-10'),
            (5,  3, 1, '2026-01-11'), (6,  3, 4, '2026-01-11'),
            (7,  4, 3, '2026-01-11'), (8,  4, 5, '2026-01-11'),
            (9,  5, 1, '2026-01-12'), (10, 5, 2, '2026-01-12'),
            (11, 6, 3, '2026-01-12'), (12, 6, 4, '2026-01-12'),
            (13, 7, 1, '2026-01-13'), (14, 7, 5, '2026-01-13'),
            (15, 8, 2, '2026-01-13'), (16, 8, 3, '2026-01-13'),
            (17, 9, 4, '2026-01-14'), (18, 9, 5, '2026-01-14'),
            (19, 10, 1, '2026-01-14'), (20, 10, 3, '2026-01-14'),
        ])

        # 5. Insert attendance records
        cursor.executemany("""
            INSERT IGNORE INTO attendance
                (attendance_id, student_id, course_id, attendance_date, status)
            VALUES (%s, %s, %s, %s, %s)
        """, [
            (1,  1, 1, '2026-05-11', 'Present'), (2,  1, 3, '2026-05-12', 'Present'),
            (3,  2, 1, '2026-05-11', 'Absent'),  (4,  2, 2, '2026-05-13', 'Late'),
            (5,  3, 1, '2026-05-11', 'Present'), (6,  3, 4, '2026-05-14', 'Present'),
            (7,  4, 3, '2026-05-12', 'Late'),    (8,  4, 5, '2026-05-15', 'Present'),
            (9,  5, 1, '2026-05-11', 'Present'), (10, 5, 2, '2026-05-13', 'Absent'),
            (11, 6, 3, '2026-05-12', 'Present'), (12, 6, 4, '2026-05-14', 'Present'),
            (13, 7, 1, '2026-05-11', 'Late'),    (14, 7, 5, '2026-05-15', 'Present'),
            (15, 8, 2, '2026-05-13', 'Present'), (16, 8, 3, '2026-05-12', 'Absent'),
            (17, 9, 4, '2026-05-14', 'Present'), (18, 9, 5, '2026-05-15', 'Present'),
            (19, 10, 1, '2026-05-11', 'Present'), (20, 10, 3, '2026-05-12', 'Late'),
        ])

        # 6. Insert grade records
        cursor.executemany("""
            INSERT IGNORE INTO grades
                (grade_id, student_id, course_id, grade_value, grade_date)
            VALUES (%s, %s, %s, %s, %s)
        """, [
            (1,  1, 1, 'A', '2026-05-11'), (2,  1, 3, 'B', '2026-05-12'),
            (3,  2, 1, 'C', '2026-05-11'), (4,  2, 2, 'B', '2026-05-13'),
            (5,  3, 1, 'A', '2026-05-11'), (6,  3, 4, 'B', '2026-05-14'),
            (7,  4, 3, 'A', '2026-05-12'), (8,  4, 5, 'C', '2026-05-15'),
            (9,  5, 1, 'B', '2026-05-11'), (10, 5, 2, 'D', '2026-05-13'),
            (11, 6, 3, 'A', '2026-05-12'), (12, 6, 4, 'B', '2026-05-14'),
            (13, 7, 1, 'C', '2026-05-11'), (14, 7, 5, 'A', '2026-05-15'),
            (15, 8, 2, 'B', '2026-05-13'), (16, 8, 3, 'C', '2026-05-12'),
            (17, 9, 4, 'A', '2026-05-14'), (18, 9, 5, 'B', '2026-05-15'),
            (19, 10, 1, 'A', '2026-05-11'), (20, 10, 3, 'B', '2026-05-12'),
        ])

        connection.commit()
        print("Test data inserted successfully.")
        cursor.close()

    except Error as err:
        print(f"Error inserting test data: {err}")


# ── ADMIN CLASS ───────────────────────────────────────────────────────────────

class Admin:
    # Admin role has full CRUD access to all system entities
    # This includes students, teachers, courses,
    # registrations, attendance and grades

    def __init__(self, db):
        self.db = db
        self.validator = InputValidator()
        self.printer = TablePrinter()

    # STUDENTS

    def add_student(self):
        # Add a new student using OOP StudentPerson class
        print("\n--- Add Student ---")
        first_name    = self.validator.get_non_empty_string("First name: ")
        last_name     = self.validator.get_non_empty_string("Last name: ")
        date_of_birth = self.validator.get_birth_date("Date of birth (YYYY-MM-DD): ")
        gender        = self.validator.get_gender("Gender (Male/Female/Other): ")
        email         = self.validator.get_email("Email: ")
        phone_number  = self.validator.get_phone_number("Phone number: ")
        address       = self.validator.get_address("Address: ")

        # OOP: encapsulate data in StudentPerson object
        student = StudentPerson(first_name, last_name, email, phone_number,
                                date_of_birth, gender, address)
        result = self.db.execute_procedure("sp_add_student", [
            student.first_name, student.last_name, student.date_of_birth,
            student.gender, student.email, student.phone_number, student.address
        ])
        if result:
            console.print("[green]Student added successfully.[/green]")

    def view_students(self):
        # Get all students from database and print as table
        rows = self.db.execute_procedure("sp_get_all_students", fetch=True)
        if rows is None:
            return []
        self.printer.print_table("Students",
            ["ID", "First Name", "Last Name", "Date of Birth",
             "Gender", "Email", "Phone Number", "Address"], rows)
        return rows

    def update_student(self):
        # Ask for student ID then new values — update in database
        print("\n--- Update Student ---")
        student_id    = self.validator.get_positive_int("Student ID: ")
        first_name    = self.validator.get_non_empty_string("New first name: ")
        last_name     = self.validator.get_non_empty_string("New last name: ")
        date_of_birth = self.validator.get_birth_date("New date of birth (YYYY-MM-DD): ")
        gender        = self.validator.get_gender("New gender: ")
        email         = self.validator.get_email("New email: ")
        phone_number  = self.validator.get_phone_number("New phone number: ")
        address       = self.validator.get_address("New address: ")
        result = self.db.execute_procedure("sp_update_student",
            [student_id, first_name, last_name, date_of_birth,
             gender, email, phone_number, address])
        if result:
            console.print("[green]Student updated successfully.[/green]")

    def delete_student(self):
        # Ask for student ID → confirm → delete from database
        print("\n--- Delete Student ---")
        student_id = self.validator.get_positive_int("Student ID: ")
        if input("Are you sure? (yes/no): ").strip().lower() != "yes":
            print("Delete cancelled.")
            return
        if self.db.execute_procedure("sp_delete_student", [student_id]):
            console.print("[green]Student deleted successfully.[/green]")

    def search_students(self):
        # Search students by name, email or ID (R5)
        print("\n--- Search Students ---")
        rows = self.db.execute_procedure("sp_get_all_students", fetch=True)
        if not rows:
            print("No students found.")
            return
        print("Search by: 1. Name/Email   2. ID")
        choice = self.validator.get_menu_choice("Choose: ", ["1", "2"])
        if choice == "1":
            keyword = input("Enter name or email: ").strip().lower()
            found = [r for r in rows if keyword in f"{r[1]} {r[2]} {r[5]}".lower()]
        else:
            student_id = input("Enter student ID: ").strip()
            if not student_id.isdigit():
                print("ID must be a number.")
                return
            found = [r for r in rows if int(r[0]) == int(student_id)]
        if not found:
            print("No students found.")
            return
        self.printer.print_table("Search Results",
            ["ID", "First Name", "Last Name", "Date of Birth",
             "Gender", "Email", "Phone Number", "Address"], found)

    def sort_students(self):
        # Get all students → sort by chosen field (R5)
        print("\n--- Sort Students ---")
        rows = self.db.execute_procedure("sp_get_all_students", fetch=True)
        if not rows:
            print("No students found.")
            return
        choice = self.validator.get_sort_choice(
            "Sort by id, first or last: ", ["id", "first", "last"])
        key_map = {
            "id":    lambda r: r[0],
            "first": lambda r: str(r[1]).lower(),
            "last":  lambda r: str(r[2]).lower(),
        }
        self.printer.print_table("Sorted Students",
            ["ID", "First Name", "Last Name", "Date of Birth",
             "Gender", "Email", "Phone Number", "Address"],
            sorted(rows, key=key_map[choice]))

    # TEACHERS

    def add_teacher(self):
        # Add a new teacher using OOP TeacherPerson class
        print("\n--- Add Teacher ---")
        first_name   = self.validator.get_non_empty_string("First name: ")
        last_name    = self.validator.get_non_empty_string("Last name: ")
        email        = self.validator.get_email("Email: ")
        phone_number = self.validator.get_phone_number("Phone number: ")
        department   = self.validator.get_non_empty_string("Department: ")

        # OOP: encapsulate data in TeacherPerson object
        teacher = TeacherPerson(first_name, last_name, email, phone_number, department)
        result = self.db.execute_procedure("sp_add_teacher", [
            teacher.first_name, teacher.last_name, teacher.email,
            teacher.phone_number, teacher.department
        ])
        if result:
            console.print("[green]Teacher added successfully.[/green]")

    def view_teachers(self):
        # Get all teachers from database and print as table
        rows = self.db.execute_procedure("sp_get_all_teachers", fetch=True)
        if rows is None:
            return []
        self.printer.print_table("Teachers",
            ["ID", "First Name", "Last Name", "Email",
             "Phone Number", "Department"], rows)
        return rows

    def update_teacher(self):
        # Ask for teacher ID then new values — update in database
        print("\n--- Update Teacher ---")
        teacher_id   = self.validator.get_positive_int("Teacher ID: ")
        first_name   = self.validator.get_non_empty_string("New first name: ")
        last_name    = self.validator.get_non_empty_string("New last name: ")
        email        = self.validator.get_email("New email: ")
        phone_number = self.validator.get_phone_number("New phone number: ")
        department   = self.validator.get_non_empty_string("New department: ")
        result = self.db.execute_procedure("sp_update_teacher",
            [teacher_id, first_name, last_name, email, phone_number, department])
        if result:
            console.print("[green]Teacher updated successfully.[/green]")

    def delete_teacher(self):
        # Delete teacher — checks for linked courses first
        print("\n--- Delete Teacher ---")
        teacher_id = self.validator.get_positive_int("Teacher ID: ")

        # Check if teacher has any courses linked to them
        courses = self.db.execute_procedure("sp_get_all_courses", fetch=True)
        linked = [r for r in courses if int(r[3]) == int(teacher_id)]
        if linked:
            print("Cannot delete this teacher — they have active courses:")
            for course in linked:
                print(f"  - {course[1]} ({course[2]})")
            print("Please reassign or delete these courses first.")
            return

        if input("Are you sure? (yes/no): ").strip().lower() != "yes":
            print("Delete cancelled.")
            return
        if self.db.execute_procedure("sp_delete_teacher", [teacher_id]):
            console.print("[green]Teacher deleted successfully.[/green]")

    def search_teachers(self):
        # Search teachers by name, email, department or ID (R5)
        print("\n--- Search Teachers ---")
        rows = self.db.execute_procedure("sp_get_all_teachers", fetch=True)
        if not rows:
            print("No teachers found.")
            return
        print("Search by: 1. Name/Email/Department   2. ID")
        choice = self.validator.get_menu_choice("Choose: ", ["1", "2"])
        if choice == "1":
            keyword = input("Enter name, email or department: ").strip().lower()
            found = [r for r in rows
                     if keyword in f"{r[1]} {r[2]} {r[3]} {r[5]}".lower()]
        else:
            teacher_id = input("Enter teacher ID: ").strip()
            if not teacher_id.isdigit():
                print("ID must be a number.")
                return
            found = [r for r in rows if int(r[0]) == int(teacher_id)]
        if not found:
            print("No teachers found.")
            return
        self.printer.print_table("Search Results",
            ["ID", "First Name", "Last Name", "Email",
             "Phone Number", "Department"], found)

    def sort_teachers(self):
        # Get all teachers → sort by chosen field (R5)
        print("\n--- Sort Teachers ---")
        rows = self.db.execute_procedure("sp_get_all_teachers", fetch=True)
        if not rows:
            print("No teachers found.")
            return
        choice = self.validator.get_sort_choice(
            "Sort by id, first or last: ", ["id", "first", "last"])
        key_map = {
            "id":    lambda r: r[0],
            "first": lambda r: str(r[1]).lower(),
            "last":  lambda r: str(r[2]).lower(),
        }
        self.printer.print_table("Sorted Teachers",
            ["ID", "First Name", "Last Name", "Email",
             "Phone Number", "Department"],
            sorted(rows, key=key_map[choice]))

    # COURSES

    def add_course(self):
        # Collect course details → save to database
        print("\n--- Add Course ---")
        course_name    = self.validator.get_non_empty_string("Course name: ")
        course_code    = self.validator.get_course_code("Course code: ")
        teacher_id     = self.validator.get_positive_int("Teacher ID: ")
        course_credits = self.validator.get_positive_int("Credits (1-10): ")
        result = self.db.execute_procedure("sp_add_course",
            [course_name, course_code, teacher_id, course_credits])
        if result:
            console.print("[green]Course added successfully.[/green]")

    def view_courses(self):
        # Get all courses from database and print as table
        rows = self.db.execute_procedure("sp_get_all_courses", fetch=True)
        if rows is None:
            return []
        self.printer.print_table("Courses",
            ["ID", "Course Name", "Course Code", "Teacher ID", "Credits"], rows)
        return rows

    def update_course(self):
        # Ask for course ID then new values — update in database
        print("\n--- Update Course ---")
        course_id      = self.validator.get_positive_int("Course ID: ")
        course_name    = self.validator.get_non_empty_string("New course name: ")
        course_code    = self.validator.get_course_code("New course code: ")
        teacher_id     = self.validator.get_positive_int("New teacher ID: ")
        course_credits = self.validator.get_positive_int("New credits: ")
        result = self.db.execute_procedure("sp_update_course",
            [course_id, course_name, course_code, teacher_id, course_credits])
        if result:
            rprint("[green]Course updated successfully.[/green]")

    def delete_course(self):
        # Ask for course ID → confirm → delete from database
        print("\n--- Delete Course ---")
        course_id = self.validator.get_positive_int("Course ID: ")
        if input("Are you sure? (yes/no): ").strip().lower() != "yes":
            print("Delete cancelled.")
            return
        if self.db.execute_procedure("sp_delete_course", [course_id]):
            console.print("[green]Course deleted successfully.[/green]")

    def search_courses(self):
        # Get all courses → keep rows where keyword matches name or code
        print("\n--- Search Courses ---")
        rows = self.db.execute_procedure("sp_get_all_courses", fetch=True)
        if not rows:
            print("No courses found.")
            return
        keyword = input("Search by name or code: ").strip().lower()
        found = [r for r in rows if keyword in f"{r[1]} {r[2]}".lower()]
        self.printer.print_table("Search Results",
            ["ID", "Course Name", "Course Code", "Teacher ID", "Credits"], found)

    def sort_courses(self):
        # Get all courses → sort by chosen field
        print("\n--- Sort Courses ---")
        rows = self.db.execute_procedure("sp_get_all_courses", fetch=True)
        if not rows:
            print("No courses found.")
            return
        choice = self.validator.get_sort_choice(
            "Sort by id, name or code: ", ["id", "name", "code"])
        key_map = {
            "id":   lambda r: r[0],
            "name": lambda r: str(r[1]).lower(),
            "code": lambda r: str(r[2]).lower(),
        }
        self.printer.print_table("Sorted Courses",
            ["ID", "Course Name", "Course Code", "Teacher ID", "Credits"],
            sorted(rows, key=key_map[choice]))

    # REGISTRATIONS

    def add_registration(self):
        # Ask for student ID and course ID → save registration
        print("\n--- Add Registration ---")
        student_id        = self.validator.get_positive_int("Student ID: ")
        course_id         = self.validator.get_positive_int("Course ID: ")
        registration_date = self.validator.get_date("Registration date (YYYY-MM-DD): ")
        result = self.db.execute_procedure("sp_add_registration",
            [student_id, course_id, registration_date])
        if result:
            console.print("[green]Registration added successfully.[/green]")

    def view_registrations(self):
        # Get all registrations from database and print as table
        rows = self.db.execute_procedure("sp_get_all_registrations", fetch=True)
        if rows is None:
            return []
        self.printer.print_table("Registrations",
            ["ID", "Student ID", "Course ID", "Registration Date"], rows)
        return rows

    def update_registration(self):
        # Ask for registration ID then new values — update in database
        print("\n--- Update Registration ---")
        registration_id   = self.validator.get_positive_int("Registration ID: ")
        student_id        = self.validator.get_positive_int("New student ID: ")
        course_id         = self.validator.get_positive_int("New course ID: ")
        registration_date = self.validator.get_date("New date (YYYY-MM-DD): ")
        result = self.db.execute_procedure("sp_update_registration",
            [registration_id, student_id, course_id, registration_date])
        if result:
            console.print("[green]Registration updated successfully.[/green]")

    def delete_registration(self):
        # Ask for registration ID → confirm → delete from database
        print("\n--- Delete Registration ---")
        registration_id = self.validator.get_positive_int("Registration ID: ")
        if input("Are you sure? (yes/no): ").strip().lower() != "yes":
            print("Delete cancelled.")
            return
        if self.db.execute_procedure("sp_delete_registration", [registration_id]):
            console.print("[green]Registration deleted successfully.[/green]")

    # ATTENDANCE

    def add_attendance(self):
        # Ask for student ID, course ID, date and status → save
        print("\n--- Add Attendance ---")
        student_id      = self.validator.get_positive_int("Student ID: ")
        course_id       = self.validator.get_positive_int("Course ID: ")
        attendance_date = self.validator.get_date("Attendance date (YYYY-MM-DD): ")
        status          = self.validator.get_attendance_status("Status (Present/Absent/Late): ")
        result = self.db.execute_procedure("sp_add_attendance",
            [student_id, course_id, attendance_date, status])
        if result:
            console.print("[green]Attendance added successfully.[/green]")

    def view_attendance(self):
        # Get all attendance records and print as table
        rows = self.db.execute_procedure("sp_get_all_attendance", fetch=True)
        if rows is None:
            return []
        self.printer.print_table("Attendance",
            ["ID", "Student ID", "Course ID", "Date", "Status"], rows)
        return rows

    def update_attendance(self):
        # Ask for attendance ID then new values — update in database
        print("\n--- Update Attendance ---")
        attendance_id   = self.validator.get_positive_int("Attendance ID: ")
        student_id      = self.validator.get_positive_int("New student ID: ")
        course_id       = self.validator.get_positive_int("New course ID: ")
        attendance_date = self.validator.get_date("New date (YYYY-MM-DD): ")
        status          = self.validator.get_attendance_status("New status (Present/Absent/Late): ")
        result = self.db.execute_procedure("sp_update_attendance",
            [attendance_id, student_id, course_id, attendance_date, status])
        if result:
            console.print("[green]Attendance updated successfully.[/green]")

    def delete_attendance(self):
        # Ask for attendance ID → confirm → delete from database
        print("\n--- Delete Attendance ---")
        attendance_id = self.validator.get_positive_int("Attendance ID: ")
        if input("Are you sure? (yes/no): ").strip().lower() != "yes":
            print("Delete cancelled.")
            return
        if self.db.execute_procedure("sp_delete_attendance", [attendance_id]):
            console.print("[green]Attendance deleted successfully.[/green]")

    # GRADES

    def add_grade(self):
        # Ask for student ID, course ID, grade and date → save
        print("\n--- Add Grade ---")
        student_id  = self.validator.get_positive_int("Student ID: ")
        course_id   = self.validator.get_positive_int("Course ID: ")
        grade_value = self.validator.get_grade_value("Grade (A/B/C/D/F): ")
        grade_date  = self.validator.get_date("Grade date (YYYY-MM-DD): ")
        result = self.db.execute_procedure("sp_add_grade",
            [student_id, course_id, grade_value, grade_date])
        if result:
            console.print("[green]Grade added successfully.[/green]")

    def view_grades(self):
        # Get all grades from database and print as table
        rows = self.db.execute_procedure("sp_get_all_grades", fetch=True)
        if rows is None:
            return []
        self.printer.print_table("Grades",
            ["ID", "Student ID", "Course ID", "Grade", "Date"], rows)
        return rows

    def update_grade(self):
        # Ask for grade ID then new values — update in database
        print("\n--- Update Grade ---")
        grade_id    = self.validator.get_positive_int("Grade ID: ")
        student_id  = self.validator.get_positive_int("New student ID: ")
        course_id   = self.validator.get_positive_int("New course ID: ")
        grade_value = self.validator.get_grade_value("New grade (A/B/C/D/F): ")
        grade_date  = self.validator.get_date("New grade date (YYYY-MM-DD): ")
        result = self.db.execute_procedure("sp_update_grade",
            [grade_id, student_id, course_id, grade_value, grade_date])
        if result:
            console.print("[green]Grade updated successfully.[/green]")

    def delete_grade(self):
        # Ask for grade ID → confirm → delete from database
        print("\n--- Delete Grade ---")
        grade_id = self.validator.get_positive_int("Grade ID: ")
        if input("Are you sure? (yes/no): ").strip().lower() != "yes":
            print("Delete cancelled.")
            return
        if self.db.execute_procedure("sp_delete_grade", [grade_id]):
            console.print("[green]Grade deleted successfully.[/green]")

    # MENUS

    def show_menu(self):
        # Main admin menu — keeps running until user picks Exit (R9)
        while True:
            print("\n========== ADMIN MENU ==========")
            print("1. Manage Students")
            print("2. Manage Teachers")
            print("3. Manage Courses")
            print("4. Manage Registrations")
            print("5. Manage Attendance")
            print("6. Manage Grades")
            print("0. Exit")
            choice = self.validator.get_menu_choice("Choose option: ",
                ["1", "2", "3", "4", "5", "6", "0"])
            match choice:
                case "1": self._student_menu()
                case "2": self._teacher_menu()
                case "3": self._course_menu()
                case "4": self._registration_menu()
                case "5": self._attendance_menu()
                case "6": self._grade_menu()
                case "0": break

    def _student_menu(self):
        while True:
            print("\n===== STUDENT MENU =====")
            print("1. Add student")
            print("2. View students")
            print("3. Update student")
            print("4. Delete student")
            print("5. Search student")
            print("6. Sort student")
            print("0. Back")
            choice = self.validator.get_menu_choice("Choose option: ",
                ["1", "2", "3", "4", "5", "6", "0"])
            match choice:
                case "1": self.add_student()
                case "2": self.view_students()
                case "3": self.update_student()
                case "4": self.delete_student()
                case "5": self.search_students()
                case "6": self.sort_students()
                case "0": break

    def _teacher_menu(self):
        while True:
            print("\n===== TEACHER MENU =====")
            print("1. Add teacher")
            print("2. View teachers")
            print("3. Update teacher")
            print("4. Delete teacher")
            print("5. Search teacher")
            print("6. Sort teachers")
            print("0. Back")
            choice = self.validator.get_menu_choice("Choose option: ",
                ["1", "2", "3", "4", "5", "6", "0"])
            match choice:
                case "1": self.add_teacher()
                case "2": self.view_teachers()
                case "3": self.update_teacher()
                case "4": self.delete_teacher()
                case "5": self.search_teachers()
                case "6": self.sort_teachers()
                case "0": break

    def _course_menu(self):
        while True:
            print("\n===== COURSE MENU =====")
            print("1. Add course")
            print("2. View courses")
            print("3. Update course")
            print("4. Delete course")
            print("5. Search course")
            print("6. Sort courses")
            print("0. Back")
            choice = self.validator.get_menu_choice("Choose option: ",
                ["1", "2", "3", "4", "5", "6", "0"])
            match choice:
                case "1": self.add_course()
                case "2": self.view_courses()
                case "3": self.update_course()
                case "4": self.delete_course()
                case "5": self.search_courses()
                case "6": self.sort_courses()
                case "0": break

    def _registration_menu(self):
        while True:
            print("\n===== REGISTRATION MENU =====")
            print("1. Add registration")
            print("2. View registrations")
            print("3. Update registration")
            print("4. Delete registration")
            print("0. Back")
            choice = self.validator.get_menu_choice("Choose option: ",
                ["1", "2", "3", "4", "0"])
            match choice:
                case "1": self.add_registration()
                case "2": self.view_registrations()
                case "3": self.update_registration()
                case "4": self.delete_registration()
                case "0": break

    def _attendance_menu(self):
        while True:
            print("\n===== ATTENDANCE MENU =====")
            print("1. Add attendance")
            print("2. View attendance")
            print("3. Update attendance")
            print("4. Delete attendance")
            print("0. Back")
            choice = self.validator.get_menu_choice("Choose option: ",
                ["1", "2", "3", "4", "0"])
            match choice:
                case "1": self.add_attendance()
                case "2": self.view_attendance()
                case "3": self.update_attendance()
                case "4": self.delete_attendance()
                case "0": break

    def _grade_menu(self):
        while True:
            print("\n===== GRADE MENU =====")
            print("1. Add grade")
            print("2. View grades")
            print("3. Update grade")
            print("4. Delete grade")
            print("0. Back")
            choice = self.validator.get_menu_choice("Choose option: ",
                ["1", "2", "3", "4", "0"])
            match choice:
                case "1": self.add_grade()
                case "2": self.view_grades()
                case "3": self.update_grade()
                case "4": self.delete_grade()
                case "0": break


# ── TEACHER CLASS ─────────────────────────────────────────────────────────────

class Teacher:
    # Teacher role has limited permissions
    # Teachers can manage attendance and grades for their course only

    def __init__(self, db, course_id):
        self.db = db
        self.course_id = course_id      # teacher is limited to this course only
        self.validator = InputValidator()
        self.printer = TablePrinter()

    def view_my_profile(self):
        # Get all teachers → filter to show only this teacher's record
        rows = self.db.execute_procedure("sp_get_all_teachers", fetch=True)
        if rows is None:
            return
        filtered = [r for r in rows if int(r[0]) == int(self.course_id)]
        self.printer.print_table("My Profile",
            ["ID", "First Name", "Last Name", "Email",
             "Phone Number", "Department"], filtered)

    def view_my_course(self):
        # Get all courses → filter to show only this teacher's course
        rows = self.db.execute_procedure("sp_get_all_courses", fetch=True)
        if rows is None:
            return
        filtered = [r for r in rows if int(r[0]) == int(self.course_id)]
        self.printer.print_table("My Course",
            ["ID", "Course Name", "Course Code", "Teacher ID", "Credits"], filtered)

    def view_students(self):
        # Get all students — read-only for teacher
        rows = self.db.execute_procedure("sp_get_all_students", fetch=True)
        if rows is None:
            return []
        self.printer.print_table("Students",
            ["ID", "First Name", "Last Name", "Date of Birth",
             "Gender", "Email", "Phone Number", "Address"], rows)
        return rows

    def search_students(self):
        # Search students by name, email or ID — read-only for teacher
        print("\n--- Search Students ---")
        rows = self.db.execute_procedure("sp_get_all_students", fetch=True)
        if not rows:
            print("No students found.")
            return
        print("Search by: 1. Name/Email   2. ID")
        choice = self.validator.get_menu_choice("Choose: ", ["1", "2"])
        if choice == "1":
            keyword = input("Enter name or email: ").strip().lower()
            found = [r for r in rows if keyword in f"{r[1]} {r[2]} {r[5]}".lower()]
        else:
            student_id = input("Enter student ID: ").strip()
            if not student_id.isdigit():
                print("ID must be a number.")
                return
            found = [r for r in rows if int(r[0]) == int(student_id)]
        if not found:
            print("No students found.")
            return
        self.printer.print_table("Search Results",
            ["ID", "First Name", "Last Name", "Date of Birth",
             "Gender", "Email", "Phone Number", "Address"], found)

    def sort_students(self):
        # Get all students → sort by chosen field — read-only
        print("\n--- Sort Students ---")
        rows = self.db.execute_procedure("sp_get_all_students", fetch=True)
        if not rows:
            print("No students found.")
            return
        choice = self.validator.get_sort_choice(
            "Sort by id, first or last: ", ["id", "first", "last"])
        key_map = {
            "id":    lambda r: r[0],
            "first": lambda r: str(r[1]).lower(),
            "last":  lambda r: str(r[2]).lower(),
        }
        self.printer.print_table("Sorted Students",
            ["ID", "First Name", "Last Name", "Date of Birth",
             "Gender", "Email", "Phone Number", "Address"],
            sorted(rows, key=key_map[choice]))

    def view_teacher_registrations(self):
        # Get all registrations → filter to show only this teacher's course
        rows = self.db.execute_procedure("sp_get_all_registrations", fetch=True)
        if rows is None:
            return
        filtered = [r for r in rows if int(r[2]) == int(self.course_id)]
        self.printer.print_table("Course Registrations",
            ["ID", "Student ID", "Course ID", "Registration Date"], filtered)

    def add_teacher_attendance(self):
        # Add attendance — course_id comes from self.course_id
        student_id      = self.validator.get_positive_int("Student ID: ")
        attendance_date = self.validator.get_date("Attendance date (YYYY-MM-DD): ")
        status          = self.validator.get_attendance_status("Status (Present/Absent/Late): ")
        result = self.db.execute_procedure("sp_add_attendance",
            [student_id, self.course_id, attendance_date, status])
        if result:
            console.print("[green]Attendance added successfully.[/green]")

    def view_teacher_attendance(self):
        # Get all attendance → filter to show only this teacher's course
        rows = self.db.execute_procedure("sp_get_all_attendance", fetch=True)
        if rows is None:
            return
        filtered = [r for r in rows if int(r[2]) == int(self.course_id)]
        self.printer.print_table("Course Attendance",
            ["ID", "Student ID", "Course ID", "Date", "Status"], filtered)

    def update_teacher_attendance(self):
        # Ask for attendance ID then new values — update in database
        print("\n--- Update Attendance ---")
        attendance_id   = self.validator.get_positive_int("Attendance ID: ")
        student_id      = self.validator.get_positive_int("New student ID: ")
        attendance_date = self.validator.get_date("New date (YYYY-MM-DD): ")
        status          = self.validator.get_attendance_status("New status (Present/Absent/Late): ")
        result = self.db.execute_procedure("sp_update_attendance",
            [attendance_id, student_id, self.course_id, attendance_date, status])
        if result:
            console.print("[green]Attendance updated successfully.[/green]")

    def delete_teacher_attendance(self):
        # Ask for attendance ID → confirm → delete from database
        print("\n--- Delete Attendance ---")
        attendance_id = self.validator.get_positive_int("Attendance ID: ")
        if input("Are you sure? (yes/no): ").strip().lower() != "yes":
            print("Delete cancelled.")
            return
        if self.db.execute_procedure("sp_delete_attendance", [attendance_id]):
            console.print("[green]Attendance deleted successfully.[/green]")

    def add_teacher_grade(self):
        # Add grade — course_id comes from self.course_id
        student_id  = self.validator.get_positive_int("Student ID: ")
        grade_value = self.validator.get_grade_value("Grade (A/B/C/D/F): ")
        grade_date  = self.validator.get_date("Grade date (YYYY-MM-DD): ")
        result = self.db.execute_procedure("sp_add_grade",
            [student_id, self.course_id, grade_value, grade_date])
        if result:
            console.print("[green]Grade added successfully.[/green]")

    def view_teacher_grades(self):
        # Get all grades → filter to show only this teacher's course
        rows = self.db.execute_procedure("sp_get_all_grades", fetch=True)
        if rows is None:
            return
        filtered = [r for r in rows if int(r[2]) == int(self.course_id)]
        self.printer.print_table("Course Grades",
            ["ID", "Student ID", "Course ID", "Grade", "Date"], filtered)

    def update_teacher_grade(self):
        # Ask for grade ID then new values — update in database
        print("\n--- Update Grade ---")
        grade_id    = self.validator.get_positive_int("Grade ID: ")
        student_id  = self.validator.get_positive_int("New student ID: ")
        grade_value = self.validator.get_grade_value("New grade (A/B/C/D/F): ")
        grade_date  = self.validator.get_date("New grade date (YYYY-MM-DD): ")
        result = self.db.execute_procedure("sp_update_grade",
            [grade_id, student_id, self.course_id, grade_value, grade_date])
        if result:
            console.print("[green]Grade updated successfully.[/green]")

    def delete_teacher_grade(self):
        # Ask for grade ID → confirm → delete from database
        print("\n--- Delete Grade ---")
        grade_id = self.validator.get_positive_int("Grade ID: ")
        if input("Are you sure? (yes/no): ").strip().lower() != "yes":
            print("Delete cancelled.")
            return
        if self.db.execute_procedure("sp_delete_grade", [grade_id]):
            console.print("[green]Grade deleted successfully.[/green]")

    def show_menu(self):
        # Teacher menu — keeps running until user picks Exit (R9)
        while True:
            print("\n========== TEACHER MENU ==========")
            print("1. View My Profile")
            print("2. View My Course")
            print("3. Manage Students")
            print("4. View Registrations")
            print("5. Manage Attendance")
            print("6. Manage Grades")
            print("0. Exit")
            choice = self.validator.get_menu_choice("Choose option: ",
                ["1", "2", "3", "4", "5", "6", "0"])
            match choice:
                case "1": self.view_my_profile()
                case "2": self.view_my_course()
                case "3": self._student_menu()
                case "4": self.view_teacher_registrations()
                case "5": self._attendance_menu()
                case "6": self._grade_menu()
                case "0": break

    def _student_menu(self):
        # Sub-menu for students — view, search, sort only (read-only)
        while True:
            print("\n===== STUDENT MENU =====")
            print("1. View Students")
            print("2. Search Students")
            print("3. Sort Students")
            print("0. Back")
            choice = self.validator.get_menu_choice("Choose option: ",
                ["1", "2", "3", "0"])
            match choice:
                case "1": self.view_students()
                case "2": self.search_students()
                case "3": self.sort_students()
                case "0": break

    def _attendance_menu(self):
        # Sub-menu for attendance — full CRUD for teacher's course only
        while True:
            print("\n===== ATTENDANCE MENU =====")
            print("1. Add Attendance")
            print("2. View Attendance")
            print("3. Update Attendance")
            print("4. Delete Attendance")
            print("0. Back")
            choice = self.validator.get_menu_choice("Choose option: ",
                ["1", "2", "3", "4", "0"])
            match choice:
                case "1": self.add_teacher_attendance()
                case "2": self.view_teacher_attendance()
                case "3": self.update_teacher_attendance()
                case "4": self.delete_teacher_attendance()
                case "0": break

    def _grade_menu(self):
        # Sub-menu for grades — full CRUD for teacher's course only
        while True:
            print("\n===== GRADE MENU =====")
            print("1. Add Grade")
            print("2. View Grades")
            print("3. Update Grade")
            print("4. Delete Grade")
            print("0. Back")
            choice = self.validator.get_menu_choice("Choose option: ",
                ["1", "2", "3", "4", "0"])
            match choice:
                case "1": self.add_teacher_grade()
                case "2": self.view_teacher_grades()
                case "3": self.update_teacher_grade()
                case "4": self.delete_teacher_grade()
                case "0": break


# ── STUDENT CLASS ─────────────────────────────────────────────────────────────

class Student:
    # Student role has read-only access to their own data only

    def __init__(self, db, student_id):
        self.db = db
        self.student_id = student_id    # student sees only their own data
        self.validator = InputValidator()
        self.printer = TablePrinter()

    def view_my_student(self):
        # Get all students → filter to show only this student's record
        rows = self.db.execute_procedure("sp_get_all_students", fetch=True)
        if rows is None:
            return
        filtered = [r for r in rows if int(r[0]) == int(self.student_id)]
        self.printer.print_table("My Profile",
            ["ID", "First Name", "Last Name", "Date of Birth",
             "Gender", "Email", "Phone", "Address"], filtered)

    def view_my_attendance(self):
        # Get all attendance → filter to show only this student's records
        rows = self.db.execute_procedure("sp_get_all_attendance", fetch=True)
        if not rows:
            print("No attendance records found.")
            return
        filtered = [r for r in rows if r[1] == self.student_id]
        self.printer.print_table("My Attendance",
            ["ID", "Student ID", "Course ID", "Date", "Status"], filtered)

    def view_my_grades(self):
        # Get all grades → filter to show only this student's records
        rows = self.db.execute_procedure("sp_get_all_grades", fetch=True)
        if not rows:
            print("No grade records found.")
            return
        filtered = [r for r in rows if r[1] == self.student_id]
        self.printer.print_table("My Grades",
            ["ID", "Student ID", "Course ID", "Grade", "Date"], filtered)

    def view_my_registrations(self):
        # Get all registrations → filter to show only this student's records
        rows = self.db.execute_procedure("sp_get_all_registrations", fetch=True)
        if rows is None:
            return
        filtered = [r for r in rows if r[1] == self.student_id]
        self.printer.print_table("My Registrations",
            ["ID", "Student ID", "Course ID", "Registration Date"], filtered)

    def show_menu(self):
        # Student menu — keeps running until user picks Exit (R9)
        while True:
            print("\n========== STUDENT MENU ==========")
            print("1. View My Profile")
            print("2. View My Attendance")
            print("3. View My Grades")
            print("4. View My Registrations")
            print("0. Exit")
            choice = self.validator.get_menu_choice("Choose option: ",
                ["1", "2", "3", "4", "0"])
            match choice:
                case "1": self.view_my_student()
                case "2": self.view_my_attendance()
                case "3": self.view_my_grades()
                case "4": self.view_my_registrations()
                case "0": break
