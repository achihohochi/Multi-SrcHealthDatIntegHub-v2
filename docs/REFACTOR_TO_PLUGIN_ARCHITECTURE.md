# REFACTOR: Plugin Architecture for Data Sources

**Status:** Not yet implemented (planned for future)  
**Priority:** HIGH - Must complete before adding new file types (PDF, DOCX, etc.)  
**Estimated Effort:** 8-10 hours  
**Target Date:** Before adding PDF support

---

## 🎯 OBJECTIVE

Refactor the current data ingestion pipeline from a rigid if/elif architecture to a flexible plugin system that allows adding new file types without modifying existing code.

---

## 📋 CONTEXT

### Current Problem

The pipeline uses if/elif chains in multiple functions to handle different file types:

```python
# In pipeline.py - this pattern repeats in 3-4 places
if file_type == "csv":
    data = load_csv(filepath)
    # CSV-specific logic
elif file_type == "json":
    data = load_json(filepath)
    # JSON-specific logic
elif file_type == "xml":
    data = load_xml_rss(filepath)
    # XML-specific logic
else:
    # Error - unsupported type
```

**Problems:**
- ❌ Adding new type requires modifying 4 functions in pipeline.py
- ❌ Risk of breaking existing types when adding new ones
- ❌ Difficult to test individual file types in isolation
- ❌ Violates Open/Closed Principle (open for extension, closed for modification)
- ❌ Will become unmaintainable with 10+ file types

### Target Architecture

**Plugin system** where each file type is a self-contained class:

```python
# Adding PDF support becomes:
# 1. Create pdf_source.py (new file)
# 2. Register it: registry.register(PDFDataSource)
# That's it - no pipeline.py changes!
```

---

## 🏗️ IMPLEMENTATION PLAN

### Phase 1: Create Base Infrastructure (2 hours)

**Task 1.1:** Create `src/ingestion/data_sources/` directory structure

```bash
mkdir -p src/ingestion/data_sources
touch src/ingestion/data_sources/__init__.py
```

**Task 1.2:** Create base class `src/ingestion/data_sources/base.py`

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Any

class DataSource(ABC):
    """
    Abstract base class for all data sources.
    
    Each data source type (CSV, JSON, PDF, etc.) implements this interface.
    This allows the pipeline to treat all sources uniformly.
    """
    
    @abstractmethod
    def load(self, filepath: str) -> Any:
        """Load the file and return raw data."""
        pass
    
    @abstractmethod
    def validate(self, data: Any, config: Dict) -> Tuple[bool, List[str]]:
        """Validate the data against requirements."""
        pass
    
    @abstractmethod
    def extract_content_for_tagging(self, data: Any) -> str:
        """Extract text content for domain detection."""
        pass
    
    @abstractmethod
    def prepare_documents(self, data: Any, metadata: Dict, filepath: str) -> List[Dict]:
        """Convert data into vector database documents."""
        pass
    
    @classmethod
    @abstractmethod
    def get_file_type(cls) -> str:
        """Return the file type this source handles (e.g., 'csv', 'pdf')."""
        pass
```

**Task 1.3:** Create registry `src/ingestion/data_sources/registry.py`

```python
from typing import Dict, Type
from .base import DataSource

class DataSourceRegistry:
    """Registry for data source types."""
    
    def __init__(self):
        self._sources: Dict[str, Type[DataSource]] = {}
    
    def register(self, source_class: Type[DataSource]):
        """Register a new data source type."""
        file_type = source_class.get_file_type()
        self._sources[file_type] = source_class
        print(f"Registered data source: {file_type} -> {source_class.__name__}")
    
    def get(self, file_type: str) -> Type[DataSource]:
        """Get data source handler for file type."""
        if file_type not in self._sources:
            available = ", ".join(self._sources.keys())
            raise ValueError(
                f"Unsupported file type: {file_type}. "
                f"Available types: {available}"
            )
        return self._sources[file_type]
    
    def get_supported_types(self) -> List[str]:
        """Return list of supported file types."""
        return list(self._sources.keys())

# Global registry instance
registry = DataSourceRegistry()
```

---

### Phase 2: Refactor Existing Types (4 hours)

**Task 2.1:** Create CSV plugin `src/ingestion/data_sources/csv_source.py`

Extract all CSV-specific logic from:
- `load_csv()` from data_loader.py → `CSVDataSource.load()`
- CSV validation from pipeline.py → `CSVDataSource.validate()`
- CSV content extraction from pipeline.py → `CSVDataSource.extract_content_for_tagging()`
- CSV document prep from pipeline.py → `CSVDataSource.prepare_documents()`

**Task 2.2:** Create JSON plugin `src/ingestion/data_sources/json_source.py`

Extract all JSON-specific logic similar to CSV.

**Task 2.3:** Create XML plugin `src/ingestion/data_sources/xml_source.py`

Extract all XML-specific logic similar to CSV.

**Task 2.4:** Update `src/ingestion/data_sources/__init__.py`

```python
from .base import DataSource
from .registry import registry
from .csv_source import CSVDataSource
from .json_source import JSONDataSource
from .xml_source import XMLDataSource

# Auto-register all sources
registry.register(CSVDataSource)
registry.register(JSONDataSource)
registry.register(XMLDataSource)

__all__ = ['DataSource', 'registry']
```

---

### Phase 3: Refactor Pipeline (2 hours)

**Task 3.1:** Simplify `load_and_validate_source()` in pipeline.py

**BEFORE:**
```python
def load_and_validate_source(self, source_config: Dict):
    if file_type == "csv":
        data = load_csv(filepath)
        is_valid, errors = self.validator.validate_csv(data, required_cols)
    elif file_type == "json":
        data = load_json(filepath)
        is_valid, errors = self.validator.validate_json(data, required_keys)
    elif file_type == "xml":
        # ... 20 more lines
```

**AFTER:**
```python
def load_and_validate_source(self, source_config: Dict):
    from src.ingestion.data_sources import registry
    
    file_type = source_config["type"]
    filepath = source_config["filepath"]
    
    try:
        source_class = registry.get(file_type)
        source = source_class()
        
        data = source.load(filepath)
        is_valid, errors = source.validate(data, source_config)
        
        return (is_valid, data, errors)
    except ValueError as e:
        return (False, None, [str(e)])
    except Exception as e:
        return (False, None, [f"Error: {str(e)}"])
```

**Task 3.2:** Simplify `_extract_content_for_tagging()` in pipeline.py

**BEFORE:** 15+ lines with if/elif

**AFTER:**
```python
def _extract_content_for_tagging(self, data: Any, file_type: str) -> str:
    from src.ingestion.data_sources import registry
    
    try:
        source_class = registry.get(file_type)
        source = source_class()
        return source.extract_content_for_tagging(data)
    except Exception:
        return str(data)[:1000]
```

**Task 3.3:** Simplify `prepare_for_vectordb()` in pipeline.py

**BEFORE:** 80+ lines with nested if/elif

**AFTER:**
```python
def prepare_for_vectordb(self, processed_sources: Dict) -> List[Dict]:
    from src.ingestion.data_sources import registry
    
    documents = []
    
    for source_info in processed_sources["sources"]:
        if source_info["status"] != "success":
            continue
        
        # Get file type from config
        file_type = self._get_file_type_for_source(source_info["filepath"])
        
        try:
            source_class = registry.get(file_type)
            source = source_class()
            
            docs = source.prepare_documents(
                data=source_info["data"],
                metadata=source_info["metadata"],
                filepath=source_info["filepath"]
            )
            documents.extend(docs)
        except Exception as e:
            print(f"Warning: Failed to prepare {source_info['filepath']}: {e}")
    
    return documents
```

**Task 3.4:** Remove validation from pipeline, move to sources

Delete or deprecate `src/ingestion/validator.py` since each source now validates itself.

---

### Phase 4: Testing (2 hours)

**Task 4.1:** Create unit tests for each plugin

```
tests/
  ingestion/
    test_csv_source.py
    test_json_source.py
    test_xml_source.py
```

**Task 4.2:** Integration test - verify existing functionality unchanged

Run the full pipeline and confirm:
- All 6 sources still load correctly
- 113 documents still generated
- Quality report still shows 100%
- Documents have same IDs, text, metadata

**Task 4.3:** Test error handling

- Invalid file types
- Missing required columns/keys
- Corrupted files
- Empty files

---

### Phase 5: Add PDF Support (1 hour) - PROOF IT WORKS

**Task 5.1:** Install PDF library

```bash
pip install PyPDF2
```

**Task 5.2:** Create `src/ingestion/data_sources/pdf_source.py`

Implement all 5 required methods following the pattern from CSV/JSON.

**Task 5.3:** Register PDF source

In `src/ingestion/data_sources/__init__.py`:
```python
from .pdf_source import PDFDataSource
registry.register(PDFDataSource)
```

**Task 5.4:** Add PDF to data sources config

In `pipeline.py __init__()`:
```python
{
    "filepath": "data/internal/plan_coverage_guide.pdf",
    "type": "pdf",
    "min_pages": 1
}
```

**Task 5.5:** Test end-to-end with PDF

Run pipeline and verify PDF loads, validates, and converts to documents.

---

## ✅ SUCCESS CRITERIA

After refactoring, you should be able to:

1. **Add new file type in <1 hour** by creating one new file
2. **No modifications to pipeline.py** when adding new types
3. **Each file type tested independently**
4. **All existing functionality preserved** (113 docs, 100% quality)
5. **Clear error messages** for unsupported types

---

## 🚨 RISKS & MITIGATION

### Risk 1: Breaking existing functionality
**Mitigation:** 
- Create integration tests BEFORE refactoring
- Refactor one type at a time (CSV, then JSON, then XML)
- Keep old code commented out until new code proven

### Risk 2: Validation logic missed during migration
**Mitigation:**
- Create checklist of all validation checks per type
- Verify each check exists in new plugin
- Test with intentionally bad data

### Risk 3: Performance degradation
**Mitigation:**
- Benchmark current pipeline performance
- Compare after refactor
- Registry lookup is O(1), should be negligible

---

## 📊 COMPARISON: Before vs After

| Metric | Before | After |
|--------|--------|-------|
| Lines in pipeline.py | ~450 | ~250 |
| Functions with if/elif | 4 | 0 |
| Files to modify for new type | 4 | 1 |
| Risk of breaking existing | High | Zero |
| Test isolation | Poor | Excellent |
| Scalability | 6 types max | Unlimited |

---

## 🎯 WHEN TO DO THIS

**TIMING:** Before adding PDF support

**WHY NOW:**
- Current system works for 6 sources (good stopping point)
- Have 3 working types (CSV, JSON, XML) to test against
- PDF becomes first new type added to plugin system
- Proves architecture before committing to it

**WHY NOT LATER:**
- Technical debt compounds
- Harder to refactor with 10+ types
- More risk of breaking production code

---

## 📝 USAGE: HOW TO GIVE THIS TO AI

### For Claude in Cursor/VSCode:

**Step 1:** Copy the entire implementation plan above

**Step 2:** Create a new chat and say:

```
I need you to implement the plugin architecture refactor described in:
/Users/chiho/ai-lab/Multi-SrcHealthDatIntegHub/docs/REFACTOR_TO_PLUGIN_ARCHITECTURE.md

Please read this file and implement Phase 1 (Create Base Infrastructure).

Before you start coding:
1. Read the existing pipeline.py to understand current structure
2. Read data_loader.py to see current CSV/JSON/XML loaders
3. Show me your implementation plan for Phase 1

After I approve, implement Phase 1 step by step.
```

**Step 3:** After Phase 1 is done and tested:

```
Phase 1 looks good. Now implement Phase 2 (Refactor Existing Types).
Start with CSV, then JSON, then XML.
Show me CSVDataSource before proceeding to the others.
```

**Step 4:** Continue through phases 3-5

---

## 🔄 ROLLBACK PLAN

If refactor fails:

1. **Keep old code** in `pipeline.py.backup`
2. **Git branch** for refactor (don't work on main)
3. **Can revert** to working state any time
4. **No pressure** - this is architectural improvement, not urgent fix

---

## 📚 REFERENCES

**Design Patterns Used:**
- Strategy Pattern (each source is a strategy)
- Factory Pattern (registry creates appropriate source)
- Adapter Pattern (uniform interface for different formats)

**Additional Reading:**
- Open/Closed Principle (SOLID)
- Plugin Architecture
- Extensibility vs Flexibility

---

## 💡 INTERVIEW TALKING POINTS

When discussing this with PaymentRailsCo:

> "I identified that the current if/elif architecture wouldn't scale beyond 6-10 source types. Before adding PDF support, I designed a plugin architecture using the Strategy pattern. Each file type becomes a self-contained DataSource class with load, validate, extract_content, and prepare_documents methods. A registry maps types to handlers, enabling new sources without pipeline modifications. The refactor takes ~8 hours but eliminates technical debt - adding PDF then takes <1 hour vs 4+ hours in the old system. I've designed the complete architecture and can implement it when adding PDF support."

**Shows:**
- Technical foresight
- Design pattern knowledge
- ROI thinking
- Production vs prototype mindset

---

## ✅ COMPLETION CHECKLIST

- [ ] Phase 1: Base infrastructure created
- [ ] Phase 2: CSV plugin working
- [ ] Phase 2: JSON plugin working
- [ ] Phase 2: XML plugin working
- [ ] Phase 3: Pipeline refactored
- [ ] Phase 4: All tests pass
- [ ] Phase 4: 113 documents still generated
- [ ] Phase 4: 100% quality maintained
- [ ] Phase 5: PDF support added
- [ ] Phase 5: PDF documents in vectordb
- [ ] Documentation updated
- [ ] Old code removed
- [ ] Git committed with clear message

---

**Last Updated:** 2026-01-25  
**Author:** Chiho (with AI assistance)  
**Status:** Detailed plan ready for implementation
