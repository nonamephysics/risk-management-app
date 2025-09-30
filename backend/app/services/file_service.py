import pandas as pd
import re
import io
import tempfile
import os
from typing import List, Dict, Any, Tuple, Optional
from app.models.document import ValidationError

# Optional imports for SAS file support
try:
    import pyreadstat
    PYREADSTAT_AVAILABLE = True
except ImportError:
    PYREADSTAT_AVAILABLE = False


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
    def get_excel_sheet_names(file_content: bytes, filename: str) -> List[str]:
        """Get list of sheet names from Excel file"""
        file_type = filename.lower().split('.')[-1]
        
        if file_type not in ['xlsx', 'xls']:
            raise ValueError("Sheet names can only be retrieved from Excel files")
        
        try:
            excel_file = pd.ExcelFile(pd.io.common.BytesIO(file_content))
            return excel_file.sheet_names
        except Exception as e:
            raise ValueError(f"Error reading Excel file sheets: {str(e)}")

    @staticmethod
    def read_file(file_content: bytes, filename: str, sheet_name: str = None) -> Tuple[List[Dict[str, Any]], str]:
        """Read CSV, XLSX, SAS7BDAT, or XPT file and return data as list of dictionaries"""
        data, file_type, _ = FileValidationService.read_file_with_metadata(file_content, filename, sheet_name)
        return data, file_type

    @staticmethod
    def read_file_with_metadata(file_content: bytes, filename: str, sheet_name: str = None) -> Tuple[List[Dict[str, Any]], str, Optional[Dict]]:
        """Read file and return data, file type, and metadata (for SAS/XPT files)"""
        file_type = filename.lower().split('.')[-1]
        metadata = None
        
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
                # Read Excel file with optional sheet selection
                if sheet_name:
                    df = pd.read_excel(pd.io.common.BytesIO(file_content), sheet_name=sheet_name)
                else:
                    # Default behavior - read first sheet
                    df = pd.read_excel(pd.io.common.BytesIO(file_content))
            except Exception as e:
                raise ValueError(f"Error reading Excel file: {str(e)}")
                
        elif file_type == 'sas7bdat':
            if not PYREADSTAT_AVAILABLE:
                raise ValueError("SAS7BDAT support requires 'pyreadstat' library. Install with: pip install pyreadstat")
            
            try:
                # Create temporary file for pyreadstat (it requires a file path)
                with tempfile.NamedTemporaryFile(delete=False, suffix='.sas7bdat') as temp_file:
                    temp_file.write(file_content)
                    temp_file_path = temp_file.name
                
                try:
                    # Use pyreadstat for SAS7BDAT files
                    df, meta = pyreadstat.read_sas7bdat(temp_file_path)
                    
                    # Safe metadata extraction function
                    def safe_extract_metadata(meta_obj, attr_name, default_value):
                        try:
                            if hasattr(meta_obj, attr_name):
                                value = getattr(meta_obj, attr_name)
                                # Convert to JSON-serializable format
                                if value is None:
                                    return default_value
                                elif isinstance(value, (dict, list)):
                                    # Convert any non-serializable objects to strings
                                    return convert_to_serializable(value)
                                else:
                                    return str(value) if value is not None else default_value
                            return default_value
                        except Exception as e:
                            print(f"WARNING: Could not extract metadata attribute '{attr_name}': {e}")
                            return default_value
                    
                    def convert_to_serializable(obj):
                        """Convert objects to JSON-serializable format"""
                        if isinstance(obj, dict):
                            return {str(k): convert_to_serializable(v) for k, v in obj.items()}
                        elif isinstance(obj, list):
                            return [convert_to_serializable(item) for item in obj]
                        elif obj is None:
                            return None
                        else:
                            return str(obj)
                    
                    # Capture metadata for SAS7BDAT files with safe extraction
                    metadata = {
                        'column_names': list(df.columns),  # Always use DataFrame columns as they're reliable
                        'column_labels': safe_extract_metadata(meta, 'column_labels', {}),
                        'variable_labels': safe_extract_metadata(meta, 'variable_labels', {}),
                        'value_labels': safe_extract_metadata(meta, 'value_labels', {}),
                        'variable_measure': safe_extract_metadata(meta, 'variable_measure', {}),
                        'variable_display_width': safe_extract_metadata(meta, 'variable_display_width', {}),
                        'variable_alignment': safe_extract_metadata(meta, 'variable_alignment', {}),
                        'notes': safe_extract_metadata(meta, 'notes', []),
                        'file_label': safe_extract_metadata(meta, 'file_label', ''),
                        'file_encoding': safe_extract_metadata(meta, 'file_encoding', ''),
                        'number_rows': len(df),
                        'number_columns': len(df.columns)
                    }
                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
                        
            except Exception as e:
                raise ValueError(f"Error reading SAS7BDAT file: {str(e)}")
                    
        elif file_type == 'xpt':
            if not PYREADSTAT_AVAILABLE:
                raise ValueError("XPT support requires 'pyreadstat' library. Install with: pip install pyreadstat")
            
            try:
                # Create temporary file for pyreadstat (it requires a file path)
                with tempfile.NamedTemporaryFile(delete=False, suffix='.xpt') as temp_file:
                    temp_file.write(file_content)
                    temp_file_path = temp_file.name
                
                try:
                    # Use pyreadstat for XPT files
                    df, meta = pyreadstat.read_xport(temp_file_path)
                    
                    # Safe metadata extraction (reuse functions from SAS7BDAT handling)
                    def safe_extract_metadata_xpt(meta_obj, attr_name, default_value):
                        try:
                            if hasattr(meta_obj, attr_name):
                                value = getattr(meta_obj, attr_name)
                                if value is None:
                                    return default_value
                                elif isinstance(value, (dict, list)):
                                    return convert_to_serializable_xpt(value)
                                else:
                                    return str(value) if value is not None else default_value
                            return default_value
                        except Exception as e:
                            print(f"WARNING: Could not extract XPT metadata attribute '{attr_name}': {e}")
                            return default_value
                    
                    def convert_to_serializable_xpt(obj):
                        """Convert objects to JSON-serializable format for XPT"""
                        if isinstance(obj, dict):
                            return {str(k): convert_to_serializable_xpt(v) for k, v in obj.items()}
                        elif isinstance(obj, list):
                            return [convert_to_serializable_xpt(item) for item in obj]
                        elif obj is None:
                            return None
                        else:
                            return str(obj)
                    
                    # Capture metadata for XPT files with safe extraction
                    metadata = {
                        'column_names': list(df.columns),  # Always use DataFrame columns as they're reliable
                        'column_labels': safe_extract_metadata_xpt(meta, 'column_labels', {}),
                        'variable_labels': safe_extract_metadata_xpt(meta, 'variable_labels', {}),
                        'value_labels': safe_extract_metadata_xpt(meta, 'value_labels', {}),
                        'file_label': safe_extract_metadata_xpt(meta, 'file_label', ''),
                        'file_encoding': safe_extract_metadata_xpt(meta, 'file_encoding', ''),
                        'creation_time': safe_extract_metadata_xpt(meta, 'creation_time', ''),
                        'modification_time': safe_extract_metadata_xpt(meta, 'modification_time', ''),
                        'number_rows': len(df),
                        'number_columns': len(df.columns)
                    }
                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
                        
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
        
        return cleaned_data, file_type, metadata