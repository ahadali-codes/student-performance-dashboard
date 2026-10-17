"""Headless Streamlit interaction checks (no browser required)."""
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest

class DashboardTests(unittest.TestCase):
    def test_navigation_and_empty_filter(self):
        app = Path(__file__).resolve().parents[1] / 'app.py'
        at = AppTest.from_file(str(app), default_timeout=30).run()
        self.assertFalse(at.exception)
        for page in ['Student Analysis', 'Subject Analysis', 'Performance Insights', 'Dataset Explorer']:
            at.sidebar.radio[0].set_value(page).run()
            self.assertFalse(at.exception, page)
        at.sidebar.multiselect[0].set_value([]).run()
        self.assertFalse(at.exception)
        self.assertTrue(at.warning)
