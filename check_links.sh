#!/bin/bash

# Directory containing the documentation
DOC_DIR="/Users/alexanderfedin/Projects/RevealDocsPlayground/tos/monotorrent-documentation"

# Output file for results
OUTPUT_FILE="$DOC_DIR/link_check_results.md"

# Clear previous results
echo "# Dangling References Report" > $OUTPUT_FILE
echo "" >> $OUTPUT_FILE
echo "## Missing Files Referenced in Documentation" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Function to check if a file exists
check_file_exists() {
  local target_file="$1"
  
  # Handle relative paths
  if [[ $target_file != /* ]]; then
    # Get the directory of the source file
    local source_dir=$(dirname "$2")
    target_file="$source_dir/$target_file"
  fi
  
  # Normalize path
  target_file=$(realpath -m "$target_file")
  
  # Check if the file exists
  if [[ -f "$target_file" ]]; then
    return 0 # File exists
  else
    return 1 # File does not exist
  fi
}

# Find all Markdown files
find "$DOC_DIR" -type f -name "*.md" | while read -r source_file; do
  # Extract relative path for display
  relative_source=${source_file#$DOC_DIR/}
  
  # Use grep to find markdown links
  grep -o '\[[^]]*\]([^)^#^h][^)]*\)' "$source_file" | while read -r link; do
    # Extract the link text and target
    link_text=$(echo "$link" | sed -E 's/\[(.*)\]\(.*/\1/')
    link_target=$(echo "$link" | sed -E 's/\[.*\]\((.*)\)/\1/')
    
    # Skip external links (http, https, ftp)
    if [[ "$link_target" =~ ^(http|https|ftp): ]]; then
      continue
    fi
    
    # Skip anchor links
    if [[ "$link_target" =~ ^# ]]; then
      continue
    fi

    # Get line number and context
    line_number=$(grep -n "$link" "$source_file" | cut -d: -f1)
    context=$(grep -A 1 -B 1 "$link" "$source_file" | sed 's/^/    /')
    
    # Check if the target file exists
    if ! check_file_exists "$link_target" "$source_file"; then
      # If it doesn't end with .md, try adding it
      if [[ ! "$link_target" =~ \.md$ ]]; then
        if check_file_exists "${link_target}.md" "$source_file"; then
          continue # File exists with .md extension
        fi
      fi
      
      echo "### Source: $relative_source (Line $line_number)" >> $OUTPUT_FILE
      echo "" >> $OUTPUT_FILE
      echo "Missing target: \`$link_target\`" >> $OUTPUT_FILE
      echo "" >> $OUTPUT_FILE
      echo "Link text: \"$link_text\"" >> $OUTPUT_FILE
      echo "" >> $OUTPUT_FILE
      echo "Context:" >> $OUTPUT_FILE
      echo '```' >> $OUTPUT_FILE
      echo "$context" >> $OUTPUT_FILE
      echo '```' >> $OUTPUT_FILE
      echo "" >> $OUTPUT_FILE
    fi
  done
done

echo "## Potential Missing API Documentation" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE
echo "Classes mentioned but without dedicated documentation files:" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Find all class names mentioned in the docs
find "$DOC_DIR" -type f -name "*.md" | xargs grep -o '\b[A-Z][a-zA-Z0-9]*\b' | sort | uniq | while read -r class_name; do
  # Check if the class name appears to be a valid class (not just a capitalized word)
  if [[ "$class_name" =~ ^[A-Z][a-zA-Z0-9]{2,}$ && ! "$class_name" =~ ^(The|This|API|README|MD|BitTorrent|MonoTorrent)$ ]]; then
    # Check if there's a corresponding MD file
    if ! find "$DOC_DIR" -type f -name "${class_name}.md" | grep -q .; then
      # Count occurrences to filter out rare mentions
      count=$(find "$DOC_DIR" -type f -name "*.md" | xargs grep -o "\b$class_name\b" | wc -l)
      if [ $count -gt 2 ]; then
        echo "- **$class_name** (mentioned $count times)" >> $OUTPUT_FILE
      fi
    fi
  fi
done

echo "Link checking completed. Results saved to $OUTPUT_FILE"