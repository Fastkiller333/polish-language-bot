"""
Database module for Learning Polish Bot
Manages user data and word progress
"""

import sqlite3
from datetime import datetime
from typing import Optional, List


class Database:
    def __init__(self, db_path: str = "polish_bot.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Create database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                daily_notifications INTEGER DEFAULT 1,
                created_at TEXT,
                timezone TEXT DEFAULT 'Europe/Warsaw'
            )
        ''')
        
        # User word history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_word_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                word_id INTEGER,
                sent_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                UNIQUE(user_id, word_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id: int, username: str = None) -> bool:
        """Add new user or update existing"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, username, created_at)
                VALUES (?, ?, ?)
            ''', (user_id, username, datetime.now().isoformat()))
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error adding user: {e}")
            return False
        finally:
            conn.close()
    
    def user_exists(self, user_id: int) -> bool:
        """Check if user exists"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
        exists = cursor.fetchone() is not None
        
        conn.close()
        return exists
    
    def get_user_sent_words(self, user_id: int) -> List[int]:
        """Get list of word IDs already sent to user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT word_id FROM user_word_history
            WHERE user_id = ?
            ORDER BY sent_at
        ''', (user_id,))
        
        word_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return word_ids
    
    def add_word_to_history(self, user_id: int, word_id: int) -> bool:
        """Mark word as sent to user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO user_word_history (user_id, word_id, sent_at)
                VALUES (?, ?, ?)
            ''', (user_id, word_id, datetime.now().isoformat()))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding word to history: {e}")
            return False
        finally:
            conn.close()
    
    def get_next_word_id(self, user_id: int, total_words: int = 300) -> int:
        """Get next word ID for user (0-299), reset if all sent"""
        sent_words = self.get_user_sent_words(user_id)
        
        # If all words sent, reset
        if len(sent_words) >= total_words:
            self.reset_user_progress(user_id)
            return 0
        
        # Find first word not sent
        for word_id in range(total_words):
            if word_id not in sent_words:
                return word_id
        
        return 0
    
    def reset_user_progress(self, user_id: int):
        """Reset user's word progress"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM user_word_history WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
    
    def toggle_notifications(self, user_id: int) -> bool:
        """Toggle daily notifications for user. Returns new state."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET daily_notifications = 1 - daily_notifications
            WHERE user_id = ?
        ''', (user_id,))
        
        cursor.execute('SELECT daily_notifications FROM users WHERE user_id = ?', (user_id,))
        new_state = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        return bool(new_state)
    
    def get_notifications_enabled(self, user_id: int) -> bool:
        """Check if user has notifications enabled"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT daily_notifications FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        conn.close()
        return bool(result[0]) if result else True
    
    def get_all_users_with_notifications(self) -> List[int]:
        """Get all user IDs with notifications enabled"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id FROM users WHERE daily_notifications = 1')
        user_ids = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return user_ids
    
    def get_user_progress(self, user_id: int, total_words: int = 300) -> dict:
        """Get user's learning progress"""
        sent_words = self.get_user_sent_words(user_id)
        
        return {
            'words_learned': len(sent_words),
            'total_words': total_words,
            'percentage': round((len(sent_words) / total_words) * 100, 1)
        }






