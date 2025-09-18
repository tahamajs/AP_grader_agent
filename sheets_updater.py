# sheets_updater.py
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import config


def get_sheet():
    """Connects to Google Sheets and returns a worksheet object."""
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        config.CREDENTIALS_FILE, scope
    )
    client = gspread.authorize(creds)
    return client.open(config.SHEET_NAME).sheet1


def get_column_mapping(assignment_type, phase=None):
    """Returns the column mapping for a specific assignment type and phase."""

    if assignment_type == "A1":
        return {
            "logic_iterators": "E",  # Logic - Using Iterators
            "logic_containers": "F",  # Logic - Using Containers
            "design_io_separation": "G",  # Design - Separate I/O from Logic
            "design_structs": "H",  # Design - Using Structs
            "design_no_god_main": "I",  # Design - No Godly Main
            "design_small_functions": "J",  # Design - Small Functions and Single Responsibility
            "clean_no_comments": "K",  # Clean Coding - No Comments
            "clean_no_duplication": "L",  # Clean Coding - No Duplication
            "clean_indentation": "M",  # Clean Coding - Indentation
            "clean_magic_values": "N",  # Clean Coding - Magic Values / No Global Variables
            "clean_naming": "O",  # Clean Coding - Naming
            "clean_consistency": "P",  # Clean Coding - Consistency
            "correctness_test_cases": "Q",  # Correctness - Test Cases
            "raw_score": "R",  # Raw Score
            "using_goto": "S",  # Using Goto
            "edit_code": "T",  # Edit Code
            "latency": "U",  # Latency
            "upload_structure": "V",  # Upload Structure
            "penalty": "W",  # Penalty
            "comment": "X",  # Comment
            "plagiarism": "Y",  # Plagiarism
            "final_score": "Z",  # Final Score
        }

    elif assignment_type == "A2":
        return {
            "data_reading_input": "E",  # Data - Reading Input
            "data_storing_information": "F",  # Data - Storing Information & Data Structures
            "design_separate_io": "G",  # Design - Separate I/O from Logic
            "design_no_godly_main": "H",  # Design - No Godly Main
            "design_small_functions": "I",  # Design - Small Functions and Single Responsibility
            "clean_no_duplication": "J",  # Clean Coding - No Duplication
            "clean_magic_values": "K",  # Clean Coding - Magic Values / No Global Variables
            "clean_naming": "L",  # Clean Coding - Naming
            "clean_consistency": "M",  # Clean Coding - Consistency
            "git_commit_messages": "N",  # Git - Commit Messages
            "git_standard_commits": "O",  # Git - Standard Commits
            "correctness_test_cases": "P",  # Correctness - Test Cases
            "raw_score": "Q",  # Raw Score
            "using_goto": "R",  # Using Goto
            "edit_code": "S",  # Edit Code
            "latency": "T",  # Latency
            "upload_structure": "U",  # Upload Structure
            "penalty": "V",  # Penalty
            "comment": "W",  # Comment
            "plagiarism": "X",  # Plagiarism
            "final_score": "Y",  # Final Score
        }
        return {
            "q1_recursive_logic": "E",  # Q1 - Recursive Logic
            "q1_test_cases": "F",  # Q1 - Test Cases
            "q1_upload_testcases": "G",  # Q1 - Upload two Testcases
            "q2_recursive_logic": "H",  # Q2 - Recursive Logic
            "q2_test_cases": "I",  # Q2 - Test Cases
            "q2_upload_testcases": "J",  # Q2 - Upload two Testcases
            "q3_backtracking": "K",  # Q3 - Backtracking
            "q3_test_cases": "L",  # Q3 - Test Cases
            "q3_upload_testcases": "M",  # Q3 - Upload two Testcases
            "q4_backtracking": "N",  # Q4 - Backtracking
            "q4_test_cases": "O",  # Q4 - Test Cases
            "q4_upload_testcases": "P",  # Q4 - Upload two Testcases
            "design_io_separation": "Q",  # Design - Separate IO from Logic
            "design_data_structures": "R",  # Design - Proper Data Structures
            "design_no_god_main": "S",  # Design - No Godly Main
            "design_small_functions": "T",  # Design - Small Functions and Single Responsibility
            "design_no_duplication": "U",  # Design - No Duplication
            "design_indentation": "V",  # Design - Indentation
            "design_magic_values": "W",  # Design - Magic Values / No Global Variables
            "design_naming": "X",  # Design - Naming
            "design_consistency": "Y",  # Design - Consistency
            "git_commit_messages": "Z",  # Git - Commit Messages
            "git_standard_commits": "AA",  # Git - Standard Commits
            "correctness_test_cases": "AB",  # Correctness - Test Cases
            "raw_score": "AC",  # Raw Score
            "mastery": "AD",  # Mastery
            "clean_code": "AE",  # Clean Code
            "edit_code": "AF",  # Edit Code
            "latency": "AG",  # Latency
            "upload_structure": "AH",  # Upload Structure
            "penalty": "AI",  # Penalty
            "comment": "AJ",  # Comment
            "plagiarism": "AK",  # Plagiarism
            "final_score": "AL",  # Final Score
        }

    elif assignment_type == "A4":
        return {
            "oop_break_classes": "E",  # Object Oriented Design - Break into Classes
            "oop_responsibility": "F",  # Object Oriented Design - Responsibility Assignment
            "oop_field_assignment": "G",  # Object Oriented Design - Field Assignment
            "oop_access_modifiers": "H",  # Object Oriented Design - Public/Private Access Modifiers
            "oop_no_logic_main": "I",  # Object Oriented Design - No Logic in Main
            "oop_small_functions": "J",  # Object Oriented Design - Small Functions
            "clean_no_duplication": "K",  # Clean Coding - No Duplication
            "clean_indentation": "L",  # Clean Coding - Indentation
            "clean_magic_values": "M",  # Clean Coding - Magic Values / No Global Variables
            "clean_naming": "N",  # Clean Coding - Naming
            "clean_consistency": "O",  # Clean Coding - Consistency
            "multifile_break_files": "P",  # Multifile - Break into Files
            "multifile_header_guards": "Q",  # Multifile - Header Guards
            "multifile_makefile": "R",  # Multifile - Makefile
            "git_commit_messages": "S",  # Git - Commit Messages
            "git_standard_commits": "T",  # Git - Standard Commits
            "correctness_test_cases": "U",  # Correctness - Test Cases
            "raw_score": "V",  # Raw Score
            "mastery": "W",  # Mastery
            "edit_code": "X",  # Edit Code
            "latency": "Y",  # Latency
            "upload_structure": "Z",  # Upload Structure
            "penalty": "AA",  # Penalty
            "comment": "AB",  # Comment
            "plagiarism": "AC",  # Plagiarism
            "final_score": "AD",  # Final Score
        }

    elif assignment_type == "A5":
        return {
            "design_attack_wave": "E",  # Design - Attack Wave
            "design_normal_tower": "F",  # Design - Normal Tower
            "design_ice_tower": "G",  # Design - Ice Tower
            "design_bomb_tower": "H",  # Design - Bomb Tower
            "design_tower_visibility": "I",  # Design - Tower Domain Visibility
            "design_normal_balloon": "J",  # Design - Normal Balloon
            "design_pregnant_balloon": "K",  # Design - Pregnant Balloon
            "design_panel": "L",  # Design - Panel
            "design_launch_control": "M",  # Design - Launch Control
            "design_health_panel": "N",  # Design - Players Health panel
            "design_music": "O",  # Design - Music
            "design_game_end": "P",  # Design - Game End
            "oop_break_classes": "Q",  # Object Oriented Design - Break into Classes
            "oop_encapsulation": "R",  # Object Oriented Design - Encapsulation
            "oop_small_functions": "S",  # Object Oriented Design - Small Functions
            "oop_no_duplication": "T",  # Object Oriented Design - No Duplication
            "oop_indentation": "U",  # Object Oriented Design - Indentation
            "clean_magic_values": "V",  # Clean Coding - Magic Values / No Global Variables
            "clean_naming": "W",  # Clean Coding - Naming
            "clean_consistency": "X",  # Clean Coding - Consistency
            "git_break_files": "Y",  # Git - Break into Files
            "git_header_guards": "Z",  # Git - Header Guards
            "git_makefile": "AA",  # Git - Makefile
            "git_commit_messages": "AB",  # Git - Commit Messages
            "git_standard_commits": "AC",  # Git - Standard Commits
            "correctness_test_cases": "AD",  # Correctness - Test Cases
            "raw_score": "AE",  # Raw Score
            "edit_code": "AF",  # Edit Code
            "latency": "AG",  # Latency
            "upload_structure": "AH",  # Upload Structure
            "penalty": "AI",  # Penalty
            "comment": "AJ",  # Comment
            "plagiarism": "AK",  # Plagiarism
            "final_score": "AL",  # Final Score
        }

    elif assignment_type == "A6":
        if phase == "phase1":
            return {
                "p1_login_signup": "E",  # Phase 1 - Login/SignUp
                "p1_normal_event": "F",  # Phase 1 - Normal Event
                "p1_periodic_event": "G",  # Phase 1 - Periodic Event
                "p1_task": "H",  # Phase 1 - Task
                "p1_object_oriented": "I",  # Phase 1 - Object Oriented Design
                "p1_no_god_class": "J",  # Phase 1 - No God Class
                "p1_polymorphism": "K",  # Phase 1 - Polymorphism
                "p1_no_downcast": "L",  # Phase 1 - No Downcast
                "p1_encapsulation": "M",  # Phase 1 - Encapsulation
                "p1_separate_io": "N",  # Phase 1 - Separate I/O from Logic
                "p1_exception_handling": "O",  # Phase 1 - Exception Handling
                "p1_no_duplication": "P",  # Phase 1 - No Duplication
                "p1_indentation": "Q",  # Phase 1 - Indentation
                "p1_magic_values": "R",  # Phase 1 - Magic Values
                "p1_naming": "S",  # Phase 1 - Naming
                "p1_consistency": "T",  # Phase 1 - Consistency
                "p1_break_files": "U",  # Phase 1 - Break into Files
                "p1_makefile": "V",  # Phase 1 - Makefile
                "p1_test_cases": "W",  # Phase 1 - Test Cases
                "p1_raw_score": "X",  # Phase 1 - Raw Score
                "p1_mastery": "Y",  # Phase 1 - Mastery
                "p1_edit_code": "Z",  # Phase 1 - Edit Code
                "p1_latency": "AA",  # Phase 1 - Latency
                "p1_upload_structure": "AB",  # Phase 1 - Upload Structure
                "p1_penalty": "AC",  # Phase 1 - Penalty
                "p1_comment": "AD",  # Phase 1 - Comment
                "p1_final_score": "AE",  # Phase 1 - Final Score
            }
        elif phase == "phase2":
            return {
                "p2_add_joint_event": "AF",  # Phase 2 - Add Joint Event
                "p2_see_joint_requests": "AG",  # Phase 2 - See Joint Event Requests
                "p2_reject_confirm": "AH",  # Phase 2 - Reject/Confirm Joint Event
                "p2_change_report_cmd": "AI",  # Phase 2 - Change Report Cmd
                "p2_polymorphism": "AJ",  # Phase 2 - Polymorphism
                "p2_no_downcast": "AK",  # Phase 2 - No Downcast
                "p2_no_duplication": "AL",  # Phase 2 - No Duplication
                "p2_indentation": "AM",  # Phase 2 - Indentation
                "p2_naming": "AN",  # Phase 2 - Naming
                "p2_consistency": "AO",  # Phase 2 - Consistency
                "p2_test_cases": "AP",  # Phase 2 - Test Cases
                "p2_raw_score": "AQ",  # Phase 2 - Raw Score
                "p2_mastery": "AR",  # Phase 2 - Mastery
                "p2_edit_code": "AS",  # Phase 2 - Edit Code
                "p2_latency": "AT",  # Phase 2 - Latency
                "p2_upload_structure": "AU",  # Phase 2 - Upload Structure
                "p2_penalty": "AV",  # Phase 2 - Penalty
                "p2_final_score": "AW",  # Phase 2 - Final Score
            }
        elif phase == "phase3":
            return {
                "p3_signup_page": "AX",  # Phase 3 - Signup Page
                "p3_login_page": "AY",  # Phase 3 - Login Page
                "p3_home_page": "AZ",  # Phase 3 - Home Page
                "p3_logout": "BA",  # Phase 3 - Logout
                "p3_add_task": "BB",  # Phase 3 - Add Task
                "p3_delete_task": "BC",  # Phase 3 - Delete Task
                "p3_edit_task": "BD",  # Phase 3 - Edit Task
                "p3_add_events": "BE",  # Phase 3 - Add Events
                "p3_get_join_events": "BF",  # Phase 3 - Get Join Events
                "p3_confirm_reject": "BG",  # Phase 3 - Confirm/Reject Join Events
                "p3_report": "BH",  # Phase 3 - Report
                "p3_html_render": "BI",  # Phase 3 - HTML Render
                "p3_handlers": "BJ",  # Phase 3 - Handlers
                "p3_css": "BK",  # Phase 3 - CSS
                "p3_js": "BL",  # Phase 3 - JS
                "p3_makefile": "BM",  # Phase 3 - Makefile
                "p3_clean_coding": "BN",  # Phase 3 - Clean Coding
                "p3_bonus": "BO",  # Phase 3 - Bonus✨🎉
                "p3_multifile": "BP",  # Phase 3 - Multifile
                "p3_raw_score": "BQ",  # Phase 3 - Raw Score
                "p3_mastery": "BR",  # Phase 3 - Mastery
                "p3_edit_code": "BS",  # Phase 3 - Edit Code
                "p3_latency": "BT",  # Phase 3 - Latency
                "p3_upload_structure": "BU",  # Phase 3 - Upload Structure
                "p3_penalty": "BV",  # Phase 3 - Penalty
                "p3_final_score": "BW",  # Phase 3 - Final Score
                "p3_comment": "BX",  # Phase 3 - Comment
                "p3_plagiarism": "BY",  # Phase 3 - Plagiarism
                "final_score": "BZ",  # Final Score
            }

    return {}


def update_student_grade(student_id, grade_data, assignment_type, phase=None):
    """Finds a student by ID and updates their grade information in the sheet."""
    try:
        sheet = get_sheet()
        cell = sheet.find(str(student_id))
        row = cell.row

        # Get the appropriate column mapping
        update_map = get_column_mapping(assignment_type, phase)

        for col, val in update_map.items():
            if val is not None and col in grade_data:
                sheet.update_acell(f"{val}{row}", grade_data[col])

        print(
            f"Successfully updated grades for student {student_id} ({assignment_type}{f' - {phase}' if phase else ''})"
        )
    except gspread.exceptions.CellNotFound:
        print(f"Error: Student ID {student_id} not found in the sheet.")
    except Exception as e:
        print(f"An error occurred while updating the sheet: {e}")


def update_multi_phase_grades(student_id, phase_grades, assignment_type="A6"):
    """Updates grades for multi-phase assignments like A6."""
    for phase, grade_data in phase_grades.items():
        update_student_grade(student_id, grade_data, assignment_type, phase)
