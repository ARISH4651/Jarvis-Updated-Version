import sqlite3
import os

class MemoryCore:
    def __init__(self, db_path="jarvis_memory.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initializes the database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Preferences Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # Tasks Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()

    def set_preference(self, key, value):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO preferences (key, value) VALUES (?, ?)', (key, value))
        conn.commit()
        conn.close()
        return f"Preference '{key}' set to '{value}'."

    def get_preference(self, key):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM preferences WHERE key = ?', (key,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def add_task(self, description):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO tasks (description) VALUES (?)', (description,))
        conn.commit()
        conn.close()
        return "Task added to memory."

    def get_tasks(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, description, status FROM tasks WHERE status != "completed"')
        tasks = cursor.fetchall()
        conn.close()
        return [{"id": t[0], "description": t[1], "status": t[2]} for t in tasks]

    # Context Memory (Transient)
    context = {}

    def set_context(self, key, value):
        self.context[key] = value

    def get_context(self, key):
        return self.context.get(key)
