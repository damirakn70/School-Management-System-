# Input validation for all user inputs in the system
# All methods are static — no object state is required

from datetime import datetime
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)


class InputValidator:
    # This class validates all user input before it is processed
    # Validation helps prevent invalid or incorrect data entry
    # Static methods are used because object state is not required

    @staticmethod
    def get_non_empty_string(prompt):
        # Check text input, must contain letters only and cannot be empty
        while True:
            value = input(prompt).strip()
            if not value:
                print("Input cannot be empty.")
                continue
            if not value.replace(" ", "").isalpha():
                print("Only letters are allowed.")
                continue
            return value.title()

    @staticmethod
    def get_int(prompt):
        # Check that input is a valid whole number
        while True:
            value = input(prompt).strip()
            try:
                return int(value)
            except ValueError:
                print("Please enter a valid number.")

    @staticmethod
    def get_positive_int(prompt):
        # Check that input is a number greater than 0
        while True:
            number = InputValidator.get_int(prompt)
            if number > 0:
                return number
            print("Number must be greater than 0.")

    @staticmethod
    def get_address(prompt):
        # Check address format, cannot be empty
        while True:
            address = input(prompt).strip()
            if not address:
                print("Address cannot be empty.")
                continue
            return address.title()

    @staticmethod
    def get_email(prompt):
        # Check email format, must have @ and a dot, no spaces
        while True:
            email = input(prompt).strip()
            if "@" in email and "." in email and " " not in email:
                return email
            print("Please enter a valid email address.")

    @staticmethod
    def get_birth_date(prompt):
        # Check date of birth, format must be YYYY-MM-DD and must be in the past
        while True:
            value = input(prompt).strip()
            try:
                entered_date = datetime.strptime(value, "%Y-%m-%d").date()
                today = datetime.today().date()
                if entered_date >= today:
                    print("Date cannot be today or a future date.")
                    continue
                return value
            except ValueError:
                print("Use this format: YYYY-MM-DD")

    @staticmethod
    def get_date(prompt):
        # Check any date, format must be YYYY-MM-DD
        while True:
            value = input(prompt).strip()
            try:
                datetime.strptime(value, "%Y-%m-%d")
                return value
            except ValueError:
                print("Use this format: YYYY-MM-DD")

    @staticmethod
    def get_gender(prompt):
        # Check gender — only Male, Female, Other are accepted
        while True:
            gender = input(prompt).strip().capitalize()
            if gender in ["Male", "Female", "Other"]:
                return gender
            print("Please enter Male, Female or Other.")

    @staticmethod
    def get_attendance_status(prompt):
        # Check attendance status — only Present, Absent, Late are accepted
        while True:
            status = input(prompt).strip().capitalize()
            if status in ["Present", "Absent", "Late"]:
                return status
            print("Please enter Present, Absent or Late.")

    @staticmethod
    def get_grade_value(prompt):
        # Check grade — only A, B, C, D, F are accepted
        while True:
            value = input(prompt).strip().upper()
            if value in ["A", "B", "C", "D", "F"]:
                return value
            print("Please enter A, B, C, D or F.")

    @staticmethod
    def get_menu_choice(prompt, valid_choices):
        # Check menu input — only options from the list are accepted
        while True:
            choice = input(prompt).strip()
            if choice in valid_choices:
                return choice
            print("Invalid option. Please try again.")

    @staticmethod
    def get_sort_choice(prompt, choices):
        # Check sort field — only the given choices are accepted
        while True:
            value = input(prompt).strip().lower()
            if value in choices:
                return value
            print(f"Choose one of these: {', '.join(choices)}")

    @staticmethod
    def get_phone_number(prompt):
        # Check Kazakhstan phone number formats
        # Supports +7XXXXXXXXXX and 8XXXXXXXXXX formats
        while True:
            phone = input(prompt).strip()
            phone = phone.replace(" ", "").replace("-", "")
            if phone.startswith("+7") and len(phone) == 12 and phone[1:].isdigit():
                return phone
            if phone.startswith("8") and len(phone) == 11 and phone.isdigit():
                return phone
            print("Please enter a valid phone number (+7XXXXXXXXXX or 8XXXXXXXXXX).")

    @staticmethod
    def get_course_code(prompt):
        # Validate course code like MATH101 or CS202
        # Must contain both letters and numbers
        while True:
            code = input(prompt).strip().upper()
            code = code.replace(" ", "")
            has_letters = any(char.isalpha() for char in code)
            has_numbers = any(char.isdigit() for char in code)
            if not has_letters or not has_numbers:
                print("Course code must contain letters and numbers.")
                continue
            return code
