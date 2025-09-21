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
            "logic_iterators": "E",
            "logic_containers": "F",
            "design_io_separation": "G",
            "design_structs": "H",
            "design_no_god_main": "I",
            "design_small_functions": "J",
            "clean_no_comments": "K",
            "clean_no_duplication": "L",
            "clean_indentation": "M",
            "clean_magic_values": "N",
            "clean_naming": "O",
            "clean_consistency": "P",
            "correctness_test_cases": "Q",
            "raw_score": "R",
            "using_goto": "S",
            "edit_code": "T",
            "latency": "U",
            "upload_structure": "V",
            "penalty": "W",
            "comment": "X",
            "plagiarism": "Y",
            "final_score": "Z",
        }

    elif assignment_type == "A2":
        return {
            "data_reading_input": "E",
            "data_storing_information": "F",
            "design_separate_io": "G",
            "design_no_godly_main": "H",
            "design_small_functions": "I",
            "clean_no_duplication": "J",
            "clean_magic_values": "K",
            "clean_naming": "L",
            "clean_consistency": "M",
            "git_commit_messages": "N",
            "git_standard_commits": "O",
            "correctness_test_cases": "P",
            "raw_score": "Q",
            "using_goto": "R",
            "edit_code": "S",
            "latency": "T",
            "upload_structure": "U",
            "penalty": "V",
            "comment": "W",
            "plagiarism": "X",
            "final_score": "Y",
        }

    elif assignment_type == "A3":
        return {
            "q1_recursive_logic": "E",
            "q1_test_cases": "F",
            "q1_upload_testcases": "G",
            "q2_recursive_logic": "H",
            "q2_test_cases": "I",
            "q2_upload_testcases": "J",
            "q3_backtracking": "K",
            "q3_test_cases": "L",
            "q3_upload_testcases": "M",
            "q4_backtracking": "N",
            "q4_test_cases": "O",
            "q4_upload_testcases": "P",
            "design_io_separation": "Q",
            "design_data_structures": "R",
            "design_no_god_main": "S",
            "design_small_functions": "T",
            "design_no_duplication": "U",
            "design_indentation": "V",
            "design_magic_values": "W",
            "design_naming": "X",
            "design_consistency": "Y",
            "git_commit_messages": "Z",
            "git_standard_commits": "AA",
            "correctness_test_cases": "AB",
            "raw_score": "AC",
            "mastery": "AD",
            "clean_code": "AE",
            "edit_code": "AF",
            "latency": "AG",
            "upload_structure": "AH",
            "penalty": "AI",
            "comment": "AJ",
            "plagiarism": "AK",
            "final_score": "AL",
        }

    elif assignment_type == "A4":
        return {
            "oop_break_classes": "E",
            "oop_responsibility": "F",
            "oop_field_assignment": "G",
            "oop_access_modifiers": "H",
            "oop_no_logic_main": "I",
            "oop_small_functions": "J",
            "clean_no_duplication": "K",
            "clean_indentation": "L",
            "clean_magic_values": "M",
            "clean_naming": "N",
            "clean_consistency": "O",
            "multifile_break_files": "P",
            "multifile_header_guards": "Q",
            "multifile_makefile": "R",
            "git_commit_messages": "S",
            "git_standard_commits": "T",
            "correctness_test_cases": "U",
            "raw_score": "V",
            "mastery": "W",
            "edit_code": "X",
            "latency": "Y",
            "upload_structure": "Z",
            "penalty": "AA",
            "comment": "AB",
            "plagiarism": "AC",
            "final_score": "AD",
        }

    elif assignment_type == "A5":
        return {
            "design_attack_wave": "E",
            "design_normal_tower": "F",
            "design_ice_tower": "G",
            "design_bomb_tower": "H",
            "design_tower_visibility": "I",
            "design_normal_balloon": "J",
            "design_pregnant_balloon": "K",
            "design_panel": "L",
            "design_launch_control": "M",
            "design_health_panel": "N",
            "design_music": "O",
            "design_game_end": "P",
            "oop_break_classes": "Q",
            "oop_encapsulation": "R",
            "oop_small_functions": "S",
            "oop_no_duplication": "T",
            "oop_indentation": "U",
            "clean_magic_values": "V",
            "clean_naming": "W",
            "clean_consistency": "X",
            "git_break_files": "Y",
            "git_header_guards": "Z",
            "git_makefile": "AA",
            "git_commit_messages": "AB",
            "git_standard_commits": "AC",
            "correctness_test_cases": "AD",
            "raw_score": "AE",
            "edit_code": "AF",
            "latency": "AG",
            "upload_structure": "AH",
            "penalty": "AI",
            "comment": "AJ",
            "plagiarism": "AK",
            "final_score": "AL",
        }

    elif assignment_type == "A6":
        if phase == "phase1":
            return {
                "p1_login_signup": "E",
                "p1_normal_event": "F",
                "p1_periodic_event": "G",
                "p1_task": "H",
                "p1_object_oriented": "I",
                "p1_no_god_class": "J",
                "p1_polymorphism": "K",
                "p1_no_downcast": "L",
                "p1_encapsulation": "M",
                "p1_separate_io": "N",
                "p1_exception_handling": "O",
                "p1_no_duplication": "P",
                "p1_indentation": "Q",
                "p1_magic_values": "R",
                "p1_naming": "S",
                "p1_consistency": "T",
                "p1_break_files": "U",
                "p1_makefile": "V",
                "p1_test_cases": "W",
                "p1_raw_score": "X",
                "p1_mastery": "Y",
                "p1_edit_code": "Z",
                "p1_latency": "AA",
                "p1_upload_structure": "AB",
                "p1_penalty": "AC",
                "p1_comment": "AD",
                "p1_final_score": "AE",
            }
        elif phase == "phase2":
            return {
                "p2_add_joint_event": "AF",
                "p2_see_joint_requests": "AG",
                "p2_reject_confirm": "AH",
                "p2_change_report_cmd": "AI",
                "p2_polymorphism": "AJ",
                "p2_no_downcast": "AK",
                "p2_no_duplication": "AL",
                "p2_indentation": "AM",
                "p2_naming": "AN",
                "p2_consistency": "AO",
                "p2_test_cases": "AP",
                "p2_raw_score": "AQ",
                "p2_mastery": "AR",
                "p2_edit_code": "AS",
                "p2_latency": "AT",
                "p2_upload_structure": "AU",
                "p2_penalty": "AV",
                "p2_final_score": "AW",
            }
        elif phase == "phase3":
            return {
                "p3_signup_page": "AX",
                "p3_login_page": "AY",
                "p3_home_page": "AZ",
                "p3_logout": "BA",
                "p3_add_task": "BB",
                "p3_delete_task": "BC",
                "p3_edit_task": "BD",
                "p3_add_events": "BE",
                "p3_get_join_events": "BF",
                "p3_confirm_reject": "BG",
                "p3_report": "BH",
                "p3_html_render": "BI",
                "p3_handlers": "BJ",
                "p3_css": "BK",
                "p3_js": "BL",
                "p3_makefile": "BM",
                "p3_clean_coding": "BN",
                "p3_bonus": "BO",
                "p3_multifile": "BP",
                "p3_raw_score": "BQ",
                "p3_mastery": "BR",
                "p3_edit_code": "BS",
                "p3_latency": "BT",
                "p3_upload_structure": "BU",
                "p3_penalty": "BV",
                "p3_final_score": "BW",
                "p3_comment": "BX",
                "p3_plagiarism": "BY",
                "final_score": "BZ",
            }

    return {}


def update_student_grade(student_id, grade_data, assignment_type, phase=None):
    """Finds a student by ID and updates their grade information in the sheet."""
    try:
        sheet = get_sheet()
        cell = sheet.find(str(student_id))
        row = cell.row

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
