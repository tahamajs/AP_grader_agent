# prompts.py
"""
Centralized prompt management for the grading agent system.
All LLM prompts are defined here for easy modification and maintenance.
"""

from typing import Dict, Any, Callable, Optional
import json
import re
import os
import logging

# Setup logging for prompts module
logger = logging.getLogger(__name__)


# -----------------------------
# LLM RESPONSE PARSING HELPERS
# -----------------------------


def _normalize_llm_output(text: str) -> str:
    """Strip common markdown/code fences and whitespace from LLM output."""
    if not isinstance(text, str):
        return text

    t = text.strip()
    # Remove triple backtick code fences with optional language
    t = re.sub(r"^```[a-zA-Z0-9]*\n", "", t)
    t = re.sub(r"\n```$", "", t)

    # Remove leading and trailing single backticks
    t = t.strip("`")

    return t.strip()


def _attempt_json_fixup(text: str) -> Optional[dict]:
    """Try some heuristics to recover JSON from common LLM formatting issues.

    Returns parsed dict on success or None on failure.
    """
    # Fast try
    try:
        return json.loads(text)
    except Exception:
        pass

    # Heuristic: extract the largest {...} block
    brace_matches = list(re.finditer(r"\{", text))
    if not brace_matches:
        return None

    # find last closing brace
    last_close = text.rfind("}")
    first_open = brace_matches[0].start()
    candidate = text[first_open : last_close + 1]

    # Remove trailing commas before } or ]
    candidate = re.sub(r",\s*(\}|\])", r"\1", candidate)

    try:
        return json.loads(candidate)
    except Exception:
        return None


def parse_and_validate_response(
    response_text: str,
    validator: Optional[Callable[[dict], Any]] = None,
    description: Optional[str] = None,
    save_raw_to: Optional[str] = None,
) -> dict:
    """Robustly parse JSON from an LLM response and optionally validate it.

    Args:
        response_text: Raw text from the LLM.
        validator: Optional callable that receives the parsed dict and
            should raise an exception if validation fails (e.g. Pydantic model).
        description: Short description used in error messages for context.
        save_raw_to: Optional file path to save the raw response for debugging.

    Returns:
        Parsed JSON as Python dict.

    Raises:
        ValueError with helpful diagnostic information when parsing or validation fails.
    """
    txt = _normalize_llm_output(response_text)

    # Save raw response if requested
    if save_raw_to:
        try:
            os.makedirs(os.path.dirname(save_raw_to), exist_ok=True)
            with open(save_raw_to, "w", encoding="utf-8") as f:
                f.write(response_text)
        except Exception as save_err:
            logger.warning(f"Failed to save raw response to {save_raw_to}: {save_err}")

    # Try direct parse
    try:
        parsed = json.loads(txt)
    except Exception as e1:
        # Try heuristics/fixup
        parsed = _attempt_json_fixup(txt)
        if parsed is None:
            ctx = f" for {description}" if description else ""
            raise ValueError(
                f"Failed to parse JSON response{ctx}: {e1}\nRaw: {txt[:1000]}"
            )

    # Handle common LLM formatting issues where properties are wrapped
    if isinstance(parsed, dict) and "properties" in parsed and len(parsed) == 1:
        # Check if this looks like a JSON schema response that wrapped the actual data
        properties_data = parsed["properties"]
        if isinstance(properties_data, dict):
            # Look for grading-related field names to confirm this is the wrapped case
            grading_fields = [
                k
                for k in properties_data.keys()
                if k.startswith(("p1_", "p2_", "p3_")) or k in ["generated_comment"]
            ]
            if grading_fields:
                logger.info(
                    f"Detected wrapped 'properties' structure, unwrapping for {description}"
                )
                parsed = properties_data

    # Optionally validate using provided callable
    if validator:
        try:
            validator(parsed)
        except Exception as ve:
            ctx = f" for {description}" if description else ""
            raise ValueError(
                f"Validation failed{ctx}: {ve}\nParsed: {json.dumps(parsed)[:1000]}"
            )

    return parsed


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
    Analyze the student's C++ code submission comprehensively. You MUST read and analyze ALL provided code files, including:
    - Header files (.h, .hpp)
    - Implementation files (.cpp)
    - Makefiles
    - Test files
    - Any other source files

    **CRITICAL ANALYSIS REQUIREMENTS:**
    1. **READ ALL CODE**: Examine every file provided, not just the main file
    2. **CODE ORGANIZATION**: Check file structure, header guards, includes
    3. **DESIGN PATTERNS**: Evaluate class design, inheritance, polymorphism
    4. **ERROR HANDLING**: Assess exception handling and input validation
    5. **CODE QUALITY**: Review naming, documentation, consistency
    6. **FUNCTIONALITY**: Verify all required features are implemented
    7. **TESTING**: Evaluate test coverage and test quality

    **COMPREHENSIVE FILE ANALYSIS:**
    - **Header Files**: Check for proper declarations, header guards, include directives
    - **Implementation Files**: Verify implementations match declarations, proper includes
    - **Main File**: Assess command-line interface, user interaction, error handling
    - **Test Files**: Evaluate test coverage, test quality, edge cases
    - **Build System**: Check Makefile completeness, compilation flags, targets
    - **Documentation**: Review README, code comments, inline documentation

    **ANALYSIS INPUTS:**

    **Test Results:**
    {test_results}

    **Static Analysis (cppcheck/valgrind):**
    {static_analysis}

    **Source Code (ALL FILES):**
    {source_code}

    **GRADING METHODOLOGY:**
    1. **Systematic Review**: Go through each file systematically
    2. **Cross-Reference**: Check consistency between header and implementation files
    3. **Functionality Verification**: Use test results to verify implemented features
    4. **Code Quality Assessment**: Use static analysis to identify potential issues
    5. **Design Evaluation**: Assess overall architecture and design patterns
    6. **Best Practices**: Check adherence to C++ best practices and standards

    **EVALUATION FRAMEWORK:**
    - **Functionality (40%)**: Does the code work as required?
    - **Design (25%)**: Is the code well-structured and maintainable?
    - **Code Quality (20%)**: Is the code clean, readable, and consistent?
    - **Testing (10%)**: Is the code properly tested?
    - **Documentation (5%)**: Is the code well-documented?

    **GRADING INSTRUCTIONS:**
    1. Carefully analyze ALL code files against assignment requirements
    2. Consider functionality (tests), code quality (static analysis), and design
    3. Provide specific, actionable recommendations for improvement
    4. Use evidence from the code to justify scores and suggestions
    5. Be thorough but fair in assessment
    6. Focus on both what works well and what needs improvement
    7. Provide concrete examples of good practices and problematic code
    8. Reference specific files and line numbers when possible
    9. Prioritize recommendations by importance and impact
    10. Suggest specific code changes with before/after examples
    """


def get_a1_grading_criteria() -> str:
    """Get A1-specific grading criteria with detailed recommendations."""
    return """

    **A1 GRADING CRITERIA (Basic C++ Programming):**

    **Logic - Iterators (1 point):**
    - Award 1.0: Correct and appropriate use of STL iterators for container traversal
      * Award 1.0: Proper iterator usage with range-based loops or traditional iterators
      * Award 0.5: Some iterator usage but with syntax errors or incorrect usage
      * Award 0.0: No iterator usage or incorrect iterator syntax

    **Logic - Containers (1 point):**
    - Award 1.0: Good use of std::vector, std::map, or other STL containers
      * Award 1.0: Appropriate container selection and usage for the problem
      * Award 0.5: Some container usage but not optimal choice or incorrect usage
      * Award 0.0: No container usage, using arrays or poor data structures

    **Design - I/O Separation (2 points):**
    - Award 2.0: Clean separation of input/output from business logic
      * Award 2.0: I/O operations completely separated into dedicated functions
      * Award 1.0: Some separation but I/O mixed with logic in places
      * Award 0.0: I/O operations mixed throughout the code with business logic

    **Design - Structs (1 point):**
    - Award 1.0: Appropriate use of structs for data organization
      * Award 1.0: Well-designed structs with meaningful member names
      * Award 0.5: Some struct usage but poor design or naming
      * Award 0.0: No structs used, using individual variables instead

    **Design - No God Main (2 points):**
    - Award 2.0: Main function is clean and focused (< 20 lines)
      * Award 2.0: Main function delegates to other functions, very clean
      * Award 1.0: Main function is reasonable but could be cleaner
      * Award 0.0: Main function is monolithic, doing too much work

    **Design - Small Functions (3 points):**
    - Award 3.0: Functions follow Single Responsibility Principle (< 15 lines)
      * Award 3.0: All functions are focused and appropriately sized
      * Award 2.0: Most functions are reasonable size with some exceptions
      * Award 1.0: Some large functions but overall acceptable
      * Award 0.0: Large functions that violate SRP principles

    **Clean Coding (6 points - 1 point each):**
    - No Duplication (1pt): DRY principle followed
    - Indentation (1pt): Consistent formatting
    - Magic Values (1pt): No hardcoded constants
    - Naming (1pt): Clear, descriptive names
    - Consistency (1pt): Consistent coding style
    - Comments (1pt): Appropriate code documentation

    **COMPREHENSIVE ANALYSIS REQUIREMENTS:**

    **File-by-File Analysis:**
    - **main.cpp**: Check main function structure, function calls, overall program flow
    - **Any header files**: Evaluate struct definitions, function declarations
    - **Makefile**: Verify build system if present

    **Code Quality Assessment:**
    - STL usage correctness and appropriateness
    - Function decomposition and responsibility assignment
    - Code readability and maintainability
    - Error handling and input validation

    **RECOMMENDATION GUIDELINES:**
    For each criterion where points are deducted, provide specific recommendations:
    - **What** is wrong or missing (with file/line references)
    - **Why** it matters for code quality/maintainability
    - **How** to fix it with concrete code examples
    - **Priority** level (High/Medium/Low) for the fix

    **EXAMPLE RECOMMENDATIONS:**
    - **High Priority**: No iterator usage - Replace manual array indexing with STL iterators
    - **Medium Priority**: Monolithic main function - Break down into smaller, focused functions
    - **Low Priority**: Inconsistent indentation - Use consistent 4-space indentation

    **CODE IMPROVEMENT EXAMPLES:**
    - **Before**: `for(int i = 0; i < vec.size(); i++) { cout << vec[i] << endl; }`
      **After**: `for(auto& item : vec) { cout << item << endl; }`
    - **Before**: Large main function with all logic
      **After**: `int main() { readInput(); processData(); displayOutput(); return 0; }`
    - **Before**: `if(x > 100)` → **After**: `const int MAX_VALUE = 100; if(x > MAX_VALUE)`

    **BEST PRACTICES FOR A1:**
    - Use range-based for loops when possible
    - Choose appropriate STL containers for the problem
    - Keep functions focused on single responsibilities
    - Use meaningful variable and function names
    - Add comments for complex logic
    - Avoid magic numbers by using named constants
    """


def get_a2_grading_criteria() -> str:
    """Get A2-specific grading criteria with detailed recommendations."""
    return """

    **A2 GRADING CRITERIA (Data Handling and Design):**

    **Data Handling (15 points):**
    - Reading Input (5pts): Proper input reading techniques with error handling
      * Award 5.0: Robust input reading with validation and error recovery
      * Award 4.0: Good input handling with some validation
      * Award 3.0: Basic input reading but missing error handling
      * Award 2.0: Poor input handling with potential crashes
      * Award 0.0: No input reading or major issues
    - Storing Information & Data Structures (10pts): Appropriate data structure usage
      * Award 10.0: Optimal data structure selection and efficient storage
      * Award 8.0: Good data structure choices with minor inefficiencies
      * Award 6.0: Acceptable data structures but not optimal
      * Award 4.0: Poor data structure choices affecting performance
      * Award 0.0: Inappropriate data structures or no data storage

    **Design (28 points):**
    - Separate I/O from Logic (8pts): Clean separation of concerns
      * Award 8.0: Complete separation, I/O in dedicated functions/classes
      * Award 6.0: Good separation with minor mixing
      * Award 4.0: Some separation but significant mixing
      * Award 0.0: I/O and logic completely intertwined
    - No Godly Main (10pts): Main function delegation and cleanliness
      * Award 10.0: Main function < 10 lines, perfect delegation
      * Award 8.0: Main function clean and focused
      * Award 6.0: Main function reasonable but could be cleaner
      * Award 4.0: Main function too long but functional
      * Award 0.0: Monolithic main function doing everything
    - Small Functions and Single Responsibility (10pts): Function design quality
      * Award 10.0: All functions follow SRP, < 15 lines each
      * Award 8.0: Most functions well-designed
      * Award 6.0: Some large functions but acceptable
      * Award 4.0: Several functions too large
      * Award 0.0: No function decomposition, everything in main

    **Clean Coding (28 points):**
    - No Duplication (7pts): DRY principle adherence
      * Award 7.0: No code duplication, perfect abstraction
      * Award 5.0: Minimal duplication, good reuse
      * Award 3.0: Some duplication but manageable
      * Award 0.0: Significant code duplication
    - Magic Values / No Global Variables (7pts): Constants and scoping
      * Award 7.0: All constants defined, no global variables
      * Award 5.0: Most constants defined, few globals
      * Award 3.0: Some magic numbers remain
      * Award 0.0: Magic numbers throughout, global variables
    - Naming (7pts): Variable and function naming quality
      * Award 7.0: Excellent descriptive names throughout
      * Award 5.0: Good naming with minor issues
      * Award 3.0: Acceptable naming but some unclear names
      * Award 0.0: Poor naming, abbreviations, unclear variables
    - Consistency (7pts): Code style and formatting consistency
      * Award 7.0: Highly consistent style across all code
      * Award 5.0: Mostly consistent with minor variations
      * Award 3.0: Some inconsistencies in style
      * Award 0.0: Inconsistent style, different conventions

    **Git (7 points):**
    - Commit Messages (4pts): Quality and descriptiveness of commits
      * Award 4.0: Clear, descriptive commit messages
      * Award 3.0: Good messages with minor issues
      * Award 2.0: Basic messages but acceptable
      * Award 0.0: Poor or missing commit messages
    - Standard Commits (3pts): Conventional commit format usage
      * Award 3.0: Proper conventional commit format
      * Award 2.0: Mostly following conventions
      * Award 1.0: Some conventional commits
      * Award 0.0: No conventional commit usage

    **Correctness (30 points):**
    - Test Cases (20pts): Test coverage and quality
      * Award 20.0: Comprehensive tests covering all scenarios
      * Award 15.0: Good test coverage with edge cases
      * Award 10.0: Basic test coverage
      * Award 5.0: Minimal testing
      * Award 0.0: No tests or failing tests
    - Functionality (10pts): Program correctness
      * Award 10.0: All requirements met, handles all cases
      * Award 8.0: Most requirements met with minor issues
      * Award 6.0: Core functionality works but missing features
      * Award 4.0: Basic functionality with major issues
      * Award 0.0: Program doesn't work or crashes

    **COMPREHENSIVE ANALYSIS REQUIREMENTS:**

    **File-by-File Analysis:**
    - **main.cpp**: Evaluate main function structure and delegation
    - **Data handling files**: Check input reading and data structure usage
    - **Header files**: Review struct/class definitions and function declarations
    - **Test files**: Assess test coverage and quality

    **Data Structure Evaluation:**
    - Appropriateness for the problem domain
    - Efficiency considerations (time/space complexity)
    - Memory management and resource usage
    - Scalability and extensibility

    **RECOMMENDATION GUIDELINES:**
    For each criterion where points are deducted, provide specific recommendations:
    - **What** is wrong or missing (with file/line references)
    - **Why** it matters for code quality/maintainability
    - **How** to fix it with concrete code examples
    - **Priority** level (High/Medium/Low) for the fix

    **EXAMPLE RECOMMENDATIONS:**
    - **High Priority**: No input validation - Add validation checks to prevent crashes from invalid input
    - **Medium Priority**: Poor data structure choice - Replace array with std::vector for dynamic sizing
    - **Low Priority**: Inconsistent naming - Use camelCase consistently for variable names

    **CODE IMPROVEMENT EXAMPLES:**
    - **Before**: `int arr[100];` → **After**: `std::vector<int> data;`
    - **Before**: `if(cin >> x)` → **After**: `if(!(cin >> x)) { cerr << "Invalid input" << endl; return 1; }`
    - **Before**: `const int SIZE = 100;` scattered throughout → **After**: Define in header file with descriptive name

    **DATA HANDLING BEST PRACTICES:**
    - Use std::vector for dynamic arrays
    - Implement proper error handling for file I/O
    - Validate all user input before processing
    - Choose data structures based on access patterns
    - Consider memory efficiency for large datasets
    """


def get_a3_grading_criteria() -> str:
    """Get A3-specific grading criteria with detailed recommendations."""
    return """

    **A3 GRADING CRITERIA (Recursion and Backtracking):**

    **Questions 1-4 (71 points total):**
    - Each question has specific requirements for recursive/backtracking logic and test cases
    - Recursive Logic (2pts per question): Correct recursive implementation
      * Award 2.0: Perfect recursive solution with proper base cases and recursive calls
      * Award 1.0: Mostly correct recursion but minor issues
      * Award 0.0: No recursion or incorrect recursive logic
    - Test Cases (15pts for Q1-3, 10pts for Q4): Test coverage and quality
      * Award full: Comprehensive test cases covering edge cases and normal scenarios
      * Award proportional: Partial test coverage or quality issues
      * Award 0: No test cases or failing tests
    - Upload Testcases (2pts per question): Proper test case submission
      * Award 2.0: Well-formatted test cases with clear expected outputs
      * Award 1.0: Test cases submitted but formatting issues
      * Award 0.0: No test cases uploaded

    **Design (20 points):**
    - I/O Separation (1pt): Clean separation of input/output
      * Award 1.0: I/O operations properly separated
      * Award 0.0: I/O mixed with business logic
    - Data Structures (3pts): Appropriate data structure usage
      * Award 3.0: Optimal data structures for the algorithms
      * Award 2.0: Good data structure choices
      * Award 1.0: Acceptable but not optimal
      * Award 0.0: Poor data structure choices
    - No God Main (1pt): Clean main function
      * Award 1.0: Main function focused and clean
      * Award 0.0: Monolithic main function
    - Small Functions (2pts): Function size and responsibility
      * Award 2.0: Functions follow SRP principles
      * Award 1.0: Some large functions but acceptable
      * Award 0.0: Very large functions violating SRP
    - No Duplication (1pt): DRY principle followed
      * Award 1.0: No code duplication
      * Award 0.0: Significant duplication present
    - Indentation (1pt): Consistent formatting
      * Award 1.0: Consistent indentation throughout
      * Award 0.0: Inconsistent formatting
    - Magic Values (1pt): No hardcoded constants
      * Award 1.0: Constants properly defined
      * Award 0.0: Magic numbers in code
    - Naming (1pt): Clear, descriptive names
      * Award 1.0: Excellent naming conventions
      * Award 0.0: Poor or unclear names
    - Consistency (1pt): Consistent coding style
      * Award 1.0: Highly consistent style
      * Award 0.0: Inconsistent style

    **Git (6 points):**
    - Commit Messages (1pt): Quality commit messages
      * Award 1.0: Clear, descriptive commit messages
      * Award 0.0: Poor commit messages
    - Standard Commits (1pt): Conventional commit format
      * Award 1.0: Proper conventional commit usage
      * Award 0.0: No conventional commits

    **COMPREHENSIVE ANALYSIS REQUIREMENTS:**

    **Algorithm Analysis:**
    - **Recursive Correctness**: Proper base cases, recursive calls, and termination
    - **Backtracking Logic**: Correct implementation of backtracking algorithms
    - **Time Complexity**: Analysis of algorithm efficiency
    - **Space Complexity**: Memory usage evaluation

    **File-by-File Analysis:**
    - **main.cpp**: Check main function and program structure
    - **Solution files**: Evaluate recursive function implementations
    - **Test files**: Assess test coverage and correctness
    - **Header files**: Review function declarations and data structures

    **RECOMMENDATION GUIDELINES:**
    For each criterion where points are deducted, provide specific recommendations:
    - **What** is wrong or missing (with file/line references)
    - **Why** it matters for algorithm correctness/efficiency
    - **How** to fix it with concrete code examples
    - **Priority** level (High/Medium/Low) for the fix

    **EXAMPLE RECOMMENDATIONS:**
    - **High Priority**: Missing base case in recursive function - Add proper termination condition
    - **Medium Priority**: Inefficient backtracking - Optimize with pruning or memoization
    - **Low Priority**: Poor variable naming - Use descriptive names for recursive parameters

    **CODE IMPROVEMENT EXAMPLES:**
    - **Before**: `if(n == 0) return 1; return n * factorial(n-1);`
      **After**: `if(n <= 1) return 1; return n * factorial(n-1);`
    - **Before**: No memoization → **After**: `std::vector<int> memo(100, -1); if(memo[n] != -1) return memo[n];`
    - **Before**: `for(int i = 0; i < candidates.size(); i++)`
      **After**: `for(size_t i = 0; i < candidates.size(); ++i)`

    **RECURSION BEST PRACTICES:**
    - Always define clear base cases
    - Ensure recursive calls progress toward base case
    - Consider stack overflow for deep recursion
    - Use memoization for optimization when applicable
    - Test with edge cases (empty input, single element, maximum size)
    - Document recursive logic with comments

    **BACKTRACKING PATTERNS:**
    - Include/exclude decisions
    - Permutation generation
    - Combination finding
    - Path finding in grids/mazes
    - Constraint satisfaction problems
    """


def get_a4_grading_criteria() -> str:
    """Get A4-specific grading criteria with detailed recommendations."""
    return """

    **A4 GRADING CRITERIA (Object-Oriented Programming):**

    **Object Oriented Design (53 points):**
    - Break into Classes (5pts): Proper class structure and organization
      * Award 5.0: Well-designed class hierarchy with clear responsibilities
      * Award 4.0: Good class structure with minor issues
      * Award 3.0: Some classes but poor organization
      * Award 2.0: Few classes, mostly procedural
      * Award 0.0: No class structure, all code in main
    - Responsibility Assignment (5pts): Single Responsibility Principle
      * Award 5.0: Each class has clear, single responsibility
      * Award 4.0: Most classes follow SRP
      * Award 3.0: Some classes have multiple responsibilities
      * Award 0.0: Classes doing too many unrelated things
    - Field Assignment (5pts): Proper member variable design
      * Award 5.0: Appropriate fields with correct access modifiers
      * Award 4.0: Good field design with minor issues
      * Award 3.0: Some fields but poor design
      * Award 0.0: No member variables or poor field usage
    - Public/Private Access Modifiers (3pts): Encapsulation implementation
      * Award 3.0: Proper use of public/private/protected
      * Award 2.0: Mostly correct access modifiers
      * Award 1.0: Some incorrect access modifiers
      * Award 0.0: All members public or no encapsulation
    - No Logic in Main (3pts): Main function cleanliness
      * Award 3.0: Main function only creates objects and calls methods
      * Award 2.0: Main function mostly clean
      * Award 1.0: Some logic in main but acceptable
      * Award 0.0: Complex logic in main function
    - Small Functions (2pts): Method size and focus
      * Award 2.0: All methods follow SRP (< 15 lines)
      * Award 1.0: Some large methods but acceptable
      * Award 0.0: Very large methods violating SRP

    **Clean Coding (10 points):**
    - No Duplication (1pt): DRY principle followed
      * Award 1.0: No code duplication
      * Award 0.0: Significant duplication present
    - Indentation (1pt): Consistent formatting
      * Award 1.0: Consistent indentation
      * Award 0.0: Inconsistent formatting
    - Magic Values (1pt): No hardcoded constants
      * Award 1.0: Constants properly defined
      * Award 0.0: Magic numbers throughout
    - Naming (1pt): Clear, descriptive names
      * Award 1.0: Excellent naming for classes/methods/variables
      * Award 0.0: Poor naming conventions
    - Consistency (1pt): Consistent coding style
      * Award 1.0: Highly consistent OOP style
      * Award 0.0: Inconsistent style

    **Multifile (10 points):**
    - Break into Files (1pt): Proper file organization
      * Award 1.0: Logical file separation (header/implementation)
      * Award 0.0: All code in one file
    - Header Guards (1pt): Proper header protection
      * Award 1.0: Correct #ifndef/#define/#endif guards
      * Award 0.0: Missing or incorrect header guards
    - Makefile (1pt): Build system completeness
      * Award 1.0: Complete Makefile with all targets
      * Award 0.0: No Makefile or incomplete

    **Git (5 points):**
    - Commit Messages (1pt): Quality commit messages
      * Award 1.0: Clear, descriptive messages
      * Award 0.0: Poor commit messages
    - Standard Commits (1pt): Conventional commit format
      * Award 1.0: Proper conventional commits
      * Award 0.0: No conventional commit usage

    **COMPREHENSIVE ANALYSIS REQUIREMENTS:**

    **OOP Design Evaluation:**
    - **Class Design**: Inheritance, composition, and relationship appropriateness
    - **Encapsulation**: Data hiding and interface design
    - **Polymorphism**: Virtual functions and dynamic binding usage
    - **Abstraction**: Appropriate use of abstract classes and interfaces

    **File-by-File Analysis:**
    - **Header files (.h/.hpp)**: Class declarations, member functions, inheritance
    - **Implementation files (.cpp)**: Method implementations, constructor/destructor logic
    - **main.cpp**: Object instantiation and high-level program flow
    - **Makefile**: Build system and compilation organization

    **RECOMMENDATION GUIDELINES:**
    For each criterion where points are deducted, provide specific recommendations:
    - **What** is wrong or missing (with file/line references)
    - **Why** it matters for OOP design and maintainability
    - **How** to fix it with concrete code examples
    - **Priority** level (High/Medium/Low) for the fix

    **EXAMPLE RECOMMENDATIONS:**
    - **High Priority**: All members public - Implement proper encapsulation with private members and public accessors
    - **Medium Priority**: Large methods in classes - Break down into smaller, focused methods
    - **Low Priority**: Missing header guards - Add proper #ifndef/#define/#endif protection

    **CODE IMPROVEMENT EXAMPLES:**
    - **Before**: `class MyClass { public: int data; void process(); };`
      **After**: `class MyClass { private: int data_; public: int getData() const { return data_; } void setData(int value) { data_ = value; } void process(); };`
    - **Before**: Large method doing multiple things
      **After**: `void process() { validateInput(); performCalculation(); updateState(); }`
    - **Before**: `#include "myclass.h"` without guards
      **After**: `#ifndef MYCLASS_H #define MYCLASS_H ... #endif`

    **OOP BEST PRACTICES:**
    - Use meaningful class names (PascalCase)
    - Implement proper encapsulation
    - Follow Single Responsibility Principle
    - Use inheritance for "is-a" relationships
    - Prefer composition over inheritance when appropriate
    - Provide clear public interfaces
    - Use const correctness for methods that don't modify state
    - Implement RAII (Resource Acquisition Is Initialization)
    """


def get_a5_grading_criteria() -> str:
    """Get A5-specific grading criteria with detailed recommendations."""
    return """

    **A5 GRADING CRITERIA (Tower Defense Game):**

    **Design (56 points):**
    - Attack Wave (6pts): Wave spawning system implementation
      * Award 6.0: Complete wave system with proper timing and enemy spawning
      * Award 4.0: Basic wave functionality with minor issues
      * Award 2.0: Partial wave implementation
      * Award 0.0: No wave system or major issues
    - Normal Tower (5pts): Basic tower functionality
      * Award 5.0: Complete tower with shooting, targeting, and upgrades
      * Award 4.0: Good tower implementation with minor issues
      * Award 3.0: Basic tower functionality
      * Award 0.0: No tower or incomplete implementation
    - Ice Tower (7pts): Specialized tower with freezing effect
      * Award 7.0: Complete ice tower with freezing mechanics and visual effects
      * Award 5.0: Ice tower with basic freezing but missing features
      * Award 3.0: Partial ice tower implementation
      * Award 0.0: No ice tower or major issues
    - Bomb Tower (7pts): Area damage tower implementation
      * Award 7.0: Complete bomb tower with area damage and effects
      * Award 5.0: Bomb tower with basic damage but missing area effect
      * Award 3.0: Partial bomb tower implementation
      * Award 0.0: No bomb tower or major issues
    - Tower Domain Visibility (5pts): Tower placement and range visualization
      * Award 5.0: Complete placement system with range indicators
      * Award 4.0: Good placement with minor visualization issues
      * Award 3.0: Basic placement but poor visualization
      * Award 0.0: No placement system or broken
    - Normal Balloon (5pts): Basic enemy implementation
      * Award 5.0: Complete balloon with movement, health, and pathfinding
      * Award 4.0: Good balloon with minor issues
      * Award 3.0: Basic balloon movement
      * Award 0.0: No balloon or broken movement
    - Pregnant Balloon (7pts): Advanced enemy with spawning mechanics
      * Award 7.0: Complete pregnant balloon with child spawning
      * Award 5.0: Pregnant balloon with basic spawning
      * Award 3.0: Partial pregnant balloon
      * Award 0.0: No pregnant balloon or broken
    - Panel (4pts): UI panel implementation
      * Award 4.0: Complete UI panels for game information
      * Award 3.0: Basic panels with some functionality
      * Award 2.0: Partial panel implementation
      * Award 0.0: No panels or broken UI
    - Launch Control (5pts): Game start and control system
      * Award 5.0: Complete game control with start/pause/reset
      * Award 4.0: Good control system with minor issues
      * Award 3.0: Basic controls
      * Award 0.0: No game controls
    - Players Health Panel (2pts): Health display system
      * Award 2.0: Complete health display and tracking
      * Award 1.0: Basic health display
      * Award 0.0: No health tracking
    - Music (2pts): Audio system implementation
      * Award 2.0: Complete audio system with background music
      * Award 1.0: Basic audio functionality
      * Award 0.0: No audio system
    - Game End (1pt): Win/lose condition handling
      * Award 1.0: Proper game end detection and handling
      * Award 0.0: No game end conditions

    **Object Oriented Design (14 points):**
    - Break into Classes (5pts): Class hierarchy and organization
      * Award 5.0: Well-designed class structure for game entities
      * Award 4.0: Good class organization
      * Award 3.0: Some classes but poor structure
      * Award 0.0: No class structure
    - Encapsulation (5pts): Data hiding and access control
      * Award 5.0: Proper encapsulation throughout
      * Award 4.0: Good encapsulation with minor issues
      * Award 3.0: Some encapsulation but inconsistent
      * Award 0.0: No encapsulation, all public members
    - Small Functions (2pts): Method size and focus
      * Award 2.0: Methods follow SRP principles
      * Award 1.0: Some large methods but acceptable
      * Award 0.0: Very large methods
    - No Duplication (1pt): DRY principle followed
      * Award 1.0: No code duplication
      * Award 0.0: Significant duplication
    - Indentation (1pt): Consistent formatting
      * Award 1.0: Consistent indentation
      * Award 0.0: Inconsistent formatting

    **Clean Coding & Git (21 points):**
    - Clean: Magic Values, Naming, Consistency (1pt each)
    - Git: Break Files, Header Guards, Makefile, Commit Messages, Standard Commits (1pt each)

    **COMPREHENSIVE ANALYSIS REQUIREMENTS:**

    **Game Architecture Analysis:**
    - **Entity Component System**: Proper separation of game entities
    - **Game Loop**: Update and render cycle implementation
    - **State Management**: Game state transitions and management
    - **Resource Management**: Memory and asset management

    **File-by-File Analysis:**
    - **Game engine files**: Core game loop, entity management, rendering
    - **Tower classes**: Individual tower implementations and inheritance
    - **Enemy classes**: Balloon types and movement logic
    - **UI classes**: Panel and control implementations
    - **Main game file**: Game initialization and high-level flow

    **RECOMMENDATION GUIDELINES:**
    For each criterion where points are deducted, provide specific recommendations:
    - **What** is wrong or missing (with file/line references)
    - **Why** it matters for game functionality and maintainability
    - **How** to fix it with concrete code examples
    - **Priority** level (High/Medium/Low) for the fix

    **EXAMPLE RECOMMENDATIONS:**
    - **High Priority**: No collision detection - Implement proper hit detection for towers and enemies
    - **Medium Priority**: Poor inheritance design - Create proper base classes for towers and enemies
    - **Low Priority**: Magic numbers for game constants - Define game balance values as named constants

    **CODE IMPROVEMENT EXAMPLES:**
    - **Before**: `if(enemy.x > tower.x - 50 && enemy.x < tower.x + 50)`
      **After**: `const float TOWER_RANGE = 50.0f; if(std::abs(enemy.x - tower.x) <= TOWER_RANGE)`
    - **Before**: Separate update methods for each tower type
      **After**: `virtual void update(float deltaTime) = 0;` in base Tower class
    - **Before**: `enemy.health = 100;` → **After**: `private: int health_; public: int getHealth() const { return health_; }`

    **GAME DEVELOPMENT BEST PRACTICES:**
    - Use inheritance hierarchies for similar game entities
    - Implement proper game loops with fixed time steps
    - Separate game logic from rendering
    - Use state machines for game state management
    - Implement object pooling for performance
    - Validate game balance values through testing
    - Document game design decisions and balance choices
    """


def get_a6_grading_criteria() -> str:
    """Get A6-specific grading criteria with detailed recommendations."""
    return """

    **A6 GRADING CRITERIA (Event Management System - Multi-Phase):**

    **PHASE 1 - CORE FEATURES (91 points):**

    **Authentication & Basic Features (8 points):**
    - Login/SignUp (2pts): Complete user authentication system with secure password handling
      * Award 2.0: Full signup/login/logout with validation, duplicate username prevention
      * Award 1.0: Basic functionality with some issues (missing validation or logout)
      * Award 0.0: No authentication system or major security issues
    - Normal Event (2pts): Basic event creation, listing, removal with time conflict detection
      * Award 2.0: Full CRUD operations with conflict detection and proper formatting
      * Award 1.0: Partial implementation (missing conflict detection or formatting)
      * Award 0.0: No event management or crashes on basic operations
    - Periodic Event (2pts): Support for recurring events (daily/weekly/monthly)
      * Award 2.0: Multiple recurrence types with proper instance generation
      * Award 1.0: Basic recurrence for one type (daily only)
      * Award 0.0: No periodic events or incorrect recurrence logic
    - Task Management (2pts): Complete task lifecycle with priorities and deadlines
      * Award 2.0: Add, update, remove, list tasks with priorities and status tracking
      * Award 1.0: Basic task operations without priorities or status updates
      * Award 0.0: No task management or incomplete lifecycle

    **Object-Oriented Design (8 points):**
    - Object Oriented Design (2pts): Proper use of classes and objects with clear responsibilities
      * Award 2.0: Well-designed class hierarchy with single responsibility principle
      * Award 1.0: Some OOP concepts used but with design issues
      * Award 0.0: Procedural code only, no class structure
    - No God Class (1pt): Main class not doing too much, responsibilities properly separated
      * Award 1.0: Clean separation of responsibilities, no monolithic classes
      * Award 0.0: Monolithic classes handling multiple unrelated responsibilities
    - Polymorphism (2pts): Effective use of inheritance and virtual functions
      * Award 2.0: Effective use of polymorphism for event/task types
      * Award 1.0: Some polymorphic behavior but limited usage
      * Award 0.0: No polymorphism, duplicate code for different types
    - No Downcast (1pt): Avoid unsafe casting, proper use of polymorphism
      * Award 1.0: No dynamic_cast or unsafe casts, proper virtual functions
      * Award 0.0: Unsafe casting present, dynamic_cast usage

    **Code Quality & Design (13 points):**
    - Encapsulation (2pts): Proper use of private/public members and data hiding
      * Award 2.0: Excellent encapsulation, all data properly encapsulated
      * Award 1.0: Good encapsulation with minor issues (some public data members)
      * Award 0.0: Poor encapsulation, direct access to internal data
    - Separate I/O (1pt): Clean separation of input/output from business logic
      * Award 1.0: I/O operations separated from business logic classes
      * Award 0.0: I/O mixed with business logic throughout the code
    - Exception Handling (2pts): Proper error handling and exception safety
      * Award 2.0: Comprehensive exception handling with custom exceptions
      * Award 1.0: Some exception handling but incomplete coverage
      * Award 0.0: No exception handling, potential crashes on errors
    - No Duplication (2pts): DRY principle followed, no code duplication
      * Award 2.0: No code duplication, proper abstraction and reuse
      * Award 1.0: Minimal duplication, some code reuse
      * Award 0.0: Significant duplication, copy-paste code patterns
    - Indentation (1pt): Consistent formatting and indentation
      * Award 1.0: Consistent indentation throughout all files
      * Award 0.0: Inconsistent formatting, mixed tabs/spaces
    - Magic Values (1pt): No hardcoded constants, proper use of named constants
      * Award 1.0: Constants properly defined, no magic numbers
      * Award 0.0: Magic numbers throughout the code
    - Naming (3pts): Clear, descriptive names following C++ conventions
      * Award 3.0: Excellent naming, camelCase, PascalCase, snake_case appropriately used
      * Award 2.0: Good naming with minor inconsistencies
      * Award 1.0: Acceptable naming but some unclear names
      * Award 0.0: Poor naming, abbreviations, unclear variable names
    - Consistency (3pts): Consistent coding style and conventions
      * Award 3.0: Highly consistent style across all files
      * Award 2.0: Mostly consistent with minor variations
      * Award 1.0: Some inconsistencies in style
      * Award 0.0: Inconsistent style, different conventions in same file

    **Project Structure (2 points):**
    - Break into Files (1pt): Proper file organization and separation of concerns
      * Award 1.0: Well-organized file structure, logical file separation
      * Award 0.0: All code in one file or poor file organization
    - Makefile (1pt): Proper build system with all necessary targets
      * Award 1.0: Complete Makefile with clean, all, test targets and proper flags
      * Award 0.0: No Makefile, incomplete Makefile, or compilation errors

    **Testing (30 points):**
    - Test Cases (30pts): Comprehensive test coverage with quality test cases
      * Award 30.0: Excellent coverage (30+ tests), edge cases, integration tests
      * Award 25.0: Good coverage (25-29 tests), most scenarios covered
      * Award 20.0: Adequate coverage (20-24 tests), basic functionality tested
      * Award 15.0: Basic coverage (15-19 tests), missing edge cases
      * Award 10.0: Minimal coverage (10-14 tests), insufficient testing
      * Award 5.0: Poor coverage (5-9 tests), insufficient testing
      * Award 0.0: No tests or failing test suite

    **PHASE 2 - ADVANCED FEATURES (15 points):**
    - Add Joint Event (3pts): Support for collaborative events with multiple participants
    - See Joint Requests (3pts): View and manage joint event invitations
    - Reject/Confirm (3pts): Accept or decline joint event participation
    - Change Report Command (3pts): Enhanced reporting functionality
    - Polymorphism (2pts): Advanced use of inheritance and polymorphism
    - No Downcast (1pt): Maintain safe casting practices

    **PHASE 3 - WEB INTERFACE (70 points):**
    - Signup/Login Pages (10pts): Complete user authentication web interface
    - Home/Dashboard (10pts): Main application interface
    - Task Management UI (15pts): Web interface for task operations
    - Event Management UI (15pts): Web interface for event operations
    - Joint Events UI (10pts): Web interface for collaborative features
    - Report Generation (5pts): Web-based reporting functionality
    - Clean Coding (5pts): Well-structured, maintainable web code

    **COMPREHENSIVE ANALYSIS REQUIREMENTS:**

    **File-by-File Analysis:**
    - **EventManager.h**: Check class declarations, member functions, inheritance hierarchy
    - **main.cpp**: Evaluate command parsing, user interaction, error handling
    - **test_suite.cpp**: Assess test coverage, test quality, edge case handling
    - **Makefile**: Verify build system completeness and compilation flags

    **Cross-File Consistency:**
    - Header/Implementation consistency
    - Naming conventions across files
    - Error handling patterns
    - Code style consistency

    **Functionality Verification:**
    - All required features implemented and working
    - Edge cases handled properly
    - Error conditions managed gracefully
    - User input validation complete

    **RECOMMENDATION GUIDELINES:**
    For each criterion where points are deducted, provide specific recommendations:
    - **What** is wrong or missing (with file/line references)
    - **Why** it matters for code quality/maintainability
    - **How** to fix it with concrete code examples
    - **Priority** level (High/Medium/Low) for the fix
    - **Expected Impact** on code quality or functionality

    **EXAMPLE RECOMMENDATIONS:**
    - **High Priority**: Missing exception handling in EventManager::addEvent() - Add try-catch blocks around file operations and provide meaningful error messages
    - **Medium Priority**: Poor encapsulation in EventManager class - Make data members private and provide public getter/setter methods
    - **Low Priority**: Inconsistent naming in test functions - Use camelCase consistently for test function names

    **CODE IMPROVEMENT EXAMPLES:**
    - **Before**: `if(events.size() > 100)` → **After**: `const int MAX_EVENTS = 100; if(events.size() > MAX_EVENTS)`
    - **Before**: `void addEvent(Event e) { events.push_back(e); }` → **After**: `void addEvent(const Event& e) { events.push_back(e); }`
    - **Before**: Direct vector access → **After**: `private: std::vector<Event> events_; public: const std::vector<Event>& getEvents() const { return events_; }`

    **TEST FAILURE ANALYSIS & DEBUGGING HELP:**

    **Test Failure Detection:**
    - Analyze test execution results for failed tests
    - Identify specific test cases that are failing
    - Determine root causes of test failures
    - Provide targeted debugging recommendations

    **Common Test Failure Patterns:**
    - **Memory Issues**: Segmentation faults, memory leaks, dangling pointers
    - **Logic Errors**: Incorrect algorithm implementation, edge case handling
    - **Input/Output Issues**: File operations, user input validation, output formatting
    - **Exception Handling**: Uncaught exceptions, improper error recovery
    - **Resource Management**: File handles, memory allocation/deallocation
    - **Concurrency Issues**: Race conditions, thread safety problems

    **Debugging Recommendations by Failure Type:**

    **For Memory-Related Failures:**
    - **Segmentation Fault**: Check for null pointer dereferences, array bounds violations
      * **Debug Steps**: Use gdb to get stack trace, check pointer initialization
      * **Common Fixes**: Add null checks, use smart pointers, validate array indices
      * **Example**: `if (ptr != nullptr) { ptr->method(); }` instead of direct access

    **For Logic Errors:**
    - **Incorrect Output**: Compare expected vs actual results, trace execution path
      * **Debug Steps**: Add debug prints, use debugger breakpoints, unit test individual functions
      * **Common Fixes**: Fix algorithm logic, handle edge cases, validate input ranges
      * **Example**: Add boundary checks for array operations and mathematical calculations

    **For Exception Handling Issues:**
    - **Unhandled Exceptions**: Add try-catch blocks around risky operations
      * **Debug Steps**: Use exception breakpoints, check exception propagation
      * **Common Fixes**: Add comprehensive exception handling, provide meaningful error messages
      * **Example**: `try { risky_operation(); } catch (const std::exception& e) { std::cerr << "Error: " << e.what() << std::endl; }`

    **For File I/O Issues:**
    - **File Operation Failures**: Check file permissions, paths, and error handling
      * **Debug Steps**: Verify file existence, check permissions, validate file paths
      * **Common Fixes**: Add file existence checks, handle I/O exceptions, validate file formats
      * **Example**: `if (!file.is_open()) { throw std::runtime_error("Failed to open file: " + filename); }`

    **TEST FAILURE DEBUGGING WORKFLOW:**
    1. **Identify Failed Tests**: List specific test cases that are failing
    2. **Categorize Failure Type**: Determine if it's memory, logic, I/O, or other issue
    3. **Locate Problem Code**: Find the specific functions/files causing the failure
    4. **Provide Debug Steps**: Give step-by-step debugging instructions
    5. **Suggest Fixes**: Provide concrete code examples for solutions
    6. **Recommend Testing**: Suggest additional test cases to verify fixes

    **EXAMPLE TEST FAILURE ANALYSIS:**
    ```
    FAILED TEST: test_add_event_with_conflict
    FAILURE TYPE: Logic Error
    LOCATION: EventManager::addEvent() in EventManager.cpp:45
    PROBLEM: Time conflict detection not working for overlapping events
    DEBUG STEPS:
    1. Add debug output to show event times being compared
    2. Check if time comparison logic is correct
    3. Verify event storage and retrieval
    FIX EXAMPLE:
    // Before: Incorrect overlap check
    if (newEvent.start < existing.end && newEvent.end > existing.start)

    // After: Correct overlap check
    if (!(newEvent.end <= existing.start || newEvent.start >= existing.end))
    ```

    **TEST FAILURE SCORING IMPACT:**
    - **No Test Failures**: Full test points awarded
    - **Minor Failures (1-2 tests)**: 80-90% of test points
    - **Moderate Failures (3-5 tests)**: 60-80% of test points
    - **Major Failures (6+ tests)**: 30-60% of test points
    - **Critical Failures (system crashes)**: 0-30% of test points

    **DEBUGGING RECOMMENDATIONS PRIORITY:**
    - **High Priority**: Crashes, memory corruption, security issues
    - **Medium Priority**: Logic errors, incorrect output, performance issues
    - **Low Priority**: Style issues, minor inefficiencies, cosmetic problems
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
    # Get the field names from the model for clearer instructions
    field_names = list(grading_model.model_fields.keys())

    return f"""
    CRITICAL: Respond ONLY with a valid JSON object. No markdown, no explanations, no additional text.

    Required JSON format for {assignment_type}:
    {{
{chr(10).join([f'      "{field}": <score>,' for field in field_names[:-1]])}
      "{field_names[-1]}": "<constructive feedback comment>"
    }}

    **IMPORTANT SCORING GUIDELINES:**
    - Return the JSON object directly, NOT wrapped in any "properties" or other structure
    - All field names must match exactly: {", ".join(f'"{f}"' for f in field_names)}
    - Use decimal scores (e.g., 3.5, 7.2) for partial credit
    - Be precise and consistent in scoring
    - Base scores on evidence from ALL code files provided
    - For multi-phase assignments (A6), evaluate each phase separately

    **RECOMMENDATION REQUIREMENTS:**
    The "generated_comment" field MUST include:
    1. **Summary**: Brief overview of strengths and main areas for improvement
    2. **Specific Recommendations**: For each low-scoring criterion, provide:
       - What is wrong or missing
       - Why it matters for code quality/maintainability
       - How to fix it with concrete code examples
       - Priority level (High/Medium/Low)
    3. **Code Examples**: Include specific code snippets showing both problems and solutions
    4. **File References**: Reference specific files and line numbers when possible
    5. **Next Steps**: Prioritized list of improvements to implement

    **EXAMPLE COMMENT STRUCTURE:**
    "Overall good start with solid basic functionality. **High Priority Issues:** 1. Missing exception handling in file I/O operations - Add try-catch blocks around all file operations. 2. Poor encapsulation - Make EventManager data members private. **Medium Priority:** 3. Add input validation for user commands. **Code Example:** Instead of direct access to events vector, use: `private: std::vector<Event> events_; public: const std::vector<Event>& getEvents() const {{ return events_; }}`"

    **EVALUATION CHECKLIST:**
    - [ ] Analyzed ALL provided code files (.h, .cpp, Makefile, tests)
    - [ ] Checked file organization and structure
    - [ ] Evaluated class design and OOP principles
    - [ ] Assessed error handling and input validation
    - [ ] Reviewed code style and consistency
    - [ ] Verified all required features are implemented
    - [ ] Provided specific, actionable recommendations
    """


# =============================================================================
# PROMPT CONFIGURATION
# =============================================================================

# Default prompt settings that can be easily modified
# Import model configuration from config.py
try:
    from config import MODEL_CONFIG

    PROMPT_CONFIG = {
        "test_generation": {
            "temperature": MODEL_CONFIG["generation"]["temperature"],
            "max_tokens": MODEL_CONFIG["generation"]["max_output_tokens"],
            "model": MODEL_CONFIG["model"],
        },
        "grading": {
            "temperature": MODEL_CONFIG["grading"]["temperature"],
            "max_tokens": MODEL_CONFIG["grading"]["max_output_tokens"],
            "model": MODEL_CONFIG["model"],
        },
    }
except ImportError:
    # Fallback to hardcoded values if config import fails
    PROMPT_CONFIG = {
        "test_generation": {
            "temperature": 0.7,
            "max_tokens": 4096,
            "model": "gemini-2.0-flash",
        },
        "grading": {
            "temperature": 0.1,
            "max_tokens": 4096,
            "model": "gemini-2.0-flash",
        },
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
