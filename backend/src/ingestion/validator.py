"""
Data validation utilities for health data integration.

This module provides comprehensive validation functions for CSV, JSON, and other
data formats to ensure data quality and integrity before processing.
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

import pandas as pd


class DataValidator:
    """
    Validates data structures and content for health data integration.
    
    The DataValidator provides methods to validate CSV DataFrames, JSON dictionaries,
    and other data structures to ensure they meet required schemas and quality standards.
    
    Example:
        >>> validator = DataValidator()
        >>> df = pd.DataFrame({'member_id': [1, 2], 'status': ['active', 'inactive']})
        >>> is_valid, errors = validator.validate_csv(df, ['member_id', 'status'])
        >>> print(is_valid)
        True
    """
    
    def validate_csv(self, df: pd.DataFrame, required_columns: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate a pandas DataFrame against required column specifications.
        
        Checks that all required columns exist in the DataFrame and that the
        DataFrame is not empty. Returns validation status and list of any errors.
        
        Args:
            df: The pandas DataFrame to validate.
            required_columns: List of column names that must be present in the DataFrame.
            
        Returns:
            Tuple[bool, List[str]]: A tuple containing:
                - is_valid: True if validation passes, False otherwise
                - errors: List of error messages describing validation failures
                
        Example:
            >>> validator = DataValidator()
            >>> df = pd.DataFrame({'member_id': [1, 2], 'status': ['active']})
            >>> is_valid, errors = validator.validate_csv(df, ['member_id', 'status', 'plan_type'])
            >>> print(errors)
            ['Missing required column: plan_type']
        """
        errors = []
        
        if not isinstance(df, pd.DataFrame):
            errors.append(f"Input is not a pandas DataFrame, got {type(df).__name__}")
            return (False, errors)
        
        if df.empty:
            errors.append("DataFrame is empty")
        
        if not required_columns:
            return (len(errors) == 0, errors)
        
        # Check for missing required columns
        missing_columns = [col for col in required_columns if col not in df.columns]
        for col in missing_columns:
            errors.append(f"Missing required column: {col}")
        
        is_valid = len(errors) == 0
        return (is_valid, errors)
    
    def validate_json(self, data: dict, required_keys: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate a JSON dictionary against required key specifications.
        
        Checks that all required keys exist in the dictionary and that the
        dictionary is not empty. Supports nested keys using dot notation
        (e.g., "claims.items" for nested structures).
        
        Args:
            data: The dictionary to validate.
            required_keys: List of keys that must be present. Supports dot notation
                          for nested keys (e.g., "claims.items").
            
        Returns:
            Tuple[bool, List[str]]: A tuple containing:
                - is_valid: True if validation passes, False otherwise
                - errors: List of error messages describing validation failures
                
        Example:
            >>> validator = DataValidator()
            >>> data = {'claims': {'items': [1, 2]}, 'total': 2}
            >>> is_valid, errors = validator.validate_json(data, ['claims.items', 'total'])
            >>> print(is_valid)
            True
        """
        errors = []
        
        if not isinstance(data, dict):
            errors.append(f"Input is not a dictionary, got {type(data).__name__}")
            return (False, errors)
        
        if not data:
            errors.append("Dictionary is empty")
        
        if not required_keys:
            return (len(errors) == 0, errors)
        
        # Check for missing required keys (supports nested keys with dot notation)
        for key in required_keys:
            if '.' in key:
                # Handle nested keys with dot notation
                keys = key.split('.')
                current = data
                found = True
                
                for k in keys:
                    if isinstance(current, dict) and k in current:
                        current = current[k]
                    else:
                        found = False
                        break
                
                if not found:
                    errors.append(f"Missing required key: {key}")
            else:
                # Handle top-level keys
                if key not in data:
                    errors.append(f"Missing required key: {key}")
        
        is_valid = len(errors) == 0
        return (is_valid, errors)
    
    def validate_date_format(self, date_string: str, expected_format: str = "%Y-%m-%d") -> Tuple[bool, str]:
        """
        Validate that a date string matches the expected format.
        
        Args:
            date_string: The date string to validate.
            expected_format: The expected date format (default: "%Y-%m-%d").
            
        Returns:
            Tuple[bool, str]: A tuple containing:
                - is_valid: True if date format is valid, False otherwise
                - error_message: Error message if validation fails, empty string otherwise
                
        Example:
            >>> validator = DataValidator()
            >>> is_valid, error = validator.validate_date_format("2024-01-15")
            >>> print(is_valid)
            True
        """
        if not date_string or not isinstance(date_string, str):
            return (False, f"Invalid date string: {date_string}")
        
        try:
            datetime.strptime(date_string, expected_format)
            return (True, "")
        except ValueError as e:
            return (False, f"Date format validation failed: {str(e)}")
    
    def validate_email(self, email: str) -> Tuple[bool, str]:
        """
        Validate email address format using regex pattern.
        
        Args:
            email: The email address string to validate.
            
        Returns:
            Tuple[bool, str]: A tuple containing:
                - is_valid: True if email format is valid, False otherwise
                - error_message: Error message if validation fails, empty string otherwise
                
        Example:
            >>> validator = DataValidator()
            >>> is_valid, error = validator.validate_email("user@example.com")
            >>> print(is_valid)
            True
        """
        if not email or not isinstance(email, str):
            return (False, f"Invalid email string: {email}")
        
        # Basic email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if re.match(pattern, email):
            return (True, "")
        else:
            return (False, f"Invalid email format: {email}")
    
    def validate_phone(self, phone: str) -> Tuple[bool, str]:
        """
        Validate phone number format (supports US formats).
        
        Args:
            phone: The phone number string to validate.
            
        Returns:
            Tuple[bool, str]: A tuple containing:
                - is_valid: True if phone format is valid, False otherwise
                - error_message: Error message if validation fails, empty string otherwise
                
        Example:
            >>> validator = DataValidator()
            >>> is_valid, error = validator.validate_phone("510-555-0101")
            >>> print(is_valid)
            True
        """
        if not phone or not isinstance(phone, str):
            return (False, f"Invalid phone string: {phone}")
        
        # Remove common formatting characters
        cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
        
        # Check if it's a valid US phone number (10 digits, optionally with country code)
        if cleaned.startswith('1') and len(cleaned) == 11:
            cleaned = cleaned[1:]  # Remove country code
        
        if re.match(r'^\d{10}$', cleaned):
            return (True, "")
        else:
            return (False, f"Invalid phone format: {phone}")
    
    def validate_numeric_range(self, value: float, min_value: float = None, 
                               max_value: float = None) -> Tuple[bool, str]:
        """
        Validate that a numeric value falls within a specified range.
        
        Args:
            value: The numeric value to validate.
            min_value: Optional minimum allowed value (inclusive).
            max_value: Optional maximum allowed value (inclusive).
            
        Returns:
            Tuple[bool, str]: A tuple containing:
                - is_valid: True if value is within range, False otherwise
                - error_message: Error message if validation fails, empty string otherwise
                
        Example:
            >>> validator = DataValidator()
            >>> is_valid, error = validator.validate_numeric_range(50.0, min_value=0, max_value=100)
            >>> print(is_valid)
            True
        """
        if not isinstance(value, (int, float)):
            return (False, f"Value is not numeric: {value}")
        
        if min_value is not None and value < min_value:
            return (False, f"Value {value} is below minimum {min_value}")
        
        if max_value is not None and value > max_value:
            return (False, f"Value {value} is above maximum {max_value}")
        
        return (True, "")


def main():
    """
    Test the DataValidator with sample data.
    
    Demonstrates validation of CSV DataFrames, JSON dictionaries, dates, emails,
    phone numbers, and numeric ranges.
    """
    print("=" * 80)
    print("Data Validator Test")
    print("=" * 80)
    
    validator = DataValidator()
    
    # Test CSV validation
    print("\n1. Testing validate_csv()...")
    print("-" * 80)
    
    # Valid CSV
    df_valid = pd.DataFrame({
        'member_id': ['BSC100001', 'BSC100002'],
        'status': ['active', 'inactive'],
        'plan_type': ['Gold PPO', 'Silver HMO']
    })
    is_valid, errors = validator.validate_csv(df_valid, ['member_id', 'status', 'plan_type'])
    print(f"Valid CSV: is_valid={is_valid}, errors={errors}")
    
    # Invalid CSV - missing column
    df_invalid = pd.DataFrame({
        'member_id': ['BSC100001'],
        'status': ['active']
    })
    is_valid, errors = validator.validate_csv(df_invalid, ['member_id', 'status', 'plan_type'])
    print(f"Invalid CSV (missing column): is_valid={is_valid}, errors={errors}")
    
    # Empty CSV
    df_empty = pd.DataFrame()
    is_valid, errors = validator.validate_csv(df_empty, ['member_id'])
    print(f"Empty CSV: is_valid={is_valid}, errors={errors}")
    
    # Test JSON validation
    print("\n2. Testing validate_json()...")
    print("-" * 80)
    
    # Valid JSON
    json_valid = {
        'claims': {
            'items': [1, 2, 3],
            'total': 3
        },
        'status': 'processed'
    }
    is_valid, errors = validator.validate_json(json_valid, ['claims.items', 'claims.total', 'status'])
    print(f"Valid JSON: is_valid={is_valid}, errors={errors}")
    
    # Invalid JSON - missing nested key
    json_invalid = {
        'claims': {
            'items': [1, 2]
        }
    }
    is_valid, errors = validator.validate_json(json_invalid, ['claims.items', 'claims.total'])
    print(f"Invalid JSON (missing nested key): is_valid={is_valid}, errors={errors}")
    
    # Empty JSON
    json_empty = {}
    is_valid, errors = validator.validate_json(json_empty, ['key'])
    print(f"Empty JSON: is_valid={is_valid}, errors={errors}")
    
    # Test date validation
    print("\n3. Testing validate_date_format()...")
    print("-" * 80)
    is_valid, error = validator.validate_date_format("2024-01-15")
    print(f"Valid date: is_valid={is_valid}, error='{error}'")
    is_valid, error = validator.validate_date_format("01/15/2024", "%m/%d/%Y")
    print(f"Valid date (custom format): is_valid={is_valid}, error='{error}'")
    is_valid, error = validator.validate_date_format("invalid-date")
    print(f"Invalid date: is_valid={is_valid}, error='{error}'")
    
    # Test email validation
    print("\n4. Testing validate_email()...")
    print("-" * 80)
    is_valid, error = validator.validate_email("user@example.com")
    print(f"Valid email: is_valid={is_valid}, error='{error}'")
    is_valid, error = validator.validate_email("invalid-email")
    print(f"Invalid email: is_valid={is_valid}, error='{error}'")
    
    # Test phone validation
    print("\n5. Testing validate_phone()...")
    print("-" * 80)
    is_valid, error = validator.validate_phone("510-555-0101")
    print(f"Valid phone: is_valid={is_valid}, error='{error}'")
    is_valid, error = validator.validate_phone("(510) 555-0101")
    print(f"Valid phone (formatted): is_valid={is_valid}, error='{error}'")
    is_valid, error = validator.validate_phone("123")
    print(f"Invalid phone: is_valid={is_valid}, error='{error}'")
    
    # Test numeric range validation
    print("\n6. Testing validate_numeric_range()...")
    print("-" * 80)
    is_valid, error = validator.validate_numeric_range(50.0, min_value=0, max_value=100)
    print(f"Valid range: is_valid={is_valid}, error='{error}'")
    is_valid, error = validator.validate_numeric_range(150.0, min_value=0, max_value=100)
    print(f"Invalid range (too high): is_valid={is_valid}, error='{error}'")
    is_valid, error = validator.validate_numeric_range(-10.0, min_value=0, max_value=100)
    print(f"Invalid range (too low): is_valid={is_valid}, error='{error}'")
    
    print("\n" + "=" * 80)
    print("Test Complete")
    print("=" * 80)


if __name__ == "__main__":
    main()
