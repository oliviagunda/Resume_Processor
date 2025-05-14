"""Main application script for the AI internship project."""
import os
import logging
from typing import List

from config import config
from db_utils import db_manager
from pdf_parser import resume_parser, ParsedResume

# Set up logging
logging.basicConfig(level=getattr(logging, config.app.log_level))
logger = logging.getLogger(__name__)


def initialize_database():
    """Initialize the database and create required tables."""
    logger.info("Initializing database...")
    
    # Create database
    if not db_manager.create_database():
        logger.error("Failed to create database")
        return False
    
    # Create tables
    if not db_manager.create_tables():
        logger.error("Failed to create tables")
        return False
    
    logger.info("Database initialized successfully")
    return True


def process_resumes(folder_path: str) -> bool:
    """Process all resumes in the specified folder."""
    logger.info(f"Processing resumes from folder: {folder_path}")
    
    # Parse all resumes
    parsed_resumes = resume_parser.parse_resumes_from_folder(folder_path)
    
    if not parsed_resumes:
        logger.warning("No resumes found or parsed")
        return False
    
    # Insert parsed data into database
    success_count = 0
    for parsed_resume in parsed_resumes:
        if insert_parsed_resume(parsed_resume):
            success_count += 1
    
    logger.info(f"Successfully processed {success_count}/{len(parsed_resumes)} resumes")
    return success_count > 0


def insert_parsed_resume(parsed_resume: ParsedResume) -> bool:
    """Insert a parsed resume into the database."""
    if not parsed_resume.name and not parsed_resume.email:
        logger.warning("Skipping resume with no name or email")
        return False
    
    # Prepare data for insertion
    job_seeker_data = {
        'name': parsed_resume.name or 'Unknown',
        'email': parsed_resume.email or '',
        'phone': parsed_resume.phone or '',
        'total_experience': parsed_resume.total_experience,
        'resume_text': parsed_resume.raw_text,
        'experiences': parsed_resume.companies,
        'skills': parsed_resume.skills
    }
    
    # Insert into database
    job_seeker_id = db_manager.insert_job_seeker_complete(job_seeker_data)
    
    if job_seeker_id:
        logger.info(f"Successfully inserted job seeker: {parsed_resume.name}")
        return True
    else:
        logger.error(f"Failed to insert job seeker: {parsed_resume.name}")
        return False


def main():
    """Main function to run the application."""
    logger.info("Starting AI Internship Project - Resume Parser")
    
    # Week 1: Initialize database
    if not initialize_database():
        logger.error("Failed to initialize database. Exiting.")
        return
    
    # Week 2: Process resumes
    resume_folder = config.app.resume_folder
    
    # Create folder if it doesn't exist
    if not os.path.exists(resume_folder):
        os.makedirs(resume_folder)
        logger.info(f"Created resume folder: {resume_folder}")
        logger.info("Please add PDF files to the resume folder and run again.")
        return
    
    # Process resumes
    if process_resumes(resume_folder):
        logger.info("Resume processing completed successfully")
    else:
        logger.error("Resume processing failed")


if __name__ == "__main__":
    main()