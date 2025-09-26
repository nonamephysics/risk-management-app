#!/bin/bash

# Risk App API Usage Examples
# Demonstrates how to retrieve and save document content by tag and save as CSV/XLSX files

API_BASE="http://localhost:8000"
CURL_CMD="curl"  # Default, will be set by check_dependencies
AUTH_TOKEN=""    # Authentication token

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_usage() {
    echo -e "${BLUE}Risk App API Usage Examples${NC}"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  auth TOKEN             Set authentication token"
    echo "  list-docs              List all documents"
    echo "  get-by-tag TAG [FILE]  Get document by tag and save as file"
    echo "  examples               Show usage examples"
    echo ""
    echo "Authentication:"
    echo "  All operations require authentication. Set token with:"
    echo "  $0 auth YOUR_SECURITY_CODE"
    echo "  Or set RISK_APP_TOKEN environment variable"
    echo ""
    echo "Options for get-by-tag:"
    echo "  TAG                    Document tag to search for"
    echo "  FILE                   Output filename (optional, defaults to TAG.csv)"
    echo "                        Supports .csv and .xlsx extensions"
    echo "                        If no path specified, saves to current directory"
    echo ""
    echo "Examples:"
    echo "  $0 auth mySecurityCode123"
    echo "  $0 list-docs"
    echo "  $0 get-by-tag YOUR_TAG"
    echo "  $0 get-by-tag YOUR_TAG data.csv"
    echo "  $0 get-by-tag YOUR_TAG /path/to/output.xlsx"
    echo "  $0 examples"
}

check_dependencies() {
    # Check if curl is available (prefer curl.exe on Windows)
    if command -v curl.exe &> /dev/null; then
        CURL_CMD="curl.exe"
    elif command -v curl &> /dev/null; then
        CURL_CMD="curl"
    else
        echo -e "${RED}Error: curl is required but not installed.${NC}"
        exit 1
    fi

    # Check available JSON processing tools (in order of preference)
    if command -v python3 &> /dev/null; then
        echo -e "${GREEN}✓ Python 3 available - will use for optimal CSV conversion${NC}" >&2
    elif command -v node &> /dev/null; then
        echo -e "${BLUE}✓ Node.js available - will use for CSV conversion${NC}" >&2
    else
        echo -e "${YELLOW}⚠ No Python/Node.js found - will use basic shell extraction${NC}" >&2
        echo -e "${YELLOW}  For best results, install Python 3 or Node.js${NC}" >&2
    fi
    return 0
}

get_auth_token() {
    # Check if token is set in current session
    if [ -n "$AUTH_TOKEN" ]; then
        echo "$AUTH_TOKEN"
        return
    fi
    
    # Check environment variable
    if [ -n "$RISK_APP_TOKEN" ]; then
        echo "$RISK_APP_TOKEN"
        return
    fi
    
    # Check token file
    local token_file="$HOME/.risk_app_token"
    if [ -f "$token_file" ]; then
        local stored_token=$(cat "$token_file" 2>/dev/null)
        if [ -n "$stored_token" ]; then
            echo "$stored_token"
            return
        fi
    fi
    
    # No token found
    echo ""
}

check_authentication() {
    local token=$(get_auth_token)
    if [ -z "$token" ]; then
        echo -e "${RED}Error: Authentication required.${NC}"
        echo "Set authentication token with:"
        echo "  $0 auth YOUR_SECURITY_CODE"
        echo "Or set environment variable:"
        echo "  export RISK_APP_TOKEN=YOUR_SECURITY_CODE"
        exit 1
    fi
}

authenticate_user() {
    local security_code="$1"
    
    if [ -z "$security_code" ]; then
        echo -e "${RED}Error: Security code is required${NC}"
        print_usage
        exit 1
    fi
    
    echo -e "${BLUE}Authenticating with security code...${NC}"
    
    # Initialize curl command
    check_dependencies > /dev/null 2>&1 || true
    
    # Get JWT token from auth endpoint
    response=$($CURL_CMD -s -w "%{http_code}" -X POST \
        -H "Accept: application/json" \
        -H "Content-Type: application/json" \
        -d "{\"security_code\": \"$security_code\"}" \
        "$API_BASE/auth/login")
    
    http_code="${response: -3}"
    body="${response%???}"
    
    if [ "$http_code" -eq 200 ]; then
        # Extract access token from JSON response using sed
        AUTH_TOKEN=$(echo "$body" | sed -n 's/.*"access_token":"\([^"]*\)".*/\1/p')
        
        if [ -z "$AUTH_TOKEN" ]; then
            echo -e "${RED}Error: Failed to extract token from response${NC}"
            echo "Response: $body"
            exit 1
        fi
        
        echo -e "${GREEN}Authentication successful!${NC}"
        
        # Save token to file for persistent authentication
        local token_file="$HOME/.risk_app_token"
        echo "$AUTH_TOKEN" > "$token_file" 2>/dev/null || {
            echo -e "${YELLOW}Warning: Could not save token to file. Authentication will only persist for this session.${NC}"
        }
        
        echo "Token acquired and saved for future use."
        echo "Authentication will persist across script runs."
        echo ""
        echo "Alternative methods:"
        echo "  - Set environment variable: export RISK_APP_TOKEN=$AUTH_TOKEN"
        echo "  - Or re-run: $0 auth YOUR_SECURITY_CODE"
        return 0
    else
        echo -e "${RED}Authentication failed (HTTP $http_code)${NC}"
        if [ "$http_code" -eq 401 ]; then
            echo "Invalid security code. Please check your credentials."
        elif [ "$http_code" -eq 422 ]; then
            echo "Invalid request format. Please check the security code."
        else
            echo "Response: $body"
        fi
        exit 1
    fi
}

list_documents() {
    check_authentication
    
    echo -e "${BLUE}Fetching all documents...${NC}"
    
    # Initialize curl command
    check_dependencies > /dev/null 2>&1 || true
    
    local token=$(get_auth_token)
    response=$($CURL_CMD -s -w "%{http_code}" -H "Accept: application/json" -H "Authorization: Bearer $token" "$API_BASE/documents/")
    http_code="${response: -3}"
    body="${response%???}"
    
    if [ "$http_code" -eq 200 ]; then
        echo -e "${GREEN}Documents found:${NC}"
        if check_dependencies > /dev/null 2>&1; then
            echo "$body" | jq -r '.[] | "Tag: \(.tag), File: \(.filename), Type: \(.file_type)" + (if .created_by then ", Created by: " + (.created_by | gsub("user_"; "")) else "" end) + (if .updated_by then ", Updated by: " + (.updated_by | gsub("user_"; "")) else "" end)'
        else
            echo "$body"
        fi
    else
        echo -e "${RED}Error: HTTP $http_code${NC}"
        echo "$body"
    fi
}

get_document_by_tag() {
    local tag="$1"
    local output_file="$2"
    
    if [ -z "$tag" ]; then
        echo -e "${RED}Error: Tag is required${NC}"
        print_usage
        exit 1
    fi
    
    # Default filename if not provided
    if [ -z "$output_file" ]; then
        output_file="${tag}.csv"
    fi
    
    # Get file extension
    extension="${output_file##*.}"
    extension=$(echo "$extension" | tr '[:upper:]' '[:lower:]')
    
    # Validate extension
    if [ "$extension" != "csv" ] && [ "$extension" != "xlsx" ]; then
        echo -e "${YELLOW}Warning: Unsupported extension '$extension'. Supported: csv, xlsx${NC}"
        echo "Proceeding anyway..."
    fi
    
    check_authentication
    
    echo -e "${BLUE}Fetching document with tag: $tag${NC}"
    
    # Initialize curl command
    check_dependencies > /dev/null 2>&1 || true
    
    # Make API request first to check if document exists
    local token=$(get_auth_token)
    response=$($CURL_CMD -s -w "%{http_code}" -H "Accept: application/json" -H "Authorization: Bearer $token" "$API_BASE/documents/tag/$tag")
    http_code="${response: -3}"
    body="${response%???}"
    
    # Check for errors first, before creating any files or directories
    if [ "$http_code" -eq 404 ]; then
        echo -e "${RED}Error: No document found with tag '$tag'${NC}"
        echo "Available tags can be viewed with: $0 list-docs"
        exit 1
    elif [ "$http_code" -ne 200 ]; then
        echo -e "${RED}Error: Failed to fetch document (HTTP $http_code)${NC}"
        if [ "$http_code" -eq 401 ]; then
            echo "Authentication failed. Please re-authenticate with: $0 auth YOUR_SECURITY_CODE"
        else
            echo "Response: $body"
        fi
        exit 1
    fi
    
    # Check if response is empty array (no documents found with this tag)
    if [ "$body" = "[]" ] || [ "$body" = "null" ] || [ -z "$body" ]; then
        echo -e "${RED}Error: No document found with tag '$tag'${NC}"
        echo -e "${YELLOW}The specified tag does not exist in the system.${NC}"
        echo ""
        echo "To see all available documents and their tags, run:"
        echo "  $0 list-docs"
        echo ""
        echo "Make sure the tag name is spelled correctly and matches exactly."
        exit 1
    fi
    
    # Only create directory after confirming document exists
    output_dir=$(dirname "$output_file")
    if [ "$output_dir" != "." ] && [ ! -d "$output_dir" ]; then
        echo -e "${BLUE}Creating directory: $output_dir${NC}"
        mkdir -p "$output_dir" || {
            echo -e "${RED}Error: Failed to create directory '$output_dir'${NC}"
            exit 1
        }
    fi
    
    echo -e "${GREEN}Document found successfully${NC}"
    
    # Extract document info using sed and awk (works on all Unix systems)
    extract_json_field() {
        local json="$1"
        local field="$2"
        # Extract field value from JSON using sed and basic regex
        echo "$json" | sed -n 's/.*"'$field'":"\([^"]*\)".*/\1/p' | head -1
    }
    
    extract_json_number() {
        local json="$1"
        local field="$2"
        # Extract numeric field value from JSON
        echo "$json" | sed -n 's/.*"'$field'":\([0-9]*\).*/\1/p' | head -1
    }
    
    # Extract basic document metadata
    filename=$(extract_json_field "$body" "filename")
    file_type=$(extract_json_field "$body" "file_type")
    error_count=$(extract_json_number "$body" "error_count")
    created_by=$(extract_json_field "$body" "created_by")
    updated_by=$(extract_json_field "$body" "updated_by")
    
    # Set defaults if extraction failed
    filename=${filename:-"unknown"}
    file_type=${file_type:-"unknown"}
    error_count=${error_count:-"0"}
    
    echo -e "${BLUE}Document Info:${NC}"
    echo "  Original File: $filename"
    echo "  File Type: $file_type"
    echo "  Validation Errors: $error_count"
    if [ -n "$created_by" ] && [ "$created_by" != "null" ]; then
        echo "  Created by: ${created_by//user_/}"
    fi
    if [ -n "$updated_by" ] && [ "$updated_by" != "null" ]; then
        echo "  Updated by: ${updated_by//user_/}"
    fi
    echo ""
    
    # Try different JSON parsing approaches based on available tools
    if command -v python3 &> /dev/null; then
        # Use Python if available (most reliable)
        extract_csv_python "$body" "$output_file"
    elif command -v node &> /dev/null; then
        # Use Node.js if available
        extract_csv_node "$body" "$output_file"
    else
        # Use pure shell/sed/awk (basic extraction)
        extract_csv_shell "$body" "$output_file"
    fi
}

# Python-based CSV extraction (most reliable)
extract_csv_python() {
    local json_data="$1"
    local output_file="$2"
    
    echo -e "${BLUE}Using Python for CSV extraction...${NC}"
    
    # Save JSON to temporary file and process with Python
    temp_json="${output_file}.temp.json"
    echo "$json_data" > "$temp_json"
    
    python3 -c "
import json
import sys
import csv
import os

# Read JSON from temp file
temp_file = '$temp_json'
output_file = '$output_file'

try:
    with open(temp_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not data or len(data) == 0:
        print('Error: No document data found')
        sys.exit(1)
    
    doc = data[0]
    data_rows = doc.get('data', [])
    
    print(f'  Data Rows: {len(data_rows)}')
    
    # Save as CSV with proper headers and data
    if data_rows:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            if len(data_rows) > 0:
                # Get headers from first row
                headers = list(data_rows[0].keys())
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                writer.writerows(data_rows)
        
        print(f'✓ CSV saved successfully to: {output_file}')
        print(f'  Rows: {len(data_rows) + 1} (including header)')
    else:
        # Create empty CSV with just headers if no data
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['tag', 'filename', 'file_type', 'error_count'])
        print(f'Warning: No data rows found. Created empty CSV: {output_file}')
    
    # Clean up temp file
    os.remove(temp_file)
    
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
" || {
        echo -e "${RED}Error: Python CSV extraction failed${NC}"
        rm -f "$temp_json" 2>/dev/null
        extract_csv_shell "$json_data" "$output_file"
    }
}

# Node.js-based CSV extraction (alternative)
extract_csv_node() {
    local json_data="$1"
    local output_file="$2"
    
    echo -e "${BLUE}Using Node.js for CSV extraction...${NC}"
    
    # Save JSON to temporary file
    temp_json="${output_file}.temp.json"
    echo "$json_data" > "$temp_json"
    
    node -e "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('$temp_json', 'utf8'));

if (!data || data.length === 0) {
    console.log('Error: No document data found');
    process.exit(1);
}

const doc = data[0];
const dataRows = doc.data || [];

console.log(\`  Data Rows: \${dataRows.length}\`);

if (dataRows.length > 0) {
    // Get headers from first row
    const headers = Object.keys(dataRows[0]);
    
    // Create CSV content
    let csvContent = headers.join(',') + '\\n';
    
    dataRows.forEach(row => {
        const values = headers.map(header => {
            let value = row[header] || '';
            // Escape quotes and wrap in quotes if contains comma or quote
            if (typeof value === 'string' && (value.includes(',') || value.includes('\"') || value.includes('\\n'))) {
                value = '\"' + value.replace(/\"/g, '\"\"') + '\"';
            }
            return value;
        });
        csvContent += values.join(',') + '\\n';
    });
    
    fs.writeFileSync('$output_file', csvContent, 'utf8');
    console.log(\`✓ CSV saved successfully to: $output_file\`);
    console.log(\`  Rows: \${dataRows.length + 1} (including header)\`);
} else {
    fs.writeFileSync('$output_file', 'tag,filename,file_type,error_count\\n', 'utf8');
    console.log('Warning: No data rows found. Created empty CSV: $output_file');
}

// Clean up temp file
fs.unlinkSync('$temp_json');
" || {
        echo -e "${RED}Error: Node.js CSV extraction failed${NC}"
        rm -f "$temp_json" 2>/dev/null
        extract_csv_shell "$json_data" "$output_file"
    }
}

# Shell-based CSV extraction using sed/awk (works everywhere)
extract_csv_shell() {
    local json_data="$1"
    local output_file="$2"
    
    echo -e "${BLUE}Using shell tools for CSV extraction...${NC}"
    echo -e "${YELLOW}Note: Basic extraction - complex CSV data may not be perfectly formatted${NC}"
    
    # Extract the data array from JSON using sed
    # This is a basic approach that works for simple JSON structures
    data_section=$(echo "$json_data" | sed -n 's/.*"data":\[\(.*\)\],"validation_errors".*/\1/p')
    
    if [ -z "$data_section" ] || [ "$data_section" = "null" ]; then
        echo "Warning: No data section found or data is empty"
        echo "tag,filename,file_type,error_count" > "$output_file"
        echo -e "${YELLOW}Created empty CSV: $output_file${NC}"
        return
    fi
    
    # Try to extract headers from first object
    # Look for the first JSON object in the data array
    first_object=$(echo "$data_section" | sed 's/^[[:space:]]*,//' | sed -n 's/^\({[^}]*}\).*/\1/p' | head -1)
    
    if [ -n "$first_object" ]; then
        # Extract field names as headers (basic approach)
        headers=$(echo "$first_object" | sed 's/[{}]//g' | sed 's/"[^"]*":[^,}]*/\n&/g' | grep ':' | sed 's/"\\([^"]*\\)":.*/\\1/' | tr '\\n' ',' | sed 's/,$//')
        
        if [ -n "$headers" ]; then
            echo "$headers" > "$output_file"
            echo -e "${GREEN}✓ CSV headers extracted: $output_file${NC}"
            echo "  Note: Data rows extraction requires Python or Node.js for proper formatting"
            echo "  Headers: $(echo "$headers" | tr ',' ' ' | wc -w) columns"
        else
            echo "tag,filename,file_type,error_count" > "$output_file"
            echo -e "${YELLOW}Could not extract headers. Created basic CSV: $output_file${NC}"
        fi
    else
        echo "tag,filename,file_type,error_count" > "$output_file"
        echo -e "${YELLOW}Could not parse data structure. Created basic CSV: $output_file${NC}"
    fi
}

show_examples() {
    echo -e "${BLUE}Risk App API Usage Examples${NC}"
    echo ""
    
    echo -e "${GREEN}1. Authentication (required first):${NC}"
    echo "   ./usage.sh auth mySecurityCode123"
    echo "   # Or set environment variable:"
    echo "   export RISK_APP_TOKEN=mySecurityCode123"
    echo ""
    
    echo -e "${GREEN}2. List all available documents:${NC}"
    echo "   ./usage.sh list-docs"
    echo ""
    
    echo -e "${GREEN}3. Get document by tag (save as CSV in current directory):${NC}"
    echo "   ./usage.sh get-by-tag YOUR_TAG"
    echo "   Output: YOUR_TAG.csv"
    echo ""
    
    echo -e "${GREEN}4. Get document and save with custom filename:${NC}"
    echo "   ./usage.sh get-by-tag YOUR_TAG my_data.csv"
    echo "   Output: my_data.csv"
    echo ""
    
    echo -e "${GREEN}5. Save to specific directory:${NC}"
    echo "   ./usage.sh get-by-tag YOUR_TAG /path/to/data/output.csv"
    echo "   Output: /path/to/data/output.csv"
    echo ""
    
    echo -e "${GREEN}6. CSV Extraction Support:${NC}"
    echo "   Works with Python 3, Node.js, or basic shell tools"
    echo "   • Python 3: Best quality CSV output with proper escaping"
    echo "   • Node.js: Good quality CSV output"
    echo "   • Shell only: Basic extraction (headers only, no complex data)"
    echo ""
    
    echo -e "${GREEN}7. Direct API calls using curl (with authentication):${NC}"
    echo "   # List documents"
    echo "   curl.exe -H 'Accept: application/json' -H 'Authorization: Bearer YOUR_TOKEN' '$API_BASE/documents/'"
    echo ""
    echo "   # Get by tag"
    echo "   curl.exe -H 'Accept: application/json' -H 'Authorization: Bearer YOUR_TOKEN' '$API_BASE/documents/tag/YOUR_TAG'"
    echo ""
    
    echo -e "${BLUE}PowerShell equivalent (Windows):${NC}"
    echo "   # List documents"
    echo "   \$headers = @{'accept'='application/json'; 'Authorization'='Bearer YOUR_TOKEN'}"
    echo "   Invoke-WebRequest -Uri '$API_BASE/documents' -Headers \$headers"
    echo ""
    echo "   # Get by tag and save"
    echo "   \$response = Invoke-WebRequest -Uri '$API_BASE/documents/tag/YOUR_TAG' -Headers \$headers"
    echo "   \$response.Content | Out-File -FilePath 'output.json'"
    echo ""
}

# Main script logic
main() {
    case "${1:-}" in
        "auth")
            if [ -z "$2" ]; then
                echo -e "${RED}Error: Please provide a security code${NC}"
                echo "Usage: $0 auth <security_code>"
                exit 1
            fi
            authenticate_user "$2"
            ;;
        "list-docs")
            check_authentication
            list_documents
            ;;
        "get-by-tag")
            check_authentication
            if [ -z "$2" ]; then
                echo -e "${RED}Error: Please provide a tag${NC}"
                echo "Usage: $0 get-by-tag <tag> [output_file]"
                exit 1
            fi
            get_document_by_tag "$2" "$3"
            ;;
        "examples")
            show_examples
            ;;
        "")
            print_usage
            ;;
        *)
            echo -e "${RED}Unknown command: $1${NC}"
            print_usage
            exit 1
            ;;
    esac
}

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi