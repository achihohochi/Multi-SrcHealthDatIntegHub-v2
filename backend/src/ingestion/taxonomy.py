"""
Taxonomy tagging utilities for health data classification.

This module provides functionality to automatically classify and tag health data
documents by domain, source type, and data classification based on keyword
analysis and file path patterns.
"""

import os
import re
from datetime import datetime
from typing import Dict, List, Tuple


class TaxonomyTagger:
    """
    Classifies and tags health data documents by domain and metadata.
    
    The TaxonomyTagger analyzes document content using keyword matching to
    identify the domain (eligibility, claims, benefits, pharmacy, compliance,
    or providers) and generates comprehensive metadata tags for each document.
    
    Attributes:
        domain_keywords (Dict[str, List[str]]): Dictionary mapping domain names
            to lists of keywords used for domain detection.
    
    Example:
        >>> tagger = TaxonomyTagger()
        >>> content = "Member ID: BSC100001, Status: active, Plan Type: Gold PPO"
        >>> metadata = tagger.tag_document(content, "data/internal/member_eligibility.csv")
        >>> print(metadata['domain'])
        'eligibility'
    """
    
    def __init__(self):
        """
        Initialize the TaxonomyTagger with domain keyword dictionaries.
        
        Sets up keyword lists for each of the six health data domains:
        eligibility, claims, benefits, pharmacy, compliance, and providers.
        """
        self.domain_keywords = {
            "eligibility": [
                "member_id", "member", "active", "inactive", "status",
                "plan_type", "effective_date"
            ],
            "claims": [
                "claim_id", "claim", "cpt_code", "diagnosis", "billed_amount",
                "provider_npi", "adjudication"
            ],
            "benefits": [
                "copay", "coinsurance", "deductible", "prior_auth",
                "out_of_pocket", "coverage"
            ],
            "pharmacy": [
                "drug", "medication", "prescription", "formulary", "tier", "fda"
            ],
            "compliance": [
                "cms", "policy", "regulation", "requirement", "mandate", "standard"
            ],
            "providers": [
                "provider", "npi", "specialty", "network", "quality_rating",
                "accepting_patients"
            ]
        }
    
    def _detect_domain(self, content: str) -> Tuple[str, int]:
        """
        Detect the domain of a document based on keyword matching.
        
        Searches the content (case-insensitive) for keywords associated with
        each domain and returns the domain with the highest keyword match count.
        If no keywords are found, returns "unknown" with count 0.
        
        Args:
            content: The text content to analyze for domain detection.
            
        Returns:
            Tuple[str, int]: A tuple containing:
                - domain_name: The detected domain name (or "unknown" if no matches)
                - keyword_match_count: The number of keyword matches found
                
        Example:
            >>> tagger = TaxonomyTagger()
            >>> domain, count = tagger._detect_domain("Member ID: 123, Status: active")
            >>> print(domain, count)
            ('eligibility', 2)
        """
        if not content or not isinstance(content, str):
            return ("unknown", 0)
        
        content_lower = content.lower()
        domain_scores = {}
        
        for domain, keywords in self.domain_keywords.items():
            match_count = 0
            for keyword in keywords:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                matches = len(re.findall(pattern, content_lower))
                match_count += matches
            
            if match_count > 0:
                domain_scores[domain] = match_count
        
        if not domain_scores:
            return ("unknown", 0)
        
        # Return domain with highest score
        best_domain = max(domain_scores, key=domain_scores.get)
        return (best_domain, domain_scores[best_domain])
    
    def tag_document(self, content: str, source_filepath: str) -> Dict:
        """
        Tag a document with comprehensive metadata.
        
        Analyzes the document content and filepath to generate metadata tags
        including domain, source type, source system, data classification,
        and timestamp information.
        
        Args:
            content: The text content of the document to tag.
            source_filepath: The file path of the source document.
            
        Returns:
            Dict: A dictionary containing metadata tags:
                - source_type: "internal" or "external" based on filepath
                - domain: Detected domain name from content analysis
                - source_system: Filename without extension
                - data_classification: "PII" for eligibility/claims, "public" otherwise
                - last_updated: Current ISO timestamp
                - filepath: The original source filepath
                
        Example:
            >>> tagger = TaxonomyTagger()
            >>> content = "Claim ID: CLM-001, CPT Code: 99213, Diagnosis: E11.9"
            >>> metadata = tagger.tag_document(content, "data/internal/claims_history.json")
            >>> print(metadata)
            {
                'source_type': 'internal',
                'domain': 'claims',
                'source_system': 'claims_history',
                'data_classification': 'PII',
                'last_updated': '2025-01-23T10:30:00',
                'filepath': 'data/internal/claims_history.json'
            }
        """
        if not source_filepath or not isinstance(source_filepath, str):
            raise ValueError(f"Invalid source_filepath provided: {source_filepath}")
        
        # Detect domain from content
        domain, match_count = self._detect_domain(content)
        
        # Determine source type based on filepath
        if "internal/" in source_filepath:
            source_type = "internal"
        else:
            source_type = "external"
        
        # Extract source system name (filename without extension)
        filename = os.path.basename(source_filepath)
        source_system, _ = os.path.splitext(filename)
        
        # Determine data classification
        if domain in ["eligibility", "claims"]:
            data_classification = "PII"
        else:
            data_classification = "public"
        
        # Generate current timestamp
        last_updated = datetime.now().isoformat()
        
        return {
            "source_type": source_type,
            "domain": domain,
            "source_system": source_system,
            "data_classification": data_classification,
            "last_updated": last_updated,
            "filepath": source_filepath
        }
    
    def get_taxonomy_summary(self, tagged_docs: List[Dict]) -> Dict:
        """
        Generate summary statistics from a list of tagged documents.
        
        Analyzes a collection of tagged documents and produces counts by
        domain, source type, and data classification.
        
        Args:
            tagged_docs: A list of dictionaries, each containing metadata
                        tags from tag_document().
                        
        Returns:
            Dict: A dictionary containing summary statistics:
                - by_domain: Dictionary mapping domain names to counts
                - by_source_type: Dictionary mapping source types to counts
                - by_classification: Dictionary mapping classifications to counts
                - total_documents: Total number of documents analyzed
                
        Example:
            >>> tagger = TaxonomyTagger()
            >>> docs = [
            ...     tagger.tag_document("Member ID: 123", "data/internal/members.csv"),
            ...     tagger.tag_document("Claim ID: 456", "data/internal/claims.json")
            ... ]
            >>> summary = tagger.get_taxonomy_summary(docs)
            >>> print(summary['by_domain'])
            {'eligibility': 1, 'claims': 1}
        """
        if not tagged_docs:
            return {
                "by_domain": {},
                "by_source_type": {},
                "by_classification": {},
                "total_documents": 0
            }
        
        by_domain = {}
        by_source_type = {}
        by_classification = {}
        
        for doc in tagged_docs:
            # Count by domain
            domain = doc.get("domain", "unknown")
            by_domain[domain] = by_domain.get(domain, 0) + 1
            
            # Count by source type
            source_type = doc.get("source_type", "unknown")
            by_source_type[source_type] = by_source_type.get(source_type, 0) + 1
            
            # Count by classification
            classification = doc.get("data_classification", "unknown")
            by_classification[classification] = by_classification.get(classification, 0) + 1
        
        return {
            "by_domain": by_domain,
            "by_source_type": by_source_type,
            "by_classification": by_classification,
            "total_documents": len(tagged_docs)
        }


def main():
    """
    Test the TaxonomyTagger with sample content from each domain.
    
    Creates sample content strings representing each of the six domains,
    tags them, displays results in a formatted table, and generates
    a taxonomy summary.
    """
    print("=" * 80)
    print("Taxonomy Tagger Test")
    print("=" * 80)
    
    tagger = TaxonomyTagger()
    
    # Sample content for each domain
    sample_contents = [
        {
            "content": "Member ID: BSC100001, Status: active, Plan Type: Gold PPO, "
                      "Effective Date: 2024-01-01, Member Name: John Doe",
            "filepath": "data/internal/member_eligibility.csv",
            "expected_domain": "eligibility"
        },
        {
            "content": "Claim ID: CLM-2025-001234, CPT Code: 99213, Diagnosis Code: E11.9, "
                      "Billed Amount: 250.00, Provider NPI: 1234567890, Adjudication Status: paid",
            "filepath": "data/internal/claims_history.json",
            "expected_domain": "claims"
        },
        {
            "content": "Copay: $35, Coinsurance: 20%, Deductible: $500, "
                      "Prior Authorization Required: Yes, Out of Pocket Maximum: $5000, Coverage: In-network",
            "filepath": "data/internal/benefits_summary.csv",
            "expected_domain": "benefits"
        },
        {
            "content": "Drug Name: Metformin, Medication: Prescription, Formulary Tier: 2, "
                      "FDA Approval Date: 1995-03-03, Prescription Required: Yes",
            "filepath": "data/external/fda_drug_database.json",
            "expected_domain": "pharmacy"
        },
        {
            "content": "CMS Policy Update: New Medicare Advantage Star Ratings for 2026, "
                      "Regulation: Prior Authorization Requirements, Mandate: Quality Standards",
            "filepath": "data/external/cms_policy_updates.xml",
            "expected_domain": "compliance"
        },
        {
            "content": "Provider Name: Dr. Smith, NPI: 9876543210, Specialty: Cardiology, "
                      "Network: In-network, Quality Rating: 4.5, Accepting Patients: Yes",
            "filepath": "data/external/provider_directory.json",
            "expected_domain": "providers"
        }
    ]
    
    tagged_documents = []
    
    print("\nTagging Documents:")
    print("-" * 80)
    print(f"{'Domain':<15} {'Source Type':<15} {'Source System':<25} {'Classification':<15} {'Filepath':<30}")
    print("-" * 80)
    
    for sample in sample_contents:
        metadata = tagger.tag_document(sample["content"], sample["filepath"])
        tagged_documents.append(metadata)
        
        print(f"{metadata['domain']:<15} "
              f"{metadata['source_type']:<15} "
              f"{metadata['source_system']:<25} "
              f"{metadata['data_classification']:<15} "
              f"{metadata['filepath']:<30}")
    
    # Generate and display summary
    summary = tagger.get_taxonomy_summary(tagged_documents)
    
    print("\n" + "=" * 80)
    print("Taxonomy Summary")
    print("=" * 80)
    
    print(f"\nTotal Documents: {summary['total_documents']}")
    
    print("\nBy Domain:")
    print("-" * 40)
    for domain, count in sorted(summary['by_domain'].items()):
        print(f"  {domain:<20} {count:>3}")
    
    print("\nBy Source Type:")
    print("-" * 40)
    for source_type, count in sorted(summary['by_source_type'].items()):
        print(f"  {source_type:<20} {count:>3}")
    
    print("\nBy Classification:")
    print("-" * 40)
    for classification, count in sorted(summary['by_classification'].items()):
        print(f"  {classification:<20} {count:>3}")
    
    print("\n" + "=" * 80)
    print("Test Complete")
    print("=" * 80)


if __name__ == "__main__":
    main()
