# DatabaseManager class — handles MySQL connection and stored procedure calls

import mysql.connector
from mysql.connector import Error

try:
    from rich.console import Console
    console = Console(force_terminal=True)
except ImportError:
    class Console:
        def print(self, msg, **kwargs):
            import re
            print(re.sub(r"\[.*?\]", "", msg))
    console = Console()


class DatabaseManager:
    # Manages MySQL database connection and stored procedure execution

    def __init__(self, config):
        self.config = config        # save connection details
        self.connection = None      # no connection open yet

    def connect(self):
        # Connect to MySQL database — returns True if successful
        try:
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                console.print("[green]Connected to MySQL successfully.[/green]")
                return True
        except Error as error:
            console.print(f"[red]Database connection error:[/red] {error}")
            return False

    def close(self):
        # Safely close the MySQL connection when program ends
        if self.connection and self.connection.is_connected():
            self.connection.close()
            console.print("[yellow]Database connection closed.[/yellow]")

    def execute_procedure(self, procedure_name, args=None, fetch=False):
        # Executes stored procedures for CRUD operations
        # fetch=True  → returns rows from SELECT queries
        # fetch=False → commits changes for INSERT/UPDATE/DELETE
        if not self.connection or not self.connection.is_connected():
            print("No database connection.")
            return None

        cursor = None
        try:
            cursor = self.connection.cursor()
            if args is None:
                args = []
            # Call the stored procedure with given arguments
            cursor.callproc(procedure_name, args)

            if fetch:
                # Collect and return all result rows
                results = []
                for result in cursor.stored_results():
                    results.extend(result.fetchall())
                return results

            # Save changes to the database
            self.connection.commit()
            return True

        except Error as error:
            print(f"Database procedure error in '{procedure_name}': {error}")
            return None

        finally:
            if cursor:
                cursor.close()
