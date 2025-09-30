#!/usr/bin/env python3
"""
Test script to create sample Excel files with multiple sheets for testing
the Excel sheet selection functionality.
"""

import pandas as pd
import os

def create_test_excel_files():
    """Create test Excel files with multiple sheets."""
    
    # Sample data for different sheets
    data_sheet1 = {
        'ID': [1, 2, 3, 4, 5],
        'Name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
        'Age': [25, 30, 35, 28, 32],
        'Department': ['IT', 'Finance', 'HR', 'IT', 'Marketing']
    }
    
    data_sheet2 = {
        'Product': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Tablet'],
        'Price': [999.99, 25.50, 75.00, 299.99, 499.99],
        'Stock': [50, 200, 150, 75, 30],
        'Category': ['Electronics', 'Accessories', 'Accessories', 'Electronics', 'Electronics']
    }
    
    data_sheet3 = {
        'Date': pd.date_range('2024-01-01', periods=5),
        'Sales': [1500, 2000, 1800, 2200, 1900],
        'Region': ['North', 'South', 'East', 'West', 'Central'],
        'Revenue': [15000, 20000, 18000, 22000, 19000]
    }
    
    # Create DataFrame objects
    df1 = pd.DataFrame(data_sheet1)
    df2 = pd.DataFrame(data_sheet2)
    df3 = pd.DataFrame(data_sheet3)
    
    # Create test files directory
    test_dir = "test_files"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    
    # Create Excel file with multiple sheets
    multi_sheet_file = os.path.join(test_dir, "multi_sheet_test.xlsx")
    with pd.ExcelWriter(multi_sheet_file, engine='openpyxl') as writer:
        df1.to_excel(writer, sheet_name='Employees', index=False)
        df2.to_excel(writer, sheet_name='Products', index=False)
        df3.to_excel(writer, sheet_name='Sales_Data', index=False)
    
    # Create Excel file with single sheet
    single_sheet_file = os.path.join(test_dir, "single_sheet_test.xlsx")
    df1.to_excel(single_sheet_file, index=False, sheet_name='Data')
    
    # Create Excel file with special characters in sheet names
    special_chars_file = os.path.join(test_dir, "special_chars_test.xlsx")
    with pd.ExcelWriter(special_chars_file, engine='openpyxl') as writer:
        df1.to_excel(writer, sheet_name='Data & Info', index=False)
        df2.to_excel(writer, sheet_name='Products (2024)', index=False)
        df3.to_excel(writer, sheet_name='Sales-Report_Q1', index=False)
    
    print("Test Excel files created successfully:")
    print(f"  - {multi_sheet_file} (3 sheets: Employees, Products, Sales_Data)")
    print(f"  - {single_sheet_file} (1 sheet: Data)")
    print(f"  - {special_chars_file} (3 sheets with special characters)")
    
    return [multi_sheet_file, single_sheet_file, special_chars_file]

def test_sheet_detection():
    """Test the sheet detection functionality."""
    try:
        # Import the file service
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        from app.services.file_service import FileValidationService
        
        service = FileValidationService()
        test_files = create_test_excel_files()
        
        print("\nTesting sheet detection:")
        for file_path in test_files:
            print(f"\nFile: {os.path.basename(file_path)}")
            try:
                sheets = service.get_excel_sheet_names(file_path)
                print(f"  Sheets found: {sheets}")
                print(f"  Number of sheets: {len(sheets)}")
            except Exception as e:
                print(f"  Error: {e}")
                
    except ImportError as e:
        print(f"\nCannot test sheet detection - missing imports: {e}")
        print("You can manually test the files created above.")

if __name__ == "__main__":
    create_test_excel_files()
    test_sheet_detection()