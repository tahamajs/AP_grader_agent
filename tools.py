# tools.py
import os
import subprocess
import xml.etree.ElementTree as ET
import logging
import json
from datetime import datetime
from git import Repo, GitCommandError
import config
import fitz  # PyMuPDF for PDF reading
import time

# Setup logging for tools
logger = logging.getLogger(__name__)


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


def generate_testcases_from_description(
    assignment: str, num_cases: int = 3, use_llm: bool = False
) -> str:
    """Generates testcase skeletons for an assignment based on its description.

    - assignment: assignment name or key, e.g., 'A1' or 'APS04-A1-Description'
    - num_cases: number of test pairs to generate
    - use_llm: whether to use LLM for better test case generation

    Returns the path to the created test directory.
    This function creates files under `config.TEST_CASES_DIR/<assignment>/tests/`.
    """
    logger.info(
        f"Starting test case generation for assignment {assignment}, num_cases={num_cases}, use_llm={use_llm}"
    )

    # Create logs directory for comprehensive logging
    logs_dir = os.path.join(os.getcwd(), "test_generation_logs")
    os.makedirs(logs_dir, exist_ok=True)

    # Log generation session start
    session_log = {
        "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "assignment": assignment,
        "num_cases_requested": num_cases,
        "use_llm": use_llm,
        "start_time": datetime.now().isoformat(),
        "status": "in_progress",
    }

    session_log_file = os.path.join(
        logs_dir, f"session_{session_log['session_id']}.json"
    )
    with open(session_log_file, "w", encoding="utf-8") as f:
        json.dump(session_log, f, indent=2, ensure_ascii=False)

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
        error_msg = f"No practice description found for assignment '{assignment}'"
        logger.error(error_msg)

        # Update session log with error
        session_log["status"] = "failed"
        session_log["error"] = error_msg
        session_log["end_time"] = datetime.now().isoformat()
        with open(session_log_file, "w", encoding="utf-8") as f:
            json.dump(session_log, f, indent=2, ensure_ascii=False)

        raise FileNotFoundError(error_msg)

    reqs = extract_practice_requirements(text)

    # Create test directory
    target_dir = os.path.join(config.TEST_CASES_DIR, assignment)
    tests_dir = os.path.join(target_dir, "tests")

    # Log requirements extraction
    reqs_log = {
        "assignment": assignment,
        "description_length": len(text),
        "extracted_requirements": reqs,
        "timestamp": datetime.now().isoformat(),
    }
    reqs_file = os.path.join(
        logs_dir,
        f"requirements_{assignment}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
    )
    with open(reqs_file, "w", encoding="utf-8") as f:
        json.dump(reqs_log, f, indent=2, ensure_ascii=False)

    if use_llm:
        # Use LLM for better test case generation
        test_cases = generate_testcases_with_llm(text, reqs, num_cases)
    else:
        # Use heuristic approach
        test_cases = generate_testcases_heuristic(reqs, num_cases)

    # Save test cases to files
    saved_files = []
    for i, (input_text, output_text) in enumerate(test_cases, 1):
        file_path = _make_testcase_pair(tests_dir, i, input_text, output_text)
        saved_files.append(file_path)

    # Save comprehensive metadata about generation
    metadata = {
        "assignment": assignment,
        "num_cases": num_cases,
        "use_llm": use_llm,
        "timestamp": datetime.now().isoformat(),
        "session_id": session_log["session_id"],
        "requirements": reqs,
        "description_summary": summarize_text(text, 200),
        "generated_test_cases": len(test_cases),
        "saved_files": saved_files,
        "test_directory": tests_dir,
        "logs_directory": logs_dir,
        "generation_method": "llm" if use_llm else "heuristic",
        "requirements_file": reqs_file,
    }

    metadata_path = os.path.join(target_dir, "generation_metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    # Update session log with success
    session_log["status"] = "completed"
    session_log["end_time"] = datetime.now().isoformat()
    session_log["generated_cases"] = len(test_cases)
    session_log["metadata_file"] = metadata_path
    session_log["test_directory"] = tests_dir
    with open(session_log_file, "w", encoding="utf-8") as f:
        json.dump(session_log, f, indent=2, ensure_ascii=False)

    logger.info(
        f"Successfully generated {num_cases} testcases for {assignment} in {tests_dir}"
    )
    logger.info(f"Comprehensive logs saved to: {logs_dir}")
    print(f"Generated {num_cases} testcases for {assignment} in {tests_dir}")
    print(f"Logs and metadata saved to: {logs_dir}")
    return tests_dir


def generate_testcases_heuristic(reqs: dict, num_cases: int) -> list:
    """Generate test cases using heuristic approach based on requirements."""
    test_cases = []

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

        test_cases.append((inp, out))

    return test_cases


def generate_testcases_with_llm(description: str, reqs: dict, num_cases: int) -> list:
    """Generate test cases using LLM for better quality and relevance."""
    try:
        # Import here to avoid circular imports
        import google.generativeai as genai
        from dotenv import load_dotenv
        from prompts import get_test_generation_prompt

        load_dotenv()
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

        # Get the prompt from the centralized prompts module
        prompt = get_test_generation_prompt(description, reqs, num_cases)

        logger.info(
            f"Generating {num_cases} test cases using LLM for assignment with requirements: {list(reqs.keys())}"
        )

        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)

        # Use centralized parser/validator from prompts.py
        from prompts import parse_and_validate_response

        response_text = response.text
        logger.debug(f"LLM raw response: {response_text[:800]}...")

        # Save raw response for debugging
        raw_dir = os.path.join(os.getcwd(), "test_generation_logs")
        os.makedirs(raw_dir, exist_ok=True)
        raw_file = os.path.join(
            raw_dir, f"llm_raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        with open(raw_file, "w", encoding="utf-8") as f:
            f.write(response_text)

        # Parse and validate
        def _validator(d: dict):
            if not isinstance(d, dict) or "test_cases" not in d:
                raise ValueError(
                    "Missing 'test_cases' key or invalid top-level structure"
                )
            if not isinstance(d["test_cases"], list):
                raise ValueError("'test_cases' must be a list")

        parsed = parse_and_validate_response(
            response_text,
            validator=_validator,
            description=(
                f"test generation for description (truncated): {description[:80]}"
            ),
            save_raw_to=raw_file,
        )

        test_cases_data = parsed["test_cases"]
        if len(test_cases_data) != num_cases:
            logger.warning(
                f"LLM generated {len(test_cases_data)} test cases, expected {num_cases}"
            )

        test_cases = []
        for i, tc in enumerate(test_cases_data):
            if not isinstance(tc, dict):
                logger.warning(f"Test case {i+1} is not a dictionary, skipping")
                continue

            # Validate required fields
            required_fields = ["input", "expected_output"]
            if not all(field in tc for field in required_fields):
                logger.warning(f"Test case {i+1} missing required fields, skipping")
                continue

            input_data = str(tc["input"])
            expected_output = str(tc["expected_output"])

            description_field = tc.get("description", f"Test case {i+1}")
            category = tc.get("category", "unknown")
            logger.info(
                f"Generated test case {i+1}: {description_field} (category: {category})"
            )

            test_cases.append((input_data, expected_output))

        # Save parsed metadata
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "assignment_description": (
                description[:200] + "..." if len(description) > 200 else description
            ),
            "requirements": reqs,
            "requested_cases": num_cases,
            "generated_cases": len(test_cases),
            "llm_raw_file": raw_file,
            "parsed_preview": {"test_cases_count": len(test_cases_data)},
        }

        metadata_dir = os.path.join(os.getcwd(), "test_generation_logs")
        os.makedirs(metadata_dir, exist_ok=True)
        metadata_file = os.path.join(
            metadata_dir,
            f"llm_generation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        )
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        logger.info(
            f"Successfully generated {len(test_cases)} test cases using LLM. Metadata saved to: {metadata_file}"
        )
        return test_cases

    except Exception as e:
        logger.error(f"Failed to generate test cases with LLM: {e}")
        # Save error information for debugging
        error_metadata = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(e).__name__,
            "error_message": str(e),
            "assignment_description": (
                description[:200] + "..." if len(description) > 200 else description
            ),
            "requirements": reqs,
            "requested_cases": num_cases,
        }

        error_dir = os.path.join(os.getcwd(), "test_generation_logs")
        os.makedirs(error_dir, exist_ok=True)
        error_file = os.path.join(
            error_dir, f"llm_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        with open(error_file, "w", encoding="utf-8") as f:
            json.dump(error_metadata, f, indent=2, ensure_ascii=False)

        logger.info(f"Error metadata saved to: {error_file}")
        return generate_testcases_heuristic(reqs, num_cases)


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

    logger.info(
        f"Starting build and test process for practice {practice_name} in {project_path}"
    )

    # Try to use judge.sh for all practices
    judge_results = run_judge_tests(project_path, practice_name)
    if (
        judge_results["total_tests"] > 0
        or "Judge folder not found" not in judge_results["execution_summary"]
    ):
        logger.info(
            f"Using judge.sh system for {practice_name}, results: {judge_results['passed_tests']}/{judge_results['total_tests']} tests passed"
        )
        save_test_results(judge_results, practice_name, "judge")
        return judge_results

    # Fallback to original test system if judge.sh is not available
    logger.info(f"Falling back to standard test system for {practice_name}")
    practice_config = config.PRACTICE_CONFIGS.get(practice_name, {})
    standard_results = run_standard_tests(project_path, practice_name, practice_config)
    save_test_results(standard_results, practice_name, "standard")
    return standard_results


def run_judge_tests(project_path: str, practice_name: str) -> dict:
    """Runs tests using the judge.sh system for any practice assignment."""
    logger.info(
        f"Attempting to run judge tests for practice {practice_name} in {project_path}"
    )

    results = {
        "build_successful": False,
        "passed_tests": 0,
        "total_tests": 0,
        "failed_tests": [],
        "execution_summary": "",
        "build_output": "",
        "test_details": [],
    }

    # Find the judge folder for the practice
    judge_dir = None
    test_cases_dir = os.path.join(config.TEST_CASES_DIR, f"practice{practice_name[1:]}")
    if os.path.exists(test_cases_dir):
        judge_path = os.path.join(test_cases_dir, "judge")
        if os.path.exists(judge_path):
            judge_dir = judge_path

    if not judge_dir:
        results["execution_summary"] = f"❌ Judge folder not found for {practice_name}"
        logger.warning(f"Judge folder not found for practice {practice_name}")
        return results

    judge_script = os.path.join(judge_dir, "judge.sh")

    if not os.path.exists(judge_script):
        results["execution_summary"] = "❌ judge.sh not found in judge directory"
        logger.error(f"judge.sh not found in {judge_dir}")
        return results

    try:
        logger.info(f"Found judge.sh at {judge_script}, determining if multi-phase")

        # Check if this is a multi-phase assignment (like A6)
        is_multi_phase = practice_name == "A6" or os.path.exists(
            os.path.join(judge_dir, "P1")
        )

        if is_multi_phase:
            logger.info(f"Running multi-phase judge tests for {practice_name}")
            # Handle multi-phase assignment
            return run_judge_tests_multi_phase(
                project_path, practice_name, judge_dir, judge_script
            )
        else:
            logger.info(f"Running single-phase judge tests for {practice_name}")
            # Handle single-phase assignment
            return run_judge_tests_single_phase(
                project_path, practice_name, judge_dir, judge_script
            )

    except Exception as e:
        results["execution_summary"] = f"❌ Error running judge.sh: {str(e)}"
        logger.error(f"Error running judge.sh for {practice_name}: {str(e)}")
        return results


def run_judge_tests_single_phase(
    project_path: str, practice_name: str, judge_dir: str, judge_script: str
) -> dict:
    """Runs tests for single-phase assignments using judge.sh scripts."""
    logger.info(f"Running single-phase judge tests for {practice_name}")

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

        logger.info(
            f"Copied {len([f for f in os.listdir(temp_run_dir) if f.endswith(('.cpp', '.h', '.hpp'))])} source files to judge directory"
        )

        # Run the judge.sh test command
        judge_command = [judge_script, "-t"]
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
            if (
                "Compiled Successfully" in process.stdout
                or "Compiled successfully" in process.stdout
            ):
                results["build_successful"] = True
                results[
                    "execution_summary"
                ] += "\n⚠️ Could not parse test results, but compilation was successful."

        logger.info(
            f"Single-phase judge test results for {practice_name}: {results['passed_tests']}/{results['total_tests']} tests passed"
        )
        return results

    except subprocess.TimeoutExpired:
        results["execution_summary"] = "❌ Testing timed out after 5 minutes."
        logger.error(f"Judge testing timed out for {practice_name}")
        return results
    except Exception as e:
        results["execution_summary"] = f"❌ Error running judge.sh: {str(e)}"
        logger.error(
            f"Error in single-phase judge testing for {practice_name}: {str(e)}"
        )
        return results


def run_judge_tests_multi_phase(
    project_path: str, practice_name: str, judge_dir: str, judge_script: str
) -> dict:
    """Runs tests for multi-phase assignments using judge.sh scripts."""
    results = {
        "build_successful": False,
        "passed_tests": 0,
        "total_tests": 0,
        "failed_tests": [],
        "execution_summary": "",
        "build_output": "",
        "test_details": [],
        "phase_results": {},
    }

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

        # Determine number of phases by checking P1, P2, P3 directories
        phases = []
        for i in range(1, 4):  # Check up to 3 phases
            if os.path.exists(os.path.join(judge_dir, f"P{i}")):
                phases.append(i)

        if not phases:
            phases = [1, 2, 3]  # Default for A6

        for phase in phases:
            print(f"Running Phase {phase} tests...")

            # Change to the specific phase
            change_command = [judge_script, "-p", str(phase)]
            subprocess.run(
                change_command, cwd=judge_dir, capture_output=True, text=True
            )

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
                "output": phase_output,
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
        results["execution_summary"] = f"❌ Error running judge.sh: {str(e)}"
        return results


def save_test_results(
    test_results: dict, practice_name: str, test_type: str, student_id: str = None
):
    """Save test results as JSON file with timestamp."""
    # Create test results directory if it doesn't exist
    results_dir = os.path.join(os.getcwd(), "test_results")
    os.makedirs(results_dir, exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    student_part = f"{student_id}_" if student_id else ""
    filename = f"{student_part}{practice_name}_{test_type}_{timestamp}.json"
    filepath = os.path.join(results_dir, filename)

    # Prepare output data
    output_data = {
        "practice_name": practice_name,
        "test_type": test_type,
        "student_id": student_id,
        "timestamp": datetime.now().isoformat(),
        "test_results": test_results,
    }

    # Save to JSON file
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    logger.info(f"Test results saved to: {filepath}")
    return filepath


def run_standard_tests(
    project_path: str, practice_name: str, practice_config: dict
) -> dict:
    """Runs tests using the standard test system for assignments."""
    results = {
        "build_successful": False,
        "passed_tests": 0,
        "total_tests": 0,
        "failed_tests": [],
        "execution_summary": "",
        "build_output": "",
        "test_details": [],
    }

    # Get build command and executable name from config or use defaults
    build_command = practice_config.get("build_command", "make")
    executable_name = practice_config.get("executable_name", "student_program")
    test_cases_dir_rel = practice_config.get(
        "test_cases_dir", f"test_cases/{practice_name}"
    )

    # Convert relative test cases dir to absolute path
    if not test_cases_dir_rel.startswith("/"):
        test_cases_dir = os.path.join(
            config.TEST_CASES_DIR, test_cases_dir_rel.replace("test_cases/", "")
        )
    else:
        test_cases_dir = test_cases_dir_rel

    # 1. Build the code with better error capture
    try:
        build_process = subprocess.run(
            build_command.split(),
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
    executable_path = os.path.join(project_path, executable_name)
    if not os.path.exists(executable_path):
        results[
            "execution_summary"
        ] += f"❌ Executable '{executable_name}' not found after build.\n"
        return results

    # 3. Run test cases with detailed reporting
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
