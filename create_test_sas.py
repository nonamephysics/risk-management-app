#!/usr/bin/env python3
"""
Create a test SAS7BDAT file with metadata to test the dual upload functionality.
"""

import pandas as pd
import os

def create_test_sas_file():
    """Create a test SAS7BDAT file with sample data."""
    
    # Create sample data
    data = {
        'USUBJID': ['SUBJ001', 'SUBJ002', 'SUBJ003', 'SUBJ004', 'SUBJ005'],
        'AGE': [25, 30, 35, 28, 42],
        'SEX': ['M', 'F', 'M', 'F', 'M'],
        'RACE': ['WHITE', 'BLACK', 'ASIAN', 'WHITE', 'OTHER'],
        'VISIT': ['BASELINE', 'WEEK2', 'WEEK4', 'WEEK8', 'WEEK12'],
        'SCORE': [8.5, 7.2, 9.1, 6.8, 8.9]
    }
    
    df = pd.DataFrame(data)
    
    # Create test files directory if it doesn't exist
    test_dir = "test_files"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    
    # Save as SAS7BDAT file using pyreadstat if available
    sas_file = os.path.join(test_dir, "clinical_data_test.sas7bdat")
    
    try:
        import pyreadstat
        
        # Define variable labels (metadata)
        variable_labels = {
            'USUBJID': 'Unique Subject Identifier',
            'AGE': 'Age at Baseline (years)',
            'SEX': 'Gender',
            'RACE': 'Race Category', 
            'VISIT': 'Visit Name',
            'SCORE': 'Clinical Assessment Score'
        }
        
        # Define value labels
        value_labels = {
            'SEX': {'M': 'Male', 'F': 'Female'},
            'RACE': {
                'WHITE': 'White/Caucasian',
                'BLACK': 'Black/African American', 
                'ASIAN': 'Asian',
                'OTHER': 'Other/Mixed'
            }
        }
        
        # Write SAS7BDAT file with metadata
        pyreadstat.write_sas7bdat(
            df, 
            sas_file,
            variable_labels=variable_labels,
            value_labels=value_labels,
            file_label="Clinical Trial Test Data"
        )
        
        print(f"✅ Created SAS7BDAT file: {sas_file}")
        print(f"   - Rows: {len(df)}")
        print(f"   - Columns: {len(df.columns)}")
        print(f"   - Variable labels: {len(variable_labels)}")
        print(f"   - Value labels: {len(value_labels)}")
        
        return sas_file
        
    except ImportError:
        print("❌ pyreadstat not available - cannot create SAS7BDAT file")
        print("   Install with: pip install pyreadstat")
        
        # Fallback: create CSV file for testing
        csv_file = os.path.join(test_dir, "clinical_data_test.csv")
        df.to_csv(csv_file, index=False)
        print(f"📄 Created CSV fallback: {csv_file}")
        return csv_file
    
    except Exception as e:
        print(f"❌ Error creating SAS7BDAT file: {e}")
        return None

def test_sas_metadata_extraction():
    """Test metadata extraction from the created SAS file."""
    sas_file = "test_files/clinical_data_test.sas7bdat"
    
    if not os.path.exists(sas_file):
        print("❌ SAS file not found for testing")
        return
    
    try:
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        from app.services.file_service import FileValidationService
        
        # Read the file content
        with open(sas_file, 'rb') as f:
            file_content = f.read()
        
        # Test the enhanced method
        data, file_type, metadata = FileValidationService.read_file_with_metadata(
            file_content, 
            os.path.basename(sas_file)
        )
        
        print("\n🧪 Testing SAS7BDAT Metadata Extraction:")
        print("=" * 50)
        print(f"✅ File type detected: {file_type}")
        print(f"✅ Data rows: {len(data)}")
        print(f"✅ Data columns: {len(data[0].keys()) if data else 0}")
        
        if metadata:
            print("✅ Metadata extracted:")
            for key, value in metadata.items():
                if isinstance(value, dict) and len(str(value)) > 100:
                    print(f"   - {key}: {type(value).__name__} ({len(value)} items)")
                else:
                    print(f"   - {key}: {value}")
        else:
            print("❌ No metadata extracted")
            
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error testing metadata extraction: {e}")

if __name__ == "__main__":
    # Create test SAS file
    sas_file = create_test_sas_file()
    
    if sas_file and sas_file.endswith('.sas7bdat'):
        # Test metadata extraction
        test_sas_metadata_extraction()
    
    print("\n🎯 Ready to test SAS7BDAT dual upload:")
    print("1. Use the created file in the application")
    print("2. Upload with tag 'clinical_test'") 
    print("3. Verify two documents are created:")
    print("   - 'clinical_test' (data)")
    print("   - 'clinical_test_meta' (metadata)")