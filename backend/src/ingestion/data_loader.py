"""
Data loading utilities for health data integration.

This module provides functions to load and parse various data formats
including CSV, JSON, and XML/RSS feeds with comprehensive error handling.
"""

import json
from pathlib import Path
from typing import Dict, List

import pandas as pd
import feedparser


def load_csv(filepath: str) -> pd.DataFrame:
    """
    Load a CSV file and return it as a pandas DataFrame.
    
    This function validates that the file exists, handles common CSV parsing
    errors, and returns a properly formatted DataFrame. Supports standard CSV
    formats with automatic type inference.
    
    Args:
        filepath: Path to the CSV file to load. Can be relative or absolute.
        
    Returns:
        pandas.DataFrame: The loaded CSV data as a DataFrame.
        
    Raises:
        FileNotFoundError: If the specified file does not exist.
        pd.errors.EmptyDataError: If the CSV file is empty.
        pd.errors.ParserError: If the CSV file cannot be parsed.
        PermissionError: If the file cannot be read due to permissions.
        ValueError: If the filepath is invalid or empty.
        
    Example:
        >>> df = load_csv('data/internal/member_eligibility.csv')
        >>> print(df.head())
    """
    if not filepath or not isinstance(filepath, str):
        raise ValueError(f"Invalid filepath provided: {filepath}")
    
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(
            f"CSV file not found: {filepath}. "
            f"Please verify the file path is correct."
        )
    
    if not filepath.is_file():
        raise ValueError(f"Path exists but is not a file: {filepath}")
    
    try:
        df = pd.read_csv(filepath)
        return df
    except pd.errors.EmptyDataError as e:
        raise pd.errors.EmptyDataError(
            f"CSV file is empty: {filepath}"
        ) from e
    except pd.errors.ParserError as e:
        raise pd.errors.ParserError(
            f"Failed to parse CSV file {filepath}. "
            f"Please check the file format. Error: {str(e)}"
        ) from e
    except PermissionError as e:
        raise PermissionError(
            f"Permission denied reading CSV file: {filepath}"
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"Unexpected error loading CSV file {filepath}: {str(e)}"
        ) from e


def load_json(filepath: str) -> Dict:
    """
    Load a JSON file and return it as a Python dictionary.
    
    This function validates that the file exists, checks for valid JSON syntax,
    and handles common JSON parsing errors with informative error messages.
    
    Args:
        filepath: Path to the JSON file to load. Can be relative or absolute.
        
    Returns:
        dict: The loaded JSON data as a Python dictionary.
        
    Raises:
        FileNotFoundError: If the specified file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON syntax.
        PermissionError: If the file cannot be read due to permissions.
        ValueError: If the filepath is invalid or empty, or if JSON is not a dict.
        
    Example:
        >>> data = load_json('data/internal/claims_history.json')
        >>> print(data.keys())
    """
    if not filepath or not isinstance(filepath, str):
        raise ValueError(f"Invalid filepath provided: {filepath}")
    
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(
            f"JSON file not found: {filepath}. "
            f"Please verify the file path is correct."
        )
    
    if not filepath.is_file():
        raise ValueError(f"Path exists but is not a file: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, dict):
            raise ValueError(
                f"JSON file {filepath} does not contain a dictionary. "
                f"Found type: {type(data).__name__}"
            )
        
        return data
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON syntax in file {filepath}",
            e.doc,
            e.pos
        ) from e
    except PermissionError as e:
        raise PermissionError(
            f"Permission denied reading JSON file: {filepath}"
        ) from e
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(
            f"Unable to decode JSON file {filepath} as UTF-8. "
            f"Please check file encoding."
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"Unexpected error loading JSON file {filepath}: {str(e)}"
        ) from e


def load_xml_rss(filepath: str) -> List[Dict]:
    """
    Load an XML/RSS feed file and parse it into a list of item dictionaries.
    
    This function uses feedparser to parse RSS/XML feeds and extracts key
    fields from each item: title, link, pubDate, description, and category.
    Handles various RSS formats and common feed structures.
    
    Args:
        filepath: Path to the XML/RSS feed file to load. Can be relative or absolute.
        
    Returns:
        list[dict]: A list of dictionaries, each containing parsed RSS item data.
                    Each dictionary contains keys: 'title', 'link', 'pubDate',
                    'description', and 'category'.
        
    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If the filepath is invalid, empty, or feed cannot be parsed.
        PermissionError: If the file cannot be read due to permissions.
        RuntimeError: If feedparser encounters an unexpected error.
        
    Example:
        >>> items = load_xml_rss('data/external/cms_policy_updates.xml')
        >>> print(f"Found {len(items)} items")
        >>> print(items[0]['title'])
    """
    if not filepath or not isinstance(filepath, str):
        raise ValueError(f"Invalid filepath provided: {filepath}")
    
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(
            f"XML/RSS file not found: {filepath}. "
            f"Please verify the file path is correct."
        )
    
    if not filepath.is_file():
        raise ValueError(f"Path exists but is not a file: {filepath}")
    
    try:
        feed = feedparser.parse(str(filepath))
        
        if feed.bozo and feed.bozo_exception:
            raise ValueError(
                f"Failed to parse XML/RSS feed {filepath}. "
                f"Error: {feed.bozo_exception}"
            )
        
        if not hasattr(feed, 'entries') or not feed.entries:
            raise ValueError(
                f"XML/RSS feed {filepath} contains no entries. "
                f"Please verify the feed structure."
            )
        
        items = []
        for entry in feed.entries:
            item = {
                'title': getattr(entry, 'title', ''),
                'link': getattr(entry, 'link', ''),
                'pubDate': getattr(entry, 'published', getattr(entry, 'pubDate', '')),
                'description': getattr(entry, 'description', ''),
                'category': getattr(entry, 'category', '')
            }
            items.append(item)
        
        return items
    except PermissionError as e:
        raise PermissionError(
            f"Permission denied reading XML/RSS file: {filepath}"
        ) from e
    except Exception as e:
        if isinstance(e, (ValueError, FileNotFoundError, PermissionError)):
            raise
        raise RuntimeError(
            f"Unexpected error loading XML/RSS file {filepath}: {str(e)}"
        ) from e


def main():
    """
    Test all three data loading functions with sample data files.
    
    This function demonstrates usage of load_csv, load_json, and load_xml_rss
    with the project's data files and prints summary information about each.
    """
    print("=" * 70)
    print("Testing Data Loader Functions")
    print("=" * 70)
    
    # Test CSV loading
    print("\n1. Testing load_csv()...")
    print("-" * 70)
    try:
        csv_path = "data/internal/member_eligibility.csv"
        df = load_csv(csv_path)
        print(f"✓ Successfully loaded CSV: {csv_path}")
        print(f"  Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"  Columns: {', '.join(df.columns.tolist())}")
        print(f"  First few rows:")
        print(df.head(3).to_string(index=False))
    except Exception as e:
        print(f"✗ Error loading CSV: {type(e).__name__}: {e}")
    
    # Test JSON loading
    print("\n2. Testing load_json()...")
    print("-" * 70)
    try:
        json_path = "data/internal/claims_history.json"
        data = load_json(json_path)
        print(f"✓ Successfully loaded JSON: {json_path}")
        print(f"  Top-level keys: {', '.join(data.keys())}")
        if 'claims' in data:
            print(f"  Number of claims: {len(data['claims'])}")
            if data['claims']:
                print(f"  Sample claim keys: {', '.join(data['claims'][0].keys())}")
    except Exception as e:
        print(f"✗ Error loading JSON: {type(e).__name__}: {e}")
    
    # Test XML/RSS loading
    print("\n3. Testing load_xml_rss()...")
    print("-" * 70)
    try:
        xml_path = "data/external/cms_policy_updates.xml"
        items = load_xml_rss(xml_path)
        print(f"✓ Successfully loaded XML/RSS: {xml_path}")
        print(f"  Number of items: {len(items)}")
        if items:
            print(f"  Sample item keys: {', '.join(items[0].keys())}")
            print(f"  First item title: {items[0]['title']}")
            print(f"  First item category: {items[0]['category']}")
    except Exception as e:
        print(f"✗ Error loading XML/RSS: {type(e).__name__}: {e}")
    
    print("\n" + "=" * 70)
    print("Testing Complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
