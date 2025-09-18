# main_agent.py
import tools
import sheets_updater
import langchain_integration
import config


def calculate_scores(llm_grades, test_results):
    """Calculates raw and final scores based on all inputs."""
    # This function implements the scoring logic from your sheet's headers
    raw_score = 0

    # Sum up all the component scores from the LLM
    for key, value in llm_grades.items():
        if isinstance(value, (int, float)):
            raw_score += value

    # Add correctness score
    total_tests = test_results.get("total_tests", 0)
    passed_tests = test_results.get("passed_tests", 0)
    correctness_score = (passed_tests / total_tests) * 30 if total_tests > 0 else 0
    raw_score += correctness_score

    # Store individual scores for sheet update
    final_grades = llm_grades.copy()
    final_grades["correctness_score"] = round(correctness_score, 2)
    final_grades["raw_score"] = round(raw_score, 2)

    # Placeholder for penalty logic
    # You would add logic here to check for goto, latency, etc.
    final_score = raw_score  # Assuming no penalties for now
    final_grades["final_score"] = round(final_score, 2)

    return final_grades


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
    # Assuming column 1 is Student Number, column 4 is GitHub URL, column 5 is Practice Name
    student_ids = sheet.col_values(1)[1:]  # Skip header
    github_urls = sheet.col_values(4)[
        1:
    ]  # Assuming GitHub URL is in column D (4th column)
    practice_names = sheet.col_values(5)[
        1:
    ]  # Assuming Practice Name is in column E (5th column)

    # 4. Process each student
    for student_id, repo_url, practice_name in zip(
        student_ids, github_urls, practice_names
    ):
        if not repo_url:
            print(f"Skipping student {student_id}: No repository URL.")
            continue

        if practice_name not in practice_descriptions:
            print(
                f"Skipping student {student_id}: Practice '{practice_name}' description not found."
            )
            continue

        print(f"\n--- Processing Student: {student_id} (Practice: {practice_name}) ---")

        try:
            # Step A: Clone the repo
            project_path = tools.clone_student_repo(repo_url, student_id)
            if not project_path:
                continue

            # Step B: Run build and tests
            test_results = tools.build_and_run_tests(project_path, practice_name)

            # Step C: Run static analysis
            analysis_report = tools.run_static_analysis(project_path)

            # Step D: Read all source code
            source_code = tools.read_project_files(project_path)

            # Step E: Perform basic code quality analysis
            code_analysis = tools.analyze_code_quality(source_code)

            # Step F: Get practice description and extract requirements
            practice_desc = practice_descriptions[practice_name]
            practice_requirements = tools.extract_practice_requirements(practice_desc)

            # Step G: Enhance practice description with extracted requirements
            enhanced_practice_desc = f"""
PRACTICE DESCRIPTION:
{practice_desc}

EXTRACTED REQUIREMENTS:
Objectives: {', '.join(practice_requirements['objectives'][:3])}
Constraints: {', '.join(practice_requirements['constraints'][:3])}
Required Features: {', '.join(practice_requirements['required_features'][:5])}
Grading Criteria: {', '.join(practice_requirements['grading_criteria'][:3])}

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
                practice_description=enhanced_practice_desc,
            )

            # Step G: Calculate final scores
            final_grade_data = calculate_scores(llm_response.model_dump(), test_results)

            # Step H: Update the Google Sheet
            sheets_updater.update_student_grade(student_id, final_grade_data)

        except Exception as e:
            print(f"A critical error occurred while processing {student_id}: {e}")


if __name__ == "__main__":
    main()
