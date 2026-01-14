#!/usr/bin/env python3
"""
Fix test_meta_search.py mocks that incorrectly return SearchResult instead of List[Dict].

The _perform_search method returns List[Dict[str, Any]], not SearchResult.
This script fixes all mocked returns to match the actual API.
"""

import re

def fix_test_file():
    """Fix the test file mocks."""
    file_path = "tests/test_integration/test_meta_search.py"

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to match incorrect mock return values
    # We need to replace:
    # mock_search.return_value = SearchResult(...)
    # with:
    # mock_search.return_value = [{"title": "...", "snippet": "...", ...}]

    # Find all SearchResult returns in mocks
    pattern = r'mock_search\.return_value = SearchResult\((.*?)\n\s*\)'

    def replacement(match):
        """Replace SearchResult with proper list return."""
        search_result_args = match.group(1)

        # Extract results array from SearchResult
        results_match = re.search(r'results=\[(.*?)\]', search_result_args, re.DOTALL)
        if results_match:
            results_content = results_match.group(1)
            # Return just the results list
            return f'mock_search.return_value = [{results_content}]'
        else:
            # Default fallback
            return 'mock_search.return_value = [{"title": "Test Result", "snippet": "Test content", "url": "https://example.com", "score": 0.9}]'

    # Apply replacements
    fixed_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)

    print(f"✅ Fixed test mocks in {file_path}")

if __name__ == "__main__":
    fix_test_file()
