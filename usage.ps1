# Risk App API Usage Examples - PowerShell Version
# Demonstrates how to retrieve document content by tag and save as CSV/XLSX files

param(
    [Parameter(Position = 0)]
    [string]$Command,
    
    [Parameter(Position = 1)]
    [string]$Tag,
    
    [Parameter(Position = 2)]
    [string]$OutputFile
)

$ApiBase = "http://localhost:8000"

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Show-Usage {
    Write-ColorOutput "Risk App API Usage Examples" "Cyan"
    Write-Host ""
    Write-Host "Usage: .\usage.ps1 [COMMAND] [OPTIONS]"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  list-docs              List all documents"
    Write-Host "  get-by-tag TAG [FILE]  Get document by tag and save as file"
    Write-Host "  examples               Show usage examples"
    Write-Host ""
    Write-Host "Options for get-by-tag:"
    Write-Host "  TAG                    Document tag to search for"
    Write-Host "  FILE                   Output filename (optional, defaults to TAG.csv)"
    Write-Host "                        Supports .csv and .xlsx extensions"
    Write-Host "                        If no path specified, saves to current directory"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\usage.ps1 get-by-tag YOUR_TAG"
    Write-Host "  .\usage.ps1 get-by-tag YOUR_TAG data.csv"
    Write-Host "  .\usage.ps1 get-by-tag YOUR_TAG C:\path\to\output.xlsx"
    Write-Host "  .\usage.ps1 examples"
}

function Test-Dependencies {
    # Check if ImportExcel module is available for XLSX support
    if (-not (Get-Module -ListAvailable -Name ImportExcel -ErrorAction SilentlyContinue)) {
        Write-ColorOutput "Note: ImportExcel module not found. XLSX export will be limited." "Yellow"
        Write-Host "Install with: Install-Module -Name ImportExcel -Scope CurrentUser"
        return $false
    }
    return $true
}

function Get-AllDocuments {
    Write-ColorOutput "Fetching all documents..." "Cyan"
    
    try {
        $response = Invoke-WebRequest -Uri "$ApiBase/documents" -Headers @{"Accept" = "application/json"} -ErrorAction Stop
        
        if ($response.StatusCode -eq 200) {
            Write-ColorOutput "Documents found:" "Green"
            $documents = $response.Content | ConvertFrom-Json
            
            foreach ($doc in $documents) {
                Write-Host "Tag: $($doc.tag), File: $($doc.filename), Type: $($doc.file_type)"
            }
        }
    }
    catch {
        Write-ColorOutput "Error: $($_.Exception.Message)" "Red"
        Write-Host $_.Exception.Response.StatusCode
    }
}

function Get-DocumentByTag {
    param(
        [string]$Tag,
        [string]$OutputFile
    )
    
    if (-not $Tag) {
        Write-ColorOutput "Error: Tag is required" "Red"
        Show-Usage
        exit 1
    }
    
    # Default filename if not provided
    if (-not $OutputFile) {
        $OutputFile = "$Tag.csv"
    }
    
    # Get file extension
    $extension = [System.IO.Path]::GetExtension($OutputFile).ToLower()
    
    # Validate extension
    if ($extension -notin @(".csv", ".xlsx")) {
        Write-ColorOutput "Warning: Unsupported extension '$extension'. Supported: .csv, .xlsx" "Yellow"
        Write-Host "Proceeding anyway..."
    }
    
    # Create directory if path is specified
    $outputDir = [System.IO.Path]::GetDirectoryName($OutputFile)
    if ($outputDir -and -not (Test-Path $outputDir)) {
        Write-ColorOutput "Creating directory: $outputDir" "Cyan"
        New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    }
    
    Write-ColorOutput "Fetching document with tag: $Tag" "Cyan"
    
    try {
        $response = Invoke-WebRequest -Uri "$ApiBase/documents/tag/$Tag" -Headers @{"Accept" = "application/json"} -ErrorAction Stop
        
        if ($response.StatusCode -eq 200) {
            Write-ColorOutput "Document found successfully" "Green"
            
            $documentData = $response.Content | ConvertFrom-Json
            $document = $documentData[0]
            
            Write-ColorOutput "Document Info:" "Cyan"
            Write-Host "  Original File: $($document.filename)"
            Write-Host "  File Type: $($document.file_type)"
            Write-Host "  Data Rows: $($document.data.Count)"
            Write-Host "  Validation Errors: $($document.error_count)"
            Write-Host ""
            
            # Save data based on file type
            switch ($extension) {
                ".csv" { Save-AsCsv -Document $document -OutputFile $OutputFile }
                ".xlsx" { Save-AsXlsx -Document $document -OutputFile $OutputFile }
                default { 
                    $response.Content | Out-File -FilePath $OutputFile -Encoding UTF8
                    Write-ColorOutput "Raw JSON saved to: $OutputFile" "Green"
                }
            }
        }
    }
    catch {
        if ($_.Exception.Response.StatusCode -eq 404) {
            Write-ColorOutput "Error: No document found with tag '$Tag'" "Red"
        }
        else {
            Write-ColorOutput "Error: $($_.Exception.Message)" "Red"
            Write-Host $_.Exception.Response.StatusCode
        }
        exit 1
    }
}

function Save-AsCsv {
    param(
        [PSCustomObject]$Document,
        [string]$OutputFile
    )
    
    Write-ColorOutput "Converting to CSV format..." "Cyan"
    
    if (-not $Document.data -or $Document.data.Count -eq 0) {
        Write-ColorOutput "Warning: No data found in document" "Yellow"
        # Create basic info CSV
        $basicInfo = [PSCustomObject]@{
            tag = $Document.tag
            filename = $Document.filename
            file_type = $Document.file_type
            error_count = $Document.error_count
        }
        $basicInfo | Export-Csv -Path $OutputFile -NoTypeInformation
    }
    else {
        # Convert data array to CSV
        $Document.data | Export-Csv -Path $OutputFile -NoTypeInformation
    }
    
    $rowCount = (Get-Content $OutputFile).Count
    Write-ColorOutput "CSV saved successfully to: $OutputFile" "Green"
    Write-Host "  Rows: $rowCount (including header)"
}

function Save-AsXlsx {
    param(
        [PSCustomObject]$Document,
        [string]$OutputFile
    )
    
    Write-ColorOutput "Converting to XLSX format..." "Cyan"
    
    # Check if ImportExcel module is available
    if (Get-Module -ListAvailable -Name ImportExcel -ErrorAction SilentlyContinue) {
        Import-Module ImportExcel -ErrorAction Stop
        
        if (-not $Document.data -or $Document.data.Count -eq 0) {
            Write-ColorOutput "Warning: No data found in document" "Yellow"
            # Create basic info XLSX
            $basicInfo = [PSCustomObject]@{
                tag = $Document.tag
                filename = $Document.filename
                file_type = $Document.file_type
                error_count = $Document.error_count
            }
            $basicInfo | Export-Excel -Path $OutputFile -AutoSize
        }
        else {
            # Convert data array to XLSX
            $Document.data | Export-Excel -Path $OutputFile -AutoSize
        }
        
        Write-ColorOutput "XLSX saved successfully to: $OutputFile" "Green"
    }
    else {
        Write-ColorOutput "ImportExcel module not available. Saving as CSV instead..." "Yellow"
        $csvFile = [System.IO.Path]::ChangeExtension($OutputFile, ".csv")
        Save-AsCsv -Document $Document -OutputFile $csvFile
        
        Write-ColorOutput "Install ImportExcel module for XLSX support:" "Yellow"
        Write-Host "  Install-Module -Name ImportExcel -Scope CurrentUser"
    }
}

function Show-Examples {
    Write-ColorOutput "Risk App API Usage Examples" "Cyan"
    Write-Host ""
    
    Write-ColorOutput "1. List all available documents:" "Green"
    Write-Host "   .\usage.ps1 list-docs"
    Write-Host ""
    
    Write-ColorOutput "2. Get document by tag (save as CSV in current directory):" "Green"
    Write-Host "   .\usage.ps1 get-by-tag YOUR_TAG"
    Write-Host "   Output: YOUR_TAG.csv"
    Write-Host ""
    
    Write-ColorOutput "3. Get document and save with custom filename:" "Green"
    Write-Host "   .\usage.ps1 get-by-tag YOUR_TAG my_data.csv"
    Write-Host "   Output: my_data.csv"
    Write-Host ""
    
    Write-ColorOutput "4. Save to specific directory:" "Green"
    Write-Host "   .\usage.ps1 get-by-tag YOUR_TAG C:\path\to\data\output.csv"
    Write-Host "   Output: C:\path\to\data\output.csv"
    Write-Host ""
    
    Write-ColorOutput "5. Save as Excel file:" "Green"
    Write-Host "   .\usage.ps1 get-by-tag YOUR_TAG data.xlsx"
    Write-Host "   Note: Requires ImportExcel module"
    Write-Host ""
    
    Write-ColorOutput "6. Direct API calls using PowerShell:" "Green"
    Write-Host "   # List documents"
    Write-Host "   Invoke-WebRequest -Uri '$ApiBase/documents' -Headers @{'Accept'='application/json'}"
    Write-Host ""
    Write-Host "   # Get by tag"
    Write-Host "   Invoke-WebRequest -Uri '$ApiBase/documents/tag/YOUR_TAG' -Headers @{'Accept'='application/json'}"
    Write-Host ""
    Write-Host "   # Save response to file"
    Write-Host "   `$response = Invoke-WebRequest -Uri '$ApiBase/documents/tag/YOUR_TAG' -Headers @{'Accept'='application/json'}"
    Write-Host "   `$response.Content | Out-File -FilePath 'output.json' -Encoding UTF8"
    Write-Host ""
    
    Write-ColorOutput "Bash equivalent (Linux/macOS):" "Cyan"
    Write-Host "   # List documents"
    Write-Host "   curl -H 'Accept: application/json' '$ApiBase/documents'"
    Write-Host ""
    Write-Host "   # Get by tag and save"
    Write-Host "   curl -H 'Accept: application/json' '$ApiBase/documents/tag/YOUR_TAG' -o output.json"
    Write-Host ""
}

# Main script logic
switch ($Command) {
    "list-docs" {
        Get-AllDocuments
    }
    "get-by-tag" {
        Get-DocumentByTag -Tag $Tag -OutputFile $OutputFile
    }
    "examples" {
        Show-Examples
    }
    default {
        if ($Command) {
            Write-ColorOutput "Unknown command: $Command" "Red"
        }
        Show-Usage
        if ($Command -and $Command -ne "help") {
            exit 1
        }
    }
}