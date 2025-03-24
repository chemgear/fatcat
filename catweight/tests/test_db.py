"""
Unit tests for the database module.
"""
import unittest
import os
import sqlite3
import datetime
from tempfile import NamedTemporaryFile
import sys
import os

# Add the parent directory to the path so we can import the db module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db import CatWeightDatabase


class TestCatWeightDatabase(unittest.TestCase):
    """Tests for the CatWeightDatabase class."""
    
    def setUp(self):
        """Set up a temporary database for each test."""
        self.temp_db = NamedTemporaryFile(delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        
        self.db = CatWeightDatabase(self.db_path)
        
    def tearDown(self):
        """Clean up after each test."""
        self.db.close()
        os.unlink(self.db_path)
    
    def test_add_entry(self):
        """Test adding a new entry to the database."""
        # Add an entry
        cat_name = "Mittens"
        initial_weight = 100.5
        entry_id = self.db.add_entry(cat_name, initial_weight)
        
        # Verify the entry was added
        self.assertIsNotNone(entry_id)
        
        # Fetch the entry and check its values
        entry = self.db.get_entry(entry_id)
        self.assertEqual(entry["cat_name"], cat_name)
        self.assertEqual(entry["initial_weight"], initial_weight)
        self.assertIsNone(entry["remaining_weight"])
        self.assertEqual(entry["date"], datetime.date.today().isoformat())
    
    def test_update_remaining_weight(self):
        """Test updating the remaining weight for an entry."""
        # Add an entry
        cat_name = "Cheddar"
        initial_weight = 150.0
        entry_id = self.db.add_entry(cat_name, initial_weight)
        
        # Update the remaining weight
        remaining_weight = 50.0
        success = self.db.update_remaining_weight(entry_id, remaining_weight)
        
        # Verify the update was successful
        self.assertTrue(success)
        
        # Fetch the entry and check the remaining weight
        entry = self.db.get_entry(entry_id)
        self.assertEqual(entry["remaining_weight"], remaining_weight)
    
    def test_get_entries_by_date_range(self):
        """Test retrieving entries within a date range."""
        # Add entries for different dates
        self.db.add_entry("Lola", 120.0, "2023-01-01")
        self.db.add_entry("Lola", 130.0, "2023-01-02")
        self.db.add_entry("Lola", 140.0, "2023-01-03")
        self.db.add_entry("Mittens", 110.0, "2023-01-02")
        
        # Test retrieving entries for a specific date range
        entries = self.db.get_entries_by_date_range("2023-01-01", "2023-01-02")
        self.assertEqual(len(entries), 3)
        
        # Test filtering by cat name
        entries = self.db.get_entries_by_date_range("2023-01-01", "2023-01-03", "Lola")
        self.assertEqual(len(entries), 3)
        
        # Verify all entries are for the correct cat
        for entry in entries:
            self.assertEqual(entry["cat_name"], "Lola")
    
    def test_get_todays_open_entries(self):
        """Test retrieving today's entries that don't have a remaining weight."""
        # Add entries for today
        today = datetime.date.today().isoformat()
        entry1_id = self.db.add_entry("Mittens", 100.0, today)
        entry2_id = self.db.add_entry("Mittens", 120.0, today)
        
        # Update one of the entries with a remaining weight
        self.db.update_remaining_weight(entry1_id, 30.0)
        
        # Get open entries for today
        open_entries = self.db.get_todays_open_entries("Mittens")
        
        # Verify there's only one open entry
        self.assertEqual(len(open_entries), 1)
        self.assertEqual(open_entries[0]["id"], entry2_id)
        self.assertIsNone(open_entries[0]["remaining_weight"])
    
    def test_get_last_30_days_data(self):
        """Test retrieving data for the last 30 days."""
        # Add entries for different cats and dates
        today = datetime.date.today()
        yesterday = (today - datetime.timedelta(days=1)).isoformat()
        
        for cat in ["Mittens", "Cheddar", "Lola"]:
            entry_id = self.db.add_entry(cat, 100.0, yesterday)
            self.db.update_remaining_weight(entry_id, 30.0)
        
        # Get last 30 days data
        data = self.db.get_last_30_days_data()
        
        # Verify data structure
        self.assertEqual(len(data), 3)  # Three cats
        
        for cat in ["Mittens", "Cheddar", "Lola"]:
            self.assertIn(cat, data)
            self.assertEqual(len(data[cat]), 1)  # One entry per cat
            self.assertEqual(data[cat][0]["initial_weight"], 100.0)
            self.assertEqual(data[cat][0]["remaining_weight"], 30.0)


if __name__ == "__main__":
    unittest.main() 