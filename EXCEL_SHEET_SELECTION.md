# Excel Sheet Selection Feature

## Overview

The Risk Assessment application now supports Excel files with multiple sheets, allowing users to select which specific sheet they want to process during file upload. This feature enhances the user experience when working with complex spreadsheet files containing multiple datasets.

## Feature Implementation

### Backend Implementation

#### File Service Enhancement
- **File**: `backend/app/services/file_service.py`
- **Method**: `get_excel_sheet_names(file_content: bytes, filename: str) -> List[str]`
- **Purpose**: Extracts sheet names from Excel files using openpyxl library
- **Returns**: List of sheet names found in the Excel file

#### API Endpoint
- **File**: `backend/app/routes/documents.py`
- **Endpoint**: `GET /excel-sheets`
- **Purpose**: Accepts multipart file upload and returns available sheet names
- **Parameters**: Excel file in multipart form data
- **Returns**: JSON response with sheet names array

#### Enhanced Upload Endpoint
- **Endpoint**: `POST /upload`
- **Enhancement**: Added optional `sheet_name` parameter
- **Behavior**: When `sheet_name` is provided, processes only the specified sheet

### Frontend Implementation

#### Component Updates
- **File**: `frontend/src/components/FileUpload.js`
- **New State Variables**:
  - `excelSheets`: Array of available sheet names
  - `selectedSheet`: Currently selected sheet name
  - `isLoadingSheets`: Loading state for sheet detection

#### User Interface Flow
1. User selects an Excel file
2. System automatically detects if file has multiple sheets
3. If multiple sheets exist, a dropdown appears for sheet selection
4. User must select a sheet before upload can proceed
5. Upload includes the selected sheet parameter

#### API Service Updates
- **File**: `frontend/src/services/api.js`
- **New Method**: `getExcelSheets(file)` - Sends file to backend for sheet detection
- **Enhanced Method**: `uploadDocument(formData)` - Supports sheet selection parameter

### CSS Styling
- **File**: `frontend/src/components/FileUpload.css`
- **Enhancements**:
  - Styled select dropdown for sheet selection
  - Loading state indicator for sheet detection
  - Focus states and proper form styling

## User Experience

### Multi-Sheet Excel Files
1. User selects Excel file with multiple sheets
2. "Loading sheets..." indicator appears briefly
3. Dropdown menu appears with available sheets
4. User selects desired sheet
5. Upload button remains disabled until sheet is selected
6. Upload proceeds with selected sheet data

### Single-Sheet Excel Files
1. User selects Excel file with single sheet
2. No additional UI elements appear
3. Upload proceeds normally with the single sheet

### Error Handling
- Invalid Excel files show appropriate error messages
- Network errors during sheet detection are handled gracefully
- Missing sheet selection prevents upload until resolved

## Testing

### Test Files Created
The system includes test Excel files for validation:

1. **multi_sheet_test.xlsx** - 3 sheets: Employees, Products, Sales_Data
2. **single_sheet_test.xlsx** - 1 sheet: Data
3. **special_chars_test.xlsx** - 3 sheets with special characters in names

### Test Results
```
File: multi_sheet_test.xlsx
  ✓ Sheets found: ['Employees', 'Products', 'Sales_Data']
  ✓ Number of sheets: 3
  ✓ Multi-sheet file detected

File: single_sheet_test.xlsx
  ✓ Sheets found: ['Data']
  ✓ Number of sheets: 1
  ✓ Single-sheet file detected

File: special_chars_test.xlsx
  ✓ Sheets found: ['Data & Info', 'Products (2024)', 'Sales-Report_Q1']
  ✓ Number of sheets: 3
  ✓ Multi-sheet file detected
```

## Technical Details

### Dependencies
- **Backend**: `openpyxl` (already required for Excel support)
- **Frontend**: Native HTML5 File API and fetch

### File Type Detection
The system automatically detects Excel files (.xlsx, .xls) and triggers sheet detection only for these formats. Other file types (CSV, SAS7BDAT, XPT) are processed normally without sheet selection.

### Sheet Name Handling
- Supports sheets with special characters in names
- Handles Unicode characters properly
- Preserves original sheet name formatting

### Performance Considerations
- Sheet detection is performed efficiently using openpyxl's worksheet iteration
- File content is read once and cached during the detection process
- UI updates are optimized to prevent unnecessary re-renders

## Future Enhancements

### Potential Improvements
1. **Sheet Preview**: Show sample data from selected sheet before upload
2. **Multi-Sheet Upload**: Allow processing multiple sheets simultaneously
3. **Sheet Validation**: Pre-validate sheet structure before upload
4. **Sheet Metadata**: Display sheet information (row count, column names)

### Configuration Options
- Maximum number of sheets to display
- Default sheet selection behavior
- Custom sheet naming conventions

## Troubleshooting

### Common Issues
1. **Sheet detection fails**: Ensure file is valid Excel format
2. **Dropdown doesn't appear**: Check browser console for JavaScript errors
3. **Upload fails with sheet selection**: Verify backend API is running

### Debug Steps
1. Check browser network tab for API calls
2. Verify Excel file format compatibility
3. Confirm backend service is accessible
4. Review console logs for error messages

## Code Examples

### Backend Sheet Detection
```python
# Get sheet names from Excel file
sheets = service.get_excel_sheet_names(file_content, filename)
if len(sheets) > 1:
    return {"sheets": sheets}
```

### Frontend Sheet Selection
```javascript
// Load available sheets when Excel file is selected
const loadExcelSheets = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await documentService.getExcelSheets(formData);
    setExcelSheets(response.sheets || []);
};
```

### Upload with Sheet Selection
```javascript
// Include selected sheet in upload
if (selectedSheet) {
    formData.append('sheet_name', selectedSheet);
}
const result = await documentService.uploadDocument(formData);
```

This feature provides a comprehensive solution for handling Excel files with multiple sheets, ensuring users have full control over which data gets processed in their risk assessment workflows.