import psycopg2

def init_db():
    conn = psycopg2.connect(
        dbname="koyebdb",
        user="koyeb-adm",
        password="MK59GFoIzBZb",
        host="ep-shy-frost-a12m58cj.ap-southeast-1.pg.koyeb.app",
        port="5432"
    )
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
            play_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
