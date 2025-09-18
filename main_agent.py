# main_agent.py
import tools
import sheets_updater
import langchain_integration
import config
from prompts import get_grading_prompt, get_format_instructions
from langchain_integration import A6GradingOutput

import argparse
import os
import csv
import json
import re
from datetime import datetime


# ANSI color codes for better terminal output
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}")


def print_section(title, content="", color=Colors.BLUE):
    """Print a section with title and content"""
    print(f"\n{color}{Colors.BOLD}{title}:{Colors.END}")
    if content:
        print(f"{color}{content}{Colors.END}")


def print_score(score, max_score, label):
    """Print a score with color coding"""
    percentage = (score / max_score) * 100 if max_score > 0 else 0
    if percentage >= 90:
        color = Colors.GREEN
    elif percentage >= 70:
        color = Colors.YELLOW
    else:
        color = Colors.RED

    print(
        f"  {label}: {color}{Colors.BOLD}{score:.1f}/{max_score:.1f}{Colors.END} ({percentage:.1f}%)"
    )


def analyze_test_failures(test_results):
    """Analyze test results for failures and provide debugging recommendations."""
    failures = []
    debug_recommendations = []

    # Parse test results for failures
    execution_summary = test_results.get("execution_summary", "")

    # Common failure patterns to look for
    failure_patterns = [
        (r"FAILED", "Test Failure"),
        (r"ERROR", "Test Error"),
        (r"SEGFAULT|Segmentation fault", "Memory Error"),
        (r"Exception|std::exception", "Exception Error"),
        (r"Assertion failed", "Assertion Failure"),
        (r"Timeout", "Timeout Error"),
        (r"Memory leak", "Memory Leak"),
    ]

    for pattern, failure_type in failure_patterns:
        if re.search(pattern, execution_summary, re.IGNORECASE):
            failures.append(failure_type)

    # Generate debugging recommendations based on failure types
    if "Memory Error" in failures:
        debug_recommendations.append(
            {
                "type": "Memory Error",
                "priority": "High",
                "description": "Segmentation fault or memory corruption detected",
                "debug_steps": [
                    "Run with gdb: gdb ./your_program",
                    "Set breakpoint at suspected location",
                    "Use valgrind: valgrind --leak-check=full ./your_program",
                    "Check for null pointer dereferences",
                    "Verify array bounds and vector access",
                ],
                "common_fixes": [
                    "Add null checks before pointer dereference",
                    "Use smart pointers (unique_ptr, shared_ptr)",
                    "Validate array indices before access",
                    "Check vector bounds with .at() instead of []",
                ],
                "code_example": """
// Before: Unsafe pointer access
if (ptr->getValue() > 0)

// After: Safe pointer access
if (ptr != nullptr && ptr->getValue() > 0)

// Before: Unsafe array access
arr[i] = value;

// After: Safe array access
if (i >= 0 && i < arr.size()) {
    arr[i] = value;
}""",
            }
        )

    if "Exception Error" in failures:
        debug_recommendations.append(
            {
                "type": "Exception Error",
                "priority": "High",
                "description": "Unhandled exceptions causing program crashes",
                "debug_steps": [
                    "Use try-catch blocks around risky operations",
                    "Check exception propagation in call stack",
                    "Use gdb to catch unhandled exceptions",
                    "Review error handling in file I/O operations",
                ],
                "common_fixes": [
                    "Add try-catch blocks around file operations",
                    "Handle std::exception and derived classes",
                    "Provide meaningful error messages",
                    "Use RAII for resource management",
                ],
                "code_example": """
// Before: No exception handling
std::ifstream file(filename);
std::string line;
while (std::getline(file, line)) {
    process_line(line);
}

// After: With exception handling
try {
    std::ifstream file(filename);
    if (!file.is_open()) {
        throw std::runtime_error("Failed to open file: " + filename);
    }

    std::string line;
    while (std::getline(file, line)) {
        process_line(line);
    }
} catch (const std::exception& e) {
    std::cerr << "Error: " << e.what() << std::endl;
    return false;
}""",
            }
        )

    if "Test Failure" in failures or "Assertion Failure" in failures:
        debug_recommendations.append(
            {
                "type": "Logic Error",
                "priority": "Medium",
                "description": "Test assertions failing due to incorrect logic",
                "debug_steps": [
                    "Review the failing test case requirements",
                    "Add debug output to trace execution flow",
                    "Use debugger to step through the failing code",
                    "Compare expected vs actual values",
                    "Check boundary conditions and edge cases",
                ],
                "common_fixes": [
                    "Fix algorithm logic errors",
                    "Handle edge cases properly",
                    "Validate input parameters",
                    "Add boundary checks for calculations",
                ],
                "code_example": """
// Before: Missing boundary check
int divide(int a, int b) {
    return a / b;  // Division by zero possible
}

// After: With boundary check
int divide(int a, int b) {
    if (b == 0) {
        throw std::invalid_argument("Division by zero");
    }
    return a / b;
}

// Before: Array access without bounds check
for (int i = 0; i <= size; i++) {  // Off-by-one error
    arr[i] = 0;
}

// After: Correct bounds checking
for (int i = 0; i < size; i++) {
    arr[i] = 0;
}""",
            }
        )

    if "Memory Leak" in failures:
        debug_recommendations.append(
            {
                "type": "Memory Leak",
                "priority": "Medium",
                "description": "Memory not properly deallocated",
                "debug_steps": [
                    "Use valgrind to detect memory leaks",
                    "Check for missing delete/delete[] calls",
                    "Review pointer ownership and lifecycle",
                    "Use smart pointers where appropriate",
                ],
                "common_fixes": [
                    "Use RAII principle with smart pointers",
                    "Ensure delete/delete[] for every new/new[]",
                    "Use std::unique_ptr for exclusive ownership",
                    "Use std::shared_ptr for shared ownership",
                ],
                "code_example": """
// Before: Manual memory management (leak prone)
Event* event = new Event();
events.push_back(event);
// Forgot to delete - memory leak!

// After: Smart pointer management
std::unique_ptr<Event> event = std::make_unique<Event>();
events.push_back(event.get());  // Store raw pointer if needed
// Automatic cleanup when unique_ptr goes out of scope

// Before: Raw pointer in container
std::vector<Event*> events;
events.push_back(new Event());

// After: Smart pointer container
std::vector<std::unique_ptr<Event>> events;
events.push_back(std::make_unique<Event>());
// Automatic cleanup of all elements""",
            }
        )

    return failures, debug_recommendations


def print_test_failure_analysis(failures, debug_recommendations):
    """Print detailed test failure analysis and debugging help."""
    if not failures:
        print(f"\n{Colors.GREEN}✅ NO TEST FAILURES DETECTED{Colors.END}")
        print(f"{Colors.GREEN}All tests are passing! Great job!{Colors.END}")
        return

    print(f"\n{Colors.RED}❌ TEST FAILURES DETECTED{Colors.END}")
    print(f"{Colors.RED}{'='*60}{Colors.END}")

    print(f"\n{Colors.YELLOW}🔍 FAILURE TYPES IDENTIFIED:{Colors.END}")
    for failure in failures:
        print(f"  {Colors.RED}• {failure}{Colors.END}")

    print(f"\n{Colors.BLUE}🛠️ DEBUGGING RECOMMENDATIONS:{Colors.END}")
    print(f"{Colors.BLUE}{'-'*60}{Colors.END}")

    for i, rec in enumerate(debug_recommendations, 1):
        priority_color = (
            Colors.RED
            if rec["priority"] == "High"
            else Colors.YELLOW if rec["priority"] == "Medium" else Colors.GREEN
        )
        priority_icon = (
            "🔴"
            if rec["priority"] == "High"
            else "🟡" if rec["priority"] == "Medium" else "🟢"
        )

        print(
            f"\n{priority_color}{Colors.BOLD}{i}. {rec['type']} ({rec['priority']} Priority){Colors.END}"
        )
        print(f"  {Colors.BLUE}📝 {rec['description']}{Colors.END}")

        print(f"\n  {Colors.GREEN}🔧 DEBUG STEPS:{Colors.END}")
        for step in rec["debug_steps"]:
            print(f"    {Colors.BLUE}• {step}{Colors.END}")

        print(f"\n  {Colors.GREEN}💡 COMMON FIXES:{Colors.END}")
        for fix in rec["common_fixes"]:
            print(f"    {Colors.BLUE}• {fix}{Colors.END}")

        if rec.get("code_example"):
            print(f"\n  {Colors.GREEN}📋 CODE EXAMPLE:{Colors.END}")
            print(f"  {Colors.BLUE}{rec['code_example'].strip()}{Colors.END}")


def print_debugging_workflow():
    """Print a comprehensive debugging workflow."""
    print(
        f"\n{Colors.BOLD}{Colors.BLUE}🔧 COMPREHENSIVE DEBUGGING WORKFLOW:{Colors.END}"
    )
    print(f"{Colors.BLUE}{'-'*60}{Colors.END}")

    workflow_steps = [
        (
            "1. Reproduce the Issue",
            "Run the failing test in isolation to confirm the problem",
        ),
        (
            "2. Gather Information",
            "Collect stack traces, error messages, and test input data",
        ),
        (
            "3. Isolate the Problem",
            "Use debugger to narrow down the exact location of failure",
        ),
        (
            "4. Analyze Root Cause",
            "Determine why the code is failing (logic, memory, I/O, etc.)",
        ),
        ("5. Implement Fix", "Apply the appropriate solution based on the analysis"),
        ("6. Test the Fix", "Run the test again to verify the fix works"),
        (
            "7. Add Regression Test",
            "Create additional tests to prevent this issue in the future",
        ),
        ("8. Code Review", "Have someone else review your fix for correctness"),
    ]

    for step, description in workflow_steps:
        print(
            f"  {Colors.BOLD}{step}:{Colors.END} {Colors.BLUE}{description}{Colors.END}"
        )

    print(f"\n{Colors.BOLD}{Colors.GREEN}🛠️ USEFUL DEBUGGING TOOLS:{Colors.END}")
    tools_list = [
        ("gdb", "GNU Debugger - step through code, inspect variables"),
        ("valgrind", "Memory error detector and profiler"),
        ("cppcheck", "Static analysis tool for C/C++ code"),
        (
            "AddressSanitizer",
            "Fast memory error detector (compile with -fsanitize=address)",
        ),
        ("ThreadSanitizer", "Data race detector (compile with -fsanitize=thread)"),
    ]

    for tool, description in tools_list:
        print(
            f"  {Colors.BOLD}{tool}:{Colors.END} {Colors.BLUE}{description}{Colors.END}"
        )


def get_test_failure_impact(failures):
    """Calculate the impact of test failures on grading."""
    if not failures:
        return 1.0, "No test failures - full credit"

    failure_count = len(failures)
    has_critical = any(f in ["Memory Error", "Exception Error"] for f in failures)

    if has_critical:
        if failure_count >= 3:
            return 0.2, "Critical failures with multiple issues - severe impact"
        else:
            return 0.4, "Critical failures detected - significant impact"
    else:
        if failure_count >= 4:
            return 0.5, "Multiple logic failures - moderate impact"
        elif failure_count >= 2:
            return 0.7, "Some test failures - minor impact"


def print_recommendations(comment):
    """Print recommendations with better formatting"""
    if not comment or comment.strip() == "":
        return

    print(f"\n{Colors.YELLOW}{Colors.BOLD}📋 DETAILED RECOMMENDATIONS:{Colors.END}")
    print(f"{Colors.YELLOW}{'-'*60}{Colors.END}")

    # Split comment into sections
    lines = comment.split("\n")
    current_section = ""
    in_code_block = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check for section headers
        if line.startswith("**") and line.endswith("**"):
            section_title = line.strip("*")
            if "Priority" in section_title:
                if "High" in section_title:
                    color = Colors.RED
                elif "Medium" in section_title:
                    color = Colors.YELLOW
                else:
                    color = Colors.GREEN
                print(f"\n{color}{Colors.BOLD}⚡ {section_title}:{Colors.END}")
            else:
                print(f"\n{Colors.BLUE}{Colors.BOLD}📌 {section_title}:{Colors.END}")
        elif (
            line.startswith("- **")
            or line.startswith("**High")
            or line.startswith("**Medium")
            or line.startswith("**Low")
        ):
            # Priority items
            if "**High" in line:
                color = Colors.RED
                icon = "🔴"
            elif "**Medium" in line:
                color = Colors.YELLOW
                icon = "🟡"
            else:
                color = Colors.GREEN
                icon = "🟢"
            print(f"  {icon} {color}{line.strip('*')}{Colors.END}")
        elif line.startswith("- ") and (
            "Priority" in line or "Why" in line or "How" in line
        ):
            print(f"    {Colors.BLUE}• {line[2:]}{Colors.END}")
        elif line.startswith("**Before**") or line.startswith("**After**"):
            if "**Before**" in line:
                print(
                    f"    {Colors.RED}❌ BEFORE: {line.replace('**Before**:', '').replace('**Before**', '').strip()}{Colors.END}"
                )
            else:
                print(
                    f"    {Colors.GREEN}✅ AFTER: {line.replace('**After**:', '').replace('**After**', '').strip()}{Colors.END}"
                )
        elif line.startswith("* **"):
            print(f"  {Colors.BLUE}• {line[4:].strip('*')}{Colors.END}")
        else:
            # Regular content
            if len(line) > 80:
                # Wrap long lines
                words = line.split()
                current_line = ""
                for word in words:
                    if len(current_line + " " + word) > 80:
                        print(f"  {Colors.BLUE}{current_line}{Colors.END}")
                        current_line = word
                    else:
                        current_line += " " + word if current_line else word
                if current_line:
                    print(f"  {Colors.BLUE}{current_line}{Colors.END}")
            else:
                print(f"  {Colors.BLUE}{line}{Colors.END}")


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def save_full_feedback(
    student_id: str,
    assignment_type: str,
    final_grade_data: dict,
    llm_structured: dict,
    test_results: dict,
    analysis_report: str,
    source_code: str,
):
    """Save full feedback as CSV row and a detailed markdown document."""
    outputs_dir = os.path.join(os.getcwd(), "feedback_outputs")
    _ensure_dir(outputs_dir)

    # CSV summary (append)
    csv_path = os.path.join(outputs_dir, "feedback_summary.csv")
    csv_exists = os.path.exists(csv_path)
    with open(csv_path, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if not csv_exists:
            writer.writerow(
                [
                    "timestamp",
                    "student_id",
                    "assignment_type",
                    "raw_score",
                    "final_score",
                    "passed_tests",
                    "total_tests",
                    "details_path",
                ]
            )

        details_fname = f"feedback_{student_id}_{assignment_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        details_path = os.path.join(outputs_dir, details_fname)

        writer.writerow(
            [
                datetime.now().isoformat(),
                student_id,
                assignment_type,
                final_grade_data.get("raw_score", ""),
                final_grade_data.get("final_score", ""),
                test_results.get("passed_tests", 0),
                test_results.get("total_tests", 0),
                details_path,
            ]
        )

    # Detailed markdown document
    with open(details_path, "w", encoding="utf-8") as f:
        f.write(f"# Feedback for {student_id} - {assignment_type}\n\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")

        f.write("## Final Grades\n")
        for k, v in final_grade_data.items():
            f.write(f"- **{k}**: {v}\n")
        f.write("\n")

        f.write("## LLM Structured Output\n")
        try:
            f.write(json.dumps(llm_structured, indent=2, ensure_ascii=False))
        except Exception:
            f.write(str(llm_structured))
        f.write("\n\n")

        f.write("## Test Results\n")
        try:
            f.write(json.dumps(test_results, indent=2, ensure_ascii=False))
        except Exception:
            f.write(str(test_results))
        f.write("\n\n")

        f.write("## Static Analysis\n")
        f.write(analysis_report if analysis_report else "No analysis available")
        f.write("\n\n")

        f.write("## Source Code (truncated)\n")
        f.write(source_code[:20000] if source_code else "")

    return csv_path, details_path


def calculate_scores(llm_grades, test_results, assignment_type):
    """Calculates raw and final scores based on assignment type and all inputs."""

    practice_config = config.PRACTICE_CONFIGS.get(assignment_type, {})
    penalties = practice_config.get("penalties", {})

    if assignment_type == "A1":
        # A1: Logic (5) + Design (35) + Clean Coding (25) + Correctness (30) = 95 total
        raw_score = 0

        # Logic criteria (5 points)
        raw_score += llm_grades.get("logic_iterators", 0) * 1
        raw_score += llm_grades.get("logic_containers", 0) * 1

        # Design criteria (35 points)
        raw_score += llm_grades.get("design_io_separation", 0) * 2
        raw_score += llm_grades.get("design_structs", 0) * 1
        raw_score += llm_grades.get("design_no_god_main", 0) * 2
        raw_score += llm_grades.get("design_small_functions", 0) * 3

        # Clean coding criteria (25 points)
        raw_score += llm_grades.get("clean_no_comments", 0) * 1
        raw_score += llm_grades.get("clean_no_duplication", 0) * 1
        raw_score += llm_grades.get("clean_indentation", 0) * 1
        raw_score += llm_grades.get("clean_magic_values", 0) * 1
        raw_score += llm_grades.get("clean_naming", 0) * 1
        raw_score += llm_grades.get("clean_consistency", 0) * 1

        # Correctness (30 points)
        total_tests = test_results.get("total_tests", 0)
        passed_tests = test_results.get("passed_tests", 0)
        correctness_score = (passed_tests / total_tests) * 30 if total_tests > 0 else 0
        raw_score += correctness_score

    elif assignment_type == "A2":
        # A2: Data (15) + Design (28) + Clean Coding (28) + Git (7) + Correctness (30) = 108 total
        raw_score = 0

        # Data criteria (15 points)
        raw_score += llm_grades.get("data_reading_input", 0) * 5
        raw_score += llm_grades.get("data_storing_information", 0) * 10

        # Design criteria (28 points)
        raw_score += llm_grades.get("design_separate_io", 0) * 8
        raw_score += llm_grades.get("design_no_godly_main", 0) * 10
        raw_score += llm_grades.get("design_small_functions", 0) * 10

        # Clean coding criteria (28 points)
        raw_score += llm_grades.get("clean_no_duplication", 0) * 7
        raw_score += llm_grades.get("clean_magic_values", 0) * 7
        raw_score += llm_grades.get("clean_naming", 0) * 7
        raw_score += llm_grades.get("clean_consistency", 0) * 7

        # Git criteria (7 points)
        raw_score += llm_grades.get("git_commit_messages", 0) * 4
        raw_score += llm_grades.get("git_standard_commits", 0) * 3

        # Correctness (30 points)
        total_tests = test_results.get("total_tests", 0)
        passed_tests = test_results.get("passed_tests", 0)
        correctness_score = (passed_tests / total_tests) * 30 if total_tests > 0 else 0
        raw_score += correctness_score

    elif assignment_type == "A3":
        # A3: Q1-Q4 (71) + Design (20) + Git (6) + Correctness (49) = 146 total
        raw_score = 0

        # Q1-Q4 criteria (71 points)
        for i in range(1, 5):
            raw_score += llm_grades.get(f"q{i}_recursive_logic", 0) * 2
            raw_score += llm_grades.get(f"q{i}_test_cases", 0) * 15
            raw_score += llm_grades.get(f"q{i}_upload_testcases", 0) * 2

        # Design criteria (20 points)
        raw_score += llm_grades.get("design_io_separation", 0) * 1
        raw_score += llm_grades.get("design_data_structures", 0) * 3
        raw_score += llm_grades.get("design_no_god_main", 0) * 1
        raw_score += llm_grades.get("design_small_functions", 0) * 2
        raw_score += llm_grades.get("design_no_duplication", 0) * 1
        raw_score += llm_grades.get("design_indentation", 0) * 1
        raw_score += llm_grades.get("design_magic_values", 0) * 1
        raw_score += llm_grades.get("design_naming", 0) * 1
        raw_score += llm_grades.get("design_consistency", 0) * 1

        # Git criteria (6 points)
        raw_score += llm_grades.get("git_commit_messages", 0) * 1
        raw_score += llm_grades.get("git_standard_commits", 0) * 1

        # Correctness (49 points)
        total_tests = test_results.get("total_tests", 0)
        passed_tests = test_results.get("passed_tests", 0)
        correctness_score = (passed_tests / total_tests) * 49 if total_tests > 0 else 0
        raw_score += correctness_score

    elif assignment_type == "A4":
        # A4: OOP (53) + Clean Coding (10) + Multifile (10) + Git (5) + Correctness (22) = 100 total
        raw_score = 0

        # OOP criteria (53 points)
        raw_score += llm_grades.get("oop_break_classes", 0) * 5
        raw_score += llm_grades.get("oop_responsibility", 0) * 5
        raw_score += llm_grades.get("oop_field_assignment", 0) * 5
        raw_score += llm_grades.get("oop_access_modifiers", 0) * 3
        raw_score += llm_grades.get("oop_no_logic_main", 0) * 3
        raw_score += llm_grades.get("oop_small_functions", 0) * 2

        # Clean coding criteria (10 points)
        raw_score += llm_grades.get("clean_no_duplication", 0) * 1
        raw_score += llm_grades.get("clean_indentation", 0) * 1
        raw_score += llm_grades.get("clean_magic_values", 0) * 1
        raw_score += llm_grades.get("clean_naming", 0) * 1
        raw_score += llm_grades.get("clean_consistency", 0) * 1

        # Multifile criteria (10 points)
        raw_score += llm_grades.get("multifile_break_files", 0) * 1
        raw_score += llm_grades.get("multifile_header_guards", 0) * 1
        raw_score += llm_grades.get("multifile_makefile", 0) * 1

        # Git criteria (5 points)
        raw_score += llm_grades.get("git_commit_messages", 0) * 1
        raw_score += llm_grades.get("git_standard_commits", 0) * 1

        # Correctness (22 points)
        total_tests = test_results.get("total_tests", 0)
        passed_tests = test_results.get("passed_tests", 0)
        correctness_score = (passed_tests / total_tests) * 22 if total_tests > 0 else 0
        raw_score += correctness_score

    elif assignment_type == "A5":
        # A5: Design (56) + OOP (14) + Clean Coding (10) + Git (10) + Correctness (22) = 112 total
        raw_score = 0

        # Design criteria (56 points)
        design_features = [
            "design_attack_wave",
            "design_normal_tower",
            "design_ice_tower",
            "design_bomb_tower",
            "design_tower_visibility",
            "design_normal_balloon",
            "design_pregnant_balloon",
            "design_panel",
            "design_launch_control",
            "design_health_panel",
            "design_music",
            "design_game_end",
        ]
        for feature in design_features:
            raw_score += llm_grades.get(feature, 0)

        # OOP criteria (14 points)
        raw_score += llm_grades.get("oop_break_classes", 0) * 5
        raw_score += llm_grades.get("oop_encapsulation", 0) * 5
        raw_score += llm_grades.get("oop_small_functions", 0) * 2
        raw_score += llm_grades.get("oop_no_duplication", 0) * 1
        raw_score += llm_grades.get("oop_indentation", 0) * 1

        # Clean coding criteria (10 points)
        raw_score += llm_grades.get("clean_magic_values", 0) * 1
        raw_score += llm_grades.get("clean_naming", 0) * 1
        raw_score += llm_grades.get("clean_consistency", 0) * 1

        # Git criteria (10 points)
        raw_score += llm_grades.get("git_break_files", 0) * 1
        raw_score += llm_grades.get("git_header_guards", 0) * 1
        raw_score += llm_grades.get("git_makefile", 0) * 1
        raw_score += llm_grades.get("git_commit_messages", 0) * 1
        raw_score += llm_grades.get("git_standard_commits", 0) * 1

        # Correctness (22 points)
        total_tests = test_results.get("total_tests", 0)
        passed_tests = test_results.get("passed_tests", 0)
        correctness_score = (passed_tests / total_tests) * 22 if total_tests > 0 else 0
        raw_score += correctness_score

    elif assignment_type == "A6":
        # A6 is multi-phase, handle differently
        return calculate_a6_scores(llm_grades, test_results)

    else:
        # Generic fallback
        raw_score = 0
        for key, value in llm_grades.items():
            if isinstance(value, (int, float)):
                raw_score += value

        total_tests = test_results.get("total_tests", 0)
        passed_tests = test_results.get("passed_tests", 0)
        correctness_score = (passed_tests / total_tests) * 30 if total_tests > 0 else 0
        raw_score += correctness_score

    # Apply penalties
    final_score = raw_score
    if penalties.get("using_goto") and llm_grades.get("using_goto"):
        final_score -= penalties["using_goto"]
    if penalties.get("late_delivery"):
        final_score -= penalties["late_delivery"] * llm_grades.get("late_delivery", 0)
    if penalties.get("clean_code"):
        final_score -= penalties["clean_code"]

    # Store individual scores for sheet update
    final_grades = llm_grades.copy()
    final_grades["correctness_test_cases"] = (
        round(correctness_score, 2) if "correctness_score" in locals() else 0
    )
    final_grades["raw_score"] = round(raw_score, 2)
    final_grades["final_score"] = round(max(0, final_score), 2)

    return final_grades


def calculate_a6_scores(llm_grades, test_results):
    """Calculate scores for A6 multi-phase assignment."""
    phase_grades = {}

    # Get phase-specific test results from judge output
    phase_results = test_results.get("phase_results", {})

    # Phase 1 (91 points total)
    p1_score = 0
    p1_features = [
        "p1_login_signup",
        "p1_normal_event",
        "p1_periodic_event",
        "p1_task",
        "p1_object_oriented",
        "p1_no_god_class",
        "p1_polymorphism",
        "p1_no_downcast",
        "p1_encapsulation",
        "p1_separate_io",
        "p1_exception_handling",
        "p1_no_duplication",
        "p1_indentation",
        "p1_magic_values",
        "p1_naming",
        "p1_consistency",
        "p1_break_files",
        "p1_makefile",
        "p1_test_cases",
    ]
    for feature in p1_features:
        p1_score += llm_grades.get(feature, 0)

    # Add test correctness score for Phase 1
    p1_test_result = phase_results.get("phase1", {})
    if p1_test_result:
        p1_correctness = (
            p1_test_result.get("passed", 0) / max(p1_test_result.get("total", 1), 1)
        ) * 20
        p1_score += p1_correctness

    phase_grades["phase1"] = {
        "p1_raw_score": round(p1_score, 2),
        "p1_final_score": round(p1_score, 2),  # Add penalty logic if needed
    }

    # Phase 2 (100 points total)
    p2_score = 0
    p2_features = [
        "p2_add_joint_event",
        "p2_see_joint_requests",
        "p2_reject_confirm",
        "p2_change_report_cmd",
        "p2_polymorphism",
        "p2_no_downcast",
        "p2_no_duplication",
        "p2_indentation",
        "p2_naming",
        "p2_consistency",
        "p2_test_cases",
    ]
    for feature in p2_features:
        p2_score += llm_grades.get(feature, 0)

    # Add test correctness score for Phase 2
    p2_test_result = phase_results.get("phase2", {})
    if p2_test_result:
        p2_correctness = (
            p2_test_result.get("passed", 0) / max(p2_test_result.get("total", 1), 1)
        ) * 30
        p2_score += p2_correctness

    phase_grades["phase2"] = {
        "p2_raw_score": round(p2_score, 2),
        "p2_final_score": round(p2_score, 2),  # Add penalty logic if needed
    }

    # Phase 3 (110 points total)
    p3_score = 0
    p3_features = [
        "p3_signup_page",
        "p3_login_page",
        "p3_home_page",
        "p3_logout",
        "p3_add_task",
        "p3_delete_task",
        "p3_edit_task",
        "p3_add_events",
        "p3_get_join_events",
        "p3_confirm_reject",
        "p3_report",
        "p3_html_render",
        "p3_handlers",
        "p3_css",
        "p3_js",
        "p3_makefile",
        "p3_clean_coding",
        "p3_bonus",
        "p3_multifile",
    ]
    for feature in p3_features:
        p3_score += llm_grades.get(feature, 0)

    # Add test correctness score for Phase 3
    p3_test_result = phase_results.get("phase3", {})
    if p3_test_result:
        p3_correctness = (
            p3_test_result.get("passed", 0) / max(p3_test_result.get("total", 1), 1)
        ) * 25
        p3_score += p3_correctness

    total_score = p1_score + p2_score + p3_score
    phase_grades["phase3"] = {
        "p3_raw_score": round(p3_score, 2),
        "p3_final_score": round(p3_score, 2),  # Add penalty logic if needed
        "final_score": round(total_score, 2),
    }

    return phase_grades


def _grade_student_flow(student_id, repo_url, assignment_type):
    """Run full grading pipeline for a single student and return summary paths."""
    print_header(f"🎯 GRADING STUDENT: {student_id} - {assignment_type}")

    project_path = tools.clone_student_repo(repo_url, student_id=student_id)
    if not project_path:
        print(f"{Colors.RED}❌ Failed to clone repository for {student_id}{Colors.END}")
        return None

    print_section("📋 RUNNING TESTS", "", Colors.GREEN)
    test_results = tools.build_and_run_tests(project_path, assignment_type)
    print(f"✅ Tests completed: {test_results['execution_summary']}")

    print_section("🔬 STATIC ANALYSIS", "", Colors.GREEN)
    analysis_report = tools.run_static_analysis(project_path)
    print("✅ Static analysis completed")

    print_section("📖 READING SOURCE CODE", "", Colors.GREEN)
    source_code = tools.read_project_files(project_path)
    print(f"✅ Source code read: {len(source_code):,} characters")

    print_section("🧠 CODE QUALITY ANALYSIS", "", Colors.GREEN)
    code_analysis = tools.analyze_code_quality(source_code)
    print("✅ Code analysis completed")

    # Test failure analysis and debugging help
    print_section("🔍 ANALYZING TEST FAILURES", "", Colors.GREEN)
    failures, debug_recommendations = analyze_test_failures(test_results)
    print(f"✅ Test failure analysis completed")

    # Display test failure analysis
    print_test_failure_analysis(failures, debug_recommendations)

    # Show debugging workflow if there are failures
    if failures:
        print_debugging_workflow()

    # Calculate test failure impact
    failure_multiplier, failure_description = get_test_failure_impact(failures)
    print(f"\n{Colors.BOLD}📊 TEST FAILURE IMPACT:{Colors.END}")
    print(
        f"  {Colors.BLUE}Multiplier: {failure_multiplier:.1f}x ({failure_description}){Colors.END}"
    )

    assignment_config = config.PRACTICE_CONFIGS[assignment_type]
    assignment_desc = assignment_config.get("name", f"Assignment {assignment_type}")

    enhanced_desc = f"""
ASSIGNMENT DESCRIPTION:
{assignment_desc}

CODE ANALYSIS SUMMARY:
- Uses Iterators: {code_analysis['uses_iterators']}
- Uses Containers: {code_analysis['uses_containers']}
- Uses Structs: {code_analysis['uses_structs']}
- Main Function Size: {code_analysis['main_function_lines']} lines
- Total Functions: {code_analysis['function_count']}
- Average Function Size: {code_analysis['average_function_size']:.1f} lines
- Global Variables: {code_analysis['global_variables']}
- Magic Numbers Detected: {code_analysis['magic_numbers']}
- Comment Lines: {code_analysis['comment_lines']}
"""

    print_section("🤖 GENERATING GRADING PROMPT", "", Colors.GREEN)
    grading_prompt = get_grading_prompt(
        assignment_type=assignment_type,
        practice_description=enhanced_desc,
        test_results=test_results["execution_summary"],
        static_analysis=analysis_report,
        source_code=source_code,
    )

    format_instructions = get_format_instructions("A6", A6GradingOutput)

    print("✅ Enhanced grading prompt generated")
    print(f"📏 Prompt length: {len(grading_prompt):,} characters")

    print_section("🎯 RUNNING AI GRADING", "", Colors.GREEN)
    try:
        llm_response = langchain_integration.grade_student_project(
            test_results=test_results["execution_summary"],
            static_analysis=analysis_report,
            source_code=source_code,
            practice_description=enhanced_desc,
            assignment_type=assignment_type,
            student_id=student_id,
        )

        print("✅ Grading completed successfully!")

        # Display results
        grading_data = llm_response.model_dump()

        print_header("📊 GRADING RESULTS")

        # Phase 1 Scores
        print_section("🏗️ PHASE 1 - CORE FEATURES (91 points)", "", Colors.BOLD)
        phase1_total = 0
        phase1_scores = [
            ("Login/SignUp", grading_data.get("p1_login_signup", 0), 2),
            ("Normal Event", grading_data.get("p1_normal_event", 0), 2),
            ("Periodic Event", grading_data.get("p1_periodic_event", 0), 2),
            ("Task Management", grading_data.get("p1_task", 0), 2),
            ("OOP Design", grading_data.get("p1_object_oriented", 0), 2),
            ("No God Class", grading_data.get("p1_no_god_class", 0), 1),
            ("Polymorphism", grading_data.get("p1_polymorphism", 0), 2),
            ("No Downcast", grading_data.get("p1_no_downcast", 0), 1),
            ("Encapsulation", grading_data.get("p1_encapsulation", 0), 2),
            ("I/O Separation", grading_data.get("p1_separate_io", 0), 1),
            ("Exception Handling", grading_data.get("p1_exception_handling", 0), 2),
            ("No Duplication", grading_data.get("p1_no_duplication", 0), 2),
            ("Indentation", grading_data.get("p1_indentation", 0), 1),
            ("Magic Values", grading_data.get("p1_magic_values", 0), 1),
            ("Naming", grading_data.get("p1_naming", 0), 3),
            ("Consistency", grading_data.get("p1_consistency", 0), 3),
            ("File Organization", grading_data.get("p1_break_files", 0), 1),
            ("Makefile", grading_data.get("p1_makefile", 0), 1),
            ("Test Cases", grading_data.get("p1_test_cases", 0), 30),
        ]

        for label, score, max_score in phase1_scores:
            print_score(score, max_score, label)
            phase1_total += score

        print(
            f"\n  {Colors.BOLD}Phase 1 Total: {Colors.GREEN}{phase1_total:.1f}/{91.0}{Colors.END} ({(phase1_total/91)*100:.1f}%)"
        )

        # Phase 2 Scores
        print_section("⚡ PHASE 2 - ADVANCED FEATURES (15 points)", "", Colors.BOLD)
        phase2_total = 0
        phase2_scores = [
            ("Joint Events", grading_data.get("p2_add_joint_event", 0), 3),
            ("Joint Requests", grading_data.get("p2_see_joint_requests", 0), 3),
            ("Accept/Reject", grading_data.get("p2_reject_confirm", 0), 3),
            ("Report Command", grading_data.get("p2_change_report_cmd", 0), 3),
            ("Polymorphism", grading_data.get("p2_polymorphism", 0), 2),
            ("No Downcast", grading_data.get("p2_no_downcast", 0), 1),
        ]

        for label, score, max_score in phase2_scores:
            print_score(score, max_score, label)
            phase2_total += score

        print(
            f"\n  {Colors.BOLD}Phase 2 Total: {Colors.YELLOW}{phase2_total:.1f}/15.0{Colors.END} ({(phase2_total/15)*100:.1f}%)"
        )

        # Phase 3 Scores
        print_section("🌐 PHASE 3 - WEB INTERFACE (70 points)", "", Colors.BOLD)
        phase3_total = 0
        phase3_scores = [
            ("Signup/Login Pages", grading_data.get("p3_signup_page", 0), 10),
            ("Home/Dashboard", grading_data.get("p3_home_page", 0), 10),
            ("Task Management UI", grading_data.get("p3_add_task", 0), 15),
            ("Event Management UI", grading_data.get("p3_add_events", 0), 15),
            ("Joint Events UI", grading_data.get("p3_get_join_events", 0), 10),
            ("Report Generation", grading_data.get("p3_report", 0), 5),
            ("Clean Coding", grading_data.get("p3_clean_coding", 0), 5),
        ]

        for label, score, max_score in phase3_scores:
            print_score(score, max_score, label)
            phase3_total += score

        print(
            f"\n  {Colors.BOLD}Phase 3 Total: {Colors.BLUE}{phase3_total:.1f}/70.0{Colors.END} ({(phase3_total/70)*100:.1f}%)"
        )

        # Overall Total
        total_score = phase1_total + phase2_total + phase3_total
        max_total = 91 + 15 + 70

        print_header("🏆 FINAL GRADE SUMMARY")
        print(
            f"  {Colors.BOLD}Overall Score: {Colors.GREEN}{total_score:.1f}/{max_total:.1f}{Colors.END}"
        )
        print(
            f"  {Colors.BOLD}Percentage: {Colors.GREEN}{Colors.BOLD}{(total_score/max_total)*100:.1f}%{Colors.END}"
        )

        # Letter grade
        percentage = (total_score / max_total) * 100
        if percentage >= 90:
            grade = "A"
            color = Colors.GREEN
        elif percentage >= 80:
            grade = "B"
            color = Colors.YELLOW
        elif percentage >= 70:
            grade = "C"
            color = Colors.BLUE
        elif percentage >= 60:
            grade = "D"
            color = Colors.YELLOW
        else:
            grade = "F"
            color = Colors.RED

        print(f"  {Colors.BOLD}Letter Grade: {color}{Colors.BOLD}{grade}{Colors.END}")

        # Print recommendations
        comment = grading_data.get("generated_comment", "")
        if comment:
            print_recommendations(comment)

        print_header("✅ GRADING COMPLETE")
        print(
            f"{Colors.GREEN}Enhanced grading system successfully completed for {student_id}!{Colors.END}"
        )
        print(
            f"{Colors.BLUE}All assignments (A1-A6) now have comprehensive recommendations.{Colors.END}"
        )

        if assignment_type == "A6":
            final_grade_data = calculate_a6_scores(
                llm_response.model_dump(), test_results
            )
            sheets_updater.update_multi_phase_grades(
                student_id, final_grade_data, assignment_type
            )
        else:
            final_grade_data = calculate_scores(
                llm_response.model_dump(), test_results, assignment_type
            )
            sheets_updater.update_student_grade(
                student_id, final_grade_data, assignment_type
            )

        # Save full feedback
        csv_path, details_path = save_full_feedback(
            student_id,
            assignment_type,
            final_grade_data,
            llm_response.model_dump(),
            test_results,
            analysis_report,
            source_code,
        )

        print(
            f"✅ Student {student_id} processed successfully! Saved feedback to: {details_path}"
        )
        return {"csv": csv_path, "details": details_path}

    except Exception as e:
        print(f"{Colors.RED}❌ Grading failed: {e}{Colors.END}")
        return None


def run_cli():
    parser = argparse.ArgumentParser(description="AP Grader Agent - CLI")
    sub = parser.add_subparsers(dest="mode", required=True)

    # Generate-only mode
    g = sub.add_parser(
        "generate", help="Generate test cases from assignment description"
    )
    g.add_argument("assignment", help="Assignment key (e.g., A1)")
    g.add_argument(
        "--num", type=int, default=3, help="Number of test cases to generate"
    )
    g.add_argument("--llm", action="store_true", help="Use LLM for generation")

    # Grade mode
    r = sub.add_parser("grade", help="Run grading for students (single or batch)")
    r.add_argument("--student", help="Student ID (single) or 'all' for sheet batch")
    r.add_argument("--repo", help="Repository URL for single student")
    r.add_argument("--assignment", help="Assignment type for single student (A1..A6)")

    args = parser.parse_args()

    if args.mode == "generate":
        # Generate testcases
        tests_dir = tools.generate_testcases_from_description(
            args.assignment, args.num, args.llm
        )
        print(f"Generated test cases at: {tests_dir}")

    elif args.mode == "grade":
        if args.student == "all":
            # Batch from sheet
            sheet = sheets_updater.get_sheet()
            student_ids = sheet.col_values(1)[1:]
            github_urls = sheet.col_values(4)[1:]
            assignment_types = sheet.col_values(5)[1:]

            for student_id, repo_url, assignment_type in zip(
                student_ids, github_urls, assignment_types
            ):
                if not repo_url or not assignment_type:
                    print(f"Skipping {student_id}: missing data")
                    continue
                _grade_student_flow(student_id, repo_url, assignment_type)
        else:
            # Single student
            if not args.student or not args.repo or not args.assignment:
                print(
                    "For single student grading provide --student, --repo and --assignment"
                )
                return
            _grade_student_flow(args.student, args.repo, args.assignment)


if __name__ == "__main__":
    run_cli()
