"""
Unit tests for the Streamlit app components.
"""
import unittest
import sys
import os
import datetime
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the app module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Create a mock for streamlit since we can't test it directly
sys.modules['streamlit'] = MagicMock()
import streamlit as st

# Now import the app module
from app import create_cat_card, display_history_chart, CATS, CAT_COLORS


class TestAppComponents(unittest.TestCase):
    """Tests for the app components."""
    
    def setUp(self):
        """Set up mocks for testing."""
        # Mock db
        self.mock_db = MagicMock()
        
        # Reset streamlit mock before each test
        st.reset_mock()
    
    def test_create_cat_card_no_open_entries(self):
        """Test creating a cat card with no open entries."""
        # Set up the mock to return no open entries
        self.mock_db.get_todays_open_entries.return_value = []
        
        # Test with no recent entries
        self.mock_db.get_entries_by_date_range.return_value = []
        
        # Call the function
        create_cat_card("Mittens", self.mock_db)
        
        # Assert that the expected calls were made
        self.mock_db.get_todays_open_entries.assert_called_once_with("Mittens")
        
        # Check that we tried to get recent entries
        today = datetime.date.today().isoformat()
        seven_days_ago = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
        self.mock_db.get_entries_by_date_range.assert_called_once_with(seven_days_ago, today, "Mittens")
    
    def test_create_cat_card_with_open_entry(self):
        """Test creating a cat card with an open entry."""
        # Set up the mock to return an open entry
        mock_entry = {
            "id": 1, 
            "cat_name": "Cheddar", 
            "date": datetime.date.today().isoformat(),
            "initial_weight": 120.0, 
            "remaining_weight": None,
            "created_at": datetime.datetime.now().isoformat()
        }
        self.mock_db.get_todays_open_entries.return_value = [mock_entry]
        
        # Test with some recent entries
        mock_recent_entry = {
            "id": 2, 
            "cat_name": "Cheddar", 
            "date": (datetime.date.today() - datetime.timedelta(days=1)).isoformat(),
            "initial_weight": 130.0, 
            "remaining_weight": 30.0,
            "created_at": (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat()
        }
        self.mock_db.get_entries_by_date_range.return_value = [mock_recent_entry]
        
        # Call the function
        create_cat_card("Cheddar", self.mock_db)
        
        # Assert that the expected calls were made
        self.mock_db.get_todays_open_entries.assert_called_once_with("Cheddar")
    
    @patch('app.plt')
    @patch('app.datetime')
    def test_display_history_chart_no_data(self, mock_datetime, mock_plt):
        """Test displaying the history chart with no data."""
        # Setup mock for datetime.date.today
        mock_today = MagicMock()
        mock_datetime.date.today.return_value = mock_today
        mock_today.isoformat.return_value = "2023-04-01"
        
        # Set up the mock to return empty data
        empty_data = {cat: [] for cat in CATS}
        self.mock_db.get_last_30_days_data.return_value = empty_data
        
        # Call the function
        display_history_chart(self.mock_db)
        
        # Assert that the function handled no data correctly
        self.mock_db.get_last_30_days_data.assert_called_once()
        
        # Streamlit should show an info message about no data
        st.info.assert_called_once()
        
        # Make sure plt.subplots was not called (no chart created)
        mock_plt.subplots.assert_not_called()
    
    @patch('app.plt')
    @patch('app.datetime')
    def test_display_history_chart_with_data(self, mock_datetime, mock_plt):
        """Test displaying the history chart with data."""
        # Setup mock for datetime
        mock_today = MagicMock()
        mock_datetime.date.today.return_value = mock_today
        mock_today.isoformat.return_value = "2023-04-01"
        
        # Mock for datetime.timedelta
        def mock_timedelta(days):
            mock_delta = MagicMock()
            mock_delta.days = days
            return mock_delta
        
        mock_datetime.timedelta = mock_timedelta
        
        # Mock for datetime.date.fromisoformat
        mock_date = MagicMock()
        mock_datetime.date.fromisoformat.return_value = mock_date
        
        # Set up the mock to return some test data
        test_data = {
            "Mittens": [
                {
                    "id": 1,
                    "cat_name": "Mittens",
                    "date": "2023-03-31",
                    "initial_weight": 100.0,
                    "remaining_weight": 20.0,
                    "created_at": "2023-03-31T12:00:00"
                }
            ],
            "Cheddar": [
                {
                    "id": 2,
                    "cat_name": "Cheddar",
                    "date": "2023-03-31",
                    "initial_weight": 120.0,
                    "remaining_weight": 30.0,
                    "created_at": "2023-03-31T12:00:00"
                }
            ],
            "Lola": [
                {
                    "id": 3,
                    "cat_name": "Lola",
                    "date": "2023-03-31",
                    "initial_weight": 140.0,
                    "remaining_weight": 40.0,
                    "created_at": "2023-03-31T12:00:00"
                }
            ]
        }
        self.mock_db.get_last_30_days_data.return_value = test_data
        
        # Mock figure and axes for pyplot
        mock_fig = MagicMock()
        mock_axes = [MagicMock(), MagicMock(), MagicMock()]
        mock_plt.subplots.return_value = (mock_fig, mock_axes)
        
        # Call the function
        display_history_chart(self.mock_db)
        
        # Assert the function made the right calls
        self.mock_db.get_last_30_days_data.assert_called_once()
        
        # Check that matplotlib was used to create the plot
        mock_plt.subplots.assert_called_once()
        
        # Verify that Streamlit shows the plot
        st.pyplot.assert_called_once_with(mock_fig)


if __name__ == "__main__":
    unittest.main() 