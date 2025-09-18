# langchain_integration.py
import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import google.generativeai as genai

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# Define grading output structures for different assignments
class A1GradingOutput(BaseModel):
    logic_iterators: float = Field(
        description="Score for using iterators (0 to 1)", ge=0, le=1
    )
    logic_containers: float = Field(
        description="Score for using std::vector, std::map (0 to 1)", ge=0, le=1
    )
    design_io_separation: float = Field(
        description="Score for separating I/O from logic (0 to 2)", ge=0, le=2
    )
    design_structs: float = Field(
        description="Score for using structs appropriately (0 to 1)", ge=0, le=1
    )
    design_no_god_main: float = Field(
        description="Score for having a clean main (0 to 2)", ge=0, le=2
    )
    design_small_functions: float = Field(
        description="Score for small functions (0 to 3)", ge=0, le=3
    )
    clean_no_comments: float = Field(
        description="Score for self-documenting code (0 to 1)", ge=0, le=1
    )
    clean_no_duplication: float = Field(
        description="Score for avoiding duplication (0 to 1)", ge=0, le=1
    )
    clean_indentation: float = Field(
        description="Score for proper indentation (0 to 1)", ge=0, le=1
    )
    clean_magic_values: float = Field(
        description="Score for using constants (0 to 1)", ge=0, le=1
    )
    clean_naming: float = Field(
        description="Score for clear naming (0 to 1)", ge=0, le=1
    )
    clean_consistency: float = Field(
        description="Score for consistency (0 to 1)", ge=0, le=1
    )
    generated_comment: str = Field(description="Constructive feedback comment")


class A2GradingOutput(BaseModel):
    data_reading_input: float = Field(
        description="Data reading input (0 to 5)", ge=0, le=5
    )
    data_storing_information: float = Field(
        description="Data storing information & data structures (0 to 10)", ge=0, le=10
    )
    design_separate_io: float = Field(
        description="Design separate I/O from logic (0 to 8)", ge=0, le=8
    )
    design_no_godly_main: float = Field(
        description="Design no godly main (0 to 10)", ge=0, le=10
    )
    design_small_functions: float = Field(
        description="Design small functions and single responsibility (0 to 10)",
        ge=0,
        le=10,
    )
    clean_no_duplication: float = Field(
        description="Clean no duplication (0 to 7)", ge=0, le=7
    )
    clean_magic_values: float = Field(
        description="Clean magic values / no global variables (0 to 7)", ge=0, le=7
    )
    clean_naming: float = Field(description="Clean naming (0 to 7)", ge=0, le=7)
    clean_consistency: float = Field(
        description="Clean consistency (0 to 7)", ge=0, le=7
    )
    git_commit_messages: float = Field(
        description="Git commit messages (0 to 4)", ge=0, le=4
    )
    git_standard_commits: float = Field(
        description="Git standard commits (0 to 3)", ge=0, le=3
    )
    correctness_test_cases: float = Field(
        description="Correctness test cases (0 to 20)", ge=0, le=20
    )
    generated_comment: str = Field(description="Constructive feedback comment")
    q1_recursive_logic: float = Field(
        description="Q1 recursive logic (0 to 2)", ge=0, le=2
    )
    q1_test_cases: float = Field(description="Q1 test cases (0 to 15)", ge=0, le=15)
    q1_upload_testcases: float = Field(
        description="Q1 upload testcases (0 to 2)", ge=0, le=2
    )
    q2_recursive_logic: float = Field(
        description="Q2 recursive logic (0 to 2)", ge=0, le=2
    )
    q2_test_cases: float = Field(description="Q2 test cases (0 to 15)", ge=0, le=15)
    q2_upload_testcases: float = Field(
        description="Q2 upload testcases (0 to 2)", ge=0, le=2
    )
    q3_backtracking: float = Field(description="Q3 backtracking (0 to 2)", ge=0, le=2)
    q3_test_cases: float = Field(description="Q3 test cases (0 to 15)", ge=0, le=15)
    q3_upload_testcases: float = Field(
        description="Q3 upload testcases (0 to 2)", ge=0, le=2
    )
    q4_backtracking: float = Field(description="Q4 backtracking (0 to 2)", ge=0, le=2)
    q4_test_cases: float = Field(description="Q4 test cases (0 to 10)", ge=0, le=10)
    q4_upload_testcases: float = Field(
        description="Q4 upload testcases (0 to 2)", ge=0, le=2
    )
    design_io_separation: float = Field(
        description="Design I/O separation (0 to 1)", ge=0, le=1
    )
    design_data_structures: float = Field(
        description="Design data structures (0 to 3)", ge=0, le=3
    )
    design_no_god_main: float = Field(
        description="Design no god main (0 to 1)", ge=0, le=1
    )
    design_small_functions: float = Field(
        description="Design small functions (0 to 2)", ge=0, le=2
    )
    design_no_duplication: float = Field(
        description="Design no duplication (0 to 1)", ge=0, le=1
    )
    design_indentation: float = Field(
        description="Design indentation (0 to 1)", ge=0, le=1
    )
    design_magic_values: float = Field(
        description="Design magic values (0 to 1)", ge=0, le=1
    )
    design_naming: float = Field(description="Design naming (0 to 1)", ge=0, le=1)
    design_consistency: float = Field(
        description="Design consistency (0 to 1)", ge=0, le=1
    )
    git_commit_messages: float = Field(
        description="Git commit messages (0 to 1)", ge=0, le=1
    )
    git_standard_commits: float = Field(
        description="Git standard commits (0 to 1)", ge=0, le=1
    )
    generated_comment: str = Field(description="Constructive feedback comment")


class A4GradingOutput(BaseModel):
    oop_break_classes: float = Field(
        description="OOP break into classes (0 to 5)", ge=0, le=5
    )
    oop_responsibility: float = Field(
        description="OOP responsibility assignment (0 to 5)", ge=0, le=5
    )
    oop_field_assignment: float = Field(
        description="OOP field assignment (0 to 5)", ge=0, le=5
    )
    oop_access_modifiers: float = Field(
        description="OOP access modifiers (0 to 3)", ge=0, le=3
    )
    oop_no_logic_main: float = Field(
        description="OOP no logic in main (0 to 3)", ge=0, le=3
    )
    oop_small_functions: float = Field(
        description="OOP small functions (0 to 2)", ge=0, le=2
    )
    clean_no_duplication: float = Field(
        description="Clean no duplication (0 to 1)", ge=0, le=1
    )
    clean_indentation: float = Field(
        description="Clean indentation (0 to 1)", ge=0, le=1
    )
    clean_magic_values: float = Field(
        description="Clean magic values (0 to 1)", ge=0, le=1
    )
    clean_naming: float = Field(description="Clean naming (0 to 1)", ge=0, le=1)
    clean_consistency: float = Field(
        description="Clean consistency (0 to 1)", ge=0, le=1
    )
    multifile_break_files: float = Field(
        description="Multifile break files (0 to 1)", ge=0, le=1
    )
    multifile_header_guards: float = Field(
        description="Multifile header guards (0 to 1)", ge=0, le=1
    )
    multifile_makefile: float = Field(
        description="Multifile makefile (0 to 1)", ge=0, le=1
    )
    git_commit_messages: float = Field(
        description="Git commit messages (0 to 1)", ge=0, le=1
    )
    git_standard_commits: float = Field(
        description="Git standard commits (0 to 1)", ge=0, le=1
    )
    generated_comment: str = Field(description="Constructive feedback comment")


class A5GradingOutput(BaseModel):
    design_attack_wave: float = Field(
        description="Design attack wave (0 to 6)", ge=0, le=6
    )
    design_normal_tower: float = Field(
        description="Design normal tower (0 to 5)", ge=0, le=5
    )
    design_ice_tower: float = Field(description="Design ice tower (0 to 7)", ge=0, le=7)
    design_bomb_tower: float = Field(
        description="Design bomb tower (0 to 7)", ge=0, le=7
    )
    design_tower_visibility: float = Field(
        description="Design tower visibility (0 to 5)", ge=0, le=5
    )
    design_normal_balloon: float = Field(
        description="Design normal balloon (0 to 5)", ge=0, le=5
    )
    design_pregnant_balloon: float = Field(
        description="Design pregnant balloon (0 to 7)", ge=0, le=7
    )
    design_panel: float = Field(description="Design panel (0 to 4)", ge=0, le=4)
    design_launch_control: float = Field(
        description="Design launch control (0 to 5)", ge=0, le=5
    )
    design_health_panel: float = Field(
        description="Design health panel (0 to 2)", ge=0, le=2
    )
    design_music: float = Field(description="Design music (0 to 2)", ge=0, le=2)
    design_game_end: float = Field(description="Design game end (0 to 1)", ge=0, le=1)
    oop_break_classes: float = Field(
        description="OOP break classes (0 to 5)", ge=0, le=5
    )
    oop_encapsulation: float = Field(
        description="OOP encapsulation (0 to 5)", ge=0, le=5
    )
    oop_small_functions: float = Field(
        description="OOP small functions (0 to 2)", ge=0, le=2
    )
    oop_no_duplication: float = Field(
        description="OOP no duplication (0 to 1)", ge=0, le=1
    )
    oop_indentation: float = Field(description="OOP indentation (0 to 1)", ge=0, le=1)
    clean_magic_values: float = Field(
        description="Clean magic values (0 to 1)", ge=0, le=1
    )
    clean_naming: float = Field(description="Clean naming (0 to 1)", ge=0, le=1)
    clean_consistency: float = Field(
        description="Clean consistency (0 to 1)", ge=0, le=1
    )
    git_break_files: float = Field(description="Git break files (0 to 1)", ge=0, le=1)
    git_header_guards: float = Field(
        description="Git header guards (0 to 1)", ge=0, le=1
    )
    git_makefile: float = Field(description="Git makefile (0 to 1)", ge=0, le=1)
    git_commit_messages: float = Field(
        description="Git commit messages (0 to 1)", ge=0, le=1
    )
    git_standard_commits: float = Field(
        description="Git standard commits (0 to 1)", ge=0, le=1
    )
    generated_comment: str = Field(description="Constructive feedback comment")


class A6GradingOutput(BaseModel):
    # Phase 1
    p1_login_signup: float = Field(
        description="Phase 1 Login/SignUp (0 to 2)", ge=0, le=2
    )
    p1_normal_event: float = Field(
        description="Phase 1 Normal Event (0 to 2)", ge=0, le=2
    )
    p1_periodic_event: float = Field(
        description="Phase 1 Periodic Event (0 to 2)", ge=0, le=2
    )
    p1_task: float = Field(description="Phase 1 Task (0 to 2)", ge=0, le=2)
    p1_object_oriented: float = Field(
        description="Phase 1 Object Oriented (0 to 2)", ge=0, le=2
    )
    p1_no_god_class: float = Field(
        description="Phase 1 No God Class (0 to 1)", ge=0, le=1
    )
    p1_polymorphism: float = Field(
        description="Phase 1 Polymorphism (0 to 2)", ge=0, le=2
    )
    p1_no_downcast: float = Field(
        description="Phase 1 No Downcast (0 to 1)", ge=0, le=1
    )
    p1_encapsulation: float = Field(
        description="Phase 1 Encapsulation (0 to 2)", ge=0, le=2
    )
    p1_separate_io: float = Field(
        description="Phase 1 Separate I/O (0 to 1)", ge=0, le=1
    )
    p1_exception_handling: float = Field(
        description="Phase 1 Exception Handling (0 to 2)", ge=0, le=2
    )
    p1_no_duplication: float = Field(
        description="Phase 1 No Duplication (0 to 2)", ge=0, le=2
    )
    p1_indentation: float = Field(
        description="Phase 1 Indentation (0 to 1)", ge=0, le=1
    )
    p1_magic_values: float = Field(
        description="Phase 1 Magic Values (0 to 1)", ge=0, le=1
    )
    p1_naming: float = Field(description="Phase 1 Naming (0 to 3)", ge=0, le=3)
    p1_consistency: float = Field(
        description="Phase 1 Consistency (0 to 3)", ge=0, le=3
    )
    p1_break_files: float = Field(
        description="Phase 1 Break Files (0 to 1)", ge=0, le=1
    )
    p1_makefile: float = Field(description="Phase 1 Makefile (0 to 1)", ge=0, le=1)
    p1_test_cases: float = Field(
        description="Phase 1 Test Cases (0 to 30)", ge=0, le=30
    )

    # Phase 2
    p2_add_joint_event: float = Field(
        description="Phase 2 Add Joint Event (0 to 2)", ge=0, le=2
    )
    p2_see_joint_requests: float = Field(
        description="Phase 2 See Joint Requests (0 to 2)", ge=0, le=2
    )
    p2_reject_confirm: float = Field(
        description="Phase 2 Reject/Confirm (0 to 2)", ge=0, le=2
    )
    p2_change_report_cmd: float = Field(
        description="Phase 2 Change Report Cmd (0 to 2)", ge=0, le=2
    )
    p2_polymorphism: float = Field(
        description="Phase 2 Polymorphism (0 to 2)", ge=0, le=2
    )
    p2_no_downcast: float = Field(
        description="Phase 2 No Downcast (0 to 1)", ge=0, le=1
    )
    p2_no_duplication: float = Field(
        description="Phase 2 No Duplication (0 to 2)", ge=0, le=2
    )
    p2_indentation: float = Field(
        description="Phase 2 Indentation (0 to 2)", ge=0, le=2
    )
    p2_naming: float = Field(description="Phase 2 Naming (0 to 2)", ge=0, le=2)
    p2_consistency: float = Field(
        description="Phase 2 Consistency (0 to 2)", ge=0, le=2
    )
    p2_test_cases: float = Field(
        description="Phase 2 Test Cases (0 to 15)", ge=0, le=15
    )

    # Phase 3
    p3_signup_page: float = Field(
        description="Phase 3 Signup Page (0 to 2)", ge=0, le=2
    )
    p3_login_page: float = Field(description="Phase 3 Login Page (0 to 2)", ge=0, le=2)
    p3_home_page: float = Field(description="Phase 3 Home Page (0 to 2)", ge=0, le=2)
    p3_logout: float = Field(description="Phase 3 Logout (0 to 2)", ge=0, le=2)
    p3_add_task: float = Field(description="Phase 3 Add Task (0 to 2)", ge=0, le=2)
    p3_delete_task: float = Field(
        description="Phase 3 Delete Task (0 to 2)", ge=0, le=2
    )
    p3_edit_task: float = Field(description="Phase 3 Edit Task (0 to 2)", ge=0, le=2)
    p3_add_events: float = Field(description="Phase 3 Add Events (0 to 2)", ge=0, le=2)
    p3_get_join_events: float = Field(
        description="Phase 3 Get Join Events (0 to 2)", ge=0, le=2
    )
    p3_confirm_reject: float = Field(
        description="Phase 3 Confirm/Reject (0 to 2)", ge=0, le=2
    )
    p3_report: float = Field(description="Phase 3 Report (0 to 3)", ge=0, le=3)
    p3_html_render: float = Field(
        description="Phase 3 HTML Render (0 to 3)", ge=0, le=3
    )
    p3_handlers: float = Field(description="Phase 3 Handlers (0 to 3)", ge=0, le=3)
    p3_css: float = Field(description="Phase 3 CSS (0 to 2)", ge=0, le=2)
    p3_js: float = Field(description="Phase 3 JS (0 to 1)", ge=0, le=1)
    p3_makefile: float = Field(description="Phase 3 Makefile (0 to 2)", ge=0, le=2)
    p3_clean_coding: float = Field(
        description="Phase 3 Clean Coding (0 to 30)", ge=0, le=30
    )
    p3_bonus: float = Field(description="Phase 3 Bonus (0 to 10)", ge=0, le=10)
    p3_multifile: float = Field(description="Phase 3 Multifile (0 to 5)", ge=0, le=5)

    generated_comment: str = Field(description="Constructive feedback comment")


def get_grading_model(assignment_type):
    """Returns the appropriate grading model for the assignment type."""
    models = {
        "A1": A1GradingOutput,
        "A2": A2GradingOutput,
        "A3": A3GradingOutput,
        "A4": A4GradingOutput,
        "A5": A5GradingOutput,
        "A6": A6GradingOutput,
    }
    return models.get(assignment_type, A1GradingOutput)


def get_grading_prompt(
    assignment_type, practice_description, test_results, static_analysis, source_code
):
    """Returns the appropriate grading prompt for the assignment type."""

    base_prompt = f"""
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

    if assignment_type == "A1":
        return (
            base_prompt
            + """

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
        )

    elif assignment_type == "A2":
        return (
            base_prompt
            + """

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
        )
        return (
            base_prompt
            + """

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
        )

    elif assignment_type == "A4":
        return (
            base_prompt
            + """

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
        )

    elif assignment_type == "A5":
        return (
            base_prompt
            + """

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
        )

    elif assignment_type == "A6":
        return (
            base_prompt
            + """

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
        )

    return base_prompt


def grade_student_project(
    test_results: str,
    static_analysis: str,
    source_code: str,
    practice_description: str,
    assignment_type: str = "A1",
) -> BaseModel:
    """Grades a student project using Gemini API with assignment-specific criteria."""

    # Get the appropriate model and prompt
    grading_model = get_grading_model(assignment_type)
    prompt = get_grading_prompt(
        assignment_type,
        practice_description,
        test_results,
        static_analysis,
        source_code,
    )

    # Initialize the model with optimized settings
    model = genai.GenerativeModel(
        "gemini-pro",
        generation_config=genai.types.GenerationConfig(
            temperature=0.1,  # Lower temperature for more consistent grading
            top_p=0.8,
            top_k=40,
            max_output_tokens=4096,  # Increased for A6 multi-phase
        ),
    )

    # Format instructions for the specific model
    format_instructions = f"""
    CRITICAL: Respond ONLY with a valid JSON object. No markdown, no explanations, no additional text.

    Required JSON format for {assignment_type}:
    {grading_model.model_json_schema()}

    Scoring Guidelines:
    - Use decimal scores (e.g., 3.5, 7.2) for partial credit
    - Be precise and consistent in scoring
    - Base scores on evidence from the code
    - For multi-phase assignments (A6), evaluate each phase separately
    """

    full_prompt = prompt + format_instructions

    # Generate response with retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content(full_prompt)

            # Clean the response text
            response_text = response.text.strip()

            # Remove potential markdown formatting
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            # Parse the JSON response
            result_dict = json.loads(response_text)
            grading_output = grading_model(**result_dict)
            return grading_output

        except json.JSONDecodeError as e:
            if attempt == max_retries - 1:
                raise ValueError(
                    f"Failed to parse JSON after {max_retries} attempts: {e}. Response: {response_text}"
                )
            print(f"JSON parsing failed (attempt {attempt + 1}), retrying...")
            continue
        except Exception as e:
            if attempt == max_retries - 1:
                raise ValueError(
                    f"Error processing response after {max_retries} attempts: {e}"
                )
            print(f"API call failed (attempt {attempt + 1}), retrying...")
            continue

    # This should never be reached, but just in case
    raise ValueError("Unexpected error in grading function")


def get_grading_chain():
    """Returns the grading function for compatibility."""
    return grade_student_project
