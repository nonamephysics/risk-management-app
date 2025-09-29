# 📊 File Format Support Documentation

## Overview

The Risk Management Application now supports multiple statistical and data file formats, making it suitable for pharmaceutical, research, and data analytics environments.

## Supported Formats

### ✅ Core Formats (Always Available)

#### CSV (Comma-Separated Values)
- **Extensions**: `.csv`
- **Encoding Support**: UTF-8, Latin-1, CP1252 (auto-detection)
- **Use Cases**: General data exchange, Excel exports, text-based data
- **Features**: Automatic encoding detection, delimiter handling

#### Excel Files
- **Extensions**: `.xlsx`, `.xls`
- **Libraries**: `openpyxl` for .xlsx, `xlrd` for .xls
- **Use Cases**: Spreadsheet data, formatted reports, business data
- **Features**: Multiple sheets, data types, formatted cells

### 📊 Statistical Formats (Optional Dependencies)

#### SAS7BDAT (SAS Dataset Files)
- **Extensions**: `.sas7bdat`
- **Library Required**: `sas7bdat` (installed) or `pyreadstat` (optional)
- **Use Cases**: Statistical analysis, pharmaceutical data, regulatory submissions
- **Features**: Variable labels, formats, metadata preservation

#### XPT (SAS Transport Files)
- **Extensions**: `.xpt`  
- **Library Required**: `pyreadstat` (requires C++ build tools)
- **Use Cases**: FDA submissions, regulatory compliance, data exchange
- **Features**: Standardized format, cross-platform compatibility

## Installation Requirements

### Basic Installation (CSV, Excel)
```bash
pip install pandas openpyxl
```

### SAS7BDAT Support
```bash
pip install sas7bdat
```

### Full Statistical Support (XPT + Enhanced SAS)
```bash
# Requires Microsoft C++ Build Tools
pip install pyreadstat
```

### Windows C++ Build Tools
For `pyreadstat` installation on Windows:
1. Download [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Install "C++ build tools" workload
3. Then install: `pip install pyreadstat`

## API Usage

### Upload Endpoint
```http
POST /documents/upload
Content-Type: multipart/form-data

file: [your_file.sas7bdat]
tag: "clinical_data_v1"
```

### Response Format
```json
{
  "message": "File uploaded successfully",
  "document_id": "507f1f77bcf86cd799439011",
  "filename": "clinical_data.sas7bdat",
  "file_type": "sas7bdat",
  "rows_processed": 1250,
  "columns": ["USUBJID", "AGE", "SEX", "RACE", "VISIT"],
  "has_errors": false,
  "validation_errors": []
}
```

## Frontend Integration

### File Input Configuration
```html
<input 
  type="file" 
  accept=".csv,.xlsx,.xls,.sas7bdat,.xpt"
  onChange={handleFileChange}
/>
```

### JavaScript Validation
```javascript
const supportedTypes = ['csv', 'xlsx', 'xls', 'sas7bdat', 'xpt'];
const fileType = file.name.split('.').pop().toLowerCase();

if (supportedTypes.includes(fileType)) {
  // Process upload
} else {
  alert('Please select a CSV, XLSX, SAS7BDAT, or XPT file');
}
```

## Data Processing Features

### Automatic Type Detection
- **Date/Time**: Converted to ISO strings for JSON serialization
- **Numbers**: Preserved with full precision
- **Text**: UTF-8 encoding with non-ASCII validation
- **Missing Values**: Handled as `null` in JSON output

### Validation Features
- **Non-ASCII Detection**: Identifies characters outside ASCII range (0-127)
- **Location Reporting**: Exact row/column positions for issues
- **Format Validation**: File structure and integrity checks
- **Size Limits**: Configurable maximum file sizes

### Metadata Preservation (SAS Files)
- Variable labels and formats
- Dataset-level metadata
- Column attributes and types
- Statistical properties

## Error Handling

### Missing Dependencies
```json
{
  "detail": "SAS7BDAT support requires 'sas7bdat' or 'pyreadstat' library. Install with: pip install sas7bdat"
}
```

### File Format Errors
```json
{
  "detail": "Error reading SAS7BDAT file: Invalid file format or corrupted data"
}
```

### Unsupported Format
```json
{
  "detail": "Unsupported file type: pdf. Supported types: csv, xlsx, xls, sas7bdat, xpt"
}
```

## Performance Considerations

### Memory Usage
- **Streaming**: Large files processed in chunks when possible
- **Efficient Libraries**: Optimized readers for each format
- **Memory Cleanup**: Automatic garbage collection after processing

### Processing Speed
- **CSV**: Fastest, direct pandas reading
- **Excel**: Moderate, depends on file complexity
- **SAS7BDAT**: Slower, binary format parsing required
- **XPT**: Moderate, standardized transport format

### File Size Recommendations
- **CSV/Excel**: Up to 100MB recommended
- **SAS Files**: Up to 50MB recommended (binary format overhead)
- **Memory Available**: Ensure 2-3x file size in available RAM

## Testing

### Sample File Creation
```python
import pandas as pd

# Create test data
data = {
    'patient_id': [1, 2, 3, 4, 5],
    'age': [25, 30, 45, 62, 38],
    'treatment': ['Drug A', 'Drug B', 'Placebo', 'Drug A', 'Drug B']
}
df = pd.DataFrame(data)

# Save in different formats
df.to_csv('test_data.csv', index=False)
df.to_excel('test_data.xlsx', index=False)

# For SAS formats (if libraries available)
import pyreadstat
pyreadstat.write_sas7bdat(df, 'test_data.sas7bdat')
pyreadstat.write_xport(df, 'test_data.xpt')
```

### Validation Testing
```python
# Test file upload with validation
import requests

files = {'file': open('test_data.sas7bdat', 'rb')}
data = {'tag': 'test_sas_data'}
headers = {'Authorization': 'Bearer your_jwt_token'}

response = requests.post(
    'http://localhost:8000/documents/upload',
    files=files,
    data=data,
    headers=headers
)

print(response.json())
```

## Troubleshooting

### Common Issues

**1. pyreadstat Installation Fails**
- Solution: Install Microsoft C++ Build Tools first
- Alternative: Use `sas7bdat` library for basic SAS support

**2. SAS File Reading Errors**
- Check file integrity and format version
- Try with different SAS reader libraries
- Verify file permissions and accessibility

**3. Large File Timeouts**
- Increase server timeout settings
- Consider file size limits
- Use chunked processing for very large files

**4. Encoding Issues**
- CSV files: Use UTF-8 encoding when saving
- Excel files: Save as modern .xlsx format
- SAS files: Check original encoding settings

### Debug Information
```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check available libraries
from app.services.file_service import SAS7BDAT_AVAILABLE, PYREADSTAT_AVAILABLE
print(f"SAS7BDAT available: {SAS7BDAT_AVAILABLE}")
print(f"PYREADSTAT available: {PYREADSTAT_AVAILABLE}")
```

## Migration Guide

### From CSV-Only Version
1. Update frontend file input accept attribute
2. No backend changes required (backward compatible)
3. Test with existing CSV files (should work unchanged)

### Adding SAS Support
1. Install `sas7bdat`: `pip install sas7bdat`
2. Optional: Install `pyreadstat` for enhanced features
3. Update requirements.txt in production
4. Test with sample SAS files

### Production Deployment
1. Update Docker image with new dependencies
2. Test all format types in staging environment
3. Monitor memory usage with large files
4. Set appropriate file size limits

---

This documentation provides comprehensive guidance for using the enhanced file format support in the Risk Management Application.