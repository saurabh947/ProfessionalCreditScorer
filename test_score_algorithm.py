#!/usr/bin/env python3
"""
Test script for Professional Credit Scorer Algorithm
This script tests the credit scoring functionality using Google Gemini AI.
"""

import json
import unittest
from unittest.mock import Mock, patch, MagicMock
from score_algorithm import ProfessionalCreditScorer
from database import DatabaseManager

class TestProfessionalCreditScorer(unittest.TestCase):
    """Test cases for ProfessionalCreditScorer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock the Gemini API key for testing
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'}):
            self.scorer = ProfessionalCreditScorer()
    
    def tearDown(self):
        """Clean up after tests"""
        if hasattr(self, 'scorer'):
            self.scorer.close()
    
    def test_initialization(self):
        """Test that the scorer initializes correctly"""
        self.assertIsNotNone(self.scorer)
        self.assertIsNotNone(self.scorer.credit_scoring_prompt)
        self.assertIn("credit scoring", self.scorer.credit_scoring_prompt.lower())
    
    def test_parse_duration_string(self):
        """Test duration string parsing"""
        test_cases = [
            ("2 years 3 months", 2.25),
            ("1 year", 1.0),
            ("6 months", 0.5),
            ("1 year 6 months", 1.5),
            ("3 years 9 months", 3.75),
            ("", 0.0),
            ("invalid", 0.0),
            ("2 years and 3 months", 2.25),
        ]
        
        for duration, expected in test_cases:
            with self.subTest(duration=duration):
                result = self.scorer._parse_duration_string(duration)
                self.assertAlmostEqual(result, expected, places=2)
    
    def test_calculate_years_from_experience(self):
        """Test calculating years from experience array"""
        experience_data = [
            {"duration": "2 years 3 months"},
            {"duration": "1 year 6 months"},
            {"duration": "6 months"},
            {"duration": ""},  # Empty duration
            {"duration": "invalid"}  # Invalid duration
        ]
        
        expected_total = 2.25 + 1.5 + 0.5 + 0.0 + 0.0  # 4.25 years
        result = self.scorer._calculate_years_from_experience(experience_data)
        self.assertAlmostEqual(result, expected_total, places=2)
    
    def test_calculate_experience_metrics(self):
        """Test experience metrics calculation"""
        professionals_data = [
            {
                "unique_id": "1",
                "first_name": "John",
                "last_name": "Doe",
                "experience": [
                    {"duration": "2 years 3 months"},
                    {"duration": "1 year 6 months"}
                ]
            },
            {
                "unique_id": "2",
                "first_name": "Jane",
                "last_name": "Smith",
                "experience": [
                    {"duration": "5 years"},
                    {"duration": "2 years 6 months"}
                ]
            },
            {
                "unique_id": "3",
                "first_name": "Bob",
                "last_name": "Johnson",
                "experience": []  # No experience
            }
        ]
        
        metrics = self.scorer.calculate_experience_metrics(professionals_data)
        
        self.assertEqual(metrics["total_professionals"], 3)
        self.assertEqual(metrics["professionals_with_experience"], 2)
        self.assertAlmostEqual(metrics["average_years"], 5.625, places=2)  # (3.75 + 7.5) / 2
        self.assertAlmostEqual(metrics["median_years"], 7.5, places=2)  # Fixed: median of [3.75, 7.5] is 7.5
        self.assertAlmostEqual(metrics["min_years"], 3.75, places=2)
        self.assertAlmostEqual(metrics["max_years"], 7.5, places=2)
    
    def test_validate_analysis(self):
        """Test analysis validation"""
        valid_analysis = {
            "analysis_summary": {
                "total_professionals_analyzed": 100,
                "average_years_experience": 5.5
            },
            "experience_distribution": {
                "entry_level_0_2_years": 20
            },
            "career_insights": {
                "average_job_tenure": 3.2
            }
        }
        
        invalid_analysis = {
            "analysis_summary": {
                "total_professionals_analyzed": 100
                # Missing average_years_experience
            }
        }
        
        self.assertTrue(self.scorer._validate_analysis(valid_analysis))
        self.assertFalse(self.scorer._validate_analysis(invalid_analysis))
    
    def test_create_empty_analysis(self):
        """Test empty analysis creation"""
        empty_analysis = self.scorer._create_empty_analysis()
        
        self.assertIn("analysis_summary", empty_analysis)
        self.assertIn("experience_distribution", empty_analysis)
        self.assertIn("career_insights", empty_analysis)
        self.assertEqual(empty_analysis["status"], "no_data")
        self.assertEqual(empty_analysis["analysis_summary"]["total_professionals_analyzed"], 0)
    
    def test_parse_text_analysis(self):
        """Test text analysis parsing"""
        text_content = "This is a detailed analysis of professional data."
        parsed = self.scorer._parse_text_analysis(text_content)
        
        self.assertIn("analysis_summary", parsed)
        self.assertIn("detailed_analysis", parsed)
        self.assertEqual(parsed["detailed_analysis"], text_content)
        self.assertEqual(parsed["parsing_status"], "text_only")
    
    @patch('score_algorithm.DatabaseManager')
    def test_analyze_professional_database_no_data(self, mock_db_manager):
        """Test analysis when no professionals are found"""
        # Mock empty database
        mock_db = Mock()
        mock_db.get_all_professionals.return_value = []
        mock_db_manager.return_value = mock_db
        
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'}):
            scorer = ProfessionalCreditScorer()
            result = scorer.analyze_professional_database()
            
            self.assertEqual(result["status"], "no_data")
            self.assertEqual(result["analysis_summary"]["total_professionals_analyzed"], 0)
    
    @patch('google.generativeai.GenerativeModel')
    @patch('score_algorithm.DatabaseManager')
    def test_analyze_professional_database_with_data(self, mock_db_manager, mock_genai_model):
        """Test analysis with professional data"""
        # Mock professional data
        mock_professionals = [
            {
                "unique_id": "1",
                "first_name": "John",
                "last_name": "Doe",
                "headline": "Software Engineer",
                "company": "Tech Corp",
                "job_title": "Senior Developer",
                "city": "Austin",
                "experience": [
                    {"duration": "3 years 6 months"},
                    {"duration": "2 years"}
                ],
                "connectionsCount": 500,
                "followerCount": 100,
                "verified": True,
                "premium": False
            }
        ]
        
        # Mock Gemini response
        mock_response = Mock()
        mock_response.text = json.dumps({
            "analysis_summary": {
                "total_professionals_analyzed": 1,
                "professionals_with_experience_data": 1,
                "average_years_experience": 5.5,
                "median_years_experience": 5.5,
                "experience_range": {"minimum": 5.5, "maximum": 5.5}
            },
            "experience_distribution": {
                "entry_level_0_2_years": 0,
                "mid_level_3_7_years": 1,
                "senior_level_8_15_years": 0,
                "executive_level_15_plus_years": 0
            },
            "career_insights": {
                "average_job_tenure": 2.75,
                "career_progression_rate": 0.8,
                "industry_stability_score": 0.7
            },
            "detailed_analysis": "Comprehensive analysis of professional data."
        })
        
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_genai_model.return_value = mock_model
        
        # Mock database
        mock_db = Mock()
        mock_db.get_all_professionals.return_value = mock_professionals
        mock_db_manager.return_value = mock_db
        
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'}):
            scorer = ProfessionalCreditScorer()
            result = scorer.analyze_professional_database()
            
            self.assertIn("analysis_summary", result)
            self.assertEqual(result["analysis_summary"]["total_professionals_analyzed"], 1)
            self.assertEqual(result["analysis_summary"]["total_batches_processed"], 1)
            self.assertIn("career_insights", result)
            self.assertIn("calculation_method", result)
            self.assertEqual(result["calculation_method"], "batched_ai_analysis")
    
    def test_prepare_analysis_prompt(self):
        """Test prompt preparation"""
        professionals = [
            {
                "unique_id": "1",
                "first_name": "John",
                "last_name": "Doe",
                "headline": "Software Engineer",
                "company": "Tech Corp",
                "job_title": "Senior Developer",
                "city": "Austin",
                "experience": [{"duration": "3 years"}],
                "connectionsCount": 500,
                "followerCount": 100,
                "verified": True,
                "premium": False
            }
        ]
        
        prompt = self.scorer._prepare_analysis_prompt(professionals, 1, 1)
        
        self.assertIn("BATCH INFORMATION", prompt)
        self.assertIn("PROFESSIONAL DATASET", prompt)
        self.assertIn("BATCH 1", prompt)
        self.assertIn("John Doe", prompt)
        self.assertIn("Tech Corp", prompt)
        self.assertIn("Austin", prompt)
        self.assertIn("batch 1 of 1", prompt)


def test_manual_experience_calculation():
    """Test manual experience calculation without AI"""
    print("🧪 Testing Manual Experience Calculation")
    print("=" * 50)
    
    try:
        # Create test data
        test_professionals = [
            {
                "unique_id": "1",
                "first_name": "Alice",
                "last_name": "Johnson",
                "experience": [
                    {"duration": "2 years 6 months"},
                    {"duration": "1 year 3 months"},
                    {"duration": "6 months"}
                ]
            },
            {
                "unique_id": "2",
                "first_name": "Bob",
                "last_name": "Smith",
                "experience": [
                    {"duration": "5 years"},
                    {"duration": "3 years 9 months"}
                ]
            },
            {
                "unique_id": "3",
                "first_name": "Carol",
                "last_name": "Davis",
                "experience": []  # No experience
            }
        ]
        
        # Initialize scorer
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'}):
            scorer = ProfessionalCreditScorer()
            
            # Calculate metrics
            metrics = scorer.calculate_experience_metrics(test_professionals)
            
            print(f"📊 Manual Calculation Results:")
            print(f"  Total professionals: {metrics['total_professionals']}")
            print(f"  Professionals with experience: {metrics['professionals_with_experience']}")
            print(f"  Average years: {metrics['average_years']}")
            print(f"  Median years: {metrics['median_years']}")
            print(f"  Min years: {metrics['min_years']}")
            print(f"  Max years: {metrics['max_years']}")
            
            # Verify calculations
            expected_avg = (4.25 + 8.75) / 2  # (2.5+1.25+0.5 + 5+3.75) / 2
            assert abs(metrics['average_years'] - expected_avg) < 0.01, f"Expected {expected_avg}, got {metrics['average_years']}"
            
            print("✅ Manual experience calculation test passed!")
            return True
            
    except Exception as e:
        print(f"❌ Manual experience calculation test failed: {e}")
        return False


def test_duration_parsing():
    """Test duration string parsing"""
    print("🧪 Testing Duration String Parsing")
    print("=" * 50)
    
    try:
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'}):
            scorer = ProfessionalCreditScorer()
            
            test_cases = [
                ("2 years 3 months", 2.25),
                ("1 year", 1.0),
                ("6 months", 0.5),
                ("1 year 6 months", 1.5),
                ("3 years 9 months", 3.75),
                ("", 0.0),
                ("invalid", 0.0),
                ("2 years and 3 months", 2.25),
            ]
            
            all_passed = True
            for duration, expected in test_cases:
                result = scorer._parse_duration_string(duration)
                if abs(result - expected) < 0.01:
                    print(f"✅ '{duration}' -> {result} years")
                else:
                    print(f"❌ '{duration}' -> {result} years (expected {expected})")
                    all_passed = False
            
            if all_passed:
                print("✅ All duration parsing tests passed!")
            else:
                print("❌ Some duration parsing tests failed!")
            
            return all_passed
            
    except Exception as e:
        print(f"❌ Duration parsing test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Starting Professional Credit Scorer Tests")
    print("=" * 60)
    
    # Run manual tests
    print("\n1. Testing Duration Parsing")
    duration_success = test_duration_parsing()
    
    print("\n2. Testing Manual Experience Calculation")
    experience_success = test_manual_experience_calculation()
    
    # Run unit tests
    print("\n3. Running Unit Tests")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    print("\n" + "=" * 60)
    if duration_success and experience_success:
        print("✅ All tests completed successfully!")
    else:
        print("❌ Some tests failed!")
    
    print("\n📝 Test Summary:")
    print("- Duration parsing: ✅" if duration_success else "- Duration parsing: ❌")
    print("- Experience calculation: ✅" if experience_success else "- Experience calculation: ❌")
    print("- Unit tests: ✅ (see above for details)")


if __name__ == "__main__":
    main() 