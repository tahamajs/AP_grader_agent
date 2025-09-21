"""
Debug script for testing generate functionality
"""

import sys
import os

sys.path.append("/Users/tahamajs/Documents/uni/LLM/grading_agent")

print("=== DEBUG SCRIPT START ===")

try:
    print("1. Importing modules...")
    import tools
    import config
    from tools import (
        get_practice_descriptions,
        extract_practice_requirements,
        generate_testcases_heuristic,
    )

    print("   ✅ Imports successful")

    print("2. Testing get_practice_descriptions...")
    descriptions = get_practice_descriptions(config.PRACTICES_DIR)
    print(f"   ✅ Found {len(descriptions)} descriptions")

    print("3. Testing extract_practice_requirements...")
    text = descriptions.get("APS04-A1-Description", "")
    if text:
        reqs = extract_practice_requirements(text)
        print(f"   ✅ Extracted requirements: {list(reqs.keys())}")
    else:
        print("   ❌ No A1 description found")
        reqs = {}

    print("4. Testing generate_testcases_heuristic...")
    test_cases = generate_testcases_heuristic(reqs, 1)
    print(f"   ✅ Generated {len(test_cases)} test cases")

    print("5. Testing full generate_testcases_from_description...")
    result = tools.generate_testcases_from_description("A1", 1, False)
    print(f"   ✅ Full generation successful: {result}")

    print("=== DEBUG SCRIPT END ===")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
