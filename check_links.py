#!/usr/bin/env python3

import os
import re
import glob
from pathlib import Path
from collections import defaultdict

# Directory containing the documentation
DOC_DIR = "/Users/alexanderfedin/Projects/RevealDocsPlayground/tos/monotorrent-documentation"

# Output file for results
OUTPUT_FILE = os.path.join(DOC_DIR, "link_check_results.md")

# Regular expression for markdown links
LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

# Class name pattern (capitalized words that might be class names)
CLASS_PATTERN = re.compile(r'\b[A-Z][a-zA-Z0-9]{2,}\b')

# Words to exclude as they are likely not class names
EXCLUDE_WORDS = {
    'README', 'The', 'This', 'API', 'MD', 'BitTorrent', 'MonoTorrent', 
    'NOTE', 'COMPLETE', 'Documentation', 'HTTP', 'TODO', 'Overview',
    'Installation', 'Configuration', 'Components', 'Related'
}

def is_internal_link(link):
    """Check if a link is internal (not external or anchor)."""
    return not (link.startswith(('http:', 'https:', 'ftp:', '#')))

def resolve_path(target, source_path):
    """Resolve a relative path based on source file location."""
    if target.startswith('/'):
        return os.path.normpath(os.path.join(DOC_DIR, target.lstrip('/')))
    
    source_dir = os.path.dirname(source_path)
    return os.path.normpath(os.path.join(source_dir, target))

def check_file_exists(target, source_path):
    """Check if target file exists, considering .md extension if missing."""
    resolved_path = resolve_path(target, source_path)
    
    # Check if file exists as-is
    if os.path.isfile(resolved_path):
        return True
    
    # If no extension, try adding .md
    if not os.path.splitext(resolved_path)[1]:
        md_path = resolved_path + '.md'
        return os.path.isfile(md_path)
    
    return False

def get_file_context(file_path, link_text, num_lines=1):
    """Get context around a link in a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    context = []
    for i, line in enumerate(lines):
        if link_text in line:
            start = max(0, i - num_lines)
            end = min(len(lines), i + num_lines + 1)
            context.append(''.join([f"    {lines[j]}" for j in range(start, end)]))
    
    return context

def main():
    # Dictionary to store dangling references
    dangling_refs = []
    
    # Set to store all existing markdown files
    existing_files = set()
    for md_file in glob.glob(os.path.join(DOC_DIR, "**/*.md"), recursive=True):
        existing_files.add(os.path.normpath(md_file))
    
    # Process each markdown file
    for file_path in existing_files:
        relative_path = os.path.relpath(file_path, DOC_DIR)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all markdown links
        for match in LINK_PATTERN.finditer(content):
            link_text = match.group(1)
            link_target = match.group(2)
            
            # Check if it's an internal link
            if is_internal_link(link_target):
                if not check_file_exists(link_target, file_path):
                    context = get_file_context(file_path, match.group(0))
                    dangling_refs.append({
                        'source': relative_path,
                        'target': link_target,
                        'text': link_text,
                        'context': context
                    })
    
    # Find potential missing API documentation
    class_mentions = defaultdict(int)
    for file_path in existing_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find potential class names
        for match in CLASS_PATTERN.finditer(content):
            class_name = match.group(0)
            if class_name not in EXCLUDE_WORDS:
                class_mentions[class_name] += 1
    
    # Filter to classes mentioned multiple times without documentation
    missing_classes = []
    for class_name, count in class_mentions.items():
        if count > 2:
            # Check if a corresponding MD file exists
            if not any(os.path.basename(f) == f"{class_name}.md" for f in existing_files):
                missing_classes.append((class_name, count))
    
    # Sort by mention count, descending
    missing_classes.sort(key=lambda x: x[1], reverse=True)
    
    # Write the report
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Dangling References Report\n\n")
        
        f.write("## Missing Files Referenced in Documentation\n\n")
        if dangling_refs:
            for ref in dangling_refs:
                f.write(f"### Source: {ref['source']}\n\n")
                f.write(f"Missing target: `{ref['target']}`\n\n")
                f.write(f"Link text: \"{ref['text']}\"\n\n")
                f.write("Context:\n```\n")
                for ctx in ref['context']:
                    f.write(f"{ctx}\n")
                f.write("```\n\n")
        else:
            f.write("No dangling references found.\n\n")
        
        f.write("## Potential Missing API Documentation\n\n")
        f.write("Classes mentioned but without dedicated documentation files:\n\n")
        if missing_classes:
            for class_name, count in missing_classes:
                f.write(f"- **{class_name}** (mentioned {count} times)\n")
        else:
            f.write("No potential missing API documentation identified.\n")
    
    print(f"Link checking completed. Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()