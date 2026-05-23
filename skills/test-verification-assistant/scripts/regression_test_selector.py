#!/usr/bin/env python3
"""
regression_test_selector.py
基于代码变更选择最小回归测试集。

Usage:
  python regression_test_selector.py \
    --diff diff.txt \
    --test-suite all_tests.json \
    --output selected_tests.json
"""

import json
import argparse
import re


def parse_diff(diff_text):
    """Parse git diff to find changed files and functions."""
    changed_files = set()
    changed_functions = set()
    
    for line in diff_text.split("\n"):
        if line.startswith("diff --git"):
            # Extract file path
            match = re.search(r"diff --git a/(.+) b/", line)
            if match:
                changed_files.add(match.group(1))
        elif line.startswith("@@"):
            # Extract function name from context
            match = re.search(r"@@ .* @@ (.+)", line)
            if match:
                changed_functions.add(match.group(1).strip())
    
    return changed_files, changed_functions


def load_test_suite(path):
    with open(path) as f:
        return json.load(f)


def select_tests(changed_files, changed_functions, test_suite):
    """Select tests based on code changes."""
    selected = []
    
    for test in test_suite:
        # Direct match: test targets changed file
        test_targets = test.get("target_files", [])
        for target in test_targets:
            if any(target in f for f in changed_files):
                selected.append(test)
                break
        
        # Module match: test module matches changed file directory
        test_module = test.get("module", "")
        for f in changed_files:
            if test_module in f:
                selected.append(test)
                break
        
        # Function match: test covers changed function
        test_functions = test.get("target_functions", [])
        for func in changed_functions:
            if any(func in tf for tf in test_functions):
                selected.append(test)
                break
    
    # Remove duplicates while preserving order
    seen = set()
    unique_selected = []
    for test in selected:
        tid = test.get("id")
        if tid not in seen:
            seen.add(tid)
            unique_selected.append(test)
    
    return unique_selected


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--diff", required=True, help="Git diff text file")
    parser.add_argument("--test-suite", required=True, help="Test suite JSON")
    parser.add_argument("--output", required=True, help="Output selected tests JSON")
    args = parser.parse_args()
    
    with open(args.diff) as f:
        diff_text = f.read()
    
    changed_files, changed_functions = parse_diff(diff_text)
    test_suite = load_test_suite(args.test_suite)
    
    selected = select_tests(changed_files, changed_functions, test_suite)
    
    print(f"Changed files: {len(changed_files)}")
    print(f"Changed functions: {len(changed_functions)}")
    print(f"Total tests: {len(test_suite)}")
    print(f"Selected tests: {len(selected)}")
    print(f"Reduction: {(1 - len(selected)/len(test_suite))*100:.1f}%")
    
    with open(args.output, "w") as f:
        json.dump(selected, f, indent=2)


if __name__ == "__main__":
    main()
