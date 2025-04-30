#!/usr/bin/env python3
"""
Validate markdown references in documentation.

This script analyzes all markdown files in the documentation, extracts links,
and verifies that all references point to valid files.
"""

import os
import re
import argparse
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

# Regular expression to find markdown links
LINK_RE = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

# Extensions to ignore in reference validation
IGNORED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.svg'}

def find_all_markdown_files(base_dir: str) -> List[str]:
    """Find all .md files in the specified directory and its subdirectories."""
    md_files = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))
    return md_files

def normalize_path(path: str) -> str:
    """Normalize a path to handle edge cases in markdown references."""
    # Remove trailing / if present for directory links
    path = path.rstrip('/')
    # Remove any leading / which makes paths absolute
    path = path.lstrip('/')
    return path

def extract_links(file_path: str) -> List[Tuple[str, str, int]]:
    """Extract all markdown links from a file along with line numbers."""
    links = []
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for i, line in enumerate(lines, 1):
            for match in LINK_RE.finditer(line):
                link_text = match.group(1)
                link_target = match.group(2)
                links.append((link_text, link_target, i))
    return links

def is_external_link(link: str) -> bool:
    """Check if a link is an external URL."""
    return link.startswith(('http://', 'https://', 'ftp://', 'mailto:'))

def is_anchor_link(link: str) -> bool:
    """Check if a link is an anchor link within the same document."""
    return link.startswith('#')

def get_target_file_path(src_file: str, link: str, base_dir: str) -> str:
    """Resolve the file path from a relative link."""
    # Handle anchor links
    if is_anchor_link(link) or not link:
        return src_file
        
    # Parse the link to separate file and anchor
    file_part = link.split('#')[0]
    
    # Skip image files
    _, ext = os.path.splitext(file_part.lower())
    if ext in IGNORED_EXTENSIONS:
        return ""
    
    # Handle relative paths
    src_dir = os.path.dirname(src_file)
    if not file_part:
        # Empty link points to the current file
        target_path = src_file
    elif file_part.startswith('./'):
        # Link relative to current directory
        target_path = os.path.normpath(os.path.join(src_dir, file_part[2:]))
    elif file_part.startswith('../'):
        # Link going up one or more directories
        target_path = os.path.normpath(os.path.join(src_dir, file_part))
    else:
        # Link without ./ or ../ - needs special handling for documentation refs
        
        # First, treat as relative to source file directory
        relative_path = os.path.join(src_dir, file_part)
        if os.path.exists(relative_path):
            target_path = relative_path
        else:
            # If not found, try treating as relative to base directory
            target_path = os.path.join(base_dir, normalize_path(file_part))
    
    # Add .md extension if missing (common in documentation references)
    if not os.path.splitext(target_path)[1]:
        if os.path.exists(target_path + '.md'):
            target_path += '.md'
        elif os.path.isdir(target_path) and os.path.exists(os.path.join(target_path, 'README.md')):
            target_path = os.path.join(target_path, 'README.md')
    
    return target_path

def validate_links(files: List[str], base_dir: str) -> Dict[str, List[Tuple[str, str, int]]]:
    """Validate all links in the given files and return broken references."""
    broken_links = defaultdict(list)
    
    # Check that the base directory exists
    if not os.path.isdir(base_dir):
        print(f"Error: Base directory '{base_dir}' does not exist.")
        sys.exit(1)
    
    # First, build a set of all actual files for efficient lookups
    actual_files = set(os.path.abspath(f) for f in files)
    actual_dirs = set(os.path.abspath(os.path.dirname(f)) for f in files)
    
    # Track all links for analysis
    all_links = {}
    
    for file_path in files:
        links = extract_links(file_path)
        all_links[file_path] = links
        
        for link_text, link_target, line_num in links:
            # Skip external links, they're not validated in this script
            if is_external_link(link_target):
                continue
                
            # Skip pure anchor links within the current doc
            if is_anchor_link(link_target):
                continue
            
            # Skip image files
            _, ext = os.path.splitext(link_target.lower())
            if ext in IGNORED_EXTENSIONS:
                continue
            
            # Resolve the target file path
            target_path = get_target_file_path(file_path, link_target, base_dir)
            if not target_path:
                continue  # Skip ignored extensions
                
            # Check if the target exists
            target_abs_path = os.path.abspath(target_path)
            
            # The file might not have a .md extension in the link
            if not os.path.exists(target_abs_path):
                # Try with .md extension
                if not target_abs_path.endswith('.md'):
                    md_path = target_abs_path + '.md'
                    if os.path.exists(md_path):
                        target_abs_path = md_path
                        
            # Check for README.md in directory references
            if os.path.isdir(target_abs_path):
                readme_path = os.path.join(target_abs_path, 'README.md')
                if os.path.exists(readme_path):
                    target_abs_path = readme_path
            
            if not os.path.exists(target_abs_path):
                # Simplify paths for better readability in the output
                rel_src = os.path.relpath(file_path, base_dir)
                rel_target = link_target
                
                # Add to broken links
                broken_links[rel_src].append((link_text, rel_target, line_num))
    
    # Analyze all links to produce a reference map
    reference_map = analyze_references(all_links, base_dir)
    
    return broken_links, reference_map

def analyze_references(all_links: Dict[str, List[Tuple[str, str, int]]], base_dir: str) -> Dict[str, Set[str]]:
    """Analyze all references to create a map of which files reference which other files."""
    # Structure: {target_file: {source_file1, source_file2, ...}}
    references = defaultdict(set)
    
    for src_file, links in all_links.items():
        rel_src = os.path.relpath(src_file, base_dir)
        
        for _, link_target, _ in links:
            # Skip external and anchor links
            if is_external_link(link_target) or is_anchor_link(link_target):
                continue
                
            # Skip image files
            _, ext = os.path.splitext(link_target.lower())
            if ext in IGNORED_EXTENSIONS:
                continue
            
            # Resolve the target file path
            target_path = get_target_file_path(src_file, link_target, base_dir)
            if not target_path:
                continue  # Skip ignored extensions
                
            # Record the reference
            rel_target = os.path.relpath(target_path, base_dir)
            references[rel_target].add(rel_src)
    
    return references

def format_broken_links_report(broken_links: Dict[str, List[Tuple[str, str, int]]]) -> str:
    """Format the broken links into a readable report."""
    if not broken_links:
        return "No broken links found! ✅"
    
    report = ["# Broken Links Report\n"]
    report.append(f"Found {sum(len(links) for links in broken_links.values())} broken links in {len(broken_links)} files\n")
    
    for file, links in sorted(broken_links.items()):
        report.append(f"\n## {file}\n")
        for link_text, link_target, line_num in sorted(links, key=lambda x: x[2]):
            report.append(f"- Line {line_num}: [{link_text}]({link_target})")
    
    return "\n".join(report)

def format_reference_map_report(reference_map: Dict[str, Set[str]]) -> str:
    """Format the reference map into a readable report."""
    report = ["# Reference Map\n"]
    report.append("This shows which files are referenced by other files.\n")
    
    # First, collect all unique targets
    all_targets = set(reference_map.keys())
    
    # Get unreferenced files
    unreferenced = []
    for target in sorted(all_targets):
        if not reference_map[target]:
            unreferenced.append(target)
    
    # Add most referenced files
    most_referenced = sorted(
        [(target, len(sources)) for target, sources in reference_map.items() if sources],
        key=lambda x: x[1],
        reverse=True
    )
    
    if most_referenced:
        report.append("\n## Most Referenced Files\n")
        for target, count in most_referenced[:10]:  # Top 10
            report.append(f"- {target}: {count} references")
    
    if unreferenced:
        report.append("\n## Unreferenced Files\n")
        report.append("These files are not referenced by any other file:\n")
        for target in unreferenced:
            report.append(f"- {target}")
    
    # Detailed reference map
    report.append("\n## Detailed Reference Map\n")
    for target in sorted(all_targets):
        sources = reference_map[target]
        if sources:
            report.append(f"\n### {target}\n")
            report.append("Referenced by:\n")
            for source in sorted(sources):
                report.append(f"- {source}")
    
    return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="Validate markdown references in documentation")
    parser.add_argument('--base-dir', default='.', help='Base directory for documentation')
    parser.add_argument('--output', default='reference_validation_report.md', help='Output file for the validation report')
    args = parser.parse_args()
    
    base_dir = os.path.abspath(args.base_dir)
    output_file = args.output
    
    print(f"Scanning markdown files in {base_dir}...")
    md_files = find_all_markdown_files(base_dir)
    print(f"Found {len(md_files)} markdown files")
    
    print("Validating links...")
    broken_links, reference_map = validate_links(md_files, base_dir)
    
    # Generate reports
    broken_links_report = format_broken_links_report(broken_links)
    reference_map_report = format_reference_map_report(reference_map)
    
    # Combined report
    full_report = f"""# Reference Validation Report

## Summary

- **Total Files Analyzed**: {len(md_files)}
- **Files with Broken Links**: {len(broken_links)}
- **Total Broken Links**: {sum(len(links) for links in broken_links.values())}

{broken_links_report}

---

{reference_map_report}
"""
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_report)
    
    print(f"Report written to {output_file}")
    
    # Print summary to console
    if broken_links:
        print(f"⚠️  Found {sum(len(links) for links in broken_links.values())} broken links in {len(broken_links)} files")
        return 1
    else:
        print("✅ No broken links found")
        return 0

if __name__ == "__main__":
    sys.exit(main())