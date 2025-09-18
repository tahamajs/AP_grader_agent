# Advanced Programming Course Grading Agent

This agent automates the grading of C++ programming assignments for an Advanced Programming course. It can handle multiple practices (A1-A6) with different requirements and test cases, automatically generating test cases from PDF descriptions.

## ✨ Key Features

- **Complete Assignment Support**: Handles all 6 programming practices (A1-A6)
- **PDF Description Processing**: Automatically reads and summarizes PDF assignment descriptions
- **Automated Test Case Generation**: Creates test cases based on extracted requirements from descriptions
- **Practice-Specific Grading**: Grades code based on specific practice requirements
- **Multi-Phase Support**: Handles A6's three-phase structure with separate grading
- **Automated Testing**: Runs test cases and builds projects with judge script integration
- **Static Analysis**: Uses cppcheck for code quality analysis
- **AI-Powered Evaluation**: Uses Google Gemini API for qualitative code assessment
- **Color-Coded Terminal Output**: Enhanced visual feedback with ANSI colors and emojis
- **Intelligent Test Failure Analysis**: Automatic failure detection with debugging recommendations
- **Comprehensive Error Handling**: Robust parsing and validation with detailed logging
- **Google Sheets Integration**: Automatically updates grades in spreadsheets for all assignments
- **SSH Git Integration**: Secure repository cloning with AP-F03 configuration
- **Structured Output & Prompts**: All LLM-based outputs use strict JSON format for reliability
- **CLI Interface**: Command-line interface for easy usage and automation

## 📁 Directory Structure

```
grading_agent/
├── .gitignore                  # Git ignore rules for logs, credentials, etc.
├── .gitattributes             # Git attributes for line endings and binary files
├── LICENSE                     # MIT License
├── config.py                    # Configuration settings
├── main_agent.py               # Main grading workflow with CLI interface
├── langchain_integration.py    # Gemini API integration
├── sheets_updater.py          # Google Sheets integration (supports A1-A6)
├── tools.py                   # Utility functions for PDF reading, test generation
├── prompts.py                 # Centralized prompt templates and format instructions
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
├── grading_outputs/          # JSON grading results with timestamps
├── test_results/             # Test execution results and logs
├── test_generation_logs/     # LLM generation logs and metadata
├── logs/                     # Application logs and debugging information
├── cloned_repos/             # Temporary cloned student repositories
└── student_projects/         # Cloned student repositories
```

## 🚀 Quick Start

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

Place PDF descriptions in the `description/` folder:

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

### 4. Configure Environment

Create a `.env` file with your API key:

```bash
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 5. Generate Test Cases

**CLI Usage:**

```bash
# Generate test cases for A1
python main_agent.py generate A1

# Generate with LLM enhancement and custom number of cases
python main_agent.py generate --llm --num 5 A1

# Generate for all assignments
python main_agent.py generate --llm A1 A2 A3 A4 A5 A6
```

**Python API:**

```python
from tools import generate_testcases_from_description

# Generate test cases for A1
generate_testcases_from_description("A1", num_cases=5, use_llm=True)
```

### 6. Grade Student Assignments

**CLI Usage:**

```bash
# Grade single student for A1
python main_agent.py grade --student student_id --repo https://github.com/student/repo --assignment A1

# Grade for A6 (multi-phase)
python main_agent.py grade --student student_id --repo https://github.com/student/repo --assignment A6

# Batch grade all students from Google Sheets
python main_agent.py grade --student all --assignment A1
```

**Python API:**

```python
from main_agent import grade_student

# Grade a student for A1
result = grade_student("student_id", "A1", "https://github.com/student/repo")
```

## 📋 Usage

### CLI Commands

The grading agent provides a comprehensive CLI interface:

```bash
# Show help
python main_agent.py --help

# Generate test cases
python main_agent.py generate --help
python main_agent.py generate A1
python main_agent.py generate --llm --num 5 A1

# Grade assignments
python main_agent.py grade --help
python main_agent.py grade --student student_id --repo https://github.com/student/repo --assignment A1
python main_agent.py grade --student all --assignment A1
```

### Enhanced Features

#### 🎨 Color-Coded Output

The system provides visually enhanced terminal output with:

- Color-coded status messages
- Emojis for different operations
- Clear phase separation
- Professional formatting

#### 🔍 Intelligent Test Failure Analysis

When tests fail, the system automatically:

- Detects failure types (compilation, runtime, logic errors)
- Provides debugging recommendations with 8-step workflow
- Suggests appropriate debugging tools (gdb, valgrind, cppcheck)
- Calculates impact multipliers for grading

#### 🛠️ Comprehensive Debugging Support

For each test failure, you get:

- Root cause analysis
- Step-by-step debugging workflow
- Tool-specific recommendations
- Code examples and best practices

### Python API Usage

#### Basic Grading

```python
from main_agent import grade_student

# Grade a student for A1
result = grade_student("student_id", "A1", "https://github.com/student/repo")
```

#### Batch Grading

```python
from main_agent import batch_grade_assignments

# Grade all students for A1 from Google Sheets
results = batch_grade_assignments("A1")
```

#### Test Case Generation

```python
from tools import generate_testcases_from_description

# Generate test cases with LLM enhancement
generate_testcases_from_description("A1", num_cases=5, use_llm=True)
```

#### Google Sheets Integration

```python
from sheets_updater import update_student_grade

# Update grades for different assignments
update_student_grade(student_id, grade_data, "A1")
update_student_grade(student_id, grade_data, "A6", "phase1")
```

## 🔄 Grading Process

For each student, the agent follows this comprehensive workflow:

### 1. 📋 Assignment Setup

- **Loads Assignment Description**: Reads and summarizes PDF descriptions from `description/` subdirectories
- **Configures Grading Criteria**: Uses assignment-specific prompts and evaluation criteria

### 2. 🧪 Test Execution

- **Clones Repository**: Downloads student code using SSH with AP-F03 configuration
- **Builds Project**: Compiles code using assignment-specific build commands
- **Runs Tests**: Executes generated test cases and compares outputs using judge scripts
- **Static Analysis**: Runs cppcheck for code quality assessment

### 3. 🔍 Intelligent Analysis

- **Test Failure Analysis**: Automatically detects and categorizes test failures
- **Debugging Recommendations**: Provides 8-step debugging workflow with tool suggestions
- **Impact Assessment**: Calculates grading multipliers based on failure severity

### 4. 🤖 AI Evaluation

Uses Google Gemini API to assess code quality based on assignment-specific criteria:

- **A1**: Logic (iterators, containers), Design (I/O separation, structs)
- **A2**: Data handling, I/O separation, Git practices
- **A3**: Recursive logic, backtracking algorithms
- **A4**: Object-oriented design, multifile organization
- **A5**: Game development, OOP principles
- **A6**: Multi-phase project with web development (Phases 1-3)

### 5. 📊 Results & Reporting

- **Calculates Scores**: Combines test results with qualitative assessment
- **Generates Feedback**: Provides detailed recommendations with code examples
- **Updates Sheets**: Writes all scores and feedback to Google Sheets
- **Color Output**: Displays results with enhanced visual formatting

### Enhanced Output Features

#### 🎨 Visual Feedback

```
============================================================
            🎯 GRADING STUDENT: student_id - A6
============================================================

📋 RUNNING TESTS:
✅ Tests completed: Build successful with 8/10 tests passed

🔬 STATIC ANALYSIS:
✅ Static analysis completed

🔍 ANALYZING TEST FAILURES:
❌ TEST FAILURES DETECTED
============================================================

🔍 FAILURE TYPES IDENTIFIED:
  • Runtime Error
  • Logic Error

🛠️ DEBUGGING RECOMMENDATIONS:
1. Reproduce the Issue: Run the failing test in isolation
2. Gather Information: Collect stack traces and error messages
3. Isolate the Problem: Use debugger to narrow down failure location
...
```

#### 📈 Detailed Grading Results

```
🏗️ PHASE 1 - CORE FEATURES (91 points):
  Login/SignUp: 2.0/2.0 (100.0%)
  Normal Event: 1.5/2.0 (75.0%)
  OOP Design: 1.0/2.0 (50.0%)
  Phase 1 Total: 13.0/91.0 (14.3%)

📋 DETAILED RECOMMENDATIONS:
The code implements basic event management functionality...
**High Priority Issues:** 1. No exception handling...
**Code Example:** Before: `sscanf(...)` After: `if (sscanf(...) != 2) throw...`
```

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

## 🔧 Troubleshooting

### Common Issues & Solutions

#### Build & Compilation Issues

- **Missing Dependencies**: Ensure all required C++ libraries are installed
- **Build Command Errors**: Verify build commands in `config.py` match project structure
- **Judge Script Permissions**: Make judge scripts executable: `chmod +x judge/judge.sh`

#### Test Execution Problems

- **Test Case Format**: Ensure `.in` and `.out` files are properly formatted
- **Path Issues**: Check that test case paths in `config.py` are correct
- **Judge Script Not Found**: Verify judge folder exists for the assignment

#### AI & API Issues

- **Gemini API Errors**: Check `GOOGLE_API_KEY` in `.env` file
- **Rate Limiting**: Add delays between API calls if hitting rate limits
- **Parsing Errors**: Check `test_generation_logs/` for raw API responses

#### Repository & Git Issues

- **SSH Clone Failures**: Verify AP-F03 SSH key configuration
- **Repository Access**: Ensure student repositories are accessible
- **Branch Issues**: Specify correct branch if not using default

#### Google Sheets Integration

- **Authentication Errors**: Verify service account credentials and permissions
- **Sheet Not Found**: Check sheet names in `config.py` match Google Sheets
- **Column Mapping**: Ensure column headers match expected format

### Debug Commands

```bash
# Test CLI functionality
python main_agent.py --help
python main_agent.py generate --help
python main_agent.py grade --help

# Test PDF reading
python -c "from tools import get_practice_descriptions; print(list(get_practice_descriptions('description/').keys()))"

# Test test case generation
python -c "from tools import generate_testcases_from_description; generate_testcases_from_description('A1')"

# Test grading with debug output
python main_agent.py grade --student test_student --repo /path/to/test/repo --assignment A1

# Check logs
tail -f logs/grading_*.log
ls -la test_generation_logs/
ls -la grading_outputs/
```

### Enhanced Debugging Features

#### Test Failure Analysis

When tests fail, the system provides:

- **Failure Type Detection**: Compilation, runtime, logic, or I/O errors
- **Impact Assessment**: Automatic multiplier calculation (0.8x for minor failures, 1.0x for no failures)
- **Debugging Workflow**: 8-step systematic approach to problem resolution

#### Logging & Monitoring

- **Application Logs**: `logs/grading_*.log` with timestamps
- **Test Generation Logs**: `test_generation_logs/` with LLM metadata
- **Grading Outputs**: `grading_outputs/` with complete JSON results
- **Test Results**: `test_results/` with execution details

#### Color Output Issues

- **Terminal Compatibility**: Ensure terminal supports ANSI colors
- **macOS Terminal**: Works with default Terminal and iTerm2
- **Windows**: Use Windows Terminal or enable ANSI support

### Performance Optimization

#### Large Assignments

- **A6 Multi-Phase**: Process phases sequentially to avoid resource conflicts
- **Batch Processing**: Limit concurrent grading to prevent API rate limits
- **Memory Usage**: Monitor memory for large codebases with many files

#### API Optimization

- **Request Batching**: Group similar requests to reduce API calls
- **Caching**: Cache PDF processing results for repeated assignments
- **Retry Logic**: Automatic retry with exponential backoff for transient failures

### Getting Help

1. **Check Logs**: Review `logs/` and `test_generation_logs/` for detailed error information
2. **Test Components**: Use debug commands to isolate issues to specific components
3. **Validate Configuration**: Ensure all paths and credentials in `config.py` are correct
4. **Update Dependencies**: Run `pip install -r requirements.txt` to ensure latest versions

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

## 📦 Dependencies

### Core Requirements

- **Python**: 3.8+ (tested with Python 3.13.1)
- **cppcheck**: Static analysis tool for C/C++ code
- **Git**: Version control for repository cloning

### Python Packages

```
PyMuPDF>=1.23.0          # PDF reading and processing
gspread>=5.0.0           # Google Sheets integration
langchain>=0.1.0         # AI integration framework
python-dotenv>=1.0.0     # Environment variable management
GitPython>=3.1.0         # Git repository operations
colorama>=0.4.0          # Cross-platform colored terminal text
```

### Installation

```bash
pip install -r requirements.txt
```

### System Requirements

- **Memory**: 4GB+ RAM recommended for large assignments
- **Storage**: 2GB+ free space for cloned repositories and logs
- **Network**: Stable internet for API calls and repository cloning

## 🆕 Recent Updates & Improvements

### Version 2.0 Enhancements (September 2025)

#### ✅ Core Features

- **CLI Interface**: Complete command-line interface for all operations
- **Color Output**: Enhanced visual feedback with ANSI colors and emojis
- **Test Failure Analysis**: Intelligent failure detection with debugging recommendations
- **Robust Error Handling**: Comprehensive error recovery and logging
- **Multi-Phase A6 Support**: Enhanced grading for all three A6 phases

#### ✅ Bug Fixes & Stability

- **Critical Bug Fix**: Fixed TypeError in `get_test_failure_impact` function
- **Judge Script Integration**: Improved compatibility with judge scripts
- **Memory Management**: Better handling of large codebases
- **API Reliability**: Enhanced retry logic for Gemini API calls

#### ✅ Testing & Validation

- **Comprehensive Testing**: Validated for all assignment types (A1-A6)
- **Production Ready**: Successfully tested with real student repositories
- **Performance Optimized**: Improved processing speed for large assignments
- **Logging Enhanced**: Detailed logs for debugging and monitoring

#### ✅ User Experience

- **Visual Feedback**: Color-coded terminal output for better readability
- **Debugging Support**: 8-step debugging workflow with tool recommendations
- **Comprehensive Reports**: Detailed grading feedback with code examples
- **Error Recovery**: Graceful handling of various failure scenarios

### CLI Usage Examples

```bash
# Generate test cases with LLM enhancement
python main_agent.py generate --llm --num 5 A1

# Grade single student with full debugging output
python main_agent.py grade --student student123 --repo https://github.com/student/repo --assignment A6

# Batch grade all students for A1
python main_agent.py grade --student all --assignment A1
```

### Output Example

```
============================================================
            🎯 GRADING STUDENT: student123 - A6
============================================================

📋 RUNNING TESTS:
✅ Tests completed: Build successful with 8/10 tests passed

🔍 ANALYZING TEST FAILURES:
❌ TEST FAILURES DETECTED

🛠️ DEBUGGING RECOMMENDATIONS:
1. Reproduce the Issue: Run the failing test in isolation...
2. Gather Information: Collect stack traces and error messages...
...

📊 TEST FAILURE IMPACT:
  Multiplier: 0.8x (Minor test failures - slight impact)

🤖 GENERATING GRADING PROMPT:
✅ Enhanced grading prompt generated (21,162 characters)

============================================================
🏗️ PHASE 1 - CORE FEATURES: 13.0/91.0 (14.3%)
⚡ PHASE 2 - ADVANCED FEATURES: 0.0/15.0 (0.0%)
🌐 PHASE 3 - WEB INTERFACE: 0.0/70.0 (0.0%)
🏆 FINAL GRADE: 13.0/176.0 (7.4%) - Letter Grade: F
============================================================
```

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes and test thoroughly
4. Update documentation as needed
5. Submit a pull request

### Code Standards

- Follow PEP 8 Python style guidelines
- Add comprehensive docstrings
- Include unit tests for new features
- Update README for significant changes

### Testing

- Test all assignment types (A1-A6)
- Validate CLI interface functionality
- Check color output on different terminals
- Verify error handling and recovery

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Last Updated**: September 18, 2025
**Version**: 2.0
**Status**: ✅ Production Ready
