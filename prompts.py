# prompts.py
"""
Centralized prompt management for the grading agent system.
All LLM prompts are defined here for easy modification and maintenance.
"""

from typing import Dict, Any
import json


# =============================================================================
# TEST GENERATION PROMPTS
# =============================================================================


def get_test_generation_prompt(description: str, reqs: dict, num_cases: int) -> str:
    """
    Generate the prompt for LLM-based test case generation.

    Args:
        description: Assignment description text
        reqs: Extracted requirements dictionary
        num_cases: Number of test cases to generate

    Returns:
        Formatted prompt string
    """
    return f"""You are an expert software testing engineer specializing in generating comprehensive test cases for programming assignments.

ASSIGNMENT CONTEXT:
{description}

TECHNICAL REQUIREMENTS:
{json.dumps(reqs, indent=2)}

TASK OBJECTIVE:
Generate exactly {num_cases} high-quality test cases that thoroughly validate this programming assignment.

TEST CASE REQUIREMENTS:
1. Each test case must have realistic input data that a student would provide
2. Each test case must have the exact expected output the program should produce
3. Cover different scenarios: normal operation, edge cases, boundary conditions
4. Consider error handling and invalid inputs where applicable
5. Ensure test cases are diverse and cover different code paths

OUTPUT FORMAT:
Return a valid JSON object with this exact structure:
{{
  "test_cases": [
    {{
      "id": 1,
      "description": "Brief description of what this test case validates",
      "category": "normal|edge|boundary|error",
      "input": "The complete input data as a string (including newlines if needed)",
      "expected_output": "The complete expected output as a string (including newlines if needed)",
      "rationale": "Why this test case is important for validation"
    }}
  ],
  "metadata": {{
    "total_cases": {num_cases},
    "coverage_areas": ["List of features/requirements covered"],
    "complexity_level": "basic|intermediate|advanced"
  }}
}}

IMPORTANT:
- Generate exactly {num_cases} test cases
- Ensure all strings properly escape special characters
- Input and expected_output should be complete and exact
- Use proper JSON formatting with double quotes
- Do not include any text outside the JSON structure"""


# =============================================================================
# GRADING PROMPTS
# =============================================================================


def get_base_grading_prompt(
    practice_description: str, test_results: str, static_analysis: str, source_code: str
) -> str:
    """
    Get the base grading prompt that applies to all assignment types.

    Args:
        practice_description: Description of the assignment
        test_results: Test execution results
        static_analysis: Static analysis results
        source_code: Student source code

    Returns:
        Base grading prompt string
    """
    return f"""
    You are an expert C++ Teaching Assistant with 10+ years of experience grading programming assignments.

    **ASSIGNMENT CONTEXT:**
    {practice_description}

    **GRADING TASK:**
    Analyze the student's C++ code submission based on the assignment requirements above and the established coding standards.

    **ANALYSIS INPUTS:**

    **Test Results:**
    {test_results}

    **Static Analysis (cppcheck):**
    {static_analysis}

    **Source Code:**
    {source_code}

    **GRADING INSTRUCTIONS:**
    1. Carefully analyze the code against the assignment requirements
    2. Consider both functionality (tests) and code quality (static analysis)
    3. Provide specific, actionable feedback in 2-3 sentences
    4. Use evidence from the code to justify your scores
    5. Be fair but thorough in your assessment
    """


def get_a1_grading_criteria() -> str:
    """Get A1-specific grading criteria."""
    return """

    **A1 GRADING CRITERIA:**

    1. **LOGIC - ITERATORS (0-1 point)**
       - Award 1.0: Correct and appropriate use of STL iterators
       - Award 0.5: Some iterator usage but with issues
       - Award 0.0: No iterator usage or incorrect usage

    2. **LOGIC - CONTAINERS (0-1 point)**
       - Award 1.0: Good use of std::vector, std::map
       - Award 0.5: Some container usage
       - Award 0.0: No container usage

    3. **DESIGN - I/O SEPARATION (0-2 points)**
       - Award 2: Clean separation of I/O from logic
       - Award 1: Some separation
       - Award 0: I/O mixed throughout

    4. **DESIGN - STRUCTS (0-1 point)**
       - Award 1.0: Appropriate use of structs
       - Award 0.5: Some struct usage
       - Award 0.0: No structs used

    5. **DESIGN - NO GOD MAIN (0-2 points)**
       - Award 2: Main function is clean (< 20 lines)
       - Award 1: Main is reasonable
       - Award 0: Main is monolithic

    6. **DESIGN - SMALL FUNCTIONS (0-3 points)**
       - Award 3: Functions follow SRP (< 15 lines)
       - Award 2: Functions are reasonable size
       - Award 0-1: Large functions

    7-12. **CLEAN CODING (0-1 point each)**
       - Award 1.0: Excellent practice
       - Award 0.5: Good with minor issues
       - Award 0.0: Poor practice
    """


def get_a2_grading_criteria() -> str:
    """Get A2-specific grading criteria."""
    return """

    **A2 GRADING CRITERIA (Data Handling and Design):**

    **Data Handling (15 points):**
    - Reading Input (5pts): Proper input reading techniques, error handling for invalid input
    - Storing Information & Data Structures (10pts): Appropriate use of data structures, efficient storage

    **Design (28 points):**
    - Separate I/O from Logic (8pts): Clean separation of input/output from business logic
    - No Godly Main (10pts): Main function should be clean and delegate to other functions
    - Small Functions and Single Responsibility (10pts): Functions should be focused and not too long

    **Clean Coding (28 points):**
    - No Duplication (7pts): Avoid code duplication through proper abstraction
    - Magic Values / No Global Variables (7pts): Use constants instead of magic numbers, avoid global variables
    - Naming (7pts): Clear, descriptive variable and function names
    - Consistency (7pts): Consistent coding style and formatting

    **Git (7 points):**
    - Commit Messages (4pts): Clear, descriptive commit messages
    - Standard Commits (3pts): Follow conventional commit format

    **Correctness (30 points):**
    - Test Cases (20pts): Comprehensive test coverage, edge cases handled properly
    """


def get_a3_grading_criteria() -> str:
    """Get A3-specific grading criteria."""
    return """

    **A3 GRADING CRITERIA:**

    **Questions 1-4 (71 points total):**
    - Each question has: Recursive Logic (2pts), Test Cases (15pts for Q1-3, 10pts for Q4), Upload Testcases (2pts)
    - Award full points for correct recursive/backtracking implementation
    - Award proportional points for partial implementation

    **Design (20 points):**
    - I/O Separation (1pt), Data Structures (3pts), No God Main (1pt), Small Functions (2pts)
    - No Duplication (1pt), Indentation (1pt), Magic Values (1pt), Naming (1pt), Consistency (1pt)

    **Git (6 points):**
    - Commit Messages (1pt), Standard Commits (1pt)
    - Award for proper commit message format and conventional commits
    """


def get_a4_grading_criteria() -> str:
    """Get A4-specific grading criteria."""
    return """

    **A4 GRADING CRITERIA:**

    **Object Oriented Design (53 points):**
    - Break into Classes (5pts), Responsibility Assignment (5pts), Field Assignment (5pts)
    - Public/Private Access Modifiers (3pts), No Logic in Main (3pts), Small Functions (2pts)

    **Clean Coding (10 points):**
    - No Duplication, Indentation, Magic Values, Naming, Consistency (1pt each)

    **Multifile (10 points):**
    - Break into Files, Header Guards, Makefile (1pt each)

    **Git (5 points):**
    - Commit Messages, Standard Commits (1pt each)
    """


def get_a5_grading_criteria() -> str:
    """Get A5-specific grading criteria."""
    return """

    **A5 GRADING CRITERIA (Tower Defense Game):**

    **Design (56 points):**
    - Attack Wave (6pts), Normal Tower (5pts), Ice Tower (7pts), Bomb Tower (7pts)
    - Tower Domain Visibility (5pts), Normal Balloon (5pts), Pregnant Balloon (7pts)
    - Panel (4pts), Launch Control (5pts), Players Health Panel (2pts)
    - Music (2pts), Game End (1pt)

    **Object Oriented Design (14 points):**
    - Break into Classes (5pts), Encapsulation (5pts), Small Functions (2pts)
    - No Duplication (1pt), Indentation (1pt)

    **Clean Coding & Git (21 points):**
    - Clean: Magic Values, Naming, Consistency (1pt each)
    - Git: Break Files, Header Guards, Makefile, Commit Messages, Standard Commits (1pt each)
    """


def get_a6_grading_criteria() -> str:
    """Get A6-specific grading criteria."""
    return """

    **A6 GRADING CRITERIA (Event Management System - Multi-Phase):**

    **Phase 1 - Core Features (91 points):**
    - Login/SignUp (2pts), Normal Event (2pts), Periodic Event (2pts), Task (2pts)
    - Object Oriented Design (2pts), No God Class (1pt), Polymorphism (2pts), No Downcast (1pt)
    - Encapsulation (2pts), Separate I/O (1pt), Exception Handling (2pts), No Duplication (2pts)
    - Indentation (1pt), Magic Values (1pt), Naming (3pts), Consistency (3pts)
    - Break into Files (1pt), Makefile (1pt), Test Cases (30pts)

    **Phase 2 - Feature Addition (100 points):**
    - Add Joint Event (2pts), See Joint Event Requests (2pts), Reject/Confirm Joint Event (2pts)
    - Change Report Cmd (2pts), Polymorphism (2pts), No Downcast (1pt), No Duplication (2pts)
    - Indentation (2pts), Naming (2pts), Consistency (2pts), Test Cases (15pts)

    **Phase 3 - Web Interface (110 points):**
    - Signup/Login/Home/Logout Pages (2pts each), Task operations (2pts each)
    - Event operations (2pts each), Report (3pts), HTML Render (3pts), Handlers (3pts)
    - CSS (2pts), JS (1pt), Makefile (2pts), Clean Coding (30pts), Bonus (10pts), Multifile (5pts)
    """


# Grading criteria mapping
GRADING_CRITERIA = {
    "A1": get_a1_grading_criteria,
    "A2": get_a2_grading_criteria,
    "A3": get_a3_grading_criteria,
    "A4": get_a4_grading_criteria,
    "A5": get_a5_grading_criteria,
    "A6": get_a6_grading_criteria,
}


def get_grading_prompt(
    assignment_type: str,
    practice_description: str,
    test_results: str,
    static_analysis: str,
    source_code: str,
) -> str:
    """
    Get the complete grading prompt for a specific assignment type.

    Args:
        assignment_type: Type of assignment (A1, A2, A3, A4, A5, A6)
        practice_description: Assignment description
        test_results: Test execution results
        static_analysis: Static analysis results
        source_code: Student source code

    Returns:
        Complete grading prompt string
    """
    base_prompt = get_base_grading_prompt(
        practice_description, test_results, static_analysis, source_code
    )

    # Get assignment-specific criteria
    criteria_func = GRADING_CRITERIA.get(assignment_type)
    if criteria_func:
        return base_prompt + criteria_func()
    else:
        return base_prompt


# =============================================================================
# FORMAT INSTRUCTIONS
# =============================================================================


def get_format_instructions(assignment_type: str, grading_model: Any) -> str:
    """
    Get format instructions for LLM responses.

    Args:
        assignment_type: Type of assignment
        grading_model: Pydantic model for grading output

    Returns:
        Format instructions string
    """
    return f"""
    CRITICAL: Respond ONLY with a valid JSON object. No markdown, no explanations, no additional text.

    Required JSON format for {assignment_type}:
    {grading_model.model_json_schema()}

    Scoring Guidelines:
    - Use decimal scores (e.g., 3.5, 7.2) for partial credit
    - Be precise and consistent in scoring
    - Base scores on evidence from the code
    - For multi-phase assignments (A6), evaluate each phase separately
    """


# =============================================================================
# PROMPT CONFIGURATION
# =============================================================================

# Default prompt settings that can be easily modified
PROMPT_CONFIG = {
    "test_generation": {"temperature": 0.7, "max_tokens": 4096, "model": "gemini-pro"},
    "grading": {"temperature": 0.1, "max_tokens": 4096, "model": "gemini-pro"},
}


def update_prompt_config(config_updates: Dict[str, Any]) -> None:
    """
    Update prompt configuration settings.

    Args:
        config_updates: Dictionary of configuration updates
    """
    global PROMPT_CONFIG
    PROMPT_CONFIG.update(config_updates)


def get_prompt_config() -> Dict[str, Any]:
    """Get current prompt configuration."""
    return PROMPT_CONFIG.copy()
