# langchain_integration.py
import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import google.generativeai as genai

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# Setup logging
def setup_logging():
    """Setup logging configuration for the grading system."""
    log_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, f"grading_{datetime.now().strftime('%Y%m%d')}.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )

    return logging.getLogger(__name__)


logger = setup_logging()


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


class A3GradingOutput(BaseModel):
    # Questions 1-4 (71 points total)
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

    # Design (20 points)
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

    # Git (6 points)
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
    assignment_type,
    practice_description,
    test_results,
    static_analysis,
    source_code,
):
    """Returns the appropriate grading prompt for the assignment type."""

    # Import the prompts module
    from prompts import get_grading_prompt as get_centralized_prompt

    # Use the centralized prompt function
    return get_centralized_prompt(
        assignment_type,
        practice_description,
        test_results,
        static_analysis,
        source_code,
    )


def grade_student_project(
    test_results: str,
    static_analysis: str,
    source_code: str,
    practice_description: str,
    assignment_type: str = "A1",
    student_id: str = None,
    save_outputs: bool = True,
) -> BaseModel:
    """Grades a student project using Gemini API with assignment-specific criteria."""

    import os
    import json
    from datetime import datetime

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
    from prompts import get_format_instructions

    format_instructions = get_format_instructions(assignment_type, grading_model)

    full_prompt = prompt + format_instructions

    # Generate response with retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            logger.info(
                f"Starting grading attempt {attempt + 1} for student {student_id}, assignment {assignment_type}"
            )

            response = model.generate_content(full_prompt)

            # Use centralized parser/validator
            from prompts import parse_and_validate_response

            response_text = response.text

            def _validator(d: dict):
                # let Pydantic validate types/required fields
                grading_model(**d)

            parsed = parse_and_validate_response(
                response_text,
                validator=_validator,
                description=f"grading for {student_id} {assignment_type}",
                save_raw_to=os.path.join(os.getcwd(), "grading_outputs", f"raw_{student_id}_{assignment_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"),
            )

            result_dict = parsed
            grading_output = grading_model(**result_dict)

            logger.info(
                f"Successfully graded student {student_id} for {assignment_type}"
            )

            # Save outputs if requested
            if save_outputs and student_id:
                saved_path = save_grading_output(
                    grading_output, assignment_type, student_id, result_dict
                )
                logger.info(f"Grading output saved to {saved_path}")

            return grading_output

        except json.JSONDecodeError as e:
            logger.warning(
                f"JSON parsing failed (attempt {attempt + 1}) for student {student_id}: {e}"
            )
            if attempt == max_retries - 1:
                logger.error(
                    f"Failed to parse JSON after {max_retries} attempts for student {student_id}: {e}. Response: {response_text}"
                )
                raise ValueError(
                    f"Failed to parse JSON after {max_retries} attempts: {e}. Response: {response_text}"
                )
            continue
        except Exception as e:
            logger.error(
                f"API call failed (attempt {attempt + 1}) for student {student_id}: {e}"
            )
            if attempt == max_retries - 1:
                logger.error(
                    f"Error processing response after {max_retries} attempts for student {student_id}: {e}"
                )
                raise ValueError(
                    f"Error processing response after {max_retries} attempts: {e}"
                )
            continue

    # This should never be reached, but just in case
    logger.error(f"Unexpected error in grading function for student {student_id}")
    raise ValueError("Unexpected error in grading function")


def save_grading_output(
    grading_output: BaseModel, assignment_type: str, student_id: str, raw_dict: dict
):
    """Save grading output as JSON file with timestamp."""
    import os
    from datetime import datetime

    # Create outputs directory if it doesn't exist
    outputs_dir = os.path.join(os.getcwd(), "grading_outputs")
    os.makedirs(outputs_dir, exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{student_id}_{assignment_type}_{timestamp}.json"
    filepath = os.path.join(outputs_dir, filename)

    # Prepare output data
    output_data = {
        "student_id": student_id,
        "assignment_type": assignment_type,
        "timestamp": datetime.now().isoformat(),
        "grading_output": raw_dict,
        "model_used": "gemini-pro",
        "structured_output": (
            grading_output.model_dump()
            if hasattr(grading_output, "model_dump")
            else grading_output.dict()
        ),
    }

    # Save to JSON file
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Grading output saved to: {filepath}")
    return filepath
