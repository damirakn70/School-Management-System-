# AuthService — handles login for admin, teacher and student roles
# Implements authentication (O1) and role-based access control (O6)

from config import (ADMIN_USERNAME, ADMIN_PASSWORD,
                    TEACHER_USERNAME, TEACHER_PASSWORD,
                    STUDENT_USERNAME, STUDENT_PASSWORD)
from validators import InputValidator

try:
    from rich.console import Console
    console = Console(force_terminal=True)
except ImportError:
    class Console:
        def print(self, msg, **kwargs):
            import re
            print(re.sub(r"\[.*?\]", "", msg))
    console = Console()


class AuthService:
    # Handles authentication and role-based login
    # Different users receive different access permissions

    @staticmethod
    def login():
        # Prompt login — returns (role, user_id, course_id)
        # Returns (None, None, None) if all 3 attempts fail
        print("\n========== SYSTEM LOGIN ==========")

        # Give user 3 attempts to enter correct credentials
        for attempt in range(3):
            username = input("Username: ").strip()
            password = input("Password: ").strip()

            # Admin — full CRUD access to everything
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                console.print("[green]Admin login successful.[/green]")
                return "admin", None, None

            # Teacher — limited to their own course only
            elif username == TEACHER_USERNAME and password == TEACHER_PASSWORD:
                teacher_id = InputValidator.get_positive_int("Enter your teacher ID: ")
                course_id  = InputValidator.get_positive_int("Enter your course ID: ")
                console.print("[green]Teacher login successful.[/green]")
                return "teacher", teacher_id, course_id

            # Student — read-only access to own data only
            elif username == STUDENT_USERNAME and password == STUDENT_PASSWORD:
                student_id = InputValidator.get_positive_int("Enter your student ID: ")
                console.print("[green]Student login successful.[/green]")
                return "student", student_id, None

            # Wrong credentials — show remaining attempts
            remaining = 2 - attempt
            console.print(f"[red]Incorrect login details.[/red] Attempts left: {remaining}")

        # All 3 attempts used — exit login
        console.print("[red]Too many failed attempts. Exiting.[/red]")
        return None, None, None
