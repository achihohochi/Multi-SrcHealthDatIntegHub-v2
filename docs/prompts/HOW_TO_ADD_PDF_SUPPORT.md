# HOW TO: Add PDF Support to RAG System

**Purpose:** Step-by-step guide to add PDF file ingestion and processing  
**Prerequisite:** Plugin architecture refactor completed (or working with current if/elif system)  
**Time Required:** 1-4 hours depending on approach  
**AI Agent:** Claude Sonnet 4.5 in Cursor or VSCode

---

## 🎯 What This Guide Does

After following this guide, you will be able to:
- ✅ Load PDF files from disk
- ✅ Extract text content from PDFs
- ✅ Validate PDF files (page count, text extraction success)
- ✅ Convert PDF content into RAG documents
- ✅ Query PDF content through your RAG system

**Example use case:**
```
Add file: data/internal/plan_coverage_guide.pdf
Query: "What are the copays for specialist visits on Gold PPO?"
Answer: [AI reads PDF and answers from its content]
```

---

## 📋 Two Approaches

Choose based on whether you've done the plugin architecture refactor:

### Approach A: With Plugin Architecture (RECOMMENDED - 1 hour)
- Clean, maintainable
- Create one new file: `pdf_source.py`
- No modifications to existing code
- **Use this if you completed `IMPLEMENT_PLUGIN_ARCHITECTURE.md`**

### Approach B: Without Plugin Architecture (LEGACY - 2-4 hours)
- Works with current if/elif system
- Modify 5 existing files
- More error-prone
- **Use this if you haven't refactored yet**

---

## 🚀 APPROACH A: With Plugin Architecture (RECOMMENDED)

### Prerequisites Checklist

Before starting, verify:
- [ ] Plugin architecture refactor is complete
- [ ] You can see files: `src/ingestion/data_sources/base.py` and `registry.py`
- [ ] Pipeline runs successfully (113 documents, 100% quality)
- [ ] Git repository has clean state (all changes committed)

---

### STEP 1: Install PDF Library

**What this does:** Adds PyPDF2 library which reads PDF files

**In your terminal:**
```bash
cd /Users/chiho/ai-lab/Multi-SrcHealthDatIntegHub

# Activate virtual environment if you have one
# source venv/bin/activate

# Install PDF library
pip install PyPDF2

# Verify installation
python -c "import PyPDF2; print('✓ PyPDF2 installed')"
```

**Expected output:**
```
✓ PyPDF2 installed
```

**If error occurs:**
- Try: `pip3 install PyPDF2`
- Or: `python3 -m pip install PyPDF2`

---

### STEP 2: Add Sample PDF File

**What this does:** Gives you a test PDF to work with

**Create a sample PDF:**

**Option A: Use existing PDF (if you have one)**
```bash
# Copy your PDF to the project
cp ~/Downloads/your_file.pdf data/internal/sample_document.pdf
```

**Option B: Create a test PDF with Python**
```bash
python << 'EOF'
from reportlab.pdfwriter import PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Create a simple test PDF
c = canvas.Canvas("data/internal/test_plan_coverage.pdf", pagesize=letter)
c.setFont("Helvetica", 12)

# Add content
c.drawString(100, 750, "HealthInsurancePayorCo Plan Coverage Guide")
c.drawString(100, 720, "")
c.drawString(100, 700, "Gold PPO Plan:")
c.drawString(100, 680, "- Primary Care Office Visit: $35 copay")
c.drawString(100, 660, "- Specialist Office Visit: $75 copay")
c.drawString(100, 640, "- Emergency Room: $500 copay")
c.drawString(100, 620, "- Urgent Care: $50 copay")
c.drawString(100, 600, "")
c.drawString(100, 580, "Silver HMO Plan:")
c.drawString(100, 560, "- Primary Care Office Visit: $45 copay")
c.drawString(100, 540, "- Specialist Office Visit: $85 copay (referral required)")
c.drawString(100, 520, "- Emergency Room: $350 copay")

c.save()
print("✓ Created test PDF: data/internal/test_plan_coverage.pdf")
EOF
```

**If reportlab not installed:**
```bash
pip install reportlab
# Then run the script again
```

---

### STEP 3: Open Project in Cursor or VSCode

**For Cursor:**
```bash
cursor /Users/chiho/ai-lab/Multi-SrcHealthDatIntegHub
```

**For VSCode:**
```bash
code /Users/chiho/ai-lab/Multi-SrcHealthDatIntegHub
```

---

### STEP 4: Give Instructions to AI Agent

**Open AI Chat:**
- **Cursor:** Press `Cmd+L` (Mac) or `Ctrl+L` (Windows/Linux)
- **VSCode with Copilot:** Open Copilot Chat panel

**Copy and paste this EXACT prompt:**

```
I need to add PDF file support to our data ingestion pipeline.

CONTEXT:
- We have a plugin architecture for data sources
- Base class: src/ingestion/data_sources/base.py
- Registry: src/ingestion/data_sources/registry.py
- Existing plugins: csv_source.py, json_source.py, xml_source.py

TASK:
Create a new PDF data source plugin following our established pattern.

REQUIREMENTS:

1. Create file: src/ingestion/data_sources/pdf_source.py

2. Implement PDFDataSource class with these 5 methods:
   
   a) get_file_type() -> return "pdf"
   
   b) load(filepath) -> Use PyPDF2 to:
      - Open PDF file
      - Extract text from all pages
      - Get metadata (title, author, page count)
      - Return dict with: {"text": full_text, "num_pages": count, "title": title}
      - Handle errors: FileNotFoundError, corrupted PDFs
   
   c) validate(data, config) -> Check:
      - PDF has extractable text (not empty)
      - Meets min_pages requirement (from config)
      - Text length is reasonable (not just whitespace)
      - Return (is_valid: bool, errors: list)
   
   d) extract_content_for_tagging(data) -> Return:
      - First 1000 characters of extracted text
      - For domain detection by taxonomy tagger
   
   e) prepare_documents(data, metadata, filepath) -> Create:
      - One document for entire PDF
      - Document ID: {filename}_full
      - Text: full extracted text
      - Metadata: include num_pages, title, domain, source, etc.

3. Follow these patterns from existing plugins:
   - Use comprehensive docstrings (Google style)
   - Include type hints
   - Handle errors with helpful messages
   - Use pathlib.Path for file paths

4. After creating pdf_source.py, update:
   src/ingestion/data_sources/__init__.py
   
   Add these lines:
   from .pdf_source import PDFDataSource
   registry.register(PDFDataSource)

DELIVERABLES:
- Show me the complete pdf_source.py code
- Show me the updated __init__.py
- Explain how to test it

Do NOT modify pipeline.py - the plugin architecture handles everything.

Ready? Start by showing me the pdf_source.py implementation.
```

---

### STEP 5: Review AI's Code

**The AI will show you code for `pdf_source.py`**

**Check these things before accepting:**

- [ ] All 5 methods implemented (get_file_type, load, validate, extract_content_for_tagging, prepare_documents)
- [ ] Uses PyPDF2 library correctly
- [ ] Has error handling (try/except blocks)
- [ ] Returns correct data types (dict from load, tuple from validate, etc.)
- [ ] Has docstrings explaining each method

**If something looks wrong, say:**
```
This doesn't match the pattern from csv_source.py.
Please review csv_source.py and follow the same structure.
```

---

### STEP 6: Test the PDF Plugin

**The AI should provide a test script. If not, ask:**

```
Create a test script to verify the PDF plugin works.

Test these scenarios:
1. Load a valid PDF
2. Validate it passes requirements
3. Extract content for tagging
4. Prepare documents for vector DB

Save as: tests/test_pdf_source.py
```

**Run the test:**
```bash
python tests/test_pdf_source.py
```

**Expected output:**
```
✓ PDF loaded successfully
✓ Validation passed
✓ Content extracted (1000 chars)
✓ Document prepared with id: test_plan_coverage_full
✓ All PDF source tests passed
```

---

### STEP 7: Add PDF to Pipeline Configuration

**Tell the AI:**

```
Now add PDF support to the pipeline configuration.

Update src/ingestion/pipeline.py

In the __init__ method, add this to self.data_sources list:

{
    "filepath": "data/internal/test_plan_coverage.pdf",
    "type": "pdf",
    "min_pages": 1
}

Just add this dict to the existing list - don't modify anything else.
```

---

### STEP 8: Run Full Pipeline Test

**Run the pipeline:**
```bash
python src/ingestion/pipeline.py
```

**Expected output:**
```
Initializing Ingestion Pipeline...
✓ Registered data source: csv -> CSVDataSource
✓ Registered data source: json -> JSONDataSource
✓ Registered data source: xml -> XMLDataSource
✓ Registered data source: pdf -> PDFDataSource    ← NEW!

Processing all data sources...

✓ Prepared 114 documents for vector database    ← Was 113, now 114!

================================================================================
DATA INGESTION PIPELINE REPORT
================================================================================
Total Sources: 7                                ← Was 6, now 7!
Successful: 7 ✓
Failed: 0 ✗
Quality Score: 100.0%

SOURCE STATUS
--------------------------------------------------------------------------------
✓ data/internal/member_eligibility.csv
    Domain: eligibility
✓ data/internal/claims_history.json
    Domain: claims
✓ data/internal/benefits_summary.csv
    Domain: benefits
✓ data/external/cms_policy_updates.xml
    Domain: compliance
✓ data/external/fda_drug_database.json
    Domain: pharmacy
✓ data/external/provider_directory.json
    Domain: providers
✓ data/internal/test_plan_coverage.pdf          ← NEW!
    Domain: benefits
    Classification: public
```

**Success indicators:**
- [ ] 114 documents (was 113)
- [ ] 7 sources (was 6)
- [ ] PDF shows as successful
- [ ] Quality score still 100%

---

### STEP 9: Upload to Pinecone (Make PDF Searchable)

**Run the upload script:**
```bash
python src/scripts/upload_to_pinecone.py
```

**Expected output:**
```
Generating embeddings for 114 documents...
Processing batch 1/2...
Processing batch 2/2...
Uploading to Pinecone...
✓ Successfully uploaded 114 documents to Pinecone
```

---

### STEP 10: Test RAG Query with PDF Content

**Test that you can query PDF content:**

```bash
python << 'EOF'
from src.rag.query_engine import RAGQueryEngine

engine = RAGQueryEngine()

# Query about content that's IN the PDF
result = engine.query("What is the copay for specialist visits on Gold PPO?")

print("Question:", result["question"])
print("Answer:", result["answer"])
print("\nSources used:")
for source in result["sources"]:
    print(f"  - {source['id']} ({source['domain']}) - Score: {source['score']:.3f}")
EOF
```

**Expected output:**
```
Question: What is the copay for specialist visits on Gold PPO?
Answer: The copay for specialist visits on Gold PPO is $75 [1].

Sources used:
  - test_plan_coverage_full (benefits) - Score: 0.842
  - benefits_summary_23 (benefits) - Score: 0.789
  - benefits_summary_45 (benefits) - Score: 0.756
```

**Success criteria:**
- [ ] Answer mentions $75
- [ ] PDF document appears in sources
- [ ] Answer cites the PDF

---

### STEP 11: Test in Streamlit UI

**Start the UI:**
```bash
streamlit run app.py
```

**In the browser:**
1. Wait for app to load
2. Type in query box: "What is the copay for specialist visits on Gold PPO?"
3. Click "Search"
4. Verify answer includes PDF content
5. Check sources - PDF should be listed

---

### STEP 12: Commit Your Work

**If everything works:**

```bash
git add .
git commit -m "feat: Add PDF data source support

- Implement PDFDataSource plugin using PyPDF2
- Add pdf_source.py with full DataSource interface
- Register PDF type in data sources registry
- Add test_plan_coverage.pdf as sample data
- Update pipeline config to include PDF source
- Verify 114 documents (was 113) with 100% quality
- Confirm PDF content queryable in RAG system

Tested:
- PDF loading and text extraction
- Validation with min_pages requirement
- Content tagging for domain detection
- Document preparation for vector DB
- End-to-end RAG query with PDF content"
```

---

## ✅ VERIFICATION CHECKLIST

After completing all steps:

### Files Created/Modified:
- [ ] `src/ingestion/data_sources/pdf_source.py` (NEW)
- [ ] `src/ingestion/data_sources/__init__.py` (MODIFIED - added PDF registration)
- [ ] `src/ingestion/pipeline.py` (MODIFIED - added PDF to data_sources list)
- [ ] `data/internal/test_plan_coverage.pdf` (NEW - sample file)
- [ ] `tests/test_pdf_source.py` (NEW - tests)

### Functionality Working:
- [ ] Pipeline runs successfully (114 documents)
- [ ] 7 sources processed (was 6)
- [ ] Quality score: 100%
- [ ] PDF in Pinecone (vector count = 114)
- [ ] Can query PDF content through RAG
- [ ] PDF appears in source citations

### No Breaking Changes:
- [ ] Original 113 documents still present
- [ ] All 6 original sources still work
- [ ] No errors in console
- [ ] No modifications to existing plugins (CSV, JSON, XML)

---

## 🎯 SUCCESS - You Can Now:

1. ✅ **Load PDF files** from disk
2. ✅ **Extract text** from PDFs automatically
3. ✅ **Validate PDF quality** (has text, meets page requirements)
4. ✅ **Categorize PDFs** by domain (benefits, compliance, etc.)
5. ✅ **Search PDF content** through RAG queries
6. ✅ **Get cited answers** from PDF sources

---

## 🚀 Next Steps

### Add More PDFs:

```python
# In pipeline.py, add to self.data_sources:
{
    "filepath": "data/internal/provider_handbook.pdf",
    "type": "pdf",
    "min_pages": 5
},
{
    "filepath": "data/external/cms_guidelines.pdf",
    "type": "pdf",
    "min_pages": 1
}
```

Then run:
```bash
python src/ingestion/pipeline.py
python src/scripts/upload_to_pinecone.py
```

### Advanced PDF Features (Future):

Ask AI to enhance `pdf_source.py` with:
- **Page splitting:** One document per page (better for long PDFs)
- **Section detection:** Split by headers (better context)
- **Table extraction:** Extract tables as structured data
- **Image extraction:** OCR on embedded images
- **Metadata enrichment:** Author, creation date, subject

---

## 📊 METRICS

| Metric | Before PDF | After PDF |
|--------|-----------|-----------|
| Supported types | 3 (CSV, JSON, XML) | 4 (CSV, JSON, XML, PDF) |
| Total sources | 6 | 7+ |
| Total documents | 113 | 114+ |
| Files modified | 0 | 2 (pdf_source.py, __init__.py) |
| Time to add | N/A | 1 hour |

---

# 🔧 APPROACH B: Without Plugin Architecture (LEGACY)

**⚠️ Warning:** This approach is more complex and error-prone. Only use if you haven't done the plugin refactor.

---

### STEP 1: Install PDF Library (Same as Approach A)

```bash
pip install PyPDF2
```

---

### STEP 2: Create PDF Loader Function

**Tell AI:**

```
Add PDF loading support to the existing data loader.

File: src/ingestion/data_loader.py

Add this new function at the end of the file (before main()):

def load_pdf(filepath: str) -> Dict:
    """
    Load a PDF file and extract text content.
    
    Args:
        filepath: Path to the PDF file
        
    Returns:
        Dict with keys: text, num_pages, title, author
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If PDF cannot be parsed
    """
    # Implementation using PyPDF2
    # - Open PDF
    # - Extract text from all pages
    # - Get metadata
    # - Return dict

Follow the same error handling pattern as load_csv().
Show me the complete function.
```

---

### STEP 3: Add PDF Validation

**Tell AI:**

```
Add PDF validation to the validator.

File: src/ingestion/validator.py

Add this new method to the DataValidator class:

def validate_pdf(self, data: Dict, config: Dict) -> Tuple[bool, List[str]]:
    """
    Validate PDF data.
    
    Args:
        data: Dict from load_pdf() with text, num_pages, etc.
        config: Dict with validation rules (min_pages, etc.)
        
    Returns:
        Tuple of (is_valid, errors)
    """
    # Check:
    # - Has text content
    # - Meets min_pages requirement
    # - Text is not just whitespace

Follow the same pattern as validate_csv().
Show me the complete method.
```

---

### STEP 4: Update Pipeline - Load and Validate

**Tell AI:**

```
Update the pipeline to handle PDF files.

File: src/ingestion/pipeline.py

In the load_and_validate_source() method, add a new elif branch for PDF:

elif file_type == "pdf":
    data = load_pdf(filepath)
    required_keys = source_config.get("required_keys", [])
    is_valid, validation_errors = self.validator.validate_pdf(data, source_config)
    errors.extend(validation_errors)

Add this AFTER the xml branch and BEFORE the else.

Show me where exactly to add it.
```

---

### STEP 5: Update Pipeline - Content Extraction

**Tell AI:**

```
Update content extraction to handle PDFs.

File: src/ingestion/pipeline.py

In the _extract_content_for_tagging() method, add:

elif data_type == "pdf" and isinstance(data, dict):
    return data.get("text", "")[:1000]

Add this AFTER the xml branch and BEFORE the else.

Show me the updated method.
```

---

### STEP 6: Update Pipeline - Document Preparation

**Tell AI:**

```
Update document preparation to handle PDFs.

File: src/ingestion/pipeline.py

In the prepare_for_vectordb() method, add this branch:

elif data_type == "pdf" and isinstance(data, dict):
    doc_id = f"{source_type}_full"
    text = data.get("text", "")
    
    doc_metadata = {
        "source": filepath,
        "domain": metadata.get("domain", "unknown"),
        "source_type": metadata.get("source_type", "unknown"),
        "data_classification": metadata.get("data_classification", "unknown"),
        "timestamp": datetime.now().isoformat(),
        "num_pages": data.get("num_pages", 0),
        "pdf_title": data.get("title", "")
    }
    
    documents.append({
        "id": doc_id,
        "text": text,
        "metadata": doc_metadata
    })

Add this AFTER the xml branch and BEFORE any error handling.

Show me where exactly to add it in the function.
```

---

### STEP 7: Add PDF to Configuration

**Tell AI:**

```
Add PDF source to pipeline configuration.

File: src/ingestion/pipeline.py

In __init__ method's self.data_sources list, add:

{
    "filepath": "data/internal/test_plan_coverage.pdf",
    "type": "pdf",
    "min_pages": 1
}

Show me the complete updated list.
```

---

### STEP 8: Import PDF Loader

**Tell AI:**

```
Update imports in pipeline.py

At the top of the file, in the import section:

from src.ingestion.data_loader import load_csv, load_json, load_xml_rss, load_pdf

Add load_pdf to the existing import line.

Show me the updated import.
```

---

### STEP 9-12: Same as Approach A

Follow steps 9-12 from Approach A:
- Test the pipeline
- Upload to Pinecone
- Test RAG queries
- Commit your work

---

## 📊 Approach Comparison

| Aspect | With Plugin (A) | Without Plugin (B) |
|--------|----------------|-------------------|
| Files to create | 1 new | 1 new |
| Files to modify | 1 | 4 |
| Lines of code | ~150 | ~200 |
| Error risk | Low | Medium-High |
| Time required | 1 hour | 2-4 hours |
| Future additions | Easy | Still hard |
| Recommended | ✅ YES | ⚠️ Only if no choice |

---

## 🆘 TROUBLESHOOTING

### Issue: "ModuleNotFoundError: No module named 'PyPDF2'"

**Solution:**
```bash
pip install PyPDF2
# or
pip3 install PyPDF2
```

### Issue: "PDF has no extractable text"

**Cause:** PDF is scanned image, not text-based

**Solution:**
- Use OCR library like `pytesseract`
- Or use text-based PDFs only
- Or skip the PDF with helpful error message

### Issue: "Only 113 documents, PDF not added"

**Possible causes:**
1. PDF not in data_sources config
2. PDF validation failed
3. PDF file path wrong

**Debug:**
```bash
python << 'EOF'
from src.ingestion.pipeline import IngestionPipeline

pipeline = IngestionPipeline()
print("Data sources configured:")
for source in pipeline.data_sources:
    print(f"  - {source['filepath']} ({source['type']})")
EOF
```

Should show 7 sources including PDF.

### Issue: "Can't query PDF content in RAG"

**Possible causes:**
1. PDF not uploaded to Pinecone
2. Text extraction failed
3. Embedding failed

**Debug:**
```python
from src.rag.vector_store import PineconeVectorStore

vs = PineconeVectorStore()
stats = vs.get_index_stats()
print(f"Vectors in Pinecone: {stats['total_vector_count']}")
# Should be 114 (was 113)
```

### Issue: AI Generated Wrong Code

**Solution:**
```
Stop. The code you generated doesn't match the pattern.

Please review src/ingestion/data_sources/csv_source.py

Copy the exact same structure:
- Same method signatures
- Same error handling pattern
- Same return types
- Same docstring format

Try again following csv_source.py exactly.
```

---

## 🎓 WHAT YOU LEARNED

After completing this guide, you now know:

- ✅ How to add new file type support to data ingestion
- ✅ How to use PyPDF2 for text extraction
- ✅ How to validate document quality
- ✅ How to integrate new sources into RAG pipeline
- ✅ How to test end-to-end (ingestion → embedding → query)
- ✅ Difference between plugin vs if/elif architecture

---

## 📝 FOR YOUR INTERVIEW

You can now say:

> "I extended the system to support PDF files. I implemented a PDFDataSource plugin that extracts text using PyPDF2, validates page count and content, and integrates seamlessly with the existing RAG pipeline. Adding PDF took about an hour thanks to the plugin architecture—it would have taken 4+ hours with the old if/elif system. The PDF content is now fully searchable and appears in query results with proper source citations."

**Demonstrates:**
- ✅ Practical implementation skills
- ✅ Knowledge of PDF processing
- ✅ Understanding of RAG pipelines
- ✅ Appreciation for good architecture

---

## ✅ COMPLETION CHECKLIST

- [ ] PyPDF2 installed
- [ ] Sample PDF created in data/internal/
- [ ] pdf_source.py created (Approach A) or functions added (Approach B)
- [ ] PDF registered in __init__.py (Approach A) or imports updated (Approach B)
- [ ] PDF added to pipeline config
- [ ] Pipeline runs successfully (114 documents)
- [ ] PDF uploaded to Pinecone
- [ ] Can query PDF content
- [ ] Changes committed to git

---

**You're now ready to add PDF support to your RAG system! 🚀**

**Estimated completion time:**
- With plugin architecture: 1 hour
- Without plugin architecture: 2-4 hours

**Start with Step 1 when you're ready to implement!**
