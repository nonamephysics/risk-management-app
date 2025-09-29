#!/usr/bin/env python3
"""
Simple test script to verify file format support
"""

import sys
import os
import pandas as pd
import tempfile

# Add backend to path
sys.path.append('backend')

def test_csv_support():
    """Test CSV file format support"""
    print("Testing CSV format...")
    try:
        from app.services.file_service import FileValidationService
        
        # Create sample CSV content
        sample_data = "name,age,city\nJohn,25,New York\nJane,30,Los Angeles\nJosé,35,São Paulo"
        file_content = sample_data.encode('utf-8')
        
        data, file_type = FileValidationService.read_file(file_content, "test.csv")
        
        print(f"  ✓ Successfully read CSV: {len(data)} rows")
        print(f"  ✓ Detected type: {file_type}")
        print(f"  ✓ Sample row: {data[0]}")
        
        # Test validation
        errors = FileValidationService.detect_non_ascii_characters(data)
        print(f"  ✓ Non-ASCII validation: {len(errors)} errors found")
        if errors:
            print(f"    - Example error: {errors[0].message}")
        
        return True
    except Exception as e:
        print(f"  ✗ CSV test failed: {e}")
        return False

def test_excel_support():
    """Test Excel file format support"""
    print("Testing Excel format...")
    try:
        from app.services.file_service import FileValidationService
        
        # Create sample Excel file in memory
        df = pd.DataFrame({
            'name': ['John', 'Jane', 'José'],
            'age': [25, 30, 35],
            'city': ['New York', 'Los Angeles', 'São Paulo']
        })
        
        # Write to bytes
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            df.to_excel(tmp_file.name, index=False)
            
            with open(tmp_file.name, 'rb') as f:
                file_content = f.read()
            
            os.unlink(tmp_file.name)
        
        data, file_type = FileValidationService.read_file(file_content, "test.xlsx")
        
        print(f"  ✓ Successfully read Excel: {len(data)} rows")
        print(f"  ✓ Detected type: {file_type}")
        print(f"  ✓ Sample row: {data[0]}")
        
        return True
    except Exception as e:
        print(f"  ✗ Excel test failed: {e}")
        return False

def test_sas_support():
    """Test SAS file format support"""
    print("Testing SAS7BDAT format...")
    try:
        from app.services.file_service import FileValidationService, SAS7BDAT_AVAILABLE, PYREADSTAT_AVAILABLE
        
        if not SAS7BDAT_AVAILABLE and not PYREADSTAT_AVAILABLE:
            print("  ⚠ SAS support libraries not available, testing error handling...")
            
            # Test that proper error is raised
            try:
                FileValidationService.read_file(b"fake_content", "test.sas7bdat")
                print("  ✗ Expected error not raised")
                return False
            except ValueError as e:
                if "SAS7BDAT support requires" in str(e):
                    print(f"  ✓ Proper error handling: {e}")
                    return True
                else:
                    print(f"  ✗ Unexpected error: {e}")
                    return False
        else:
            print(f"  ✓ SAS libraries available: sas7bdat={SAS7BDAT_AVAILABLE}, pyreadstat={PYREADSTAT_AVAILABLE}")
            # Would need actual SAS file to test further
            return True
            
    except Exception as e:
        print(f"  ✗ SAS test failed: {e}")
        return False

def test_xpt_support():
    """Test XPT file format support"""
    print("Testing XPT format...")
    try:
        from app.services.file_service import FileValidationService, PYREADSTAT_AVAILABLE
        
        if not PYREADSTAT_AVAILABLE:
            print("  ⚠ XPT support requires pyreadstat, testing error handling...")
            
            # Test that proper error is raised
            try:
                FileValidationService.read_file(b"fake_content", "test.xpt")
                print("  ✗ Expected error not raised")
                return False
            except ValueError as e:
                if "XPT support requires" in str(e):
                    print(f"  ✓ Proper error handling: {e}")
                    return True
                else:
                    print(f"  ✗ Unexpected error: {e}")
                    return False
        else:
            print(f"  ✓ XPT library available: pyreadstat={PYREADSTAT_AVAILABLE}")
            # Would need actual XPT file to test further
            return True
            
    except Exception as e:
        print(f"  ✗ XPT test failed: {e}")
        return False

def test_unsupported_format():
    """Test handling of unsupported file formats"""
    print("Testing unsupported format handling...")
    try:
        from app.services.file_service import FileValidationService
        
        try:
            FileValidationService.read_file(b"fake_content", "test.pdf")
            print("  ✗ Expected error not raised")
            return False
        except ValueError as e:
            if "Unsupported file type" in str(e):
                print(f"  ✓ Proper error handling: {e}")
                return True
            else:
                print(f"  ✗ Unexpected error: {e}")
                return False
                
    except Exception as e:
        print(f"  ✗ Unsupported format test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 File Format Support Test")
    print("=" * 50)
    
    tests = [
        test_csv_support,
        test_excel_support, 
        test_sas_support,
        test_xpt_support,
        test_unsupported_format
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)