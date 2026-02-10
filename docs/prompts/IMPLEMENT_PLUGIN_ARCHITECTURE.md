# PROMPT: Implement Plugin Architecture for Data Ingestion Pipeline

**Purpose:** Step-by-step instructions for AI coding assistant to refactor data ingestion pipeline  
**Target AI:** Claude Sonnet 4.5, GitHub Copilot, or similar  
**Estimated Time:** 8-10 hours of AI-assisted implementation  
**Complexity:** Medium-High

---

## 🎯 YOUR MISSION

Refactor the current data ingestion pipeline from a rigid if/elif architecture to a flexible plugin system that allows adding new file types (PDF, DOCX, Parquet, etc.) without modifying existing code.

---

## 📋 BEFORE YOU START

### 1. Read These Files First (MANDATORY)

```bash
# Current implementation to understand
src/ingestion/pipeline.py
src/ingestion/data_loader.py
src/ingestion/validator.py
src/ingestion/taxonomy.py

# Architecture plan (context)
docs/REFACTOR_TO_PLUGIN_ARCHITECTURE.md
```

### 2. Understand Current Pain Points

The pipeline currently has **if/elif chains** in 4 functions:
- `load_and_validate_source()` - 30+ lines
- `_extract_content_for_tagging()` - 20+ lines  
- `prepare_for_vectordb()` - 80+ lines

**Problem:** Adding PDF support requires modifying all 4 functions + data_loader.py = 5 files touched, high risk of breaking CSV/JSON/XML.

### 3. Target Architecture

**Plugin system** where each file type is self-contained:

```
src/ingestion/data_sources/
├── __init__.py           # Registry auto-registration
├── base.py               # Abstract DataSource interface
├── registry.py           # Dynamic type lookup
├── csv_source.py         # CSV implementation
├── json_source.py        # JSON implementation
├── xml_source.py         # XML implementation
└── pdf_source.py         # (FUTURE) PDF implementation
```

**Benefit:** Adding PDF = create 1 new file, register it. NO changes to pipeline.py.

---

## 🏗️ IMPLEMENTATION PHASES

---

## PHASE 1: Create Base Infrastructure (START HERE)

**Estimated Time:** 1-2 hours  
**Risk Level:** LOW (no existing code modified)

### Task 1.1: Create Directory Structure

```bash
mkdir -p src/ingestion/data_sources
touch src/ingestion/data_sources/__init__.py
```

### Task 1.2: Create Abstract Base Class

**File:** `src/ingestion/data_sources/base.py`

**Requirements:**
- Use Python ABC (Abstract Base Class)
- Define 5 abstract methods that ALL data sources must implement
- Include comprehensive docstrings explaining what each method does

**Implementation Template:**

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Any

class DataSource(ABC):
    """
    Abstract base class for all data source types.
    
    Each file type (CSV, JSON, PDF, etc.) must implement this interface.
    This enables the pipeline to handle all sources uniformly without
    knowing their internal implementation details.
    
    Design Pattern: Strategy Pattern
    - Each concrete class is a "strategy" for handling one file type
    - Pipeline uses the strategy interface without caring about specifics
    """
    
    @abstractmethod
    def load(self, filepath: str) -> Any:
        """
        Load the file from disk and return parsed data.
        
        Args:
            filepath: Absolute or relative path to the file
            
        Returns:
            Parsed data in appropriate format:
            - CSV: pandas DataFrame
            - JSON: dict or list
            - XML: list of dicts
            - PDF: dict with text/metadata
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file cannot be parsed
            
        Example:
            >>> source = CSVDataSource()
            >>> df = source.load("data/members.csv")
            >>> print(type(df))
            <class 'pandas.DataFrame'>
        """
        pass
    
    @abstractmethod
    def validate(self, data: Any, config: Dict) -> Tuple[bool, List[str]]:
        """
        Validate the loaded data meets requirements.
        
        Args:
            data: The loaded data (from load() method)
            config: Configuration dict with validation rules
                   For CSV: {"required_cols": ["col1", "col2"]}
                   For JSON: {"required_keys": ["key1", "key2"]}
                   For PDF: {"min_pages": 1, "max_size_mb": 10}
                   
        Returns:
            Tuple of (is_valid, errors):
            - is_valid: True if all validations pass
            - errors: List of error messages (empty if valid)
            
        Example:
            >>> source = CSVDataSource()
            >>> df = source.load("data/members.csv")
            >>> is_valid, errors = source.validate(df, {"required_cols": ["member_id"]})
            >>> print(is_valid)
            True
        """
        pass
    
    @abstractmethod
    def extract_content_for_tagging(self, data: Any) -> str:
        """
        Extract text content for taxonomy domain detection.
        
        The taxonomy tagger uses keyword matching to detect domains
        (eligibility, claims, pharmacy, etc.). This method extracts
        representative text from the data for that detection.
        
        Args:
            data: The loaded data (from load() method)
            
        Returns:
            String containing representative content (max ~1000 chars)
            
        Strategy:
            - CSV: column names + sample rows
            - JSON: keys + sample values
            - XML: tag names + sample content
            - PDF: first page text
            
        Example:
            >>> source = CSVDataSource()
            >>> df = source.load("data/members.csv")
            >>> content = source.extract_content_for_tagging(df)
            >>> print(content[:100])
            "member_id first_name last_name plan_type status WHP100001 James Anderson Gold PPO active..."
        """
        pass
    
    @abstractmethod
    def prepare_documents(self, data: Any, metadata: Dict, filepath: str) -> List[Dict]:
        """
        Convert loaded data into documents for vector database.
        
        Each document must have:
        - id: Unique identifier string
        - text: Searchable text content
        - metadata: Dict with source, domain, classification, etc.
        
        Args:
            data: The loaded data (from load() method)
            metadata: Taxonomy metadata (domain, source_type, classification)
            filepath: Original file path
            
        Returns:
            List of document dicts ready for embedding
            
        Strategy by type:
            - CSV: One document per row
            - JSON: One document per array item
            - XML: One document per RSS item
            - PDF: One document for entire PDF (or split by page)
            
        Example:
            >>> source = CSVDataSource()
            >>> df = source.load("data/members.csv")  # 20 rows
            >>> docs = source.prepare_documents(df, metadata, "data/members.csv")
            >>> len(docs)
            20
            >>> print(docs[0])
            {
                "id": "member_eligibility_1",
                "text": "member_id: WHP100001. first_name: James...",
                "metadata": {
                    "domain": "eligibility",
                    "source": "data/members.csv",
                    ...
                }
            }
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_file_type(cls) -> str:
        """
        Return the file type identifier this source handles.
        
        This is used by the registry to map file types to handlers.
        
        Returns:
            File type string (lowercase, no period)
            
        Examples:
            CSVDataSource.get_file_type() -> "csv"
            JSONDataSource.get_file_type() -> "json"
            PDFDataSource.get_file_type() -> "pdf"
        """
        pass
```

**Validation Checklist:**
- [ ] File created at correct path
- [ ] All 5 methods decorated with @abstractmethod
- [ ] Comprehensive docstrings with examples
- [ ] Proper type hints
- [ ] Imports are correct

### Task 1.3: Create Registry

**File:** `src/ingestion/data_sources/registry.py`

**Requirements:**
- Store mapping of file_type → DataSource class
- Provide register() method to add new types
- Provide get() method to retrieve handler for a type
- Raise helpful error if unsupported type requested

**Implementation Template:**

```python
from typing import Dict, Type, List
from .base import DataSource

class DataSourceRegistry:
    """
    Registry for data source type handlers.
    
    Implements Factory Pattern - creates appropriate DataSource
    instance based on file type string.
    
    Usage:
        # Register types (usually done in __init__.py)
        registry.register(CSVDataSource)
        registry.register(JSONDataSource)
        
        # Get handler for a type
        source_class = registry.get("csv")
        source = source_class()
        data = source.load("file.csv")
    """
    
    def __init__(self):
        """Initialize empty registry."""
        self._sources: Dict[str, Type[DataSource]] = {}
    
    def register(self, source_class: Type[DataSource]) -> None:
        """
        Register a data source type.
        
        Args:
            source_class: A class that inherits from DataSource
            
        Raises:
            TypeError: If source_class doesn't inherit from DataSource
            ValueError: If file type already registered
            
        Example:
            >>> from .csv_source import CSVDataSource
            >>> registry.register(CSVDataSource)
            Registered data source: csv -> CSVDataSource
        """
        # Validate it's a DataSource subclass
        if not issubclass(source_class, DataSource):
            raise TypeError(
                f"{source_class.__name__} must inherit from DataSource"
            )
        
        file_type = source_class.get_file_type()
        
        # Check for duplicates
        if file_type in self._sources:
            raise ValueError(
                f"File type '{file_type}' already registered "
                f"to {self._sources[file_type].__name__}"
            )
        
        self._sources[file_type] = source_class
        print(f"✓ Registered data source: {file_type} -> {source_class.__name__}")
    
    def get(self, file_type: str) -> Type[DataSource]:
        """
        Get data source handler class for file type.
        
        Args:
            file_type: File type string (e.g., "csv", "json", "pdf")
            
        Returns:
            DataSource subclass (not instance - you must instantiate it)
            
        Raises:
            ValueError: If file type not registered
            
        Example:
            >>> source_class = registry.get("csv")
            >>> source = source_class()  # Instantiate it
            >>> data = source.load("file.csv")
        """
        if file_type not in self._sources:
            available = ", ".join(self.get_supported_types())
            raise ValueError(
                f"Unsupported file type: '{file_type}'. "
                f"Registered types: {available}"
            )
        
        return self._sources[file_type]
    
    def get_supported_types(self) -> List[str]:
        """
        Return list of registered file types.
        
        Returns:
            List of file type strings
            
        Example:
            >>> registry.get_supported_types()
            ['csv', 'json', 'xml']
        """
        return sorted(list(self._sources.keys()))
    
    def is_supported(self, file_type: str) -> bool:
        """
        Check if file type is supported.
        
        Args:
            file_type: File type to check
            
        Returns:
            True if registered, False otherwise
            
        Example:
            >>> registry.is_supported("csv")
            True
            >>> registry.is_supported("pdf")
            False
        """
        return file_type in self._sources

# Global singleton instance
registry = DataSourceRegistry()
```

**Validation Checklist:**
- [ ] File created at correct path
- [ ] Registry stores type → class mapping
- [ ] Helpful error messages
- [ ] get_supported_types() for debugging
- [ ] Singleton pattern (one global instance)

### Task 1.4: Verify Phase 1

Run this test:

```python
# Test in Python REPL or create test file
from src.ingestion.data_sources.base import DataSource
from src.ingestion.data_sources.registry import registry

# Should work without errors
print("✓ Base infrastructure created")
print(f"✓ Registry initialized: {registry}")
```

**Checkpoint:** Before proceeding to Phase 2, confirm:
- [ ] Directory created: `src/ingestion/data_sources/`
- [ ] `base.py` exists with DataSource ABC
- [ ] `registry.py` exists with DataSourceRegistry class
- [ ] No import errors when importing both
- [ ] Ready to create concrete implementations

---

## PHASE 2: Create CSV Plugin (REFERENCE IMPLEMENTATION)

**Estimated Time:** 1-2 hours  
**Risk Level:** LOW (new file, doesn't modify existing code yet)

This is your REFERENCE implementation. JSON and XML will follow the same pattern.

### Task 2.1: Create CSV Data Source

**File:** `src/ingestion/data_sources/csv_source.py`

**Requirements:**
- Implement ALL 5 methods from DataSource interface
- Extract logic from current `load_csv()`, `validate_csv()`, etc.
- Each method should be self-contained and testable

**Where to find current logic:**
- `load()` → Copy from `data_loader.py::load_csv()`
- `validate()` → Copy from `validator.py::validate_csv()`
- `extract_content_for_tagging()` → Copy from `pipeline.py::_extract_content_for_tagging()` CSV branch
- `prepare_documents()` → Copy from `pipeline.py::prepare_for_vectordb()` CSV branch

**Implementation Guide:**

```python
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime
from .base import DataSource

class CSVDataSource(DataSource):
    """
    Data source handler for CSV files.
    
    Encapsulates all CSV-specific logic for loading, validation,
    content extraction, and document preparation.
    
    Expected data format after load(): pandas DataFrame
    """
    
    @classmethod
    def get_file_type(cls) -> str:
        """Return 'csv' as the file type identifier."""
        return "csv"
    
    def load(self, filepath: str) -> pd.DataFrame:
        """
        Load CSV file into pandas DataFrame.
        
        COPY LOGIC FROM: data_loader.py::load_csv()
        
        Steps:
        1. Validate filepath is string
        2. Convert to Path object
        3. Check file exists
        4. Use pd.read_csv()
        5. Handle common errors with helpful messages
        
        Returns:
            pandas DataFrame with CSV data
        """
        # TODO: Copy implementation from data_loader.py::load_csv()
        # HINT: This is ~40 lines of code
        pass
    
    def validate(self, data: pd.DataFrame, config: Dict) -> Tuple[bool, List[str]]:
        """
        Validate DataFrame has required columns and no null values.
        
        COPY LOGIC FROM: validator.py::validate_csv()
        
        Config keys used:
        - required_cols: List of column names that must exist
        
        Checks:
        1. DataFrame not empty
        2. Required columns present
        3. No null values in required columns
        
        Returns:
            (is_valid, errors) tuple
        """
        # TODO: Copy implementation from validator.py::validate_csv()
        # HINT: This is ~20 lines of code
        pass
    
    def extract_content_for_tagging(self, data: pd.DataFrame) -> str:
        """
        Extract column names + sample rows for domain detection.
        
        COPY LOGIC FROM: pipeline.py::_extract_content_for_tagging() CSV branch
        
        Strategy:
        - Include all column names (for keyword matching)
        - Include first 5 rows as sample data
        - Format: "col1 col2 col3 row1data row2data..."
        
        Returns:
            String with column names and sample rows
        """
        # TODO: Copy from pipeline.py::_extract_content_for_tagging()
        # Look for: if data_type == "csv" branch
        # HINT: This is ~2 lines of code
        pass
    
    def prepare_documents(self, data: pd.DataFrame, metadata: Dict, filepath: str) -> List[Dict]:
        """
        Convert each DataFrame row into a document.
        
        COPY LOGIC FROM: pipeline.py::prepare_for_vectordb() CSV branch
        
        Strategy:
        - Loop through DataFrame rows with iterrows()
        - Create unique ID: {source_name}_{row_number}
        - Convert row to text: "col1: val1. col2: val2. ..."
        - Attach metadata from taxonomy
        
        Returns:
            List of document dicts with id, text, metadata
        """
        # TODO: Copy from pipeline.py::prepare_for_vectordb()
        # Look for: if data_type == "csv" and isinstance(data, pd.DataFrame) branch
        # HINT: This is ~30 lines of code
        
        # Helper method for row-to-text conversion
        def _row_to_text(row: pd.Series) -> str:
            """Convert DataFrame row to readable text string."""
            parts = []
            for col, val in row.items():
                if pd.notna(val):  # Skip NaN/None values
                    parts.append(f"{col}: {val}")
            return ". ".join(parts)
        
        # Your implementation here
        pass
```

**Testing Task 2.1:**

Create test file `tests/test_csv_source.py`:

```python
from src.ingestion.data_sources.csv_source import CSVDataSource
import pandas as pd

def test_csv_source():
    source = CSVDataSource()
    
    # Test load
    df = source.load("data/internal/member_eligibility.csv")
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 20  # Should have 20 members
    
    # Test validate
    config = {"required_cols": ["member_id", "status", "plan_type"]}
    is_valid, errors = source.validate(df, config)
    assert is_valid == True
    assert len(errors) == 0
    
    # Test extract_content
    content = source.extract_content_for_tagging(df)
    assert "member_id" in content
    assert "status" in content
    
    # Test prepare_documents
    metadata = {"domain": "eligibility", "source_type": "internal"}
    docs = source.prepare_documents(df, metadata, "data/internal/member_eligibility.csv")
    assert len(docs) == 20
    assert docs[0]["id"] == "member_eligibility_1"
    assert "WHP100001" in docs[0]["text"]
    
    print("✓ All CSV source tests passed")

if __name__ == "__main__":
    test_csv_source()
```

Run: `python tests/test_csv_source.py`

**Validation Checklist:**
- [ ] `csv_source.py` created
- [ ] All 5 methods implemented
- [ ] Logic copied from existing code
- [ ] Test file passes
- [ ] No modifications to existing files yet

---

## PHASE 3: Create JSON and XML Plugins

**Estimated Time:** 2-3 hours  
**Risk Level:** LOW

Follow the exact same pattern as CSV:

### Task 3.1: Create JSON Data Source

**File:** `src/ingestion/data_sources/json_source.py`

**Copy logic from:**
- `load()` → `data_loader.py::load_json()`
- `validate()` → `validator.py::validate_json()`
- `extract_content_for_tagging()` → `pipeline.py` JSON branch
- `prepare_documents()` → `pipeline.py` JSON branch

**Note:** JSON is more complex because it handles arrays (claims, drugs, providers).

### Task 3.2: Create XML Data Source

**File:** `src/ingestion/data_sources/xml_source.py`

**Copy logic from:**
- `load()` → `data_loader.py::load_xml_rss()`
- `validate()` → `pipeline.py` XML validation (basic list check)
- `extract_content_for_tagging()` → `pipeline.py` XML branch
- `prepare_documents()` → `pipeline.py` XML branch

### Task 3.3: Test JSON and XML

Create similar test files and verify they work with existing data.

---

## PHASE 4: Register All Plugins

**Estimated Time:** 15 minutes  
**Risk Level:** LOW

### Task 4.1: Update `__init__.py`

**File:** `src/ingestion/data_sources/__init__.py`

```python
"""
Data source plugins for ingestion pipeline.

To add a new data source type:
1. Create {type}_source.py implementing DataSource interface
2. Import it here
3. Call registry.register()

No pipeline.py modifications needed!
"""

from .base import DataSource
from .registry import registry
from .csv_source import CSVDataSource
from .json_source import JSONDataSource
from .xml_source import XMLDataSource

# Auto-register all data source types
registry.register(CSVDataSource)
registry.register(JSONDataSource)
registry.register(XMLDataSource)

__all__ = ['DataSource', 'registry', 'CSVDataSource', 'JSONDataSource', 'XMLDataSource']
```

### Task 4.2: Verify Registration

```python
from src.ingestion.data_sources import registry

print("Supported types:", registry.get_supported_types())
# Should print: ['csv', 'json', 'xml']

# Test getting a handler
csv_class = registry.get("csv")
print("CSV handler:", csv_class)  # Should print: <class 'CSVDataSource'>

# Test error handling
try:
    pdf_class = registry.get("pdf")
except ValueError as e:
    print("Expected error:", e)
    # Should print: "Unsupported file type: 'pdf'. Registered types: csv, json, xml"
```

---

## PHASE 5: Refactor Pipeline to Use Plugins

**Estimated Time:** 2-3 hours  
**Risk Level:** MEDIUM (modifying existing code)

### CRITICAL: Make a Backup First

```bash
cp src/ingestion/pipeline.py src/ingestion/pipeline.py.backup
```

### Task 5.1: Simplify `load_and_validate_source()`

**Find this function in pipeline.py:**

Currently ~50 lines with if/elif for each type.

**Replace with:**

```python
def load_and_validate_source(self, source_config: Dict) -> Tuple[bool, Any, List[str]]:
    """
    Load and validate using plugin architecture.
    
    NO MORE IF/ELIF CHAINS!
    The registry handles type dispatch.
    """
    from src.ingestion.data_sources import registry
    
    filepath = source_config.get("filepath")
    file_type = source_config.get("type", "").lower()
    
    try:
        # Get appropriate handler from registry
        source_class = registry.get(file_type)
        source = source_class()
        
        # Load the data
        data = source.load(filepath)
        
        # Validate the data
        is_valid, errors = source.validate(data, source_config)
        
        return (is_valid, data, errors)
        
    except ValueError as e:
        # Unsupported file type
        return (False, None, [str(e)])
    except Exception as e:
        # Any other error
        return (False, None, [f"Error loading {filepath}: {str(e)}"])
```

**Before/After comparison:**

BEFORE: 50 lines, 3 if/elif branches  
AFTER: 20 lines, ZERO if/elif branches

### Task 5.2: Simplify `_extract_content_for_tagging()`

**Find this function in pipeline.py:**

Currently ~15 lines with if/elif for each type.

**Replace with:**

```python
def _extract_content_for_tagging(self, data: Any, data_type: str) -> str:
    """
    Extract content using plugin.
    
    NO MORE IF/ELIF CHAINS!
    """
    from src.ingestion.data_sources import registry
    
    try:
        source_class = registry.get(data_type)
        source = source_class()
        return source.extract_content_for_tagging(data)
    except Exception as e:
        # Fallback for any errors
        return str(data)[:1000]
```

**Before/After comparison:**

BEFORE: 15 lines, 4 if/elif branches  
AFTER: 8 lines, ZERO if/elif branches

### Task 5.3: Simplify `prepare_for_vectordb()`

**Find this function in pipeline.py:**

Currently ~100 lines with nested if/elif for each type.

**Replace with:**

```python
def prepare_for_vectordb(self, processed_sources: Dict) -> List[Dict]:
    """
    Prepare documents using plugins.
    
    NO MORE IF/ELIF CHAINS!
    Each source type knows how to convert itself.
    """
    from src.ingestion.data_sources import registry
    
    documents = []
    
    for source_info in processed_sources["sources"]:
        # Skip failed sources
        if source_info["status"] != "success" or source_info["data"] is None:
            continue
        
        filepath = source_info["filepath"]
        file_type = self._get_file_type_from_config(filepath)
        
        try:
            # Get appropriate handler
            source_class = registry.get(file_type)
            source = source_class()
            
            # Let the source convert itself to documents
            docs = source.prepare_documents(
                data=source_info["data"],
                metadata=source_info["metadata"],
                filepath=filepath
            )
            
            documents.extend(docs)
            
        except Exception as e:
            print(f"⚠️  Warning: Failed to prepare {filepath}: {e}")
            continue
    
    return documents

def _get_file_type_from_config(self, filepath: str) -> str:
    """Helper to get file type from data_sources config."""
    for config in self.data_sources:
        if config["filepath"] == filepath:
            return config["type"]
    # Fallback: guess from extension
    return Path(filepath).suffix[1:]  # .csv -> csv
```

**Before/After comparison:**

BEFORE: 100 lines, nested if/elif/elif  
AFTER: 35 lines, ZERO if/elif branches

---

## PHASE 6: Testing & Validation

**Estimated Time:** 2 hours  
**Risk Level:** CRITICAL (verifying nothing broke)

### Task 6.1: Integration Test - Run Full Pipeline

```bash
cd /Users/chiho/ai-lab/Multi-SrcHealthDatIntegHub
python src/ingestion/pipeline.py
```

**Expected output:**

```
Initializing Ingestion Pipeline...
✓ Registered data source: csv -> CSVDataSource
✓ Registered data source: json -> JSONDataSource
✓ Registered data source: xml -> XMLDataSource

Processing all data sources...

✓ Prepared 113 documents for vector database

Generating report...

================================================================================
DATA INGESTION PIPELINE REPORT
================================================================================
...
Total Sources: 6
Successful: 6 ✓
Failed: 0 ✗
Quality Score: 100.0%
================================================================================
```

**Validation checklist:**
- [ ] All 6 sources load successfully
- [ ] 113 documents prepared (same as before)
- [ ] Quality score: 100%
- [ ] No errors in console

### Task 6.2: Document Comparison Test

Create `tests/test_refactor_comparison.py`:

```python
"""
Compare documents before and after refactor.
Ensures refactor didn't change output.
"""

import json
from src.ingestion.pipeline import IngestionPipeline

def test_document_output_unchanged():
    """Verify refactored pipeline produces identical documents."""
    
    # Run new pipeline
    pipeline = IngestionPipeline()
    results = pipeline.process_all_sources()
    documents = pipeline.prepare_for_vectordb(results)
    
    # Checks
    assert len(documents) == 113, f"Expected 113 docs, got {len(documents)}"
    
    # Verify member_eligibility documents
    member_docs = [d for d in documents if d["id"].startswith("member_eligibility")]
    assert len(member_docs) == 20, f"Expected 20 member docs, got {len(member_docs)}"
    
    # Verify claims documents
    claims_docs = [d for d in documents if d["id"].startswith("claims_history")]
    assert len(claims_docs) == 10, f"Expected 10 claims docs, got {len(claims_docs)}"
    
    # Verify benefits documents
    benefits_docs = [d for d in documents if d["id"].startswith("benefits_summary")]
    assert len(benefits_docs) == 60, f"Expected 60 benefits docs, got {len(benefits_docs)}"
    
    # Spot check: verify first member doc has correct structure
    first_member = member_docs[0]
    assert first_member["id"] == "member_eligibility_1"
    assert "WHP100001" in first_member["text"]
    assert first_member["metadata"]["domain"] == "eligibility"
    assert first_member["metadata"]["source_type"] == "internal"
    
    print("✓ All document output tests passed - refactor successful!")

if __name__ == "__main__":
    test_document_output_unchanged()
```

Run: `python tests/test_refactor_comparison.py`

### Task 6.3: Edge Case Testing

Test error handling:

```python
from src.ingestion.data_sources import registry

# Test 1: Unsupported type
try:
    registry.get("pdf")
    assert False, "Should have raised error"
except ValueError as e:
    assert "pdf" in str(e).lower()
    print("✓ Unsupported type error handling works")

# Test 2: Invalid file path
from src.ingestion.data_sources.csv_source import CSVDataSource
source = CSVDataSource()
try:
    source.load("nonexistent.csv")
    assert False, "Should have raised error"
except FileNotFoundError:
    print("✓ Missing file error handling works")

# Test 3: Missing required columns
import pandas as pd
df = pd.DataFrame({"wrong_col": [1, 2, 3]})
is_valid, errors = source.validate(df, {"required_cols": ["member_id"]})
assert is_valid == False
assert len(errors) > 0
print("✓ Validation error handling works")
```

---

## PHASE 7: Cleanup & Documentation

**Estimated Time:** 30 minutes  
**Risk Level:** LOW

### Task 7.1: Remove Old Validation Code (Optional)

**File:** `src/ingestion/validator.py`

This file is now mostly unused since each source validates itself.

**Options:**
1. Delete it entirely (aggressive)
2. Keep it but add deprecation notice (safe)
3. Keep it for backward compatibility (safest)

**Recommendation:** Add deprecation notice for now:

```python
# At top of validator.py
"""
DEPRECATED: This module is being phased out in favor of plugin architecture.

Each data source type now handles its own validation in:
- src/ingestion/data_sources/csv_source.py
- src/ingestion/data_sources/json_source.py
- src/ingestion/data_sources/xml_source.py

This file is kept for backward compatibility only.
"""
```

### Task 7.2: Update README

Add section to project README:

```markdown
## Data Source Plugin Architecture

The data ingestion pipeline uses a plugin architecture for handling different file types.

### Adding a New File Type

1. Create a new file in `src/ingestion/data_sources/{type}_source.py`
2. Implement the `DataSource` interface (5 required methods)
3. Register it in `src/ingestion/data_sources/__init__.py`

Example for PDF:

```python
from .base import DataSource

class PDFDataSource(DataSource):
    @classmethod
    def get_file_type(cls): return "pdf"
    
    def load(self, filepath): ...
    def validate(self, data, config): ...
    def extract_content_for_tagging(self, data): ...
    def prepare_documents(self, data, metadata, filepath): ...
```

Then register:

```python
# In __init__.py
from .pdf_source import PDFDataSource
registry.register(PDFDataSource)
```

No modifications to `pipeline.py` needed!
```

### Task 7.3: Git Commit

```bash
git add src/ingestion/data_sources/
git add src/ingestion/pipeline.py
git commit -m "refactor: Implement plugin architecture for data sources

- Create DataSource abstract base class
- Implement registry for dynamic type lookup  
- Refactor CSV, JSON, XML into plugins
- Simplify pipeline.py (removed all if/elif chains)
- Add comprehensive tests
- Maintains 100% backward compatibility (113 docs, 100% quality)

Enables adding new file types (PDF, DOCX, etc.) without modifying pipeline code."
```

---

## 🎯 COMPLETION CHECKLIST

### Phase 1: Base Infrastructure
- [ ] `data_sources/` directory created
- [ ] `base.py` with DataSource ABC
- [ ] `registry.py` with DataSourceRegistry
- [ ] `__init__.py` created
- [ ] No import errors

### Phase 2-3: Plugin Implementations
- [ ] `csv_source.py` created and tested
- [ ] `json_source.py` created and tested
- [ ] `xml_source.py` created and tested
- [ ] All plugins registered in `__init__.py`

### Phase 4-5: Pipeline Refactor
- [ ] Backup created: `pipeline.py.backup`
- [ ] `load_and_validate_source()` simplified
- [ ] `_extract_content_for_tagging()` simplified
- [ ] `prepare_for_vectordb()` simplified
- [ ] All if/elif chains removed

### Phase 6: Testing
- [ ] Full pipeline runs successfully
- [ ] 113 documents generated
- [ ] 100% quality score
- [ ] Document comparison test passes
- [ ] Error handling tests pass

### Phase 7: Cleanup
- [ ] Deprecation notices added
- [ ] README updated
- [ ] Code committed to git
- [ ] Old backup files deleted (after verification)

---

## 🚀 SUCCESS CRITERIA

After completing all phases, you should achieve:

1. ✅ **Zero breaking changes** - All 113 documents still generated
2. ✅ **Simplified code** - Pipeline.py reduced by ~150 lines
3. ✅ **Extensible architecture** - Adding PDF takes <1 hour
4. ✅ **Better testing** - Each source type testable in isolation
5. ✅ **Maintainable** - No more if/elif chains

---

## 🆘 TROUBLESHOOTING

### Issue: "ModuleNotFoundError: No module named 'src'"

**Cause:** Python can't find the src package

**Fix:**
```bash
cd /Users/chiho/ai-lab/Multi-SrcHealthDatIntegHub
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

Or add to start of test files:
```python
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
```

### Issue: "ValueError: Unsupported file type: csv"

**Cause:** Source not registered

**Fix:** Check `data_sources/__init__.py` has:
```python
from .csv_source import CSVDataSource
registry.register(CSVDataSource)
```

### Issue: Documents different after refactor

**Cause:** Logic copied incorrectly from old code

**Fix:** 
1. Compare old `pipeline.py.backup` with new implementation
2. Check each method in plugin matches original logic exactly
3. Run document comparison test to see specific differences

---

## 📊 METRICS

Track these metrics before and after refactor:

| Metric | Before | Target After |
|--------|--------|--------------|
| pipeline.py lines | ~450 | ~300 |
| Functions with if/elif | 4 | 0 |
| Files to modify for new type | 5 | 1 |
| Test isolation | Poor | Excellent |
| Time to add PDF | 4+ hours | <1 hour |

---

## 🎓 LEARNING OUTCOMES

After implementing this refactor, you'll understand:

- **Strategy Pattern** - Different strategies (CSV, JSON, XML) for same interface
- **Factory Pattern** - Registry creates appropriate handler based on type
- **Open/Closed Principle** - Open for extension (new plugins), closed for modification (pipeline)
- **Separation of Concerns** - Each plugin owns its own loading/validation/conversion logic
- **Plugin Architecture** - How to design extensible systems

---

**END OF IMPLEMENTATION GUIDE**

When complete, you'll have a production-ready, scalable data ingestion system! 🚀
