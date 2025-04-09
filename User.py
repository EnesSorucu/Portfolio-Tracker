import sqlite3 as sql

class User:
    def __init__(self, user):
        self.user = user
        self.conn = sql.connect(f"{user}.db")  # Connect to the SQLite database
        self.cursor = self.conn.cursor()  # Cursor for executing SQL queries

    def tables(self):
        # Fetch and return all table names from the database
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [table[0] for table in self.cursor.fetchall()]

    def create_new_portfolio(self, name):
        # Create a new portfolio if it doesn't exist
        if name in self.tables():
            print(f"You have a portfolio named {name}")  # Notify user if portfolio exists
            return

        # SQL query to create a new portfolio table
        text = '''CREATE TABLE IF NOT EXISTS {} (
                    symbol TEXT,
                    name TEXT,
                    cost REAL,
                    quantity REAL, 
                    exchange TEXT,
                    market TEXT
                )'''
        text = text.format(name)  # Format table name into SQL query
        self.cursor.execute(text)
        self.conn.commit()
        print(f"{name} portfolio has been created successfully.")

    def delete_the_portfolio(self, name):
        # Delete a portfolio if it exists
        if name not in self.tables():
            print(f"Portfolio not found: Portfolios {self.tables()}")  # Notify if portfolio doesn't exist
            return
        self.cursor.execute(f"DROP TABLE {name}")  # Drop the table from the database
        self.conn.commit()  # Commit the changes
        print(f"Your {name} portfolio has been successfully deleted.")  # Success message

    def close_conn(self):
        # Commit and close the database connection
        self.conn.commit()
        self.conn.close()
        print("The database connection was closed.")  # Closing message

