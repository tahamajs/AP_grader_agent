# tools.py
import os
import subprocess
import xml.etree.ElementTree as ET
from git import Repo, GitCommandError
import config
import fitz  # PyMuPDF for PDF reading
import time


def clone_student_repo(repo_url: str, student_id: str) -> str:
    """Clones or pulls the latest from a student's Git repository."""
    local_path = os.path.join(config.PROJECTS_DIR, str(student_id))
    try:
        if os.path.exists(local_path):
            repo = Repo(local_path)
            repo.remotes.origin.pull()
            print(f"Pulled latest changes for {student_id}")
        else:
            Repo.clone_from(repo_url, local_path)
            print(f"Cloned repo for {student_id}")
        return local_path
    except GitCommandError as e:
        print(f"Error with Git for {student_id}: {e}")
        return None


def read_project_files(project_path: str) -> str:
    """Reads all .cpp and .h files in a directory and concatenates them with analysis."""
    full_code = ""
    code_metrics = {
        "total_files": 0,
        "total_lines": 0,
        "cpp_files": 0,
        "header_files": 0,
        "largest_file": "",
        "max_lines": 0
    }

    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith((".cpp", ".h", ".hpp")):
                file_path = os.path.join(root, file)
                code_metrics["total_files"] += 1

                if file.endswith(".cpp"):
                    code_metrics["cpp_files"] += 1
                else:
                    code_metrics["header_files"] += 1

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        lines = content.count('\n') + 1
                        code_metrics["total_lines"] += lines

                        if lines > code_metrics["max_lines"]:
                            code_metrics["max_lines"] = lines
                            code_metrics["largest_file"] = file

                        full_code += f"--- START OF FILE: {file} ({lines} lines) ---\n"
                        full_code += content
                        full_code += f"\n--- END OF FILE: {file} ---\n\n"

                except Exception as e:
                    full_code += f"--- START OF FILE: {file} ---\n"
                    full_code += f"Error reading file: {e}"
                    full_code += f"\n--- END OF FILE: {file} ---\n\n"

    # Add code metrics summary at the beginning
    metrics_summary = f"""
📈 CODE METRICS SUMMARY:
- Total Files: {code_metrics['total_files']} ({code_metrics['cpp_files']} .cpp, {code_metrics['header_files']} .h/.hpp)
- Total Lines: {code_metrics['total_lines']}
- Largest File: {code_metrics['largest_file']} ({code_metrics['max_lines']} lines)
- Average Lines per File: {code_metrics['total_lines'] / max(code_metrics['total_files'], 1):.1f}

"""

    return metrics_summary + full_code


def analyze_code_quality(source_code: str) -> dict:
    """Performs basic code quality analysis."""
    analysis = {
        "uses_iterators": False,
        "uses_containers": False,
        "uses_structs": False,
        "main_function_lines": 0,
        "function_count": 0,
        "average_function_size": 0,
        "global_variables": 0,
        "magic_numbers": 0,
        "comment_lines": 0,
        "total_lines": 0
    }

    lines = source_code.split('\n')
    analysis["total_lines"] = len(lines)

    in_main = False
    main_lines = 0
    functions = []
    current_function_lines = 0

    for line in lines:
        stripped = line.strip()

        # Count comments
        if stripped.startswith('//') or stripped.startswith('/*'):
            analysis["comment_lines"] += 1
            continue

        # Check for iterators
        if 'iterator' in stripped.lower() or '->begin()' in stripped or '->end()' in stripped:
            analysis["uses_iterators"] = True

        # Check for containers
        if any(container in stripped for container in ['std::vector', 'std::map', 'std::set']):
            analysis["uses_containers"] = True

        # Check for structs
        if stripped.startswith('struct ') or 'struct ' in stripped:
            analysis["uses_structs"] = True

        # Check for global variables (simplified)
        if not in_main and '=' in stripped and not stripped.startswith(' ') and not stripped.startswith('\t'):
            if not any(keyword in stripped for keyword in ['int main', 'void', 'int ', 'float ', 'double ', 'char ', 'bool ']):
                analysis["global_variables"] += 1

        # Check for magic numbers (simplified)
        import re
        magic_nums = re.findall(r'\b\d+\b', stripped)
        for num in magic_nums:
            if num not in ['0', '1', '2', '10', '100']:  # Common acceptable numbers
                analysis["magic_numbers"] += 1

        # Track main function
        if 'int main(' in stripped or 'void main(' in stripped:
            in_main = True
            analysis["function_count"] += 1
        elif in_main and stripped == '}':
            in_main = False
            analysis["main_function_lines"] = main_lines
            main_lines = 0
        elif in_main:
            main_lines += 1

        # Track other functions
        if any(keyword in stripped for keyword in ['int ', 'void ', 'float ', 'double ', 'char ', 'bool ']) and '(' in stripped:
            if not in_main:
                analysis["function_count"] += 1
                if current_function_lines > 0:
                    functions.append(current_function_lines)
                current_function_lines = 1
            else:
                current_function_lines += 1
        elif current_function_lines > 0:
            current_function_lines += 1
            if stripped == '}':
                functions.append(current_function_lines)
                current_function_lines = 0

    # Calculate average function size
    if functions:
        analysis["average_function_size"] = sum(functions) / len(functions)

    return analysis


def read_practice_description(pdf_path: str) -> str:
    """Reads and extracts text content from a PDF practice description with enhanced formatting."""
    try:
        doc = fitz.open(pdf_path)
        text_content = []

        for page_num in range(len(doc)):
            page = doc[page_num]

            # Extract text with better formatting preservation
            page_text = page.get_text()

            # Clean up common PDF extraction issues
            page_text = page_text.replace('\n\n', '\n')  # Remove excessive newlines
            page_text = page_text.replace('  ', ' ')     # Remove double spaces

            # Add page separator for multi-page documents
            if page_num > 0:
                text_content.append(f"\n--- Page {page_num + 1} ---\n")

            text_content.append(page_text)

        doc.close()

        full_text = ''.join(text_content)

        # Final cleanup
        full_text = full_text.strip()

        if not full_text:
            return "Error: PDF appears to be empty or contains no extractable text."

        return full_text

    except Exception as e:
        return f"Error reading PDF: {str(e)}. Please ensure the PDF is not password-protected and contains text content."


def extract_practice_requirements(pdf_text: str) -> dict:
    """Extracts specific grading requirements from practice description text."""
    requirements = {
        "objectives": [],
        "constraints": [],
        "required_features": [],
        "grading_criteria": [],
        "bonus_features": []
    }

    # Simple keyword-based extraction (can be enhanced with NLP if needed)
    lines = pdf_text.split('\n')

    for line in lines:
        line_lower = line.lower().strip()

        # Extract objectives
        if any(keyword in line_lower for keyword in ['objective', 'goal', 'purpose', 'task']):
            if len(line.strip()) > 10:  # Avoid very short lines
                requirements["objectives"].append(line.strip())

        # Extract constraints
        elif any(keyword in line_lower for keyword in ['constraint', 'limitation', 'restriction', 'must not', 'cannot']):
            if len(line.strip()) > 10:
                requirements["constraints"].append(line.strip())

        # Extract required features
        elif any(keyword in line_lower for keyword in ['required', 'implement', 'create', 'write']):
            if len(line.strip()) > 10:
                requirements["required_features"].append(line.strip())

        # Extract grading criteria
        elif any(keyword in line_lower for keyword in ['grade', 'point', 'score', 'criteria', 'evaluation']):
            if len(line.strip()) > 10:
                requirements["grading_criteria"].append(line.strip())

        # Extract bonus features
        elif any(keyword in line_lower for keyword in ['bonus', 'extra', 'additional', 'optional']):
            if len(line.strip()) > 10:
                requirements["bonus_features"].append(line.strip())

    return requirements


def get_practice_descriptions(practices_dir: str) -> dict:
    """Reads all practice description PDFs from a directory."""
    practice_descriptions = {}
    if not os.path.exists(practices_dir):
        return practice_descriptions

    for file in os.listdir(practices_dir):
        if file.endswith(".pdf"):
            practice_name = os.path.splitext(file)[0]
            pdf_path = os.path.join(practices_dir, file)
            description = read_practice_description(pdf_path)
            practice_descriptions[practice_name] = description
            print(f"Loaded practice description: {practice_name}")

    return practice_descriptions


def run_static_analysis(project_path: str) -> str:
    """Runs cppcheck and returns a detailed summary of the results with severity categorization."""
    xml_output_file = os.path.join(project_path, "cppcheck_results.xml")

    # Enhanced cppcheck command with more options
    command = [
        "cppcheck",
        "--enable=all",
        "--inconclusive",
        "--xml-version=2",
        "--language=c++",
        "--std=c++11",  # Adjust based on your course requirements
        "--suppress=missingIncludeSystem",  # Suppress common false positives
        "--inline-suppr",  # Allow inline suppressions
        project_path,
    ]

    try:
        # Run cppcheck
        with open(xml_output_file, "w") as f:
            result = subprocess.run(command, stderr=f, text=True, timeout=60)

        # Parse the XML and create a detailed summary
        tree = ET.parse(xml_output_file)
        root = tree.getroot()
        errors = root.find("errors")

        if errors is None or len(errors) == 0:
            return "✅ Cppcheck Static Analysis: No issues found. Code appears clean."

        # Categorize errors by severity
        severity_counts = {"error": 0, "warning": 0, "style": 0, "performance": 0, "information": 0}
        error_details = []

        for error in errors:
            location = error.find("location")
            if location is not None:
                file = location.get("file", "unknown")
                line = location.get("line", "unknown")
                msg = error.get("msg", "No message")
                severity = error.get("severity", "unknown")
                error_id = error.get("id", "unknown")

                severity_counts[severity] = severity_counts.get(severity, 0) + 1

                # Format error details
                error_details.append(f"[{severity.upper()}] {file}:{line} - {msg} (ID: {error_id})")

        # Create summary report
        summary = "📊 Cppcheck Static Analysis Report:\n\n"

        # Severity breakdown
        summary += "Severity Breakdown:\n"
        for severity, count in severity_counts.items():
            if count > 0:
                summary += f"  • {severity.capitalize()}: {count}\n"

        summary += f"\nTotal Issues: {sum(severity_counts.values())}\n\n"

        # Detailed issues
        if error_details:
            summary += "Detailed Issues:\n"
            for detail in error_details[:20]:  # Limit to first 20 issues
                summary += f"  {detail}\n"

            if len(error_details) > 20:
                summary += f"  ... and {len(error_details) - 20} more issues\n"

        # Recommendations based on severity
        if severity_counts["error"] > 0:
            summary += "\n⚠️  CRITICAL: Address error-level issues immediately - these may cause runtime problems.\n"
        if severity_counts["warning"] > 0:
            summary += "\n⚠️  WARNING: Review warning-level issues - potential runtime or logic errors.\n"
        if severity_counts["performance"] > 0:
            summary += "\n💡 PERFORMANCE: Consider optimization opportunities identified.\n"
        if severity_counts["style"] > 0:
            summary += "\n📝 STYLE: Code style improvements suggested for better readability.\n"

        return summary

    except subprocess.TimeoutExpired:
        return "❌ Cppcheck Static Analysis: Analysis timed out after 60 seconds."
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        return f"❌ Cppcheck Static Analysis: Execution failed - {e}"
    except ET.ParseError:
        return "❌ Cppcheck Static Analysis: Failed to parse XML output."
    except Exception as e:
        return f"❌ Cppcheck Static Analysis: Unexpected error - {e}"


def build_and_run_tests(project_path: str, practice_name: str = None) -> dict:
    """Builds the project and runs it against test cases."""
    # Get practice-specific configuration
    practice_config = config.PRACTICE_CONFIGS.get(
        practice_name,
        {
            "build_command": config.BUILD_COMMAND,
            "executable_name": config.EXECUTABLE_NAME,
            "test_cases_dir": config.TEST_CASES_DIR,
        },
    )

    results = {
        "build_successful": False,
        "passed_tests": 0,
        "total_tests": 0,
        "failed_tests": [],
        "execution_summary": "",
        "build_output": "",
        "test_details": []
    }

    # 1. Build the code with better error capture
    try:
        build_process = subprocess.run(
            practice_config["build_command"].split(),
            cwd=project_path,
            check=True,
            capture_output=True,
            text=True,
            timeout=120  # 2-minute timeout for build
        )
        results["build_successful"] = True
        results["build_output"] = "✅ Build successful"
        results["execution_summary"] += "✅ Build successful.\n"
    except subprocess.TimeoutExpired:
        results["build_output"] = "❌ Build timed out after 2 minutes"
        results["execution_summary"] = "❌ Build failed: Timeout after 2 minutes.\n"
        return results
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        results["build_output"] = f"❌ Build failed: {e.stderr}"
        results["execution_summary"] = f"❌ Build failed: {e.stderr}\n"
        return results

    # 2. Check if executable exists
    executable_path = os.path.join(project_path, practice_config["executable_name"])
    if not os.path.exists(executable_path):
        results["execution_summary"] += f"❌ Executable '{practice_config['executable_name']}' not found after build.\n"
        return results

    # 3. Run test cases with detailed reporting
    test_cases_dir = practice_config["test_cases_dir"]
    if not os.path.exists(test_cases_dir):
        results["execution_summary"] += f"❌ Test cases directory '{test_cases_dir}' not found.\n"
        return results

    test_files = [f for f in os.listdir(test_cases_dir) if f.endswith(".in")]
    results["total_tests"] = len(test_files)

    if results["total_tests"] == 0:
        results["execution_summary"] += "⚠️  No test cases found in the directory.\n"
        return results

    results["execution_summary"] += f"🧪 Running {results['total_tests']} test cases...\n\n"

    for i, test_file in enumerate(test_files, 1):
        input_path = os.path.join(test_cases_dir, test_file)
        output_path = os.path.join(test_cases_dir, test_file.replace(".in", ".out"))

        test_result = {
            "test_name": test_file,
            "passed": False,
            "execution_time": 0,
            "error": None,
            "expected_output": "",
            "actual_output": ""
        }

        try:
            # Read expected output
            with open(output_path, "r") as f_out:
                expected_output = f_out.read().strip()

            # Run the test
            start_time = time.time()
            run_process = subprocess.run(
                [executable_path],
                stdin=open(input_path, "r"),
                capture_output=True,
                text=True,
                timeout=10  # 10-second timeout per test
            )
            execution_time = time.time() - start_time

            actual_output = run_process.stdout.strip()

            # Compare outputs
            if actual_output == expected_output:
                results["passed_tests"] += 1
                test_result["passed"] = True
                results["execution_summary"] += f"✅ Test {i}/{results['total_tests']}: {test_file} - PASSED\n"
            else:
                results["failed_tests"].append(test_file)
                test_result["passed"] = False
                results["execution_summary"] += f"❌ Test {i}/{results['total_tests']}: {test_file} - FAILED\n"
                results["execution_summary"] += f"   Expected: {expected_output[:100]}{'...' if len(expected_output) > 100 else ''}\n"
                results["execution_summary"] += f"   Got:      {actual_output[:100]}{'...' if len(actual_output) > 100 else ''}\n"

            test_result["execution_time"] = round(execution_time, 3)
            test_result["expected_output"] = expected_output
            test_result["actual_output"] = actual_output

        except subprocess.TimeoutExpired:
            results["failed_tests"].append(test_file)
            test_result["error"] = "Timeout (10s)"
            results["execution_summary"] += f"⏰ Test {i}/{results['total_tests']}: {test_file} - TIMEOUT\n"
        except FileNotFoundError:
            results["failed_tests"].append(test_file)
            test_result["error"] = "Expected output file missing"
            results["execution_summary"] += f"📁 Test {i}/{results['total_tests']}: {test_file} - MISSING OUTPUT FILE\n"
        except Exception as e:
            results["failed_tests"].append(test_file)
            test_result["error"] = str(e)
            results["execution_summary"] += f"💥 Test {i}/{results['total_tests']}: {test_file} - ERROR: {e}\n"

        results["test_details"].append(test_result)

    # Add summary statistics
    pass_rate = (results["passed_tests"] / results["total_tests"]) * 100 if results["total_tests"] > 0 else 0
    results["execution_summary"] += f"\n📊 Test Summary: {results['passed_tests']}/{results['total_tests']} passed ({pass_rate:.1f}%)\n"

    if results["failed_tests"]:
        results["execution_summary"] += f"❌ Failed tests: {', '.join(results['failed_tests'])}\n"

    return results
