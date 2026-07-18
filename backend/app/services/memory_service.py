import sqlite3
import json
from typing import List, Dict
import os

class SQLiteMemoryManager:
    def __init__(self, db_path="chat_memory.db"):
        # Put the DB in the backend folder
        self.db_path = os.path.join(os.path.dirname(__file__), "..", db_path)
        self._init_db()

    def _init_db(self):
        """Creates the SQLite table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory (
                    session_id TEXT PRIMARY KEY,
                    history TEXT
                )
            """)

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """Retrieve session history from SQLite."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT history FROM memory WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
            return []
            
    def save_history(self, session_id: str, messages: List[Dict[str, str]]):
        """Overwrite session history in SQLite."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO memory (session_id, history) VALUES (?, ?)",
                (session_id, json.dumps(messages))
            )
            
    def add_exchange(self, session_id: str, user_query: str, assistant_reply: str):
        """Append a single Q&A exchange to the session memory."""
        history = self.get_history(session_id)
        history.append({"role": "user", "content": user_query})
        history.append({"role": "assistant", "content": assistant_reply})
        
        # Keep only the last 10 exchanges (20 messages) for "Short-Term Memory"
        if len(history) > 20:
            history = history[-20:]
            
        self.save_history(session_id, history)
        
    def clear_history(self, session_id: str):
        """Delete a specific session."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM memory WHERE session_id = ?", (session_id,))

# Singleton instance for the app
memory_manager = SQLiteMemoryManager()