#!/usr/bin/env python3
"""
Test script to run enhanced A6 grading on local project
"""

import sys
import os

sys.path.append("/Users/tahamajs/Documents/uni/LLM/grading_agent")

import tools
import langchain_integration
import config
from prompts import get_grading_prompt, get_format_instructions
from langchain_integration import A6GradingOutput


def test_enhanced_grading():
    """Test the enhanced A6 grading system on the local project."""

    project_path = "/Users/tahamajs/Documents/uni/LLM/grading_agent/test_project"

    print("🔍 Testing Enhanced A6 Grading System")
    print("=" * 50)

    # Step 1: Build and run tests
    print("📋 Running tests...")
    test_results = tools.build_and_run_tests(project_path, "A6")
    print(f"✅ Tests completed: {test_results['execution_summary']}")

    # Step 2: Run static analysis
    print("🔬 Running static analysis...")
    analysis_report = tools.run_static_analysis(project_path)
    print("✅ Static analysis completed")

    # Step 3: Read source code
    print("📖 Reading source code...")
    source_code = tools.read_project_files(project_path)
    print(f"✅ Source code read: {len(source_code)} characters")

    # Step 4: Analyze code quality
    print("🧠 Analyzing code quality...")
    code_analysis = tools.analyze_code_quality(source_code)
    print("✅ Code analysis completed")

    # Step 5: Prepare assignment description
    assignment_config = config.PRACTICE_CONFIGS["A6"]
    assignment_desc = assignment_config.get("name", "Assignment A6")

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

    # Step 6: Generate grading prompt
    print("🤖 Generating grading prompt...")
    grading_prompt = get_grading_prompt(
        assignment_type="A6",
        practice_description=enhanced_desc,
        test_results=test_results["execution_summary"],
        static_analysis=analysis_report,
        source_code=source_code,
    )

    format_instructions = get_format_instructions("A6", A6GradingOutput)

    print("✅ Enhanced grading prompt generated")
    print(f"📏 Prompt length: {len(grading_prompt)} characters")

    # Step 7: Run grading
    print("🎯 Running AI grading...")
    try:
        llm_response = langchain_integration.grade_student_project(
            test_results=test_results["execution_summary"],
            static_analysis=analysis_report,
            source_code=source_code,
            practice_description=enhanced_desc,
            assignment_type="A6",
            student_id="test_student",
        )

        print("✅ Grading completed successfully!")
        print("\n" + "=" * 50)
        print("📊 GRADING RESULTS:")
        print("=" * 50)

        # Display results
        grading_data = llm_response.model_dump()
        for key, value in grading_data.items():
            if key != "generated_comment":
                print(f"{key}: {value}")
            else:
                print(f"\n{key}:")
                print(value)

        return grading_data

    except Exception as e:
        print(f"❌ Grading failed: {e}")
        return None


if __name__ == "__main__":
    test_enhanced_grading()
