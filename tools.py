# tools.py
import os
import subprocess
import xml.etree.ElementTree as ET
from git import Repo, GitCommandError
import config
import fitz  # PyMuPDF for PDF reading
import time


def clone_student_repo(
    repo_url: str, commit_sha: str = None, student_id: str = None
) -> str:
    """Clones a student's repository using SSH with AP-F03 configuration."""
    try:
        # Create a unique directory for this student
        if student_id:
            repo_name = f"student_{student_id}"
        else:
            repo_name = f"repo_{hash(repo_url) % 10000}"

        clone_path = os.path.join(config.CLONE_DIR, repo_name)

        # Clean up any existing directory
        if os.path.exists(clone_path):
            import shutil

            shutil.rmtree(clone_path)

        os.makedirs(clone_path, exist_ok=True)

        # Configure SSH for AP-F03 if not already configured
        ssh_config_path = os.path.expanduser("~/.ssh/config")
        apf03_config = """
# AP-F03 GitHub configuration
Host AP-F03
    HostName github.com
    User git
    IdentityFile ~/.ssh/AP-F03
    IdentitiesOnly yes
"""

        # Check if AP-F03 config already exists
        if os.path.exists(ssh_config_path):
            with open(ssh_config_path, "r") as f:
                ssh_config_content = f.read()
            if "Host AP-F03" not in ssh_config_content:
                with open(ssh_config_path, "a") as f:
                    f.write(apf03_config)
        else:
            # Create SSH config directory if it doesn't exist
            os.makedirs(os.path.dirname(ssh_config_path), exist_ok=True)
            with open(ssh_config_path, "w") as f:
                f.write(apf03_config)

        # Set proper permissions on SSH config
        os.chmod(ssh_config_path, 0o600)

        # Copy the SSH private key if it exists in the test cases directory
        ssh_key_source = os.path.join(
            config.TEST_CASES_DIR, "practice6", "AP-F03-git-ssh", "ssh.txt"
        )
        ssh_key_dest = os.path.expanduser("~/.ssh/AP-F03")

        if os.path.exists(ssh_key_source):
            import shutil

            os.makedirs(os.path.dirname(ssh_key_dest), exist_ok=True)
            shutil.copy2(ssh_key_source, ssh_key_dest)
            os.chmod(ssh_key_dest, 0o600)

        # Convert HTTPS URL to SSH URL using AP-F03 host
        if repo_url.startswith("https://github.com/"):
            # Extract owner/repo from HTTPS URL
            parts = repo_url.replace("https://github.com/", "").split("/")
            if len(parts) >= 2:
                owner = parts[0]
                repo = parts[1].replace(".git", "")
                ssh_url = f"git@AP-F03:{owner}/{repo}.git"
            else:
                ssh_url = repo_url  # fallback
        else:
            ssh_url = repo_url  # already SSH or other format

        # Clone the repository
        clone_command = ["git", "clone", "--depth", "1", ssh_url, clone_path]
        process = subprocess.run(
            clone_command,
            capture_output=True,
            text=True,
            timeout=120,  # 2-minute timeout
        )

        if process.returncode != 0:
            raise Exception(f"Git clone failed: {process.stderr}")

        # If commit SHA is specified, checkout that specific commit
        if commit_sha:
            checkout_command = ["git", "checkout", commit_sha]
            process = subprocess.run(
                checkout_command,
                cwd=clone_path,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if process.returncode != 0:
                raise Exception(f"Git checkout failed: {process.stderr}")

        return clone_path

    except Exception as e:
        raise Exception(f"Failed to clone repository {repo_url}: {str(e)}")


def read_project_files(project_path: str) -> str:
    """Reads all .cpp and .h files in a directory and concatenates them with analysis."""
    full_code = ""
    code_metrics = {
        "total_files": 0,
        "total_lines": 0,
        "cpp_files": 0,
        "header_files": 0,
        "largest_file": "",
        "max_lines": 0,
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
                        lines = content.count("\n") + 1
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
        "total_lines": 0,
    }

    lines = source_code.split("\n")
    analysis["total_lines"] = len(lines)

    in_main = False
    main_lines = 0
    functions = []
    current_function_lines = 0

    for line in lines:
        stripped = line.strip()

        # Count comments
        if stripped.startswith("//") or stripped.startswith("/*"):
            analysis["comment_lines"] += 1
            continue

        # Check for iterators
        if (
            "iterator" in stripped.lower()
            or "->begin()" in stripped
            or "->end()" in stripped
        ):
            analysis["uses_iterators"] = True

        # Check for containers
        if any(
            container in stripped
            for container in ["std::vector", "std::map", "std::set"]
        ):
            analysis["uses_containers"] = True

        # Check for structs
        if stripped.startswith("struct ") or "struct " in stripped:
            analysis["uses_structs"] = True

        # Check for global variables (simplified)
        if (
            not in_main
            and "=" in stripped
            and not stripped.startswith(" ")
            and not stripped.startswith("\t")
        ):
            if not any(
                keyword in stripped
                for keyword in [
                    "int main",
                    "void",
                    "int ",
                    "float ",
                    "double ",
                    "char ",
                    "bool ",
                ]
            ):
                analysis["global_variables"] += 1

        # Check for magic numbers (simplified)
        import re

        magic_nums = re.findall(r"\b\d+\b", stripped)
        for num in magic_nums:
            if num not in ["0", "1", "2", "10", "100"]:  # Common acceptable numbers
                analysis["magic_numbers"] += 1

        # Track main function
        if "int main(" in stripped or "void main(" in stripped:
            in_main = True
            analysis["function_count"] += 1
        elif in_main and stripped == "}":
            in_main = False
            analysis["main_function_lines"] = main_lines
            main_lines = 0
        elif in_main:
            main_lines += 1

        # Track other functions
        if (
            any(
                keyword in stripped
                for keyword in ["int ", "void ", "float ", "double ", "char ", "bool "]
            )
            and "(" in stripped
        ):
            if not in_main:
                analysis["function_count"] += 1
                if current_function_lines > 0:
                    functions.append(current_function_lines)
                current_function_lines = 1
            else:
                current_function_lines += 1
        elif current_function_lines > 0:
            current_function_lines += 1
            if stripped == "}":
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
            page_text = page_text.replace("\n\n", "\n")  # Remove excessive newlines
            page_text = page_text.replace("  ", " ")  # Remove double spaces

            # Add page separator for multi-page documents
            if page_num > 0:
                text_content.append(f"\n--- Page {page_num + 1} ---\n")

            text_content.append(page_text)

        doc.close()

        full_text = "".join(text_content)

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
        "bonus_features": [],
    }

    # Simple keyword-based extraction (can be enhanced with NLP if needed)
    lines = pdf_text.split("\n")

    for line in lines:
        line_lower = line.lower().strip()

        # Extract objectives
        if any(
            keyword in line_lower
            for keyword in ["objective", "goal", "purpose", "task"]
        ):
            if len(line.strip()) > 10:  # Avoid very short lines
                requirements["objectives"].append(line.strip())

        # Extract constraints
        elif any(
            keyword in line_lower
            for keyword in [
                "constraint",
                "limitation",
                "restriction",
                "must not",
                "cannot",
            ]
        ):
            if len(line.strip()) > 10:
                requirements["constraints"].append(line.strip())

        # Extract required features
        elif any(
            keyword in line_lower
            for keyword in ["required", "implement", "create", "write"]
        ):
            if len(line.strip()) > 10:
                requirements["required_features"].append(line.strip())

        # Extract grading criteria
        elif any(
            keyword in line_lower
            for keyword in ["grade", "point", "score", "criteria", "evaluation"]
        ):
            if len(line.strip()) > 10:
                requirements["grading_criteria"].append(line.strip())

        # Extract bonus features
        elif any(
            keyword in line_lower
            for keyword in ["bonus", "extra", "additional", "optional"]
        ):
            if len(line.strip()) > 10:
                requirements["bonus_features"].append(line.strip())

    return requirements


def summarize_text(text: str, max_length: int = 500) -> str:
    """Summarizes the given text to the specified maximum length."""
    if len(text) <= max_length:
        return text

    # Simple summarization by truncating and appending ellipsis
    return text[:max_length] + "..."


def get_practice_descriptions(practices_dir: str) -> dict:
    """Reads and summarizes all practice description PDFs from a directory."""
    practice_descriptions = {}
    if not os.path.exists(practices_dir):
        return practice_descriptions

    # Walk through the directory and subdirectories
    for root, _, files in os.walk(practices_dir):
        for file in files:
            if file.lower().endswith(".pdf"):
                pdf_path = os.path.join(root, file)
                practice_name = os.path.splitext(file)[0]
                full_text = read_practice_description(pdf_path)
                summarized_text = summarize_text(full_text)
                practice_descriptions[practice_name] = summarized_text

    return practice_descriptions


def _make_testcase_pair(test_dir: str, index: int, input_text: str, output_text: str):
    """Helper: write a .in/.out pair in test_dir with zero-padded index."""
    os.makedirs(test_dir, exist_ok=True)
    name = f"{index:02d}"
    in_path = os.path.join(test_dir, f"{name}.in")
    out_path = os.path.join(test_dir, f"{name}.out")
    with open(in_path, "w") as f:
        f.write(input_text)
    with open(out_path, "w") as f:
        f.write(output_text)


def generate_testcases_from_description(assignment: str, num_cases: int = 3) -> str:
    """Generates simple testcase skeletons for an assignment based on its description.

    - assignment: assignment name or key, e.g., 'A1' or 'APS04-A1-Description'
    - num_cases: number of test pairs to generate

    Returns the path to the created test directory.
    This function creates files under `config.TEST_CASES_DIR/<assignment>/tests/`.
    """
    descriptions = get_practice_descriptions(config.PRACTICES_DIR)
    # Try exact key, then look for key-containing entry
    text = descriptions.get(assignment)
    if not text:
        # fallback: find first key that contains the assignment substring
        for k, v in descriptions.items():
            if assignment.lower() in k.lower():
                text = v
                break

    if not text:
        raise FileNotFoundError(
            f"No practice description found for assignment '{assignment}'"
        )

    reqs = extract_practice_requirements(text)

    # Create test directory
    target_dir = os.path.join(config.TEST_CASES_DIR, assignment)
    tests_dir = os.path.join(target_dir, "tests")

    # Simple heuristic to produce input/output based on required features or objectives
    features = reqs.get("required_features", []) or reqs.get("objectives", [])
    # If no features found, produce generic arithmetic tests
    if not features:
        features = ["Sum numbers", "Multiply numbers", "Edge case zero"]

    # Generate testcases
    for i in range(1, num_cases + 1):
        feature = features[(i - 1) % len(features)]
        # Very simple mapping: if feature mentions 'sum' or 'add' -> sum input
        feature_lower = feature.lower()
        if any(w in feature_lower for w in ["sum", "add", "total"]):
            inp = "5\n1 2 3 4 5\n"
            out = str(sum([1, 2, 3, 4, 5])) + "\n"
        elif any(w in feature_lower for w in ["multiply", "product"]):
            inp = "3\n2 3 4\n"
            out = str(2 * 3 * 4) + "\n"
        elif any(w in feature_lower for w in ["edge", "zero"]):
            inp = "1\n0\n"
            out = "0\n"
        else:
            # default numeric test
            inp = f"{i}\n{ ' '.join(str(x) for x in range(1, i+2)) }\n"
            out = str(sum(range(1, i + 2))) + "\n"

        _make_testcase_pair(tests_dir, i, inp, out)

    print(f"Generated {num_cases} testcases for {assignment} in {tests_dir}")
    return tests_dir


def generate_all_testcases():
    """Generates test cases for all assignments in the practices directory."""
    descriptions = get_practice_descriptions(config.PRACTICES_DIR)
    for assignment in descriptions.keys():
        try:
            generate_testcases_from_description(assignment)
        except Exception as e:
            print(f"Failed to generate test cases for {assignment}: {e}")

    print("Test case generation completed for all assignments.")


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
        severity_counts = {
            "error": 0,
            "warning": 0,
            "style": 0,
            "performance": 0,
            "information": 0,
        }
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
                error_details.append(
                    f"[{severity.upper()}] {file}:{line} - {msg} (ID: {error_id})"
                )

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
            summary += (
                "\n💡 PERFORMANCE: Consider optimization opportunities identified.\n"
            )
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
    """Builds the project and runs it against test cases using the judge.sh system."""

    # Special handling for A6 multi-phase
    if practice_name == "A6":
        return run_judge_tests_a6(project_path, practice_name)

    # Try to use judge.sh for other practices
    judge_results = run_judge_tests(project_path, practice_name)
    if judge_results["total_tests"] > 0 or "Judge folder not found" not in judge_results["execution_summary"]:
        return judge_results

    # Fallback to original test system if judge.sh is not available
    return run_standard_tests(project_path, practice_name)


def run_judge_tests(
    project_path: str, practice_name: str, judge_script_path: str
) -> dict:
    """Runs tests using the judge.sh system for A6 assignments."""
    results = {
        "build_successful": False,
        "passed_tests": 0,
        "total_tests": 0,
        "failed_tests": [],
        "execution_summary": "",
        "build_output": "",
        "test_details": [],
    }

    try:
        # Copy student's code to the judge directory
        judge_dir = os.path.dirname(judge_script_path)
        temp_run_dir = os.path.join(judge_dir, "temp-run")

        # Clean and create temp directory
        if os.path.exists(temp_run_dir):
            import shutil

            shutil.rmtree(temp_run_dir)
        os.makedirs(temp_run_dir)

        # Copy all source files from student's project
        for root, _, files in os.walk(project_path):
            for file in files:
                if file.endswith((".cpp", ".h", ".hpp", "Makefile", "makefile")):
                    src_path = os.path.join(root, file)
                    dst_path = os.path.join(temp_run_dir, file)
                    import shutil

                    shutil.copy2(src_path, dst_path)

        # Run the judge.sh test command
        judge_command = [judge_script_path, "-t"]
        process = subprocess.run(
            judge_command,
            cwd=judge_dir,
            capture_output=True,
            text=True,
            timeout=300,  # 5-minute timeout
        )

        results["execution_summary"] = process.stdout
        if process.stderr:
            results["execution_summary"] += f"\nSTDERR:\n{process.stderr}"

        # Parse the output to extract test results
        output_lines = process.stdout.split("\n")
        for line in output_lines:
            if "Passed:" in line and "Failed:" in line:
                # Parse summary line like "Passed: 3 out of 5"
                parts = line.split()
                if len(parts) >= 5:
                    try:
                        passed = int(parts[1])
                        total = int(parts[4])
                        results["passed_tests"] = passed
                        results["total_tests"] = total
                        results["failed_tests"] = list(range(passed + 1, total + 1))
                        results["build_successful"] = True
                    except ValueError:
                        pass

        if results["total_tests"] == 0:
            # If parsing failed, assume build was successful if no clear errors
            if "Compiled Successfully" in process.stdout or "Compiled successfully" in process.stdout:
                results["build_successful"] = True
                results["execution_summary"] += "\n⚠️ Could not parse test results, but compilation was successful."

        return results

    except subprocess.TimeoutExpired:
        results["execution_summary"] = "❌ Testing timed out after 5 minutes."
        return results
    except Exception as e:
        results["execution_summary"] = f"❌ Error running judge.sh: {str(e)}"
        return results


def run_standard_tests(
    project_path: str, practice_name: str, practice_config: dict
) -> dict:
    """Runs tests using the standard test system for non-A6 assignments."""
    results = {
        "build_successful": False,
        "passed_tests": 0,
        "total_tests": 0,
        "failed_tests": [],
        "execution_summary": "",
        "build_output": "",
        "test_details": [],
    }

    # 1. Build the code with better error capture
    try:
        build_process = subprocess.run(
            practice_config["build_command"].split(),
            cwd=project_path,
            check=True,
            capture_output=True,
            text=True,
            timeout=120,  # 2-minute timeout for build
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
        results[
            "execution_summary"
        ] += f"❌ Executable '{practice_config['executable_name']}' not found after build.\n"
        return results

    # 3. Run test cases with detailed reporting
    test_cases_dir = practice_config["test_cases_dir"]
    if not os.path.exists(test_cases_dir):
        results[
            "execution_summary"
        ] += f"❌ Test cases directory '{test_cases_dir}' not found.\n"
        return results

    test_files = [f for f in os.listdir(test_cases_dir) if f.endswith(".in")]
    results["total_tests"] = len(test_files)

    if results["total_tests"] == 0:
        results["execution_summary"] += "⚠️  No test cases found in the directory.\n"
        return results

    results[
        "execution_summary"
    ] += f"🧪 Running {results['total_tests']} test cases...\n\n"

    for i, test_file in enumerate(test_files, 1):
        input_path = os.path.join(test_cases_dir, test_file)
        output_path = os.path.join(test_cases_dir, test_file.replace(".in", ".out"))

        test_result = {
            "test_name": test_file,
            "passed": False,
            "execution_time": 0,
            "error": None,
            "expected_output": "",
            "actual_output": "",
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
                timeout=10,  # 10-second timeout per test
            )
            execution_time = time.time() - start_time

            actual_output = run_process.stdout.strip()

            # Compare outputs
            if actual_output == expected_output:
                results["passed_tests"] += 1
                test_result["passed"] = True
                results[
                    "execution_summary"
                ] += f"✅ Test {i}/{results['total_tests']}: {test_file} - PASSED\n"
            else:
                results["failed_tests"].append(test_file)
                test_result["passed"] = False
                results[
                    "execution_summary"
                ] += f"❌ Test {i}/{results['total_tests']}: {test_file} - FAILED\n"
                results[
                    "execution_summary"
                ] += f"   Expected: {expected_output[:100]}{'...' if len(expected_output) > 100 else ''}\n"
                results[
                    "execution_summary"
                ] += f"   Got:      {actual_output[:100]}{'...' if len(actual_output) > 100 else ''}\n"

            test_result["execution_time"] = round(execution_time, 3)
            test_result["expected_output"] = expected_output
            test_result["actual_output"] = actual_output

        except subprocess.TimeoutExpired:
            results["failed_tests"].append(test_file)
            test_result["error"] = "Timeout (10s)"
            results[
                "execution_summary"
            ] += f"⏰ Test {i}/{results['total_tests']}: {test_file} - TIMEOUT\n"
        except FileNotFoundError:
            results["failed_tests"].append(test_file)
            test_result["error"] = "Expected output file missing"
            results[
                "execution_summary"
            ] += f"📁 Test {i}/{results['total_tests']}: {test_file} - MISSING OUTPUT FILE\n"
        except Exception as e:
            results["failed_tests"].append(test_file)
            test_result["error"] = str(e)
            results[
                "execution_summary"
            ] += f"💥 Test {i}/{results['total_tests']}: {test_file} - ERROR: {e}\n"

        results["test_details"].append(test_result)

    # Add summary statistics
    pass_rate = (
        (results["passed_tests"] / results["total_tests"]) * 100
        if results["total_tests"] > 0
        else 0
    )
    results[
        "execution_summary"
    ] += f"\n📊 Test Summary: {results['passed_tests']}/{results['total_tests']} passed ({pass_rate:.1f}%)\n"

    if results["failed_tests"]:
        results[
            "execution_summary"
        ] += f"❌ Failed tests: {', '.join(results['failed_tests'])}\n"

    return results


def run_judge_tests_a6(project_path: str, practice_name: str) -> dict:
    """Runs tests for A6 multi-phase assignment using judge.sh scripts."""
    results = {
        "build_successful": False,
        "passed_tests": 0,
        "total_tests": 0,
        "failed_tests": [],
        "execution_summary": "",
        "build_output": "",
        "test_details": [],
        "phase_results": {}
    }

    # Find the judge folder for A6
    judge_dir = None
    test_cases_dir = os.path.join(config.TEST_CASES_DIR, "practice6")
    if os.path.exists(test_cases_dir):
        judge_path = os.path.join(test_cases_dir, "judge")
        if os.path.exists(judge_path):
            judge_dir = judge_path

    if not judge_dir:
        results["execution_summary"] = "❌ Judge folder not found for A6"
        return results

    judge_script = os.path.join(judge_dir, "judge.sh")

    if not os.path.exists(judge_script):
        results["execution_summary"] = "❌ judge.sh not found in judge directory"
        return results

    try:
        # Copy student's code to judge directory
        temp_run_dir = os.path.join(judge_dir, "temp-P3")  # Use P3 as default
        if os.path.exists(temp_run_dir):
            import shutil
            shutil.rmtree(temp_run_dir)
        os.makedirs(temp_run_dir)

        # Copy all source files from student's project
        for root, _, files in os.walk(project_path):
            for file in files:
                if file.endswith((".cpp", ".h", ".hpp", "Makefile", "makefile")):
                    src_path = os.path.join(root, file)
                    dst_path = os.path.join(temp_run_dir, file)
                    import shutil
                    shutil.copy2(src_path, dst_path)

        # Run tests for all phases
        phase_results = {}
        total_passed = 0
        total_tests = 0

        for phase in [1, 2, 3]:
            print(f"Running Phase {phase} tests...")

            # Change to the specific phase
            change_command = [judge_script, "-p", str(phase)]
            subprocess.run(change_command, cwd=judge_dir, capture_output=True, text=True)

            # Run tests for this phase
            test_command = [judge_script, "-t"]
            process = subprocess.run(
                test_command,
                cwd=judge_dir,
                capture_output=True,
                text=True,
                timeout=300,
            )

            phase_output = process.stdout
            if process.stderr:
                phase_output += f"\nSTDERR:\n{process.stderr}"

            # Parse results for this phase
            passed = 0
            total = 0
            output_lines = phase_output.split("\n")
            for line in output_lines:
                if "Passed:" in line and "Failed:" in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        try:
                            passed = int(parts[1])
                            total = int(parts[4])
                            break
                        except ValueError:
                            pass

            phase_results[f"phase{phase}"] = {
                "passed": passed,
                "total": total,
                "output": phase_output
            }

            total_passed += passed
            total_tests += total

        results["passed_tests"] = total_passed
        results["total_tests"] = total_tests
        results["phase_results"] = phase_results
        results["build_successful"] = True

        # Combine all phase outputs
        combined_output = ""
        for phase, phase_data in phase_results.items():
            combined_output += f"\n=== PHASE {phase.upper()} ===\n"
            combined_output += phase_data["output"]
            combined_output += f"\nPhase {phase}: {phase_data['passed']}/{phase_data['total']} tests passed\n"

        results["execution_summary"] = combined_output

        return results

    except subprocess.TimeoutExpired:
        results["execution_summary"] = "❌ Testing timed out after 5 minutes."
        return results
    except Exception as e:
        results["execution_summary"] = f"❌ Error running A6 judge.sh: {str(e)}"
        return results
