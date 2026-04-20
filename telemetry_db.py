import sqlite3
import os
import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "game_data.db")

class TelemetryDB:
    @staticmethod
    def setup():
        """Initialize the local SQLite database and create the games_sessions table if it doesn't exist."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_name TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                duration_seconds INTEGER NOT NULL,
                score INTEGER NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()

    @staticmethod
    def log_game(game_name: str, start_time: float, end_time: float, duration_seconds: int, score: int):
        """Log a completed game session into the database."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Convert unix timestamps to ISO format for easier reading
            start_iso = datetime.datetime.fromtimestamp(start_time).isoformat()
            end_iso = datetime.datetime.fromtimestamp(end_time).isoformat()
            
            cursor.execute('''
                INSERT INTO game_sessions (game_name, start_time, end_time, duration_seconds, score)
                VALUES (?, ?, ?, ?, ?)
            ''', (game_name, start_iso, end_iso, duration_seconds, int(score)))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error logging telemetry data: {e}")
