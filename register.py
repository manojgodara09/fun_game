import psycopg2
from passlib.context import CryptContext
import getpass
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Utility Functions
def add_user_to_database(username: str, password: str, balance: float):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    hashed_password = pwd_context.hash(password)
    try:
        cursor.execute("INSERT INTO user_data (username, password, balance) VALUES (%s, %s, %s)",
                       (username, hashed_password, balance))
        conn.commit()
        print(f"User {username} created successfully.")
    except psycopg2.IntegrityError:
        conn.rollback()
        print("Username already exists.")
    finally:
        conn.close()

def update_user_balance(username: str, new_balance: float):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("UPDATE user_data SET balance=%s WHERE username=%s", (new_balance, username))
    if cursor.rowcount == 0:
        print("User not found.")
    else:
        conn.commit()
        print(f"Balance for user {username} updated to {new_balance}.")
    conn.close()

def update_user_password(username: str, new_password: str):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    hashed_password = pwd_context.hash(new_password)
    cursor.execute("UPDATE user_data SET password=%s WHERE username=%s", (hashed_password, username))
    if cursor.rowcount == 0:
        print("User not found.")
    else:
        conn.commit()
        print(f"Password for user {username} updated successfully.")
    conn.close()

def delete_user(username: str):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_data WHERE username=%s", (username,))
    if cursor.rowcount == 0:
        print("User not found.")
    else:
        conn.commit()
        print(f"User {username} deleted successfully.")
    conn.close()

def view_users():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, balance, logged_in FROM user_data")
    users = cursor.fetchall()
    conn.close()
    if users:
        for user in users:
            print(f"ID: {user[0]}, Username: {user[1]}, Balance: {user[2]}, Logged In: {user[3]}")
    else:
        print("No users found.")

def get_user_game_record(username: str):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT game_name, before_balance, after_balance, multiplier, play_time
        FROM user_game_history
        WHERE user_id = (SELECT id FROM user_data WHERE username=%s)
    """, (username,))
    records = cursor.fetchall()
    conn.close()
    if records:
        for record in records:
            print(f"Game: {record[0]}, Before Balance: {record[1]}, After Balance: {record[2]}, Multiplier: {record[3]}, Play Time: {record[4]}")
    else:
        print("No game records found for user.")

def main():
    while True:
        print("\n1. Register a new user")
        print("2. Update user balance")
        print("3. Update user password")
        print("4. Delete user")
        print("5. View users")
        print("6. Get user game record")
        print("7. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            username = input("Enter username: ")
            password = getpass.getpass("Enter password: ")
            balance = float(input("Enter initial balance: "))
            add_user_to_database(username, password, balance)
        elif choice == '2':
            username = input("Enter username: ")
            new_balance = float(input("Enter new balance: "))
            update_user_balance(username, new_balance)
        elif choice == '3':
            username = input("Enter username: ")
            new_password = getpass.getpass("Enter new password: ")
            update_user_password(username, new_password)
        elif choice == '4':
            username = input("Enter username: ")
            delete_user(username)
        elif choice == '5':
            view_users()
        elif choice == '6':
            username = input("Enter username: ")
            get_user_game_record(username)
        elif choice == '7':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()