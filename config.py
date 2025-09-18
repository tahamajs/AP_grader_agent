# config.py

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google Sheets Configuration
SHEET_NAME = "1swgtRM3awVelITJdgJC9cc6eUIsBvd5GKq1YhwVFGEg"
CREDENTIALS_FILE = "credentials.json"

# Local directory to store cloned student projects
PROJECTS_DIR = "student_projects"

# Path to your test cases directory (organized by practice)
TEST_CASES_DIR = "/Users/tahamajs/Documents/uni/LLM/grading_agent/test_cases"

# Path to practice description PDFs
PRACTICES_DIR = "/Users/tahamajs/Documents/uni/LLM/grading_agent/description"

# Clone directory for student repositories
CLONE_DIR = "cloned_repos"

# The command to build a student's project (e.g., 'make', 'cmake . && make')
BUILD_COMMAND = "make"

# The name of the executable produced by the build
EXECUTABLE_NAME = "student_program"

# Model Configuration
MODEL_CONFIG = {
    "api_key": os.getenv("GOOGLE_API_KEY"),
    "model": os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
    "grading": {
        "temperature": float(os.getenv("GRADING_TEMPERATURE", "0.1")),
        "top_p": float(os.getenv("GRADING_TOP_P", "0.8")),
        "top_k": int(os.getenv("GRADING_TOP_K", "40")),
        "max_output_tokens": int(os.getenv("GRADING_MAX_OUTPUT_TOKENS", "4096")),
    },
    "generation": {
        "temperature": float(os.getenv("GENERATION_TEMPERATURE", "0.7")),
        "top_p": float(os.getenv("GENERATION_TOP_P", "0.9")),
        "top_k": int(os.getenv("GENERATION_TOP_K", "50")),
        "max_output_tokens": int(os.getenv("GENERATION_MAX_OUTPUT_TOKENS", "2048")),
    },
    "retry": {
        "max_retries": int(os.getenv("MAX_RETRIES", "3")),
        "delay": float(os.getenv("RETRY_DELAY", "1.0")),
    },
}

# Logging Configuration
LOG_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "max_size": int(os.getenv("LOG_MAX_SIZE", "10485760")),  # 10MB
    "backup_count": int(os.getenv("LOG_BACKUP_COUNT", "5")),
}

# Practice-specific configurations with detailed grading metrics
PRACTICE_CONFIGS = {
    "A1": {
        "name": "Assignment 1 - Basic Programming",
        "build_command": "make",
        "executable_name": "student_program",
        "test_cases_dir": "test_cases/A1",
        "grading_criteria": {
            "logic": {
                "weight": 5,
                "sub_criteria": {"using_iterators": 1, "using_containers": 1},
            },
            "design": {
                "weight": 35,
                "sub_criteria": {
                    "separate_io_from_logic": 2,
                    "using_structs": 1,
                    "no_godly_main": 2,
                    "small_functions_single_responsibility": 3,
                },
            },
            "clean_coding": {
                "weight": 25,
                "sub_criteria": {
                    "no_comments": 1,
                    "no_duplication": 1,
                    "indentation": 1,
                    "magic_values_no_global_vars": 1,
                    "naming": 1,
                    "consistency": 1,
                },
            },
            "correctness": {"weight": 30, "sub_criteria": {"test_cases": 20}},
        },
        "penalties": {
            "using_goto": -5,
            "late_delivery": -10,
            "raw_late": 4,
            "final_late": 0.2,
            "upload_structure": 4,
            "penalty": 0.15,
        },
    },
    "A3": {
        "name": "Assignment 3 - Algorithms and Data Structures",
        "build_command": "make",
        "executable_name": "student_program",
        "test_cases_dir": "test_cases/A3",
        "grading_criteria": {
            "q1_latex": {
                "weight": 18,
                "sub_criteria": {
                    "recursive_logic": 2,
                    "test_cases": 15,
                    "upload_two_testcases": 2,
                },
            },
            "q2_household": {
                "weight": 18,
                "sub_criteria": {
                    "recursive_logic": 2,
                    "test_cases": 15,
                    "upload_two_testcases": 2,
                },
            },
            "q3_foodro": {
                "weight": 20,
                "sub_criteria": {
                    "backtracking": 2,
                    "test_cases": 15,
                    "upload_two_testcases": 2,
                },
            },
            "q4_unknown": {
                "weight": 15,
                "sub_criteria": {
                    "backtracking": 2,
                    "test_cases": 10,
                    "upload_two_testcases": 2,
                },
            },
            "design": {
                "weight": 20,
                "sub_criteria": {
                    "separate_io_from_logic": 1,
                    "proper_data_structures": 3,
                    "no_godly_main": 1,
                    "small_functions_single_responsibility": 2,
                    "no_duplication": 1,
                    "indentation": 1,
                    "magic_values_no_global_vars": 1,
                    "naming": 1,
                    "consistency": 1,
                },
            },
            "git": {
                "weight": 6,
                "sub_criteria": {"commit_messages": 1, "standard_commits": 1},
            },
            "correctness": {"weight": 49, "sub_criteria": {"test_cases": 60}},
        },
        "penalties": {
            "clean_code": -2,
            "late_delivery": -10,
            "raw_late": 4,
            "final_late": 0.2,
            "upload_structure": 4,
            "penalty": 0.15,
        },
    },
    "A4": {
        "name": "Assignment 4 - Object Oriented Programming",
        "build_command": "make",
        "executable_name": "student_program",
        "test_cases_dir": "test_cases/A4",
        "grading_criteria": {
            "object_oriented_design": {
                "weight": 53,
                "sub_criteria": {
                    "break_into_classes": 5,
                    "responsibility_assignment": 5,
                    "field_assignment": 5,
                    "public_private_access_modifiers": 3,
                    "no_logic_in_main": 3,
                    "small_functions": 2,
                },
            },
            "clean_coding": {
                "weight": 10,
                "sub_criteria": {
                    "no_duplication": 1,
                    "indentation": 1,
                    "magic_values_no_global_vars": 1,
                    "naming": 1,
                    "consistency": 1,
                },
            },
            "multifile": {
                "weight": 10,
                "sub_criteria": {
                    "break_into_files": 1,
                    "header_guards": 1,
                    "makefile": 1,
                },
            },
            "git": {
                "weight": 5,
                "sub_criteria": {"commit_messages": 1, "standard_commits": 1},
            },
            "correctness": {"weight": 22, "sub_criteria": {"test_cases": 10}},
        },
        "penalties": {
            "late_delivery": -10,
            "raw_late": 4,
            "final_late": 0.1,
            "upload_structure": 4,
            "penalty": 0.05,
        },
    },
    "A5": {
        "name": "Assignment 5 - Tower Defense Game",
        "build_command": "make",
        "executable_name": "student_program",
        "test_cases_dir": "test_cases/A5",
        "grading_criteria": {
            "design": {
                "weight": 56,
                "sub_criteria": {
                    "attack_wave": 6,
                    "normal_tower": 5,
                    "ice_tower": 7,
                    "bomb_tower": 7,
                    "tower_domain_visibility": 5,
                    "normal_balloon": 5,
                    "pregnant_balloon": 7,
                    "panel": 4,
                    "launch_control": 5,
                    "players_health_panel": 2,
                    "music": 2,
                    "game_end": 1,
                },
            },
            "object_oriented_design": {
                "weight": 14,
                "sub_criteria": {
                    "break_into_classes": 5,
                    "encapsulation": 5,
                    "small_functions": 2,
                    "no_duplication": 1,
                    "indentation": 1,
                },
            },
            "clean_coding": {
                "weight": 10,
                "sub_criteria": {
                    "magic_values_no_global_vars": 1,
                    "naming": 1,
                    "consistency": 1,
                },
            },
            "git": {
                "weight": 10,
                "sub_criteria": {
                    "break_into_files": 1,
                    "header_guards": 1,
                    "makefile": 1,
                    "commit_messages": 1,
                    "standard_commits": 1,
                },
            },
            "correctness": {"weight": 22, "sub_criteria": {"test_cases": 10}},
        },
        "penalties": {
            "late_delivery": -10,
            "raw_late": 4,
            "final_late": 0.2,
            "upload_structure": 4,
            "penalty": 0.15,
        },
    },
    "A6": {
        "name": "Assignment 6 - Event Management System",
        "build_command": "make",
        "executable_name": "student_program",
        "test_cases_dir": "test_cases/A6",
        "phases": {
            "phase1": {
                "name": "Phase 1 - Core Features",
                "grading_criteria": {
                    "features": {
                        "weight": 12,
                        "sub_criteria": {
                            "login_signup": 2,
                            "normal_event": 2,
                            "periodic_event": 2,
                            "task": 2,
                            "object_oriented_design": 2,
                            "no_god_class": 1,
                            "polymorphism": 2,
                            "no_downcast": 1,
                            "encapsulation": 2,
                            "separate_io_from_logic": 1,
                            "exception_handling": 2,
                            "no_duplication": 2,
                            "indentation": 1,
                            "magic_values": 1,
                            "naming": 3,
                            "consistency": 3,
                            "break_into_files": 1,
                            "makefile": 1,
                            "test_cases": 30,
                        },
                    },
                    "design": {"weight": 39},
                    "clean_coding": {"weight": 10},
                    "multifile": {"weight": 9},
                    "correctness": {"weight": 30},
                },
            },
            "phase2": {
                "name": "Phase 2 - Feature Addition",
                "grading_criteria": {
                    "feature_addition": {
                        "weight": 40,
                        "sub_criteria": {
                            "add_joint_event": 2,
                            "see_joint_event_requests": 2,
                            "reject_confirm_joint_event": 2,
                            "change_report_cmd": 2,
                            "polymorphism": 2,
                            "no_downcast": 1,
                            "no_duplication": 2,
                            "indentation": 2,
                            "naming": 2,
                            "consistency": 2,
                            "test_cases": 15,
                        },
                    },
                    "design": {"weight": 18},
                    "clean_coding": {"weight": 12},
                    "correctness": {"weight": 30},
                },
            },
            "phase3": {
                "name": "Phase 3 - Web Interface",
                "grading_criteria": {
                    "web": {
                        "weight": 65,
                        "sub_criteria": {
                            "signup_page": 2,
                            "login_page": 2,
                            "home_page": 2,
                            "logout": 2,
                            "add_task": 2,
                            "delete_task": 2,
                            "edit_task": 2,
                            "add_events": 2,
                            "get_join_events": 2,
                            "confirm_reject_join_events": 2,
                            "report": 3,
                            "html_render": 3,
                            "handlers": 3,
                            "css": 2,
                            "js": 1,
                            "makefile": 2,
                        },
                    },
                    "clean_coding": {"weight": 30},
                    "bonus": {"weight": 10},
                    "multifile": {"weight": 5},
                },
            },
        },
        "penalties": {
            "grace": 1,
            "late_delivery": -10,
            "raw_late": 4,
            "final_late": 0.2,
            "upload_structure": 4,
            "penalty": 0.15,
        },
    },
    "A2": {
        "name": "Assignment 2 - Data Handling and Design",
        "build_command": "make",
        "executable_name": "student_program",
        "test_cases_dir": "test_cases/A2",
        "grading_criteria": {
            "data": {
                "weight": 15,
                "sub_criteria": {
                    "reading_input": 5,
                    "storing_information_data_structures": 10,
                },
            },
            "design": {
                "weight": 28,
                "sub_criteria": {
                    "separate_io_from_logic": 8,
                    "no_godly_main": 10,
                    "small_functions_single_responsibility": 10,
                },
            },
            "clean_coding": {
                "weight": 28,
                "sub_criteria": {
                    "no_duplication": 7,
                    "magic_values_no_global_vars": 7,
                    "naming": 7,
                    "consistency": 7,
                },
            },
            "git": {
                "weight": 7,
                "sub_criteria": {
                    "commit_messages": 4,
                    "standard_commits": 3,
                },
            },
            "correctness": {
                "weight": 30,
                "sub_criteria": {
                    "test_cases": 20,
                },
            },
        },
        "penalties": {
            "no_goto": -5,
            "no_comment": -2,
            "late_delivery": -10,
            "raw_late": 4,
            "final_late": 0.2,
            "upload_structure": 4,
            "penalty": 0.15,
        },
    },
}
