"""
Data ingestion pipeline for health data integration.

This module integrates data loading, validation, and taxonomy tagging into a
unified pipeline that processes multiple data sources and prepares them for
vector database ingestion.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.ingestion.data_loader import load_csv, load_json, load_xml_rss
from src.ingestion.taxonomy import TaxonomyTagger
from src.ingestion.validator import DataValidator


class IngestionPipeline:
    """
    Integrated pipeline for loading, validating, and tagging health data sources.
    
    The IngestionPipeline orchestrates the complete data ingestion workflow:
    loading data from various formats, validating against schemas, applying
    taxonomy tags, and preparing documents for vector database storage.
    
    Example:
        >>> pipeline = IngestionPipeline()
        >>> results = pipeline.process_all_sources()
        >>> documents = pipeline.prepare_for_vectordb(results)
        >>> report = pipeline.generate_report(results)
        >>> print(report)
    """
    
    def __init__(self):
        """
        Initialize the ingestion pipeline with tagger, validator, and data sources.
        
        Sets up the TaxonomyTagger and DataValidator instances, and defines
        the configuration for all data sources to be processed.
        """
        self.tagger = TaxonomyTagger()
        self.validator = DataValidator()
        
        self.data_sources = [
            {
                "filepath": "data/internal/member_eligibility.csv",
                "type": "csv",
                "required_cols": ["member_id", "status", "plan_type"]
            },
            {
                "filepath": "data/internal/claims_history.json",
                "type": "json",
                "required_keys": ["claims"]
            },
            {
                "filepath": "data/internal/benefits_summary.csv",
                "type": "csv",
                "required_cols": ["plan_type", "service_category"]
            },
            {
                "filepath": "data/external/cms_policy_updates.xml",
                "type": "xml",
                "required_keys": []
            },
            {
                "filepath": "data/external/fda_drug_database.json",
                "type": "json",
                "required_keys": ["drugs"]
            },
            {
                "filepath": "data/external/provider_directory.json",
                "type": "json",
                "required_keys": ["providers"]
            }
        ]
    
    def load_and_validate_source(self, source_config: Dict) -> Tuple[bool, any, List[str]]:
        """
        Load and validate a single data source.
        
        Loads the file based on its type (csv/json/xml) and validates it
        against the required schema (columns or keys).
        
        Args:
            source_config: Dictionary containing:
                - filepath: Path to the data file
                - type: File type ("csv", "json", or "xml")
                - required_cols: List of required columns (for CSV)
                - required_keys: List of required keys (for JSON/XML)
                
        Returns:
            Tuple[bool, any, List[str]]: A tuple containing:
                - is_valid: True if loading and validation succeeded
                - data: The loaded data (DataFrame for CSV, dict/list for JSON/XML)
                - errors: List of error messages if validation failed
                
        Example:
            >>> pipeline = IngestionPipeline()
            >>> config = {"filepath": "data/internal/members.csv", "type": "csv", "required_cols": ["member_id"]}
            >>> is_valid, data, errors = pipeline.load_and_validate_source(config)
        """
        filepath = source_config.get("filepath")
        file_type = source_config.get("type", "").lower()
        errors = []
        data = None
        
        try:
            # Load data based on type
            if file_type == "csv":
                data = load_csv(filepath)
                # Validate CSV
                required_cols = source_config.get("required_cols", [])
                is_valid, validation_errors = self.validator.validate_csv(data, required_cols)
                errors.extend(validation_errors)
                
            elif file_type == "json":
                data = load_json(filepath)
                # Validate JSON
                required_keys = source_config.get("required_keys", [])
                is_valid, validation_errors = self.validator.validate_json(data, required_keys)
                errors.extend(validation_errors)
                
            elif file_type == "xml":
                data = load_xml_rss(filepath)
                # XML/RSS validation (basic check for empty list)
                if not isinstance(data, list) or len(data) == 0:
                    errors.append("XML/RSS feed contains no items")
                    is_valid = False
                else:
                    is_valid = True
                    
            else:
                errors.append(f"Unsupported file type: {file_type}")
                is_valid = False
                
        except Exception as e:
            errors.append(f"Error loading {filepath}: {str(e)}")
            is_valid = False
        
        return (is_valid, data, errors)
    
    def process_all_sources(self) -> Dict:
        """
        Process all configured data sources.
        
        Iterates through all data sources, loads and validates each one,
        applies taxonomy tags, and tracks success/failure status.
        
        Returns:
            Dict: A dictionary containing:
                - sources: List of processed source results with status, data, metadata, and errors
                - summary: Overall statistics including total, successful, failed counts and quality score
                
        Example:
            >>> pipeline = IngestionPipeline()
            >>> results = pipeline.process_all_sources()
            >>> print(f"Processed {results['summary']['total']} sources")
        """
        processed_sources = []
        
        for source_config in self.data_sources:
            filepath = source_config["filepath"]
            
            # Load and validate
            is_valid, data, errors = self.load_and_validate_source(source_config)
            
            # Generate taxonomy tags
            metadata = None
            if is_valid and data is not None:
                # Create content string for taxonomy tagging
                content = self._extract_content_for_tagging(data, source_config["type"])
                metadata = self.tagger.tag_document(content, filepath)
            
            # Determine status
            status = "success" if is_valid and data is not None else "failed"
            
            processed_sources.append({
                "filepath": filepath,
                "status": status,
                "data": data,
                "metadata": metadata,
                "errors": errors
            })
        
        # Calculate summary statistics
        total = len(processed_sources)
        successful = sum(1 for s in processed_sources if s["status"] == "success")
        failed = total - successful
        quality_score = (successful / total * 100) if total > 0 else 0.0
        
        return {
            "sources": processed_sources,
            "summary": {
                "total": total,
                "successful": successful,
                "failed": failed,
                "quality_score": quality_score
            }
        }
    
    def _extract_content_for_tagging(self, data: any, data_type: str) -> str:
        """
        Extract content string from data for taxonomy tagging.
        
        Helper method to convert data into a string representation suitable
        for keyword-based domain detection.
        
        Args:
            data: The loaded data (DataFrame, dict, or list)
            data_type: Type of data ("csv", "json", or "xml")
            
        Returns:
            str: String representation of the data content
        """
        if data_type == "csv" and isinstance(data, pd.DataFrame):
            # Convert DataFrame to string representation
            return " ".join(data.columns.tolist()) + " " + data.to_string(max_rows=5)
        elif data_type == "json" and isinstance(data, dict):
            # Convert dict keys and sample values to string
            return json.dumps(data, default=str)[:1000]  # Limit length
        elif data_type == "xml" and isinstance(data, list):
            # Convert list items to string
            return " ".join([str(item) for item in data[:5]])  # Sample first 5 items
        else:
            return str(data)[:1000]  # Fallback with length limit
    
    def prepare_for_vectordb(self, processed_sources: Dict) -> List[Dict]:
        """
        Convert processed sources to uniform format for Pinecone vector database.
        
        Transforms all successful data sources into a list of document dictionaries
        ready for embedding. Each document includes an ID, text content, and metadata.
        
        Args:
            processed_sources: Dictionary from process_all_sources() containing
                             sources and summary information.
                             
        Returns:
            List[Dict]: List of document dictionaries, each containing:
                - id: Unique identifier for the document
                - text: Text content for embedding
                - metadata: Dictionary with source, domain, source_type,
                          data_classification, and timestamp
                          
        Example:
            >>> pipeline = IngestionPipeline()
            >>> results = pipeline.process_all_sources()
            >>> documents = pipeline.prepare_for_vectordb(results)
            >>> print(f"Prepared {len(documents)} documents for vector DB")
        """
        documents = []
        
        for source in processed_sources["sources"]:
            if source["status"] != "success" or source["data"] is None:
                continue
            
            filepath = source["filepath"]
            metadata = source["metadata"]
            data = source["data"]
            source_type = Path(filepath).stem  # Filename without extension
            
            # Determine data type from filepath
            if filepath.endswith(".csv"):
                data_type = "csv"
            elif filepath.endswith(".json"):
                data_type = "json"
            elif filepath.endswith(".xml"):
                data_type = "xml"
            else:
                data_type = "unknown"
            
            # Convert data to documents based on type
            if data_type == "csv" and isinstance(data, pd.DataFrame):
                # Each row becomes a document
                for idx, row in data.iterrows():
                    doc_id = f"{source_type}_{idx + 1}"
                    text = self._dataframe_row_to_text(row)
                    doc_metadata = {
                        "source": filepath,
                        "domain": metadata.get("domain", "unknown"),
                        "source_type": metadata.get("source_type", "unknown"),
                        "data_classification": metadata.get("data_classification", "unknown"),
                        "timestamp": datetime.now().isoformat()
                    }
                    documents.append({
                        "id": doc_id,
                        "text": text,
                        "metadata": doc_metadata
                    })
                    
            elif data_type == "json" and isinstance(data, dict):
                # Find array key (claims, drugs, providers, etc.)
                array_key = None
                for key in ["claims", "drugs", "providers"]:
                    if key in data and isinstance(data[key], list):
                        array_key = key
                        break
                
                if array_key:
                    # Each array item becomes a document
                    for item in data[array_key]:
                        # Generate ID from item (prefer ID field, fallback to index)
                        item_id = None
                        if isinstance(item, dict):
                            item_id = item.get("claim_id") or item.get("drug_name") or item.get("npi") or item.get("id")
                        
                        if not item_id:
                            item_id = f"{source_type}_{len(documents) + 1}"
                        else:
                            item_id = f"{source_type}_{item_id}"
                        
                        text = self._json_item_to_text(item)
                        doc_metadata = {
                            "source": filepath,
                            "domain": metadata.get("domain", "unknown"),
                            "source_type": metadata.get("source_type", "unknown"),
                            "data_classification": metadata.get("data_classification", "unknown"),
                            "timestamp": datetime.now().isoformat()
                        }
                        documents.append({
                            "id": item_id,
                            "text": text,
                            "metadata": doc_metadata
                        })
                else:
                    # Single document for entire JSON
                    doc_id = f"{source_type}_1"
                    text = json.dumps(data, indent=2, default=str)
                    doc_metadata = {
                        "source": filepath,
                        "domain": metadata.get("domain", "unknown"),
                        "source_type": metadata.get("source_type", "unknown"),
                        "data_classification": metadata.get("data_classification", "unknown"),
                        "timestamp": datetime.now().isoformat()
                    }
                    documents.append({
                        "id": doc_id,
                        "text": text,
                        "metadata": doc_metadata
                    })
                    
            elif data_type == "xml" and isinstance(data, list):
                # Each XML/RSS item becomes a document
                for idx, item in enumerate(data):
                    if isinstance(item, dict):
                        # Use title or link as ID basis
                        item_id = item.get("title", f"{source_type}_{idx + 1}")
                        # Sanitize ID (remove special chars)
                        item_id = "".join(c if c.isalnum() or c in "_-" else "_" for c in str(item_id))
                        doc_id = f"{source_type}_{item_id[:50]}"  # Limit length
                        
                        text = self._xml_item_to_text(item)
                        doc_metadata = {
                            "source": filepath,
                            "domain": metadata.get("domain", "unknown"),
                            "source_type": metadata.get("source_type", "unknown"),
                            "data_classification": metadata.get("data_classification", "unknown"),
                            "timestamp": datetime.now().isoformat()
                        }
                        documents.append({
                            "id": doc_id,
                            "text": text,
                            "metadata": doc_metadata
                        })
        
        return documents
    
    def _dataframe_row_to_text(self, row: pd.Series) -> str:
        """Convert a DataFrame row to readable text."""
        parts = []
        for col, val in row.items():
            if pd.notna(val):
                parts.append(f"{col}: {val}")
        return ". ".join(parts)
    
    def _json_item_to_text(self, item: Dict) -> str:
        """Convert a JSON item to readable text."""
        if not isinstance(item, dict):
            return str(item)
        
        parts = []
        for key, val in item.items():
            if val is not None:
                if isinstance(val, list):
                    val_str = ", ".join(str(v) for v in val)
                else:
                    val_str = str(val)
                parts.append(f"{key.replace('_', ' ').title()}: {val_str}")
        return ". ".join(parts)
    
    def _xml_item_to_text(self, item: Dict) -> str:
        """Convert an XML/RSS item to readable text."""
        parts = []
        for key in ["title", "description", "category", "pubDate"]:
            if key in item and item[key]:
                parts.append(f"{key.replace('_', ' ').title()}: {item[key]}")
        return ". ".join(parts)
    
    def generate_report(self, processed_sources: Dict) -> str:
        """
        Generate a formatted text report of the ingestion process.
        
        Creates a comprehensive report showing overall statistics, per-source
        status, data quality metrics, errors, and breakdowns by domain and source type.
        
        Args:
            processed_sources: Dictionary from process_all_sources() containing
                             sources and summary information.
                             
        Returns:
            str: Formatted text report
            
        Example:
            >>> pipeline = IngestionPipeline()
            >>> results = pipeline.process_all_sources()
            >>> report = pipeline.generate_report(results)
            >>> print(report)
        """
        lines = []
        lines.append("=" * 80)
        lines.append("DATA INGESTION PIPELINE REPORT")
        lines.append("=" * 80)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Overall statistics
        summary = processed_sources["summary"]
        lines.append("OVERALL STATISTICS")
        lines.append("-" * 80)
        lines.append(f"Total Sources: {summary['total']}")
        lines.append(f"Successful: {summary['successful']} ✓")
        lines.append(f"Failed: {summary['failed']} ✗")
        lines.append(f"Quality Score: {summary['quality_score']:.1f}%")
        lines.append("")
        
        # Per-source status
        lines.append("SOURCE STATUS")
        lines.append("-" * 80)
        for source in processed_sources["sources"]:
            status_symbol = "✓" if source["status"] == "success" else "✗"
            lines.append(f"{status_symbol} {source['filepath']}")
            
            if source["metadata"]:
                metadata = source["metadata"]
                lines.append(f"    Domain: {metadata.get('domain', 'unknown')}")
                lines.append(f"    Source Type: {metadata.get('source_type', 'unknown')}")
                lines.append(f"    Classification: {metadata.get('data_classification', 'unknown')}")
            
            if source["errors"]:
                lines.append(f"    Errors:")
                for error in source["errors"]:
                    lines.append(f"      - {error}")
            lines.append("")
        
        # Errors and warnings
        all_errors = []
        for source in processed_sources["sources"]:
            if source["errors"]:
                all_errors.extend([f"{source['filepath']}: {e}" for e in source["errors"]])
        
        if all_errors:
            lines.append("ERRORS AND WARNINGS")
            lines.append("-" * 80)
            for error in all_errors:
                lines.append(f"  ✗ {error}")
            lines.append("")
        
        # Breakdown by domain
        domain_counts = {}
        for source in processed_sources["sources"]:
            if source["metadata"]:
                domain = source["metadata"].get("domain", "unknown")
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        if domain_counts:
            lines.append("BREAKDOWN BY DOMAIN")
            lines.append("-" * 80)
            for domain, count in sorted(domain_counts.items()):
                lines.append(f"  {domain}: {count}")
            lines.append("")
        
        # Breakdown by source type
        source_type_counts = {}
        for source in processed_sources["sources"]:
            if source["metadata"]:
                source_type = source["metadata"].get("source_type", "unknown")
                source_type_counts[source_type] = source_type_counts.get(source_type, 0) + 1
        
        if source_type_counts:
            lines.append("BREAKDOWN BY SOURCE TYPE")
            lines.append("-" * 80)
            for source_type, count in sorted(source_type_counts.items()):
                lines.append(f"  {source_type}: {count}")
            lines.append("")
        
        lines.append("=" * 80)
        lines.append("END OF REPORT")
        lines.append("=" * 80)
        
        return "\n".join(lines)


def main():
    """
    Run the complete ingestion pipeline and display results.
    
    Processes all data sources, prepares documents for vector database,
    and generates a comprehensive report.
    """
    print("Initializing Ingestion Pipeline...")
    pipeline = IngestionPipeline()
    
    print("\nProcessing all data sources...")
    results = pipeline.process_all_sources()
    
    print("\nPreparing documents for vector database...")
    documents = pipeline.prepare_for_vectordb(results)
    
    print(f"\n✓ Prepared {len(documents)} documents for vector database")
    
    print("\nGenerating report...")
    report = pipeline.generate_report(results)
    print("\n" + report)
    
    # Display sample documents
    if documents:
        print("\n" + "=" * 80)
        print("SAMPLE DOCUMENTS (First 3)")
        print("=" * 80)
        for i, doc in enumerate(documents[:3], 1):
            print(f"\nDocument {i}:")
            print(f"  ID: {doc['id']}")
            print(f"  Domain: {doc['metadata']['domain']}")
            print(f"  Text Preview: {doc['text'][:100]}...")
            print(f"  Metadata: {doc['metadata']}")


if __name__ == "__main__":
    main()
