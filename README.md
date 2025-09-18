# Advanced Programming Course Grading Agent

This agent automates the grading of C++ programming assignments for an Advanced Programming course. It can handle multiple practices (A1-A6) with different requirements and test cases, automatically generating test cases from PDF descriptions.

## Features

- **Complete Assignment Support**: Handles all 6 programming practices (A1-A6)
- **PDF Description Processing**: Automatically reads and summarizes PDF assignment descriptions from subdirectories
- **Automated Test Case Generation**: Creates test cases based on extracted requirements from descriptions
- **Practice-Specific Grading**: Grades code based on specific practice requirements
- **Multi-Phase Support**: Handles A6's three-phase structure
- **Automated Testing**: Runs test cases and builds projects
- **Static Analysis**: Uses cppcheck for code quality analysis
- **AI-Powered Evaluation**: Uses Gemini API for qualitative code assessment
- **Google Sheets Integration**: Automatically updates grades in spreadsheets for all assignments
- **SSH Git Integration**: Secure repository cloning with AP-F03 configuration
- **Structured Output & Prompts**: All LLM-based outputs (test case generation, grading) use a strict JSON format for easy parsing and downstream automation. Prompts and format instructions are centralized in `prompts.py` for maintainability.
- **Robust Parsing & Validation**: The agent uses shared helpers to parse and validate LLM responses, saving raw outputs and errors for debugging. This ensures reliable integration and easier troubleshooting.

## Directory Structure

```
grading_agent/
├── .gitignore                  # Git ignore rules for logs, credentials, etc.
├── .gitattributes             # Git attributes for line endings and binary files
├── LICENSE                     # MIT License
├── config.py                    # Configuration settings
├── main_agent.py               # Main grading workflow
├── langchain_integration.py    # Gemini API integration
├── sheets_updater.py          # Google Sheets integration (supports A1-A6)
├── tools.py                   # Utility functions for PDF reading, test generation
├── requirements.txt           # Python dependencies
├── description/               # PDF assignment descriptions organized by assignment
│   ├── A1/
│   │   └── APS04-A1-Description.pdf
│   ├── A2/
│   │   └── APS04-A2-Description.pdf
│   ├── A3/
│   │   └── APS04-A3-Description.pdf
│   ├── A4/
│   │   └── APS04-A4-Description.pdf
│   ├── A5/
│   │   └── APS04-A5-Description.pdf
│   └── A6/
│       ├── APS04-A6.1-Description-1.pdf
│       ├── APS04-A6.2-Description.pdf
│       └── APS04-A6.3-Description.pdf
├── test_cases/               # Test cases organized by assignment
│   ├── A1/
│   │   └── tests/
│   │       ├── 01.in
│   │       ├── 01.out
│   │       └── ...
│   ├── A2/
│   ├── A3/
│   ├── A4/
│   ├── A5/
│   └── A6/
└── student_projects/         # Cloned student repositories
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Required Tools

**macOS:**

```bash
brew install cppcheck
```

**Ubuntu:**

```bash
sudo apt-get install cppcheck
```

**Windows:**
Download cppcheck from https://cppcheck.sourceforge.io/

### 3. Set up Assignment Descriptions

The `description/` folder should contain subdirectories for each assignment (A1-A6) with their respective PDF files:

```
description/
├── A1/APS04-A1-Description.pdf
├── A2/APS04-A2-Description.pdf
├── A3/APS04-A3-Description.pdf
├── A4/APS04-A4-Description.pdf
├── A5/APS04-A5-Description.pdf
└── A6/
    ├── APS04-A6.1-Description-1.pdf
    ├── APS04-A6.2-Description.pdf
    └── APS04-A6.3-Description.pdf
```

### 4. Generate Test Cases

Automatically generate test cases from descriptions:

```python
from tools import generate_all_testcases
generate_all_testcases()
```

Or generate for specific assignments:

```python
from tools import generate_testcases_from_description
generate_testcases_from_description("A1")
```

### 5. Configure Google Sheets

1. Create separate sheets for each assignment (A1, A2, A3, A4, A5, A6)
2. Set up service account credentials
3. Update `config.py` with your sheet names and credentials

### 6. Set up Environment Variables

Create a `.env` file:

```
GOOGLE_API_KEY=your_gemini_api_key_here
```

### Structured Output Format

All LLM-generated outputs (test cases, grading) are returned in strict JSON format. Example for test case generation:

```json
{
  "test_cases": [
    {
      "input": "5\n1 2 3 4 5\n",
      "expected_output": "15\n",
      "description": "Sum of numbers",
      "category": "basic"
    },
    ...
  ]
}
```

Grading outputs follow assignment-specific schemas (see `langchain_integration.py` for Pydantic models).

### Centralized Prompt Helpers

All prompt templates, format instructions, and parsing helpers are located in `prompts.py`. To change the output format or prompt wording, edit this file.

### Robust LLM Output Parsing

The agent uses shared helpers to parse and validate LLM responses. Raw responses and errors are saved to `test_generation_logs/` for debugging. If parsing fails, the system falls back to heuristic generation or reports the error with full context.

## Usage

### Basic Grading

```python
from main_agent import grade_student

# Grade a student for A1
result = grade_student("student_id", "A1", "https://github.com/student/repo")
```

### Batch Grading

```python
from main_agent import batch_grade_assignments

# Grade all students for A1
results = batch_grade_assignments("A1")
```

### Google Sheets Integration

```python
from sheets_updater import update_student_grade

# Update grades for different assignments
update_student_grade(student_id, grade_data, "A1")
update_student_grade(student_id, grade_data, "A3")
update_student_grade(student_id, grade_data, "A6", "phase1")
```

## Grading Process

For each student, the agent:

1. **Loads Assignment Description**: Reads and summarizes PDF descriptions from `description/` subdirectories
2. **Generates Test Cases**: Creates relevant test cases based on extracted requirements
3. **Clones Repository**: Downloads student code using SSH with AP-F03 configuration
4. **Builds Project**: Compiles code using assignment-specific build commands
5. **Runs Tests**: Executes generated test cases and compares outputs
6. **Static Analysis**: Runs cppcheck for code quality assessment
7. **AI Evaluation**: Uses Gemini API to assess code quality based on:
   - **A1**: Logic (iterators, containers), Design (I/O separation, structs)
   - **A2**: Data handling, I/O separation, Git practices
   - **A3**: Recursive logic, backtracking algorithms
   - **A4**: Object-oriented design, multifile organization
   - **A5**: Game development, OOP principles
   - **A6**: Multi-phase project with web development (Phases 1-3)
8. **Calculates Scores**: Combines test results with qualitative assessment
9. **Updates Sheets**: Writes all scores and feedback to Google Sheets

## Assignment-Specific Features

### A1 - Basic C++ Programming

- Focus: Iterators, containers, structs
- Test cases: Basic data structure operations

### A2 - Data Handling

- Focus: Input reading, data storage, I/O separation
- Includes: Git commit message quality

### A3 - Algorithms

- Focus: Recursive functions, backtracking
- Test cases: Algorithm correctness for Q1-Q4

### A4 - Object-Oriented Programming

- Focus: Classes, encapsulation, inheritance
- Includes: Multifile organization, header guards

### A5 - Game Development

- Focus: OOP in game context, design patterns
- Includes: Tower defense game mechanics

### A6 - Multi-Phase Project

- **Phase 1**: Core functionality, OOP design
- **Phase 2**: Joint events, polymorphism
- **Phase 3**: Web interface, full-stack development
- Separate grading for each phase

## Configuration

### config.py Settings

```python
# Directory paths
PRACTICES_DIR = "description/"
TEST_CASES_DIR = "test_cases/"
CLONE_DIR = "student_projects/"

# Google Sheets
SHEET_NAME = "AP-Grades-2025"
CREDENTIALS_FILE = "credentials.json"

# Build commands for each assignment
PRACTICE_CONFIGS = {
    'A1': {
        'build_command': ['g++', 'main.cpp', '-o', 'main'],
        'executable_name': 'main',
        'test_cases_dir': 'test_cases/A1/tests'
    },
    # ... configurations for A2-A6
}
```

### Google Sheets Column Mappings

The `sheets_updater.py` includes column mappings for all assignments:

- **A1**: Logic, Design, Clean Coding, Correctness
- **A2**: Data handling, Design, Git practices
- **A3**: Q1-Q4 algorithms, Design, Clean coding
- **A4**: OOP design, Multifile, Clean coding
- **A5**: Game design, OOP, Clean coding
- **A6**: Phase-specific grading (Phase 1, 2, 3)

## Test Case Generation

### Automatic Generation

The system can automatically generate test cases from PDF descriptions:

```python
from tools import generate_testcases_from_description

# Generate test cases for A1
generate_testcases_from_description("A1", num_cases=5)

# Generate for all assignments
from tools import generate_all_testcases
generate_all_testcases()
```

### Manual Test Case Structure

Test cases follow the format:

```
test_cases/A1/tests/
├── 01.in   # Input for test case 1
├── 01.out  # Expected output for test case 1
├── 02.in
├── 02.out
└── ...
```

## Judge Script Integration

The system now integrates with judge scripts located in each practice's `judge/` folder to run authentic tests and get accurate scores.

### Automatic Judge Detection

```python
# The system automatically detects and uses judge scripts
test_results = tools.build_and_run_tests(project_path, "A1")
# This will use test_cases/practice1/judge/judge.sh if available
```

### Supported Judge Scripts

Each practice folder contains:

- **judge.sh**: Main testing script with compilation and test execution
- **config.sh**: Configuration file for test parameters
- **clone.sh**: Repository cloning and commit analysis
- **repos.json**: Student repository mappings for each phase (A6)

### A6 Multi-Phase Testing

For A6 assignments, the system automatically runs tests for all three phases:

```bash
# Automatically runs Phase 1, 2, and 3 tests
./judge.sh -p 1 && ./judge.sh -t
./judge.sh -p 2 && ./judge.sh -t
./judge.sh -p 3 && ./judge.sh -t
```

### Judge Script Features

- **Compilation Testing**: Tests if code compiles successfully
- **Test Execution**: Runs test cases against student code
- **Output Validation**: Compares student output with expected results
- **Scoring**: Provides pass/fail counts and detailed feedback
- **Multi-Phase Support**: Handles A6's three-phase structure

## Troubleshooting

### Common Issues

- **PDF Reading Errors**: Ensure PDFs contain extractable text (not image scans)
- **Build Failures**: Verify build commands match student project structure
- **SSH Clone Issues**: Check AP-F03 SSH key configuration
- **Test Case Generation**: Ensure description PDFs are properly formatted
- **Google Sheets Access**: Verify service account permissions

### Debug Commands

```python
# Test PDF reading
from tools import get_practice_descriptions
descriptions = get_practice_descriptions("description/")
print(descriptions.keys())

# Test test case generation
from tools import generate_testcases_from_description
generate_testcases_from_description("A1")

# Test sheet connection
from sheets_updater import get_sheet
sheet = get_sheet()
print("Connected to sheet:", sheet.title)
```

## Output and Reporting

The agent provides comprehensive output:

- **Quantitative Scores**: Test pass rates, build success rates
- **Qualitative Assessment**: AI-generated feedback based on assignment criteria
- **Detailed Reports**: Code quality analysis, static analysis results
- **Final Grades**: Calculated scores for each assignment component
- **Google Sheets Integration**: Automatic updates for all assignments A1-A6

## Development and Extension

### Adding New Assignments

1. Add PDF description to `description/A7/`
2. Update `sheets_updater.py` with column mapping
3. Add configuration to `config.py`
4. Update grading logic in `main_agent.py`

### Customizing Grading Criteria

Modify the prompts in `langchain_integration.py` to adjust grading criteria for specific assignments.

### Editing Prompts and Output Format

To change the LLM prompt wording or output format, edit `grading_agent/prompts.py`. All format instructions and parsing helpers are centralized there for easy maintenance.

### Validating Structured Outputs

Use the shared parser in `prompts.py` to validate and load LLM responses. If you encounter parsing errors, check the logs in `test_generation_logs/` for the raw output and error details.

## Dependencies

- Python 3.8+
- cppcheck (static analysis)
- PyMuPDF (PDF reading)
- gspread (Google Sheets)
- langchain (AI evaluation)
- GitPython (repository cloning)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
