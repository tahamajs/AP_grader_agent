# langchain_integration.py
import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import google.generativeai as genai

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# Define the desired JSON output structure using Pydantic
class GradingOutput(BaseModel):
    logic_iterators: float = Field(description="Score for using iterators (0 to 1)")
    design_containers: float = Field(
        description="Score for using std::vector, std::map (0 to 5)"
    )
    design_io_separation: float = Field(
        description="Score for separating I/O from logic (0 to 5)"
    )
    design_structs: float = Field(
        description="Score for using structs appropriately (0 to 5)"
    )
    design_no_god_main: float = Field(
        description="Score for having a clean, non-monolithic main (0 to 10)"
    )
    design_small_functions: float = Field(
        description="Score for small, single-responsibility functions (0 to 10)"
    )
    clean_no_comments: float = Field(
        description="Score for self-documenting code, not unnecessary comments (0 to 3)"
    )
    clean_no_duplication: float = Field(
        description="Score for avoiding duplicated code (DRY principle) (0 to 5)"
    )
    clean_indentation: float = Field(
        description="Score for proper and consistent indentation (0 to 3)"
    )
    clean_magic_values: float = Field(
        description="Score for using named constants instead of magic values/globals (0 to 4)"
    )
    clean_naming: float = Field(
        description="Score for clear and consistent variable/function naming (0 to 5)"
    )
    clean_consistency: float = Field(
        description="Score for overall code style consistency (0 to 5)"
    )
    generated_comment: str = Field(
        description="A 2-3 sentence constructive feedback comment for the student."
    )


def grade_student_project(
    test_results: str, static_analysis: str, source_code: str, practice_description: str
) -> GradingOutput:
    """Grades a student project using Gemini API directly with optimized prompts."""

    # Initialize the model with optimized settings
    model = genai.GenerativeModel(
        "gemini-pro",
        generation_config=genai.types.GenerationConfig(
            temperature=0.1,  # Lower temperature for more consistent grading
            top_p=0.8,
            top_k=40,
            max_output_tokens=2048,
        ),
    )

    # Enhanced format instructions with validation
    format_instructions = """
    CRITICAL: Respond ONLY with a valid JSON object. No markdown, no explanations, no additional text.

    Required JSON format:
    {
        "logic_iterators": number (0.0 to 1.0),
        "design_containers": number (0.0 to 5.0),
        "design_io_separation": number (0.0 to 5.0),
        "design_structs": number (0.0 to 5.0),
        "design_no_god_main": number (0.0 to 10.0),
        "design_small_functions": number (0.0 to 10.0),
        "clean_no_comments": number (0.0 to 3.0),
        "clean_no_duplication": number (0.0 to 5.0),
        "clean_indentation": number (0.0 to 3.0),
        "clean_magic_values": number (0.0 to 4.0),
        "clean_naming": number (0.0 to 5.0),
        "clean_consistency": number (0.0 to 5.0),
        "generated_comment": "string with 2-3 specific, actionable sentences"
    }

    Scoring Guidelines:
    - Use decimal scores (e.g., 3.5, 7.2) for partial credit
    - Be precise and consistent in scoring
    - Base scores on evidence from the code
    """

    # Enhanced prompt with detailed C++ grading criteria
    prompt = f"""
    You are an expert C++ Teaching Assistant with 10+ years of experience grading programming assignments.

    **ASSIGNMENT CONTEXT:**
    {practice_description}

    **GRADING TASK:**
    Analyze the student's C++ code submission based on the assignment requirements above and the established coding standards.

    **DETAILED GRADING CRITERIA:**

    1. **LOGIC - ITERATORS (0-1 point)**
       - Award 1.0: Correct and appropriate use of STL iterators (vector, map, set iterators)
       - Award 0.5: Some iterator usage but with issues
       - Award 0.0: No iterator usage or incorrect usage

    2. **DESIGN - CONTAINERS (0-5 points)**
       - Award 4-5: Excellent use of std::vector, std::map, std::set where appropriate
       - Award 2-3: Good container usage with minor issues
       - Award 0-1: Poor or no container usage, using arrays instead

    3. **DESIGN - I/O SEPARATION (0-5 points)**
       - Award 4-5: Clean separation of input/output from business logic
       - Award 2-3: Some separation but could be improved
       - Award 0-1: I/O mixed throughout the code

    4. **DESIGN - STRUCTS (0-5 points)**
       - Award 4-5: Appropriate use of structs/classes for data organization
       - Award 2-3: Some struct usage but incomplete
       - Award 0-1: No structs used, using primitive types everywhere

    5. **DESIGN - NO GOD MAIN (0-10 points)**
       - Award 8-10: Main function is clean, delegates to other functions (< 20 lines)
       - Award 5-7: Main is reasonable but could be cleaner
       - Award 0-4: Main is monolithic, contains all logic

    6. **DESIGN - SMALL FUNCTIONS (0-10 points)**
       - Award 8-10: Functions follow Single Responsibility Principle (< 15 lines each)
       - Award 5-7: Functions are reasonable size but could be smaller
       - Award 0-4: Large functions with multiple responsibilities

    7. **CLEAN - NO COMMENTS (0-3 points)**
       - Award 2-3: Code is self-documenting, minimal helpful comments
       - Award 1: Some unnecessary comments
       - Award 0: Excessive or unhelpful comments

    8. **CLEAN - NO DUPLICATION (0-5 points)**
       - Award 4-5: No code duplication, DRY principle followed
       - Award 2-3: Some duplication but manageable
       - Award 0-1: Significant code duplication

    9. **CLEAN - INDENTATION (0-3 points)**
       - Award 3: Perfect, consistent indentation
       - Award 2: Good indentation with minor inconsistencies
       - Award 0-1: Poor or inconsistent indentation

    10. **CLEAN - MAGIC VALUES/GLOBALS (0-4 points)**
        - Award 3-4: Named constants, no global variables
        - Award 1-2: Some magic numbers or globals
        - Award 0: Many magic numbers and global variables

    11. **CLEAN - NAMING (0-5 points)**
        - Award 4-5: Clear, consistent, descriptive names
        - Award 2-3: Good naming with minor issues
        - Award 0-1: Poor, inconsistent, or unclear naming

    12. **CLEAN - CONSISTENCY (0-5 points)**
        - Award 4-5: Consistent style throughout
        - Award 2-3: Mostly consistent with some variations
        - Award 0-1: Inconsistent style

    **ANALYSIS INPUTS:**

    **Test Results:**
    {test_results}

    **Static Analysis (cppcheck):**
    {static_analysis}

    **Source Code:**
    {source_code}

    **GRADING INSTRUCTIONS:**
    1. Carefully analyze the code against the assignment requirements
    2. Consider both functionality (tests) and code quality (static analysis)
    3. Provide specific, actionable feedback in 2-3 sentences
    4. Use evidence from the code to justify your scores
    5. Be fair but thorough in your assessment

    {format_instructions}
    """

    # Generate response with retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)

            # Clean the response text
            response_text = response.text.strip()

            # Remove potential markdown formatting
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            # Parse the JSON response
            result_dict = json.loads(response_text)
            grading_output = GradingOutput(**result_dict)
            return grading_output

        except json.JSONDecodeError as e:
            if attempt == max_retries - 1:
                raise ValueError(
                    f"Failed to parse JSON after {max_retries} attempts: {e}. Response: {response_text}"
                )
            print(f"JSON parsing failed (attempt {attempt + 1}), retrying...")
            continue
        except Exception as e:
            if attempt == max_retries - 1:
                raise ValueError(
                    f"Error processing response after {max_retries} attempts: {e}"
                )
            print(f"API call failed (attempt {attempt + 1}), retrying...")
            continue

    # This should never be reached, but just in case
    raise ValueError("Unexpected error in grading function")


def get_grading_chain():
    """Returns the grading function for compatibility."""
    return grade_student_project
