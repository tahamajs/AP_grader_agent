# Advanced Programming Course Grading Agent

This agent automates the grading of C++ programming assignments for an Advanced Programming course. It can handle multiple practices with different requirements and test cases.

## Features

- **Multi-Practice Support**: Handles 7+ different programming practices
- **PDF Description Reading**: Extracts requirements from PDF assignment descriptions
- **Practice-Specific Grading**: Grades code based on specific practice requirements
- **Automated Testing**: Runs test cases and builds projects
- **Static Analysis**: Uses cppcheck for code quality analysis
- **AI-Powered Evaluation**: Uses Gemini API for qualitative code assessment
- **Google Sheets Integration**: Automatically updates grades in spreadsheets

## Directory Structure

```
grading_agent/
├── config.py                    # Configuration settings
├── main_agent.py               # Main grading workflow
├── langchain_integration.py    # Gemini API integration
├── sheets_updater.py          # Google Sheets integration
├── tools.py                   # Utility functions
├── requirements.txt           # Python dependencies
├── practice_descriptions/     # PDF files for each practice
│   ├── practice1.pdf
│   ├── practice2.pdf
│   └── ...
├── test_cases/               # Test cases organized by practice
│   ├── practice1/
│   │   ├── test1.in
│   │   ├── test1.out
│   │   └── ...
│   ├── practice2/
│   │   ├── test1.in
│   │   └── ...
│   └── ...
└── student_projects/         # Cloned student repositories
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install cppcheck

**macOS:**

```bash
brew install cppcheck
```

**Ubuntu:**

```bash
sudo apt-get install cppcheck
```

**Windows:**
Download from https://cppcheck.sourceforge.io/

### 3. Set up Practice Descriptions

1. Create a `practice_descriptions/` directory
2. Add PDF files for each practice (e.g., `practice1.pdf`, `practice2.pdf`)
3. The PDF should contain the assignment requirements and specifications

### 4. Set up Test Cases

1. Create a `test_cases/` directory
2. For each practice, create a subdirectory (e.g., `test_cases/practice1/`)
3. Add test case files:
   - `test1.in` - Input for test case 1
   - `test1.out` - Expected output for test case 1
   - `test2.in`, `test2.out`, etc.

### 5. Configure Practice Settings

Edit `config.py` and update the `PRACTICE_CONFIGS` dictionary:

```python
PRACTICE_CONFIGS = {
    'practice1': {
        'build_command': 'make',
        'executable_name': 'student_program',
        'test_cases_dir': 'test_cases/practice1'
    },
    'practice2': {
        'build_command': 'cmake . && make',
        'executable_name': 'main',
        'test_cases_dir': 'test_cases/practice2'
    },
    # Add configurations for all 7 practices
}
```

### 6. Set up Google Sheets

1. Create a Google Sheet with the following columns:

   - A: Student Number
   - B: Name
   - C: Family Name
   - D: TA
   - E: Practice Name (e.g., "practice1", "practice2")
   - F: GitHub URL
   - G+: Grading columns (as per your rubric)

2. Create a service account and download `credentials.json`
3. Share the Google Sheet with the service account email
4. Update `config.py` with your sheet name and credentials file path

### 7. Set up Environment Variables

Create a `.env` file:

```
GOOGLE_API_KEY=your_gemini_api_key_here
```

## Usage

1. **Prepare Student Data:**

   - Fill your Google Sheet with student information
   - Ensure each row has: Student Number, Practice Name, GitHub URL

2. **Run the Grading Agent:**

   ```bash
   python main_agent.py
   ```

3. **Monitor Progress:**
   - The agent will process each student
   - Clone their repositories
   - Run builds and tests
   - Analyze code quality
   - Update grades in the spreadsheet

## Grading Process

For each student, the agent:

1. **Loads Practice Description**: Reads the relevant PDF for the assigned practice
2. **Clones Repository**: Downloads the student's code from GitHub
3. **Builds Project**: Compiles the code using practice-specific build commands
4. **Runs Tests**: Executes test cases and compares outputs
5. **Static Analysis**: Runs cppcheck for code quality issues
6. **AI Evaluation**: Uses Gemini API to assess code quality based on:
   - Logic (iterators, containers)
   - Design (I/O separation, structs, function organization)
   - Clean coding (comments, duplication, indentation, naming)
7. **Calculates Scores**: Combines test results with qualitative assessment
8. **Updates Sheet**: Writes all scores and feedback to Google Sheets

## Customization

### Adding New Practices

1. Add PDF description to `practice_descriptions/`
2. Create test cases in `test_cases/practice_name/`
3. Add configuration to `PRACTICE_CONFIGS` in `config.py`
4. Update Google Sheet column mappings if needed

### Modifying Grading Criteria

Edit the `GradingOutput` class in `langchain_integration.py` and update the prompt accordingly.

## Troubleshooting

- **PDF Reading Issues**: Ensure PDFs are text-based (not image scans)
- **Build Failures**: Check that build commands match student project structure
- **Test Case Issues**: Verify input/output file formats
- **API Errors**: Check your Gemini API key and quota
- **Sheet Access**: Ensure service account has edit permissions

## Output

The agent provides:

- **Quantitative Scores**: Test pass rates, build success
- **Qualitative Assessment**: Code quality scores based on rubric
- **Detailed Feedback**: AI-generated comments for improvement
- **Final Grades**: Calculated based on your weighting system

All results are automatically uploaded to your Google Sheet for easy review and distribution.
