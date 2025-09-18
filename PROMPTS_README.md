# PROMPTS CONFIGURATION GUIDE
"""
This file explains how to modify prompts in the grading agent system.

All prompts are now centralized in prompts.py for easy maintenance and modification.

## HOW TO MODIFY PROMPTS:

### 1. Test Generation Prompts
Located in: `get_test_generation_prompt()` function

To modify test generation behavior:
- Change the prompt text in the function
- Modify the JSON output format requirements
- Adjust test case categories or requirements

### 2. Grading Prompts
Located in: Various `get_*_grading_criteria()` functions

To modify grading criteria for any assignment:
- Edit the corresponding function (e.g., `get_a3_grading_criteria()`)
- Update point allocations
- Modify evaluation criteria
- Change scoring guidelines

### 3. Format Instructions
Located in: `get_format_instructions()` function

To modify output format requirements:
- Change JSON schema requirements
- Update scoring guidelines
- Modify response format expectations

## CONFIGURATION OPTIONS:

### Prompt Settings
Modify `PROMPT_CONFIG` dictionary to change:
- Temperature settings
- Max tokens
- Model selection

### Example Modifications:

```python
# To make grading more lenient
def get_a1_grading_criteria():
    return """
    **A1 GRADING CRITERIA (Lenient Version):**

    1. **LOGIC - ITERATORS (0-2 points)**  # Increased from 0-1
       - Award 2.0: Perfect iterator usage
       - Award 1.0: Good iterator usage
       - Award 0.5: Some iterator usage
       - Award 0.0: No iterator usage
    # ... rest of criteria
    """

# To change test generation focus
def get_test_generation_prompt(description, reqs, num_cases):
    return f"""
    You are an expert software testing engineer specializing in EDGE CASE DETECTION for programming assignments.
    # ... modified prompt focusing on edge cases
    """
```

## BEST PRACTICES:

1. **Test Changes**: Always test prompt modifications with sample data
2. **Version Control**: Keep track of prompt versions and their performance
3. **Documentation**: Document why changes were made and their expected impact
4. **Gradual Changes**: Make small, incremental changes to prompts
5. **Backup**: Keep backups of working prompt configurations

## QUICK REFERENCE:

- `get_test_generation_prompt()` - Test case generation
- `get_*_grading_criteria()` - Assignment-specific grading criteria
- `get_format_instructions()` - Output format requirements
- `PROMPT_CONFIG` - Model and generation settings
"""