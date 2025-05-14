"""Week 1 - Database Setup Script

This standalone script handles the Week 1 requirements:
1. Connects to local MySQL server
2. Creates the 'interviewees' database if it doesn't exist
"""
import mysql.connector
from mysql.connector import Error
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_mysql_connection(host='localhost', user='root', password='', port=3306):
    """
    Create a connection to MySQL server.
    
    Args:
        host (str): MySQL server host
        user (str): MySQL username
        password (str): MySQL password
        port (int): MySQL port number
    
    Returns:
        mysql.connector.connection: Database connection object or None
    """
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            port=port
        )
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            logger.info(f"Successfully connected to MySQL Server version {db_info}")
            return connection
            
    except Error as e:
        logger.error(f"Error while connecting to MySQL: {e}")
        return None


def create_database(connection, database_name='interviewees'):
    """
    Create a database if it doesn't already exist.
    
    Args:
        connection: MySQL connection object
        database_name (str): Name of the database to create
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        
        # Verify database was created
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        
        database_exists = any(database_name in db for db in databases)
        
        if database_exists:
            logger.info(f"Database '{database_name}' created successfully or already exists")
            return True
        else:
            logger.error(f"Failed to create database '{database_name}'")
            return False
            
    except Error as e:
        logger.error(f"Error creating database: {e}")
        return False
    finally:
        if cursor:
            cursor.close()


def main():
    """Main function to execute Week 1 setup."""
    logger.info("Starting Week 1 - Database Setup")
    
    # Get database credentials from environment variables or use defaults
    db_host = os.getenv('DB_HOST', 'localhost')
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', '')
    db_port = int(os.getenv('DB_PORT', 3306))
    database_name = 'interviewees'
    
    logger.info(f"Connecting to MySQL at {db_host}:{db_port} as user '{db_user}'")
    
    # Create MySQL connection
    connection = create_mysql_connection(
        host=db_host,
        user=db_user,
        password=db_password,
        port=db_port
    )
    
    if connection:
        # Create the database
        if create_database(connection, database_name):
            logger.info("Week 1 setup completed successfully!")
        else:
            logger.error("Week 1 setup failed!")
        
        # Close the connection
        if connection.is_connected():
            connection.close()
            logger.info("MySQL connection closed")
    else:
        logger.error("Failed to establish MySQL connection")


if __name__ == "__main__":
    main()