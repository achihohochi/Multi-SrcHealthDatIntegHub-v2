import json
import logging
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException

from api.models.responses import DataSourceInfo, DataSourcePreview, DataSourcesResponse

logger = logging.getLogger(__name__)

router = APIRouter()

DATA_DIR = Path(__file__).parent.parent.parent / "data"

# Fields redacted in previews of PII-classified sources
_PII_FIELDS = {"first_name", "last_name", "dob", "date_of_birth", "email", "phone", "ssn", "zip_code"}


def _redact_record(record: dict, classification: str) -> dict:
    """Mask PII fields in records from PII-classified sources."""
    if classification.upper() != "PII":
        return record
    return {
        k: "**REDACTED**" if k.lower() in _PII_FIELDS else v
        for k, v in record.items()
    }

# Canonical source definitions matching the original app.py
SOURCE_DEFINITIONS = [
    {
        "id": "member_eligibility",
        "name": "Member Eligibility",
        "domain": "eligibility",
        "source_type": "internal",
        "classification": "PII",
        "filepath": "internal/member_eligibility.csv",
        "file_format": "csv",
    },
    {
        "id": "claims_history",
        "name": "Claims History",
        "domain": "claims",
        "source_type": "internal",
        "classification": "PII",
        "filepath": "internal/claims_history.json",
        "file_format": "json",
    },
    {
        "id": "benefits_summary",
        "name": "Benefits Summary",
        "domain": "benefits",
        "source_type": "internal",
        "classification": "public",
        "filepath": "internal/benefits_summary.csv",
        "file_format": "csv",
    },
    {
        "id": "cms_policy_updates",
        "name": "CMS Policy Updates",
        "domain": "compliance",
        "source_type": "external",
        "classification": "public",
        "filepath": "external/cms_policy_updates.xml",
        "file_format": "xml",
    },
    {
        "id": "fda_drug_database",
        "name": "FDA Drug Database",
        "domain": "pharmacy",
        "source_type": "external",
        "classification": "public",
        "filepath": "external/fda_drug_database.json",
        "file_format": "json",
    },
    {
        "id": "provider_directory",
        "name": "Provider Directory",
        "domain": "providers",
        "source_type": "external",
        "classification": "public",
        "filepath": "external/provider_directory.json",
        "file_format": "json",
    },
]


def _get_record_count(source_def: dict) -> int | None:
    """Get record count from a data file."""
    filepath = DATA_DIR / source_def["filepath"]
    if not filepath.exists():
        return None

    try:
        fmt = source_def["file_format"]
        if fmt == "csv":
            df = pd.read_csv(filepath)
            return len(df)
        elif fmt == "json":
            with open(filepath) as f:
                data = json.load(f)
            if isinstance(data, list):
                return len(data)
            # JSON files may have a wrapper key containing the array
            for value in data.values():
                if isinstance(value, list):
                    return len(value)
            return 1
        elif fmt == "xml":
            import feedparser
            feed = feedparser.parse(str(filepath))
            return len(feed.entries)
    except Exception:
        return None


@router.get("/sources", response_model=DataSourcesResponse)
def get_data_sources():
    """List all data sources with metadata and record counts."""
    sources = []
    for src in SOURCE_DEFINITIONS:
        count = _get_record_count(src)
        sources.append(
            DataSourceInfo(
                id=src["id"],
                name=src["name"],
                domain=src["domain"],
                source_type=src["source_type"],
                classification=src["classification"],
                filepath=src["filepath"],
                record_count=count,
                file_format=src["file_format"],
            )
        )
    return DataSourcesResponse(sources=sources)


@router.get("/sources/{source_id}/preview", response_model=DataSourcePreview)
def get_source_preview(source_id: str):
    """Get a preview of records from a specific data source."""
    source_def = next(
        (s for s in SOURCE_DEFINITIONS if s["id"] == source_id), None
    )
    if not source_def:
        raise HTTPException(status_code=404, detail=f"Source '{source_id}' not found")

    filepath = DATA_DIR / source_def["filepath"]
    if not filepath.exists():
        raise HTTPException(status_code=404, detail=f"Data file not found: {source_def['filepath']}")

    try:
        fmt = source_def["file_format"]
        classification = source_def["classification"]
        columns = None
        sample_records = []
        total_records = 0

        if fmt == "csv":
            df = pd.read_csv(filepath)
            total_records = len(df)
            columns = list(df.columns)
            raw = df.head(10).to_dict(orient="records")
            sample_records = [_redact_record(r, classification) for r in raw]

        elif fmt == "json":
            with open(filepath) as f:
                data = json.load(f)
            if isinstance(data, list):
                records = data
            else:
                for value in data.values():
                    if isinstance(value, list):
                        records = value
                        break
                else:
                    records = [data]
            total_records = len(records)
            raw = records[:10]
            sample_records = [
                _redact_record(r, classification)
                for r in raw if isinstance(r, dict)
            ]
            if records:
                columns = list(records[0].keys()) if isinstance(records[0], dict) else None

        elif fmt == "xml":
            import feedparser
            feed = feedparser.parse(str(filepath))
            entries = feed.entries
            total_records = len(entries)
            sample_records = [dict(e) for e in entries[:10]]
            if entries:
                columns = list(entries[0].keys())

        return DataSourcePreview(
            source_name=source_def["name"],
            filepath=source_def["filepath"],
            columns=columns,
            sample_records=sample_records,
            total_records=total_records,
        )

    except Exception:
        logger.exception("Failed to load preview for source: %s", source_id)
        raise HTTPException(
            status_code=500,
            detail="Failed to load source preview.",
        )
