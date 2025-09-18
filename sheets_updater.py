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


def update_student_grade(student_id, grade_data):
    """Finds a student by ID and updates their grade information in the sheet."""
    try:
        sheet = get_sheet()
        cell = sheet.find(str(student_id))
        row = cell.row

        # This mapping depends on your sheet's column order. ADJUST AS NEEDED.
        # Based on the provided sheet structure
        update_map = {
            "E": grade_data.get("logic_iterators"),  # Logic - Using Iterators
            "F": grade_data.get("design_containers"),  # Design - Using Containers
            "G": grade_data.get("design_io_separation"),  # Design - I/O Separation
            "H": grade_data.get("design_structs"),  # Design - Structs
            "I": grade_data.get("design_no_god_main"),  # Design - No Godly Main
            "J": grade_data.get("design_small_functions"),  # Design - Small Functions
            "K": grade_data.get("clean_no_comments"),  # Clean - No Comments
            "L": grade_data.get("clean_no_duplication"),  # Clean - No Duplication
            "M": grade_data.get("clean_indentation"),  # Clean - Indentation
            "N": grade_data.get("clean_magic_values"),  # Clean - Magic Values
            "O": grade_data.get("clean_naming"),  # Clean - Naming
            "P": grade_data.get("clean_consistency"),  # Clean - Consistency
            "Q": grade_data.get("correctness_score"),  # Correctness
            "R": grade_data.get("raw_score"),  # Raw Score
            "Z": grade_data.get("generated_comment"),  # Comment
            "AB": grade_data.get("final_score"),  # Final Score
        }

        for col, val in update_map.items():
            if val is not None:
                sheet.update_acell(f"{col}{row}", val)

        print(f"Successfully updated grades for student {student_id}")
    except gspread.exceptions.CellNotFound:
        print(f"Error: Student ID {student_id} not found in the sheet.")
    except Exception as e:
        print(f"An error occurred while updating the sheet: {e}")
