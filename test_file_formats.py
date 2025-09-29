#!/usr/bin/env python3
"""
Test file format support for SAS7BDAT and XPT files
This script creates sample files and tests the upload functionality
"""

import pandas as pd
import numpy as np
import os
import requests
from datetime import datetime, date
import pyreadstat

# Sample data for testing
sample_data = {
    'patient_id': [1, 2, 3, 4, 5],
    'age': [25, 30, 45, 62, 38],
    'gender': ['M', 'F', 'M', 'F', 'M'],
    'treatment': ['Drug A', 'Drug B', 'Drug A', 'Placebo', 'Drug B'],
    'outcome': [85.2, 92.1, 78.9, 65.3, 89.7],
    'visit_date': [date(2024, 1, 15), date(2024, 1, 16), date(2024, 1, 17), date(2024, 1, 18), date(2024, 1, 19)],
    'notes': ['Good response', 'Excellent', 'Fair response', 'No change', 'Good response']
}

def create_test_files():
    """Create test files in different formats"""
    print("Creating test files for format support verification...")
    
    # Create DataFrame
    df = pd.DataFrame(sample_data)
    
    # Create test directory
    test_dir = "test_files"
    os.makedirs(test_dir, exist_ok=True)
    
    # CSV file
    csv_path = os.path.join(test_dir, "sample_data.csv")
    df.to_csv(csv_path, index=False)
    print(f"✓ Created CSV: {csv_path}")
    
    # Excel file
    excel_path = os.path.join(test_dir, "sample_data.xlsx")
    df.to_excel(excel_path, index=False)
    print(f"✓ Created Excel: {excel_path}")
    
    # SAS7BDAT file (using pyreadstat)
    try:
        sas_path = os.path.join(test_dir, "sample_data.sas7bdat")
        # Convert date column to datetime for SAS compatibility
        df_sas = df.copy()
        df_sas['visit_date'] = pd.to_datetime(df_sas['visit_date'])
        
        pyreadstat.write_sas7bdat(df_sas, sas_path)
        print(f"✓ Created SAS7BDAT: {sas_path}")
    except Exception as e:
        print(f"⚠ Failed to create SAS7BDAT: {e}")
        sas_path = None
    
    # XPT file (SAS Transport format)
    try:
        xpt_path = os.path.join(test_dir, "sample_data.xpt")
        # Convert date column to datetime for XPT compatibility
        df_xpt = df.copy()
        df_xpt['visit_date'] = pd.to_datetime(df_xpt['visit_date'])
        
        pyreadstat.write_xport(df_xpt, xpt_path)
        print(f"✓ Created XPT: {xpt_path}")
    except Exception as e:
        print(f"⚠ Failed to create XPT: {e}")
        xpt_path = None
    
    return {
        'csv': csv_path,
        'excel': excel_path,
        'sas7bdat': sas_path,
        'xpt': xpt_path
    }

def test_file_reading():
    """Test local file reading capabilities"""
    print("\n" + "="*50)
    print("Testing File Reading Capabilities")
    print("="*50)
    
    # Import the file service
    import sys
    sys.path.append('backend')
    from app.services.file_service import FileValidationService
    
    test_files = create_test_files()
    
    for file_type, file_path in test_files.items():
        if file_path and os.path.exists(file_path):
            print(f"\nTesting {file_type.upper()} file: {file_path}")
            try:
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                
                filename = os.path.basename(file_path)
                data, detected_type = FileValidationService.read_file(file_content, filename)
                
                print(f"  ✓ Successfully read {len(data)} rows")
                print(f"  ✓ Detected type: {detected_type}")
                print(f"  ✓ Columns: {list(data[0].keys()) if data else 'No data'}")
                
                # Show sample data
                if data:
                    print(f"  ✓ Sample row: {data[0]}")
                
            except Exception as e:
                print(f"  ✗ Failed to read {file_type}: {str(e)}")

def test_upload_api(base_url="http://localhost:8000", token=None):
    """Test API upload functionality with different file formats"""
    print("\n" + "="*50)
    print("Testing API Upload Functionality")
    print("="*50)
    
    if not token:
        print("⚠ No authentication token provided. Skipping API tests.")
        print("  To test API uploads, provide a valid JWT token.")
        return
    
    test_files = create_test_files()
    headers = {"Authorization": f"Bearer {token}"}
    
    for file_type, file_path in test_files.items():
        if file_path and os.path.exists(file_path):
            print(f"\nTesting {file_type.upper()} upload: {file_path}")
            try:
                with open(file_path, 'rb') as f:
                    files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
                    data = {'tag': f'test_{file_type}_{int(datetime.now().timestamp())}'}
                    
                    response = requests.post(
                        f"{base_url}/documents/upload",
                        files=files,
                        data=data,
                        headers=headers,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"  ✓ Upload successful!")
                        print(f"  ✓ Document ID: {result.get('document_id', 'Unknown')}")
                        print(f"  ✓ Rows processed: {result.get('rows_processed', 0)}")
                        print(f"  ✓ Has errors: {result.get('has_errors', False)}")
                        
                        if result.get('validation_errors'):
                            print(f"  ⚠ Validation errors found: {len(result['validation_errors'])}")
                    else:
                        print(f"  ✗ Upload failed: {response.status_code}")
                        print(f"  ✗ Response: {response.text}")
                        
            except Exception as e:
                print(f"  ✗ Failed to upload {file_type}: {str(e)}")

def create_test_files_with_issues():
    """Create test files with various data issues for validation testing"""
    print("\n" + "="*50)
    print("Creating Test Files with Data Issues")
    print("="*50)
    
    # Data with non-ASCII characters and other issues
    problematic_data = {
        'patient_id': [1, 2, 3, 4, 5],
        'name': ['João Silva', 'María García', 'François Müller', 'Åke Björk', 'Naïve Test'],
        'city': ['São Paulo', 'México City', 'Zürich', 'Malmö', 'Café Paris'],
        'notes': ['Good résponse', 'Excelente!', 'Très bien', 'Bra svar', 'Naïve approach'],
        'unicode_test': ['α', 'β', 'γ', 'δ', 'ε']  # Greek letters
    }
    
    df_issues = pd.DataFrame(problematic_data)
    
    test_dir = "test_files"
    os.makedirs(test_dir, exist_ok=True)
    
    # CSV with encoding issues
    csv_issues_path = os.path.join(test_dir, "data_with_issues.csv")
    df_issues.to_csv(csv_issues_path, index=False, encoding='utf-8')
    print(f"✓ Created CSV with non-ASCII characters: {csv_issues_path}")
    
    # Excel with issues
    excel_issues_path = os.path.join(test_dir, "data_with_issues.xlsx")
    df_issues.to_excel(excel_issues_path, index=False)
    print(f"✓ Created Excel with non-ASCII characters: {excel_issues_path}")
    
    # Try to create SAS/XPT with issues (may need special handling)
    try:
        sas_issues_path = os.path.join(test_dir, "data_with_issues.sas7bdat")
        pyreadstat.write_sas7bdat(df_issues, sas_issues_path)
        print(f"✓ Created SAS7BDAT with non-ASCII characters: {sas_issues_path}")
    except Exception as e:
        print(f"⚠ Failed to create SAS7BDAT with issues: {e}")
    
    try:
        xpt_issues_path = os.path.join(test_dir, "data_with_issues.xpt")
        pyreadstat.write_xport(df_issues, xpt_issues_path)
        print(f"✓ Created XPT with non-ASCII characters: {xpt_issues_path}")
    except Exception as e:
        print(f"⚠ Failed to create XPT with issues: {e}")

if __name__ == "__main__":
    print("🧪 File Format Support Testing Tool")
    print("=" * 60)
    
    # Test file reading capabilities
    test_file_reading()
    
    # Create test files with issues
    create_test_files_with_issues()
    
    # API testing (requires manual token input)
    print("\n" + "="*50)
    print("API Testing")
    print("="*50)
    print("To test API uploads, you need to:")
    print("1. Start your backend server (uvicorn app.main:app --reload)")
    print("2. Login to get a JWT token")
    print("3. Run this script with the token as argument")
    print("\nExample:")
    print("python test_file_formats.py your_jwt_token_here")
    
    import sys
    if len(sys.argv) > 1:
        token = sys.argv[1]
        test_upload_api(token=token)
    else:
        print("\n⚠ No JWT token provided. Skipping API tests.")
    
    print("\n🎉 Testing complete!")
    print("📁 Test files are available in the 'test_files' directory")