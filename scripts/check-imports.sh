#!/bin/bash

# Import analysis script for Python, JavaScript, and TypeScript files
# Outputs CSV to audit/imports.csv and console summary

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Output file
OUTPUT_CSV="audit/imports.csv"
mkdir -p audit

# Initialize counters
total_imports=0
ok_count=0
missing_count=0
ambiguous_count=0

# Write CSV header
echo "calling_file,referenced_path,resolved_absolute_path,status" > "$OUTPUT_CSV"

# Function to resolve Python import
resolve_python_import() {
    local calling_file="$1"
    local import_path="$2"
    local calling_dir
    calling_dir=$(dirname "$calling_file")

    # Use Python to resolve the import path
    python3 -c "
import sys
import os
sys.path.insert(0, '$calling_dir')
try:
    # Try to import the module
    __import__('$import_path')
    # If successful, get the module file path
    module = sys.modules['$import_path']
    if hasattr(module, '__file__') and module.__file__:
        print(module.__file__)
    else:
        print('OK')  # Built-in or package
except ImportError:
    print('MISSING')
except Exception as e:
    print('AMBIGUOUS')
"
}

# Function to resolve JS/TS import
resolve_js_import() {
    local calling_file="$1"
    local import_path="$2"
    local calling_dir
    calling_dir=$(dirname "$calling_file")

    # For relative imports
    if [[ "$import_path" == ./* ]] || [[ "$import_path" == ../* ]]; then
        local resolved_path
        resolved_path=$(realpath -m "$calling_dir/$import_path" 2>/dev/null || echo "MISSING")
        if [[ -f "$resolved_path" ]]; then
            echo "$resolved_path"
        elif [[ -d "$resolved_path" ]] && [[ -f "$resolved_path/index.js" ]]; then
            echo "$resolved_path/index.js"
        elif [[ -d "$resolved_path" ]] && [[ -f "$resolved_path/index.ts" ]]; then
            echo "$resolved_path/index.ts"
        else
            echo "MISSING"
        fi
    else
        # For absolute imports or node_modules, assume OK if not relative
        echo "OK"
    fi
}

# Find all relevant files
find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.ts" \) \
    -not -path "*/.venv/*" \
    -not -path "*/node_modules/*" \
    -not -path "*/__pycache__/*" \
    -not -path "*/.git/*" \
    -not -path "*/.cache/*" \
    -not -path "*/.ruff_cache/*" \
    -print0 | while IFS= read -r -d '' file; do

    echo "Analyzing $file"

    # Python files
    if [[ "$file" == *.py ]]; then
        # Find import statements
        grep -n "^[[:space:]]*import \|^[[:space:]]*from " "$file" | while IFS=: read -r line_num import_line; do
            # Extract module name using sed
            module=$(echo "$import_line" | sed -n 's/^import\s*\([^[:space:]]*\).*/\1/p')
            if [[ -z "$module" ]]; then
                module=$(echo "$import_line" | sed -n 's/^from\s*\([^[:space:]]*\)\s*import.*/\1/p')
            fi
            # Remove as alias if present
            module=$(echo "$module" | sed 's/ as .*//')

            if [[ -n "$module" ]]; then
                ((total_imports++))
                resolved=$(resolve_python_import "$file" "$module")
                if [[ "$resolved" == "OK" ]]; then
                    status="OK"
                    ((ok_count++))
                elif [[ "$resolved" == "MISSING" ]]; then
                    status="MISSING"
                    ((missing_count++))
                elif [[ "$resolved" == "AMBIGUOUS" ]]; then
                    status="AMBIGUOUS"
                    ((ambiguous_count++))
                else
                    status="OK"
                    ((ok_count++))
                fi
                echo "$file,$module,$resolved,$status" >> "$OUTPUT_CSV"
            fi
        done
    fi

    # JS/TS files
    if [[ "$file" == *.js ]] || [[ "$file" == *.ts ]]; then
        # Find import statements
        grep -n "^[[:space:]]*import \|^[[:space:]]*const.*require(" "$file" | while IFS=: read -r line_num import_line; do
            # Extract import path using sed
            import_path=$(echo "$import_line" | sed -n 's/.*from\s*['\''"]\([^'\''"]*\)['\''"].*/\1/p')
            if [[ -z "$import_path" ]]; then
                import_path=$(echo "$import_line" | sed -n 's/.*require\s*(\s*['\''"]\([^'\''"]*\)['\''"].*/\1/p')
            fi

            if [[ -n "$import_path" ]]; then
                ((total_imports++))
                resolved=$(resolve_js_import "$file" "$import_path")
                if [[ "$resolved" == "OK" ]]; then
                    status="OK"
                    ((ok_count++))
                elif [[ "$resolved" == "MISSING" ]]; then
                    status="MISSING"
                    ((missing_count++))
                else
                    status="OK"
                    ((ok_count++))
                fi
                echo "$file,$import_path,$resolved,$status" >> "$OUTPUT_CSV"
            fi
        done
    fi
done

# Print summary
echo -e "\n${GREEN}Import Analysis Summary:${NC}"
echo "Total imports analyzed: $total_imports"
echo -e "${GREEN}OK: $ok_count${NC}"
echo -e "${RED}MISSING: $missing_count${NC}"
echo -e "${YELLOW}AMBIGUOUS: $ambiguous_count${NC}"
echo "Results saved to $OUTPUT_CSV"