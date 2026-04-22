import sqlite3
import os
import random
import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "game_data.db")

GAMES = [
    {"name": "Cyber-Grid Snake", "score_range": (1, 35), "duration_range": (15, 180)},
    {"name": "Cyber Dash", "score_range": (5, 100), "duration_range": (5, 90)},
    {"name": "Cyber Reaction", "score_range": (10, 150), "duration_range": (20, 100)},
    {"name": "Data Drop", "score_range": (50, 1200), "duration_range": (30, 300)},
    {"name": "Cyber Breakout", "score_range": (20, 450), "duration_range": (30, 200)},
    {"name": "Cyber Pong", "score_range": (0, 7), "duration_range": (45, 180)},
]

def generate_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Ensure table exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_name TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            duration_seconds INTEGER NOT NULL,
            score INTEGER NOT NULL,
            ab_variant TEXT NOT NULL DEFAULT 'Control'
        )
    ''')
    
    now = datetime.datetime.now()
    records = []
    
    # Generate 300 fake sessions over the past 30 days
    for _ in range(300):
        game = random.choice(GAMES)
        
        # Random time in the past 30 days
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        
        end_time = now - datetime.timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        duration = random.randint(*game["duration_range"])
        start_time = end_time - datetime.timedelta(seconds=duration)
        
        # Simulate a learning curve: scores increase as days_ago approaches 0
        learning_factor = 1.0 - (days_ago / 30.0) # 0.0 (oldest) to 1.0 (newest)
        
        min_score, max_score = game["score_range"]
        # Shift the scale towards max_score based on learning factor
        shift = int((max_score - min_score) * 0.5 * learning_factor)
        
        final_score = random.randint(min_score + shift, max_score)
        if game["name"] == "Cyber Dash": final_score = min(100, final_score)
        if game["name"] == "Cyber Pong": final_score = min(7, final_score)
        
        ab_variant = "Control"
        if game["name"] == "Cyber Reaction":
            ab_variant = random.choice(["Control", "Neon_High_Contrast"])
        elif game["name"] == "Cyber Dash":
            ab_variant = random.choice(["Control_Speed", "Slower_Start"])
            
            # Boost score artificially if Slower Start to simulate successful test
            if ab_variant == "Slower_Start":
                final_score = min(100, int(final_score * 1.15))

        records.append((
            game["name"],
            start_time.isoformat(),
            end_time.isoformat(),
            duration,
            final_score,
            ab_variant
        ))
    
    # Insert records
    cursor.executemany('''
        INSERT INTO game_sessions (game_name, start_time, end_time, duration_seconds, score, ab_variant)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', records)
    
    conn.commit()
    conn.close()
    print("Successfully inserted 300 mock game sessions into game_data.db!")

if __name__ == "__main__":
    generate_data()
