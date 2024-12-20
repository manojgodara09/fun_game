import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Create user_data table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_data (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            balance FLOAT NOT NULL,
            logged_in BOOLEAN DEFAULT FALSE
        )
    """)
    
    # Create user_game_history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_game_history (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            game_name TEXT NOT NULL,
            before_balance FLOAT NOT NULL,
            after_balance FLOAT NOT NULL,
            multiplier FLOAT NOT NULL,
            play_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user_data (id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
