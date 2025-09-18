# main_agent.py
import tools
import sheets_updater
import langchain_integration
import config


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


def main():
    """Main function to run the grading agent."""
    # 1. Load practice descriptions
    practice_descriptions = tools.get_practice_descriptions(config.PRACTICES_DIR)
    if not practice_descriptions:
        print(
            "Warning: No practice descriptions found. Please add PDF files to the practice_descriptions directory."
        )

    # 2. Get the grading function
    grading_function = langchain_integration.get_grading_chain()

    # 3. Get the list of students from the sheet
    sheet = sheets_updater.get_sheet()
    # Assuming column 1 is Student Number, column 4 is GitHub URL, column 5 is Assignment Type
    student_ids = sheet.col_values(1)[1:]  # Skip header
    github_urls = sheet.col_values(4)[1:]  # GitHub URL
    assignment_types = sheet.col_values(5)[1:]  # Assignment Type (A1, A3, A4, A5, A6)

    # 4. Process each student
    for student_id, repo_url, assignment_type in zip(
        student_ids, github_urls, assignment_types
    ):
        if not repo_url or not assignment_type:
            print(
                f"Skipping student {student_id}: Missing repository URL or assignment type."
            )
            continue

        if assignment_type not in config.PRACTICE_CONFIGS:
            print(
                f"Skipping student {student_id}: Assignment type '{assignment_type}' not configured."
            )
            continue

        print(
            f"\n--- Processing Student: {student_id} (Assignment: {assignment_type}) ---"
        )

        try:
            # Step A: Clone the repo
            project_path = tools.clone_student_repo(repo_url, student_id)
            if not project_path:
                continue

            # Step B: Run build and tests
            test_results = tools.build_and_run_tests(project_path, assignment_type)

            # Step C: Run static analysis
            analysis_report = tools.run_static_analysis(project_path)

            # Step D: Read all source code
            source_code = tools.read_project_files(project_path)

            # Step E: Perform basic code quality analysis
            code_analysis = tools.analyze_code_quality(source_code)

            # Step F: Get assignment description and extract requirements
            assignment_config = config.PRACTICE_CONFIGS[assignment_type]
            assignment_desc = assignment_config.get(
                "name", f"Assignment {assignment_type}"
            )

            # Step G: Enhance assignment description with extracted requirements
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

            # Step H: Invoke the LLM for qualitative grading
            print("Invoking AI for qualitative grading...")
            llm_response = grading_function(
                test_results=test_results["execution_summary"],
                static_analysis=analysis_report,
                source_code=source_code,
                practice_description=enhanced_desc,
                assignment_type=assignment_type,
            )

            # Step I: Calculate final scores
            if assignment_type == "A6":
                final_grade_data = calculate_a6_scores(
                    llm_response.model_dump(), test_results
                )
                # Update multi-phase grades
                sheets_updater.update_multi_phase_grades(
                    student_id, final_grade_data, assignment_type
                )
            else:
                final_grade_data = calculate_scores(
                    llm_response.model_dump(), test_results, assignment_type
                )
                # Update single-phase grades
                sheets_updater.update_student_grade(
                    student_id, final_grade_data, assignment_type
                )

            # Print summary for this student
            print(f"✅ Student {student_id} processed successfully!")
            if assignment_type == "A6":
                print(
                    f"   Phase 1 Score: {final_grade_data.get('phase1', {}).get('p1_final_score', 0)}"
                )
                print(
                    f"   Phase 2 Score: {final_grade_data.get('phase2', {}).get('p2_final_score', 0)}"
                )
                print(
                    f"   Phase 3 Score: {final_grade_data.get('phase3', {}).get('p3_final_score', 0)}"
                )
                print(
                    f"   Total Score: {final_grade_data.get('phase3', {}).get('final_score', 0)}"
                )
            else:
                print(f"   Raw Score: {final_grade_data.get('raw_score', 0)}")
                print(f"   Final Score: {final_grade_data.get('final_score', 0)}")
            print(
                f"   Tests Passed: {test_results.get('passed_tests', 0)}/{test_results.get('total_tests', 0)}"
            )

        except Exception as e:
            print(f"❌ Critical error processing {student_id}: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    main()
