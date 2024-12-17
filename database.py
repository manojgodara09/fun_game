import sqlite3

def init_db():
    conn = sqlite3.connect("casino.db")
    cursor = conn.cursor()
    
    # Create user_data table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            balance FLOAT NOT NULL
        )
    """)
    
    # Create user_game_history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_game_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            game_name TEXT NOT NULL,
            before_balance FLOAT NOT NULL,
            after_balance FLOAT NOT NULL,
            multiplier FLOAT NOT NULL,
            play_time DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
