import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name='notes.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def add_note(self, user_id, content):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO notes (user_id, content)
            VALUES (?, ?)
        ''', (user_id, content))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_user_notes(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, content, created_at 
            FROM notes 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        ''', (user_id,))
        return cursor.fetchall()
    
    def delete_note(self, user_id, note_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            DELETE FROM notes 
            WHERE id = ? AND user_id = ?
        ''', (note_id, user_id))
        self.conn.commit()
        return cursor.rowcount > 0