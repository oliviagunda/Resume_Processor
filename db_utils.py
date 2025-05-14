"""Database utilities for the AI internship project."""
import mysql.connector
from mysql.connector import Error
from typing import Optional, List, Dict, Any, Tuple
import logging
from contextlib import contextmanager

from config import config

# Set up logging
logging.basicConfig(level=getattr(logging, config.app.log_level))
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self):
        self.db_config = config.db
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        connection = None
        try:
            connection = mysql.connector.connect(
                host=self.db_config.host,
                user='root',    #self.db_config.user,
                password='lulu@123',    #self.db_config.password,
                port=self.db_config.port
            )
            yield connection
        except Error as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    @contextmanager
    def get_cursor(self, connection):
        """Context manager for database cursors."""
        cursor = None
        try:
            cursor = connection.cursor()
            yield cursor
        except Error as e:
            logger.error(f"Database cursor error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    def create_database(self) -> bool:
        """Create the interviewees database if it doesn't exist."""
        try:
            with self.get_connection() as connection:
                with self.get_cursor(connection) as cursor:
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_config.database}")
                    connection.commit()
                    logger.info(f"Database '{self.db_config.database}' created or already exists")
                    return True
        except Error as e:
            logger.error(f"Error creating database: {e}")
            return False
    
    def connect_to_database(self):
        """Connect to the specific database."""
        try:
            connection = mysql.connector.connect(
                host=self.db_config.host,
                user='root', #self.db_config.user,
                password='lulu@123',  #self.db_config.password,
                database=self.db_config.database,
                port=self.db_config.port
            )
            return connection
        except Error as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    def create_tables(self) -> bool:
        """Create required tables for the interviewees database."""
        tables_sql = [
            """
            CREATE TABLE IF NOT EXISTS job_seeker (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE,
                phone VARCHAR(50),
                total_experience DECIMAL(5,2),
                resume_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS job_seeker_experience (
                id INT AUTO_INCREMENT PRIMARY KEY,
                job_seeker_id INT,
                company_name VARCHAR(255) NOT NULL,
                tenure VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_seeker_id) REFERENCES job_seeker(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS job_seeker_skills (
                id INT AUTO_INCREMENT PRIMARY KEY,
                job_seeker_id INT,
                skill VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_seeker_id) REFERENCES job_seeker(id) ON DELETE CASCADE
            )
            """
        ]
        
        try:
            with self.connect_to_database() as connection:
                with self.get_cursor(connection) as cursor:
                    for table_sql in tables_sql:
                        cursor.execute(table_sql)
                    connection.commit()
                    logger.info("All tables created successfully")
                    return True
        except Error as e:
            logger.error(f"Error creating tables: {e}")
            return False
    
    def insert_job_seeker(self, name: str, email: str, phone: str, 
                         total_experience: float, resume_text: str) -> Optional[int]:
        """Insert a job seeker and return the ID."""
        sql = """
        INSERT INTO job_seeker (name, email, phone, total_experience, resume_text)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        try:
            with self.connect_to_database() as connection:
                with self.get_cursor(connection) as cursor:
                    cursor.execute(sql, (name, email, phone, total_experience, resume_text))
                    connection.commit()
                    job_seeker_id = cursor.lastrowid
                    logger.info(f"Inserted job seeker with ID: {job_seeker_id}")
                    return job_seeker_id
        except Error as e:
            logger.error(f"Error inserting job seeker: {e}")
            return None
    
    def insert_experience(self, job_seeker_id: int, company_name: str, tenure: str) -> bool:
        """Insert job seeker experience."""
        sql = """
        INSERT INTO job_seeker_experience (job_seeker_id, company_name, tenure)
        VALUES (%s, %s, %s)
        """
        
        try:
            with self.connect_to_database() as connection:
                with self.get_cursor(connection) as cursor:
                    cursor.execute(sql, (job_seeker_id, company_name, tenure))
                    connection.commit()
                    logger.info(f"Inserted experience for job seeker ID: {job_seeker_id}")
                    return True
        except Error as e:
            logger.error(f"Error inserting experience: {e}")
            return False
    
    def insert_skill(self, job_seeker_id: int, skill: str) -> bool:
        """Insert job seeker skill."""
        sql = """
        INSERT INTO job_seeker_skills (job_seeker_id, skill)
        VALUES (%s, %s)
        """
        
        try:
            with self.connect_to_database() as connection:
                with self.get_cursor(connection) as cursor:
                    cursor.execute(sql, (job_seeker_id, skill))
                    connection.commit()
                    logger.info(f"Inserted skill for job seeker ID: {job_seeker_id}")
                    return True
        except Error as e:
            logger.error(f"Error inserting skill: {e}")
            return False
    
    def insert_job_seeker_complete(self, job_seeker_data: Dict[str, Any]) -> Optional[int]:
        connection = None  # ✅ Make sure connection is always defined
        try:
            with self.connect_to_database() as connection:
                with self.get_cursor(connection) as cursor:
                    connection.start_transaction()
                    
                    # Insert job seeker
                    insert_seeker_query = """
                        INSERT INTO job_seeker (name, email, phone, total_experience, resume_text)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_seeker_query, (
                        job_seeker_data['name'],
                        job_seeker_data['email'],
                        job_seeker_data['phone'],
                        job_seeker_data['total_experience'],
                        job_seeker_data['resume_text']
                    ))
                    job_seeker_id = cursor.lastrowid
                    
                    # Insert experiences
                    for experience in job_seeker_data.get('experiences', []):
                        cursor.execute("""
                            INSERT INTO job_seeker_experience (job_seeker_id, company_name, tenure)
                            VALUES (%s, %s, %s)
                        """, (job_seeker_id, experience['company_name'], experience['tenure']))
                    
                    # Insert skills
                    for skill in job_seeker_data.get('skills', []):
                        cursor.execute("""
                            INSERT INTO job_seeker_skills (job_seeker_id, skill)
                            VALUES (%s, %s)
                        """, (job_seeker_id, skill))
                    
                    connection.commit()
                    logger.info(f"Successfully inserted complete data for job seeker ID: {job_seeker_id}")
                    return job_seeker_id

        except Error as e:
            logger.error(f"Error inserting complete job seeker data: {e}")
            if connection:
                connection.rollback()
            return None

    
    def get_job_seeker_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Retrieve job seeker by email."""
        sql = "SELECT * FROM job_seeker WHERE email = %s"
        
        try:
            with self.connect_to_database() as connection:
                with self.get_cursor(connection) as cursor:
                    cursor.execute(sql, (email,))
                    result = cursor.fetchone()
                    
                    if result:
                        columns = [desc[0] for desc in cursor.description]
                        return dict(zip(columns, result))
                    return None
        except Error as e:
            logger.error(f"Error retrieving job seeker: {e}")
            return None


# Global database manager instance
db_manager = DatabaseManager()