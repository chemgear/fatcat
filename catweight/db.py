"""
Database operations for the cat weight tracking app.
"""
import sqlite3
import os
import datetime
from typing import List, Tuple, Optional, Dict, Any


class CatWeightDatabase:
    """Database handler for cat food weight tracking."""
    
    def __init__(self, db_path="/opt/db/fatcat.db"):
        """Initialize the database connection and create tables if they don't exist."""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._ensure_db_directory_exists()
        self.connect()
        self.create_tables()
        
    def _ensure_db_directory_exists(self):
        """Ensure the directory for the database file exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            
    def connect(self):
        """Connect to the SQLite database."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
    def create_tables(self):
        """Create necessary tables if they don't exist."""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS cat_weights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cat_name TEXT NOT NULL,
            date TEXT NOT NULL,
            initial_weight REAL NOT NULL,
            remaining_weight REAL,
            created_at TEXT NOT NULL
        )
        ''')
        self.conn.commit()
        
    def add_entry(self, cat_name: str, initial_weight: float, date: Optional[str] = None) -> int:
        """
        Add a new food weight entry for a cat.
        
        Args:
            cat_name: Name of the cat (Mittens, Cheddar, or Lola)
            initial_weight: Initial weight of the food bowl in grams
            date: Date of the entry in YYYY-MM-DD format (defaults to today)
            
        Returns:
            The ID of the newly created entry
        """
        if date is None:
            date = datetime.date.today().isoformat()
        
        created_at = datetime.datetime.now().isoformat()
        
        self.cursor.execute(
            "INSERT INTO cat_weights (cat_name, date, initial_weight, created_at) "
            "VALUES (?, ?, ?, ?)",
            (cat_name, date, initial_weight, created_at)
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def update_remaining_weight(self, entry_id: int, remaining_weight: float) -> bool:
        """
        Update the remaining weight for an existing entry.
        
        Args:
            entry_id: The ID of the entry to update
            remaining_weight: The remaining weight in the bowl in grams
            
        Returns:
            True if the update was successful, False otherwise
        """
        self.cursor.execute(
            "UPDATE cat_weights SET remaining_weight = ? WHERE id = ?",
            (remaining_weight, entry_id)
        )
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def get_entry(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific weight entry by ID.
        
        Args:
            entry_id: The ID of the entry to retrieve
            
        Returns:
            A dictionary with the entry data or None if not found
        """
        self.cursor.execute(
            "SELECT * FROM cat_weights WHERE id = ?",
            (entry_id,)
        )
        row = self.cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def get_entries_by_date_range(self, start_date: str, end_date: str, cat_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get entries within a specific date range, optionally filtered by cat name.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            cat_name: Optional cat name filter
            
        Returns:
            A list of dictionaries with entry data
        """
        query = "SELECT * FROM cat_weights WHERE date BETWEEN ? AND ?"
        params = [start_date, end_date]
        
        if cat_name:
            query += " AND cat_name = ?"
            params.append(cat_name)
            
        query += " ORDER BY date DESC"
        
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_last_30_days_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get data for the last 30 days grouped by cat.
        
        Returns:
            A dictionary with cat names as keys and lists of entries as values
        """
        today = datetime.date.today()
        start_date = (today - datetime.timedelta(days=30)).isoformat()
        end_date = today.isoformat()
        
        cats = ["Mittens", "Cheddar", "Lola"]
        result = {}
        
        for cat in cats:
            result[cat] = self.get_entries_by_date_range(start_date, end_date, cat)
            
        return result
    
    def get_todays_open_entries(self, cat_name: str) -> List[Dict[str, Any]]:
        """
        Get entries for today that don't have a remaining weight recorded yet.
        
        Args:
            cat_name: The name of the cat
            
        Returns:
            A list of dictionaries with entry data
        """
        today = datetime.date.today().isoformat()
        
        self.cursor.execute(
            "SELECT * FROM cat_weights WHERE cat_name = ? AND date = ? AND remaining_weight IS NULL",
            (cat_name, today)
        )
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def reset_database(self):
        """
        Reset the database by deleting all entries.
        
        This is a destructive operation that removes all data from the cat_weights table.
        It does not delete the table structure itself.
        """
        self.cursor.execute("DELETE FROM cat_weights")
        self.conn.commit()
        print("Database has been reset - all cat weight entries have been deleted.")
        
    def delete_entries_by_date(self, date: str) -> int:
        """
        Delete all entries for a specific date.
        
        Args:
            date: The date in YYYY-MM-DD format for which to delete entries
            
        Returns:
            The number of entries deleted
        """
        self.cursor.execute(
            "DELETE FROM cat_weights WHERE date = ?",
            (date,)
        )
        self.conn.commit()
        return self.cursor.rowcount 