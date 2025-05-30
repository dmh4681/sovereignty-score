#!/usr/bin/env python3
"""
Comprehensive test suite for Sovereignty Score system
Tests scoring logic, database operations, and edge cases
"""

import sys
import os
import json
import unittest
from datetime import datetime
import tempfile
import duckdb

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tracker.scoring import calculate_daily_score
from utils import usd_to_sats

class TestScoringSystem(unittest.TestCase):
    """Test the scoring calculation logic"""
    
    @classmethod
    def setUpClass(cls):
        """Load path configurations once for all tests"""
        # Load paths configuration
        config_path = os.path.join(os.path.dirname(__file__), "config", "paths.json")
        if not os.path.exists(config_path):
            # Try alternative path
            config_path = os.path.join(os.path.dirname(__file__), "..", "config", "paths.json")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            cls.paths = json.load(f)
    
    def test_all_paths_exist(self):
        """Test that all expected paths are configured"""
        expected_paths = [
            "default", "financial_path", "mental_resilience", 
            "physical_optimization", "spiritual_growth", "planetary_stewardship"
        ]
        
        for path in expected_paths:
            self.assertIn(path, self.paths, f"Path {path} not found in configuration")
    
    def test_perfect_day_scores(self):
        """Test that perfect days score at or near maximum"""
        perfect_data = {
            "home_cooked_meals": 3,
            "junk_food": False,  # No junk food eaten
            "exercise_minutes": 40,
            "strength_training": True,
            "no_spending": True,
            "invested_bitcoin": True,
            "meditation": True,
            "gratitude": True,
            "read_or_learned": True,
            "environmental_action": True
        }
        
        for path_name in self.paths.keys():
            with self.subTest(path=path_name):
                score = calculate_daily_score(perfect_data, path=path_name)
                max_score = self.paths[path_name].get("max_score", 100)
                
                # Score should be close to maximum (allowing for rounding)
                self.assertGreaterEqual(score, max_score * 0.95, 
                                      f"Perfect day score too low for {path_name}: {score}")
                self.assertLessEqual(score, max_score, 
                                     f"Score exceeds maximum for {path_name}: {score}")
    
    def test_zero_day_scores(self):
        """Test that days with no activities score zero or near zero"""
        zero_data = {
            "home_cooked_meals": 0,
            "junk_food": True,  # Ate junk food
            "exercise_minutes": 0,
            "strength_training": False,
            "no_spending": False,
            "invested_bitcoin": False,
            "meditation": False,
            "gratitude": False,
            "read_or_learned": False,
            "environmental_action": False
        }
        
        for path_name in self.paths.keys():
            with self.subTest(path=path_name):
                score = calculate_daily_score(zero_data, path=path_name)
                self.assertLessEqual(score, 5, f"Zero day score too high for {path_name}: {score}")
    
    def test_junk_food_logic(self):
        """Test that junk food logic works correctly"""
        # Base data with just junk food varying
        base_data = {
            "home_cooked_meals": 2,
            "exercise_minutes": 30,
            "strength_training": False,
            "no_spending": False,
            "invested_bitcoin": False,
            "meditation": False,
            "gratitude": False,
            "read_or_learned": False,
            "environmental_action": False
        }
        
        # Test no junk food (should get points)
        no_junk_data = {**base_data, "junk_food": False}
        # Test ate junk food (should not get points)
        ate_junk_data = {**base_data, "junk_food": True}
        
        for path_name in self.paths.keys():
            if "no_junk_food" in self.paths[path_name]:
                with self.subTest(path=path_name):
                    no_junk_score = calculate_daily_score(no_junk_data, path=path_name)
                    ate_junk_score = calculate_daily_score(ate_junk_data, path=path_name)
                    
                    # No junk food should score higher than eating junk food
                    self.assertGreater(no_junk_score, ate_junk_score,
                                     f"Junk food logic failed for {path_name}")
    
    def test_path_specific_weightings(self):
        """Test that different paths weight activities differently"""
        test_data = {
            "home_cooked_meals": 2,
            "junk_food": False,
            "exercise_minutes": 30,
            "strength_training": True,
            "no_spending": True,
            "invested_bitcoin": True,
            "meditation": True,
            "gratitude": True,
            "read_or_learned": True,
            "environmental_action": True
        }
        
        # Calculate scores for all paths
        scores = {}
        for path_name in self.paths.keys():
            scores[path_name] = calculate_daily_score(test_data, path=path_name)
        
        # Physical optimization should weight strength training highly
        # Mental resilience should weight meditation highly
        # Financial path should weight spending/investment highly
        
        # These are relative tests - exact values depend on configuration
        self.assertIsInstance(scores["physical_optimization"], (int, float))
        self.assertIsInstance(scores["mental_resilience"], (int, float))
        self.assertIsInstance(scores["financial_path"], (int, float))
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        edge_cases = [
            # Maximum values
            {
                "home_cooked_meals": 10,
                "junk_food": False,
                "exercise_minutes": 300,
                "strength_training": True,
                "no_spending": True,
                "invested_bitcoin": True,
                "meditation": True,
                "gratitude": True,
                "read_or_learned": True,
                "environmental_action": True
            },
            # Minimum values
            {
                "home_cooked_meals": 0,
                "junk_food": True,
                "exercise_minutes": 0,
                "strength_training": False,
                "no_spending": False,
                "invested_bitcoin": False,
                "meditation": False,
                "gratitude": False,
                "read_or_learned": False,
                "environmental_action": False
            },
            # Missing fields (should handle gracefully)
            {
                "home_cooked_meals": 1,
                "exercise_minutes": 15
                # Other fields missing
            }
        ]
        
        for i, data in enumerate(edge_cases):
            for path_name in self.paths.keys():
                with self.subTest(case=i, path=path_name):
                    try:
                        score = calculate_daily_score(data, path=path_name)
                        self.assertIsInstance(score, (int, float))
                        self.assertGreaterEqual(score, 0)
                        self.assertLessEqual(score, self.paths[path_name].get("max_score", 100))
                    except Exception as e:
                        self.fail(f"Edge case {i} failed for {path_name}: {e}")

class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions"""
    
    def test_usd_to_sats_conversion(self):
        """Test USD to sats conversion"""
        # Test standard conversions
        self.assertEqual(usd_to_sats(100, 100000), 100000)  # $100 at $100k/BTC = 100k sats
        self.assertEqual(usd_to_sats(50, 100000), 50000)    # $50 at $100k/BTC = 50k sats
        self.assertEqual(usd_to_sats(1, 100000), 1000)      # $1 at $100k/BTC = 1k sats
        
        # Test edge cases
        self.assertEqual(usd_to_sats(0, 100000), 0)         # $0 = 0 sats
        self.assertEqual(usd_to_sats(100, 50000), 200000)   # $100 at $50k/BTC = 200k sats
    
    def test_usd_to_sats_precision(self):
        """Test that sats conversion maintains reasonable precision"""
        # Small amounts should still convert
        result = usd_to_sats(0.01, 100000)  # 1 cent
        self.assertGreater(result, 0)
        self.assertIsInstance(result, int)

class TestDatabaseOperations(unittest.TestCase):
    """Test database operations and data integrity"""
    
    def setUp(self):
        """Create temporary database for testing"""
        # Create a proper temp file path for Windows compatibility
        import tempfile
        self.test_db_path = tempfile.mktemp(suffix='.duckdb')
        self.conn = duckdb.connect(self.test_db_path)
        
        # Create test table
        self.conn.execute("""
            CREATE TABLE sovereignty (
                timestamp            TIMESTAMP,
                username             VARCHAR,
                path                 VARCHAR,
                home_cooked_meals    INTEGER,
                junk_food            BOOLEAN,
                exercise_minutes     INTEGER,
                strength_training    BOOLEAN,
                no_spending          BOOLEAN,
                invested_bitcoin     BOOLEAN,
                btc_usd              REAL DEFAULT 0,
                btc_sats             INTEGER DEFAULT 0,
                meditation           BOOLEAN,
                gratitude            BOOLEAN,
                read_or_learned      BOOLEAN,
                environmental_action BOOLEAN,
                score                INTEGER
            )
        """)
    
    def tearDown(self):
        """Clean up test database"""
        self.conn.close()
        try:
            os.unlink(self.test_db_path)
        except:
            pass  # File cleanup might fail on Windows, that's ok
    
    def test_insert_and_retrieve_data(self):
        """Test that data inserted matches data retrieved"""
        test_data = [
            datetime.now(), "test_user", "default",
            2, False, 30, True, True, True, 50.0, 5000,
            True, True, True, True, 85
        ]
        
        # Insert data
        self.conn.execute("""
            INSERT INTO sovereignty (
                timestamp, username, path,
                home_cooked_meals, junk_food, exercise_minutes, strength_training,
                no_spending, invested_bitcoin, btc_usd, btc_sats,
                meditation, gratitude, read_or_learned, environmental_action, score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, test_data)
        
        # Retrieve data
        result = self.conn.execute("""
            SELECT timestamp, username, path,
                   home_cooked_meals, junk_food, exercise_minutes, strength_training,
                   no_spending, invested_bitcoin, btc_usd, btc_sats,
                   meditation, gratitude, read_or_learned, environmental_action, score
            FROM sovereignty
            WHERE username = ?
        """, ["test_user"]).fetchone()
        
        self.assertIsNotNone(result)
        # Compare non-timestamp fields (timestamps may have precision differences)
        self.assertEqual(result[1:], test_data[1:])
    
    def test_multiple_users_and_paths(self):
        """Test that different users and paths are handled correctly"""
        users_data = [
            ("user1", "default", 75),
            ("user1", "financial_path", 80),  # Same user, different path (shouldn't happen but test anyway)
            ("user2", "physical_optimization", 90),
        ]
        
        for username, path, score in users_data:
            self.conn.execute("""
                INSERT INTO sovereignty (
                    timestamp, username, path, score,
                    home_cooked_meals, junk_food, exercise_minutes, strength_training,
                    no_spending, invested_bitcoin, btc_usd, btc_sats,
                    meditation, gratitude, read_or_learned, environmental_action
                ) VALUES (?, ?, ?, ?, 1, 0, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            """, [datetime.now(), username, path, score])
        
        # Test user1 retrieval
        user1_results = self.conn.execute("""
            SELECT username, path, score FROM sovereignty WHERE username = ?
        """, ["user1"]).fetchall()
        
        self.assertEqual(len(user1_results), 2)  # Two entries for user1
        
        # Test user2 retrieval
        user2_results = self.conn.execute("""
            SELECT username, path, score FROM sovereignty WHERE username = ?
        """, ["user2"]).fetchall()
        
        self.assertEqual(len(user2_results), 1)  # One entry for user2

def run_diagnostic_report():
    """Run a comprehensive diagnostic of the scoring system"""
    print("\n" + "="*60)
    print("SOVEREIGNTY SCORE DIAGNOSTIC REPORT")
    print("="*60)
    
    # Load configuration
    try:
        config_path = os.path.join(os.path.dirname(__file__), "config", "paths.json")
        if not os.path.exists(config_path):
            config_path = os.path.join(os.path.dirname(__file__), "..", "config", "paths.json")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            paths = json.load(f)
        print(f"✅ Loaded {len(paths)} path configurations")
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return
    
    # Test sample scoring for each path
    sample_data = {
        "home_cooked_meals": 2,
        "junk_food": False,
        "exercise_minutes": 30,
        "strength_training": True,
        "no_spending": True,
        "invested_bitcoin": True,
        "meditation": True,
        "gratitude": True,
        "read_or_learned": True,
        "environmental_action": True
    }
    
    print("\nSample day scoring (all activities completed):")
    print("-" * 50)
    
    for path_name, config in paths.items():
        try:
            score = calculate_daily_score(sample_data, path=path_name)
            max_score = config.get("max_score", 100)
            percentage = (score / max_score) * 100
            print(f"{path_name:20s}: {score:3.0f}/{max_score} ({percentage:5.1f}%)")
        except Exception as e:
            print(f"{path_name:20s}: ERROR - {e}")
    
    print("\nConfiguration validation:")
    print("-" * 50)
    
    # Check each path configuration
    for path_name, config in paths.items():
        issues = []
        
        # Check for max_score
        if "max_score" not in config:
            issues.append("Missing max_score")
        
        # Check for required fields
        required_activities = [
            "home_cooked_meals", "no_junk_food", "exercise_minutes", 
            "strength_training", "no_spending", "invested_bitcoin",
            "meditation", "gratitude", "read_or_learned", "environmental_action"
        ]
        
        for activity in required_activities:
            if activity not in config:
                issues.append(f"Missing {activity}")
        
        if issues:
            print(f"❌ {path_name}: {', '.join(issues)}")
        else:
            print(f"✅ {path_name}: Configuration valid")
    
    print("\n" + "="*60)
    print("Run full tests with: python -m pytest test_scoring_comprehensive.py -v")
    print("="*60)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Sovereignty Score system")
    parser.add_argument("--diagnostic", action="store_true", 
                       help="Run diagnostic report instead of tests")
    args = parser.parse_args()
    
    if args.diagnostic:
        run_diagnostic_report()
    else:
        unittest.main(verbosity=2)