#!/usr/bin/env python3
"""
Test the Excel sheet detection functionality directly.
"""

import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.file_service import FileValidationService

def test_excel_sheet_detection():
    """Test Excel sheet detection with our test files."""
    
    service = FileValidationService()
    
    test_files = [
        "test_files/multi_sheet_test.xlsx",
        "test_files/single_sheet_test.xlsx", 
        "test_files/special_chars_test.xlsx"
    ]
    
    print("Testing Excel Sheet Detection:")
    print("=" * 40)
    
    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"\nFile: {os.path.basename(file_path)}")
            try:
                # Read file content as bytes
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                
                sheets = service.get_excel_sheet_names(file_content, os.path.basename(file_path))
                print(f"  ✓ Sheets found: {sheets}")
                print(f"  ✓ Number of sheets: {len(sheets)}")
                
                # Test if it's a multi-sheet file
                if len(sheets) > 1:
                    print(f"  ✓ Multi-sheet file detected")
                else:
                    print(f"  ✓ Single-sheet file detected")
                    
            except Exception as e:
                print(f"  ✗ Error: {e}")
        else:
            print(f"\nFile not found: {file_path}")
    
    print("\n" + "=" * 40)
    print("Test completed!")

if __name__ == "__main__":
    test_excel_sheet_detection()