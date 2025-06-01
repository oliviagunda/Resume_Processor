## Installation Steps:
1. Regarding MySql:

a) Install MySql
   docker run --name mysql \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=resume_db \
  -p 3306:3306 \
  -d mysql:8

b) To run MySql in the docker:

docker logs -f mysql

c) To check the status:

docker ps

d) To connect to MySql:

docker exec -it mysql mysql -u root -p

When prompted for pwd, enter root

2. Install Spacy

python3 -m spacy download en_core_web_sm

3. Install Pypdf

pip install pypdf

# AI Internship Project - Resume Parser

A modular Python application for parsing resume PDFs and storing candidate information in MySQL database. This project is designed to be extended over multiple weeks with additional features like job matching and skill scoring.

## 📋 Project Structure

```
ai_internship_project/
├── config.py           # Configuration management
├── db_utils.py         # Database operations and management
├── pdf_parser.py       # PDF parsing and text extraction
├── main.py            # Main application script
├── test_suite.py      # Comprehensive unit tests
├── requirements.txt   # Project dependencies
└── README.md          # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- MySQL Server installed and running
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai_internship_project
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (optional):
```bash
export DB_HOST=localhost
export DB_USER=your_mysql_user
export DB_PASSWORD=your_mysql_password
export DB_NAME=interviewees
export RESUME_FOLDER=resumes
```

### Database Setup

1. Ensure MySQL is running
2. Create a MySQL user with appropriate permissions
3. The application will automatically create the database and tables

## 📖 Usage

### Basic Usage

1. Create a `resumes` folder in the project directory
2. Add PDF resume files to the folder
3. Run the main script:
```bash
python main.py
```

### Running Tests

Run all unit tests:
```bash
python test_suite.py
```

Run with verbose output:
```bash
python -m unittest test_suite.py -v
```

## 🏗️ Architecture

### Week 1 - Database Setup (✅ Complete)
- Database connection management
- Table creation for job seekers, experiences, and skills
- Proper foreign key relationships

### Week 2 - Resume Parsing (✅ Complete)
- PDF text extraction using `pdfplumber`
- Information extraction (name, email, phone, experience, companies, skills)
- Database population with parsed data
- Comprehensive unit tests

### Week 3 - Job Description Parsing (🔄 Future)
- Parse job description files
- Extract requirements and qualifications
- Store in new job-related tables

### Week 4 - AI-Powered Matching (🔄 Future)
- Integration with ChatGPT API
- Skill matching and scoring
- Opportunity score calculation

## 📊 Database Schema

### Tables Created

1. **job_seeker**
   - `id` (PK, auto-increment)
   - `name`, `email`, `phone`
   - `total_experience`
   - `resume_text`
   - Timestamps

2. **job_seeker_experience**
   - `id` (PK, auto-increment)
   - `job_seeker_id` (FK)
   - `company_name`, `tenure`

3. **job_seeker_skills**
   - `id` (PK, auto-increment)
   - `job_seeker_id` (FK)
   - `skill`

## 🔧 Configuration

The application uses a centralized configuration system:

- Default values are set in `config.py`
- Override with environment variables
- Supports different environments (development, testing, production)

## 🧪 Testing

The project includes comprehensive unit tests:

- Configuration management tests
- Database operation tests
- PDF parsing functionality tests
- Integration tests
- Mock-based testing for external dependencies

## 📝 Code Quality

The codebase follows best practices:

- Modular design with separation of concerns
- Parameterized queries to prevent SQL injection
- Error handling and logging
- Type hints for better code documentation
- Comprehensive test coverage

## 🔮 Future Extensions

The codebase is designed for easy extension:

1. **Job Matching Module**: Add job description parsing
2. **AI Integration**: Incorporate OpenAI API for intelligent matching
3. **Scoring System**: Implement candidate-job compatibility scoring
4. **Web Interface**: Add a web-based UI using Flask/Django
5. **API Layer**: Create REST API endpoints
6. **Data Analytics**: Add reporting and analytics features

## 🐛 Troubleshooting

### Common Issues

1. **MySQL Connection Error**
   - Verify MySQL is running
   - Check credentials in environment variables
   - Ensure user has proper permissions

2. **PDF Parsing Issues**
   - Verify PDF files are not corrupted
   - Check if files are password-protected
   - Ensure sufficient file permissions

3. **Module Import Errors**
   - Verify all dependencies are installed
   - Check Python path is correctly set

## 📄 License

This project is for educational purposes as part of an AI internship program.

## 🤝 Contributing

This is an internship project. For contributions:

1. Follow the existing code style
2. Add unit tests for new features
3. Update documentation as needed
4. Ensure all tests pass before submitting

## 📧 Contact

For questions or issues, please contact the internship supervisor.