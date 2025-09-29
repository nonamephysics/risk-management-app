import pandas as pd
import re
import io
from typing import List, Dict, Any, Tuple
from app.models.document import ValidationError

# Optional imports for SAS file support
try:
    import pyreadstat
    PYREADSTAT_AVAILABLE = True
except ImportError:
    PYREADSTAT_AVAILABLE = False

try:
    from sas7bdat import SAS7BDAT
    SAS7BDAT_AVAILABLE = True
except ImportError:
    SAS7BDAT_AVAILABLE = False


class FileValidationService:
    @staticmethod
    def detect_non_ascii_characters(data: List[Dict[str, Any]]) -> List[ValidationError]:
        """Detect non-ASCII characters in the data and return their locations"""
        validation_errors = []
        
        for row_idx, row in enumerate(data):
            for column, value in row.items():
                if value is not None:
                    str_value = str(value)
                    # Check for non-ASCII characters
                    non_ascii_chars = [char for char in str_value if ord(char) > 127]
                    
                    if non_ascii_chars:
                        validation_errors.append(ValidationError(
                            column=column,
                            row=row_idx + 1,  # 1-based row numbering
                            value=str_value,
                            message=f"Contains non-ASCII characters: {', '.join(set(non_ascii_chars))}"
                        ))
        
        return validation_errors

    @staticmethod
    def read_file(file_content: bytes, filename: str) -> Tuple[List[Dict[str, Any]], str]:
        """Read CSV, XLSX, SAS7BDAT, or XPT file and return data as list of dictionaries"""
        file_type = filename.lower().split('.')[-1]
        
        if file_type == 'csv':
            try:
                # Try different encodings
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        df = pd.read_csv(pd.io.common.BytesIO(file_content), encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise ValueError("Unable to decode CSV file with supported encodings")
            except Exception as e:
                raise ValueError(f"Error reading CSV file: {str(e)}")
                
        elif file_type in ['xlsx', 'xls']:
            try:
                df = pd.read_excel(pd.io.common.BytesIO(file_content))
            except Exception as e:
                raise ValueError(f"Error reading Excel file: {str(e)}")
                
        elif file_type == 'sas7bdat':
            if not SAS7BDAT_AVAILABLE and not PYREADSTAT_AVAILABLE:
                raise ValueError("SAS7BDAT support requires 'sas7bdat' or 'pyreadstat' library. Install with: pip install sas7bdat")
            
            try:
                if PYREADSTAT_AVAILABLE:
                    # Use pyreadstat for SAS7BDAT files (more reliable)
                    file_like = io.BytesIO(file_content)
                    df, meta = pyreadstat.read_sas7bdat(file_like)
                elif SAS7BDAT_AVAILABLE:
                    # Fallback to sas7bdat library
                    file_like = io.BytesIO(file_content)
                    with SAS7BDAT(file_like, skip_header=False) as reader:
                        df = reader.to_data_frame()
                else:
                    raise ValueError("No SAS7BDAT reader available")
            except Exception as e:
                raise ValueError(f"Error reading SAS7BDAT file: {str(e)}")
                    
        elif file_type == 'xpt':
            if not PYREADSTAT_AVAILABLE:
                raise ValueError("XPT support requires 'pyreadstat' library. Install with: pip install pyreadstat")
            
            try:
                # Use pyreadstat for XPT files
                file_like = io.BytesIO(file_content)
                df, meta = pyreadstat.read_xport(file_like)
            except Exception as e:
                raise ValueError(f"Error reading XPT file: {str(e)}")
                
        else:
            supported_types = ['csv', 'xlsx', 'xls', 'sas7bdat', 'xpt']
            raise ValueError(f"Unsupported file type: {file_type}. Supported types: {', '.join(supported_types)}")
        
        # Convert NaN values to None and ensure all values are JSON serializable
        df = df.where(pd.notnull(df), None)
        
        # Convert DataFrame to list of dictionaries
        data = df.to_dict('records')
        
        # Clean up data types for JSON serialization
        cleaned_data = []
        for row in data:
            cleaned_row = {}
            for key, value in row.items():
                if pd.isna(value):
                    cleaned_row[key] = None
                elif isinstance(value, (pd.Timestamp, pd.NaT.__class__)):
                    cleaned_row[key] = str(value) if pd.notna(value) else None
                else:
                    cleaned_row[key] = value
            cleaned_data.append(cleaned_row)
        
        return cleaned_data, file_type