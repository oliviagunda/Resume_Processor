"""Comprehensive unit tests for the AI internship project."""
import unittest
import os
import tempfile
import mysql.connector
from unittest.mock import Mock, patch, MagicMock

from config import Config, DatabaseConfig, AppConfig
from db_utils import DatabaseManager
from pdf_parser import ResumeParser, ParsedResume


class TestConfig(unittest.TestCase):
    """Test configuration management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Config()
    
    def test_default_configuration(self):
        """Test default configuration values."""
        self.assertEqual(self.config.db.host, 'localhost')
        self.assertEqual(self.config.db.database, 'interviewees')
        self.assertEqual(self.config.app.resume_folder, 'resumes')
    
    @patch.dict(os.environ, {'DB_HOST': 'testhost', 'DB_USER': 'testuser'})
    def test_environment_override(self):
        """Test configuration override from environment variables."""
        config = Config()
        self.assertEqual(config.db.host, 'testhost')
        self.assertEqual(config.db.user, 'testuser')
    
    def test_to_dict(self):
        """Test configuration serialization to dictionary."""
        config_dict = self.config.to_dict()
        self.assertIn('database', config_dict)
        self.assertIn('app', config_dict)
        self.assertEqual(config_dict['database']['host'], 'localhost')


class TestDatabaseManager(unittest.TestCase):
    """Test database management functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.db_manager = DatabaseManager()
    
    @patch('mysql.connector.connect')
    def test_create_database(self, mock_connect):
        """Test database creation."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        result = self.db_manager.create_database()
        
        self.assertTrue(result)
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()
    
    @patch('mysql.connector.connect')
    def test_create_tables(self, mock_connect):
        """Test table creation."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        result = self.db_manager.create_tables()
        
        self.assertTrue(result)
        # Should execute 3 CREATE TABLE statements
        self.assertEqual(mock_cursor.execute.call_count, 3)
        mock_connection.commit.assert_called_once()
    
    @patch('mysql.connector.connect')
    def test_insert_job_seeker(self, mock_connect):
        """Test job seeker insertion."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 123
        
        job_seeker_id = self.db_manager.insert_job_seeker(
            'John Doe', 'john@example.com', '123-456-7890', 5.0, 'Resume text'
        )
        
        self.assertEqual(job_seeker_id, 123)
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()
    
    @patch('mysql.connector.connect')
    def test_insert_complete_job_seeker(self, mock_connect):
        """Test complete job seeker insertion with experiences and skills."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 123
        
        job_seeker_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '123-456-7890',
            'total_experience': 5.0,
            'resume_text': 'Resume text',
            'experiences': [
                {'company_name': 'Tech Corp', 'tenure': '2020-2023'},
                {'company_name': 'StartupXYZ', 'tenure': '2018-2020'}
            ],
            'skills': ['Python', 'JavaScript', 'SQL']
        }
        
        # Mock the insert_job_seeker, insert_experience, and insert_skill methods
        self.db_manager.insert_job_seeker = Mock(return_value=123)
        self.db_manager.insert_experience = Mock(return_value=True)
        self.db_manager.insert_skill = Mock(return_value=True)
        
        job_seeker_id = self.db_manager.insert_job_seeker_complete(job_seeker_data)
        
        self.assertEqual(job_seeker_id, 123)
        self.db_manager.insert_job_seeker.assert_called_once()
        self.assertEqual(self.db_manager.insert_experience.call_count, 2)
        self.assertEqual(self.db_manager.insert_skill.call_count, 3)
    
    @patch('mysql.connector.connect')
    def test_database_connection_error(self, mock_connect):
        """Test handling of database connection errors."""
        mock_connect.side_effect = mysql.connector.Error("Connection failed")
        
        result = self.db_manager.create_database()
        self.assertFalse(result)


class TestResumeParser(unittest.TestCase):
    """Test resume parsing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = ResumeParser()
    
    def test_extract_email(self):
        """Test email extraction from text."""
        text = "Contact me at john.doe@example.com for more information."
        email = self.parser.extract_email(text)
        self.assertEqual(email, "john.doe@example.com")
    
    def test_extract_phone(self):
        """Test phone number extraction from text."""
        text = "Call me at (555) 123-4567 or email."
        phone = self.parser.extract_phone(text)
        self.assertEqual(phone, "(555) 123-4567")
    
    def test_extract_name(self):
        """Test name extraction from text."""
        text = "John Smith\nSoftware Engineer\nSummary: Experienced developer..."
        name = self.parser.extract_name(text)
        self.assertEqual(name, "John Smith")
    
    def test_extract_experience_years(self):
        """Test experience years extraction."""
        text = "I have 5 years of experience in software development."
        years = self.parser.extract_experience_years(text)
        self.assertEqual(years, 5.0)
        
        text2 = "Experience: 7+ years in web development"
        years2 = self.parser.extract_experience_years(text2)
        self.assertEqual(years2, 7.0)
    
    def test_extract_companies(self):
        """Test company extraction from text."""
        text = """
        Work Experience:
        Tech Corp, 2020 - Present
        Software Engineer
        
        Previous Role:
        StartupXYZ Inc, 2018 - 2020
        Junior Developer
        """
        companies = self.parser.extract_companies(text)
        self.assertGreater(len(companies), 0)
        self.assertIn('company_name', companies[0])
        self.assertIn('tenure', companies[0])
    
    def test_extract_skills(self):
        """Test skills extraction from text."""
        text = """
        Technical Skills:
        Python, JavaScript, SQL, React, Node.js
        
        Other experience with Java and C++.
        """
        skills = self.parser.extract_skills(text)
        self.assertIn('Python', skills)
        self.assertIn('JavaScript', skills)
        self.assertIn('SQL', skills)
    
    @patch('pdfplumber.open')
    def test_extract_text_from_pdf(self, mock_open):
        """Test PDF text extraction."""
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample resume text"
        mock_pdf.pages = [mock_page]
        mock_open.return_value.__enter__.return_value = mock_pdf
        
        text = self.parser.extract_text_from_pdf("test.pdf")
        self.assertEqual(text, "Sample resume text")
    
    @patch('pdfplumber.open')
    def test_parse_resume(self, mock_open):
        """Test complete resume parsing."""
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = """
        John Smith
        john.smith@email.com
        (555) 123-4567
        
        Experience: 5 years of experience
        
        Work History:
        Tech Corp, 2020 - Present
        
        Skills: Python, JavaScript, SQL
        """
        mock_pdf.pages = [mock_page]
        mock_open.return_value.__enter__.return_value = mock_pdf
        
        parsed = self.parser.parse_resume("test.pdf")
        
        self.assertEqual(parsed.name, "John Smith")
        self.assertEqual(parsed.email, "john.smith@email.com")
        self.assertEqual(parsed.phone, "(555) 123-4567")
        self.assertEqual(parsed.total_experience, 5.0)
        self.assertGreater(len(parsed.skills), 0)
    
    @patch('os.listdir')
    @patch('os.path.exists')
    def test_parse_resumes_from_folder(self, mock_exists, mock_listdir):
        """Test parsing multiple resumes from folder."""
        mock_exists.return_value = True
        mock_listdir.return_value = ['resume1.pdf', 'resume2.pdf', 'not_a_pdf.txt']
        
        self.parser.parse_resume = Mock(return_value=ParsedResume(name="Test"))
        
        results = self.parser.parse_resumes_from_folder("/test/folder")
        
        self.assertEqual(len(results), 2)  # Only PDF files should be processed
        self.assertEqual(self.parser.parse_resume.call_count, 2)


class TestParsedResume(unittest.TestCase):
    """Test ParsedResume data class."""
    
    def test_default_initialization(self):
        """Test default values for ParsedResume."""
        resume = ParsedResume()
        self.assertIsNone(resume.name)
        self.assertIsNone(resume.email)
        self.assertEqual(resume.total_experience, 0.0)
        self.assertEqual(resume.companies, [])
        self.assertEqual(resume.skills, [])
    
    def test_custom_initialization(self):
        """Test custom initialization of ParsedResume."""
        companies = [{'company_name': 'Test Corp', 'tenure': '2020-2023'}]
        skills = ['Python', 'JavaScript']
        
        resume = ParsedResume(
            name="John Doe",
            email="john@example.com",
            phone="123-456-7890",
            total_experience=5.5,
            companies=companies,
            skills=skills,
            raw_text="Resume text"
        )
        
        self.assertEqual(resume.name, "John Doe")
        self.assertEqual(resume.email, "john@example.com")
        self.assertEqual(resume.phone, "123-456-7890")
        self.assertEqual(resume.total_experience, 5.5)
        self.assertEqual(resume.companies, companies)
        self.assertEqual(resume.skills, skills)
        self.assertEqual(resume.raw_text, "Resume text")


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple components."""
    
    @patch('mysql.connector.connect')
    @patch('pdfplumber.open')
    def test_end_to_end_resume_processing(self, mock_open, mock_connect):
        """Test end-to-end resume processing from PDF to database."""
        # Mock PDF content
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = """
        Jane Doe
        jane.doe@email.com
        (555) 987-6543
        
        Experience: 7 years of experience
        
        Work History:
        Amazing Company Inc, 2018 - Present
        Senior Developer
        
        Previous Company LLC, 2016 - 2018
        
        Skills: Python, Django, PostgreSQL, Docker
        """
        mock_pdf.pages = [mock_page]
        mock_open.return_value.__enter__.return_value = mock_pdf
        
        # Mock database operations
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 456
        
        # Parse resume
        parser = ResumeParser()
        parsed_resume = parser.parse_resume("test_resume.pdf")
        
        # Verify parsing
        self.assertEqual(parsed_resume.name, "Jane Doe")
        self.assertEqual(parsed_resume.email, "jane.doe@email.com")
        self.assertEqual(parsed_resume.total_experience, 7.0)
        self.assertIn('Python', parsed_resume.skills)
        
        # Insert into database
        db_manager = DatabaseManager()
        job_seeker_data = {
            'name': parsed_resume.name,
            'email': parsed_resume.email,
            'phone': parsed_resume.phone,
            'total_experience': parsed_resume.total_experience,
            'resume_text': parsed_resume.raw_text,
            'experiences': parsed_resume.companies,
            'skills': parsed_resume.skills
        }
        
        # Mock individual methods for the test
        db_manager.insert_job_seeker = Mock(return_value=456)
        db_manager.insert_experience = Mock(return_value=True)
        db_manager.insert_skill = Mock(return_value=True)
        
        job_seeker_id = db_manager.insert_job_seeker_complete(job_seeker_data)
        
        # Verify database insertion
        self.assertEqual(job_seeker_id, 456)
        db_manager.insert_job_seeker.assert_called_once()


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestConfig))
    test_suite.addTest(unittest.makeSuite(TestDatabaseManager))
    test_suite.addTest(unittest.makeSuite(TestResumeParser))
    test_suite.addTest(unittest.makeSuite(TestParsedResume))
    test_suite.addTest(unittest.makeSuite(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)