#!/usr/bin/env bash
# Compress all Python source files of MetaboMind into a ZIP archive
# Usage: ./zip_sources.sh [output.zip]

set -euo pipefail

out_file="${1:-metabomind_sources.zip}"

# Find all .py files excluding __pycache__ directories and feed them to zip
find . -type d -name '__pycache__' -prune -o -name '*.py' -print | zip -@ "$out_file"

echo "Created $out_file"
