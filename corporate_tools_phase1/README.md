# Corporate Tools Phase 1

This folder contains the first batch of Python-based corporate utility tools. Each tool is saved as an individual script and can be used from the command line now, then wrapped later as a web/mobile service endpoint.

## Setup

Python 3.10+ is recommended.

Install optional dependencies for Excel and PDF tools:
OCR image extraction also requires the Tesseract OCR app installed on the server or user machine.

```bash
pip install -r requirements.txt
```

Most text/CSV tools use only the Python standard library.

## Streamlit Test Workspace

Run every current service from one browser interface while the product is in
MVP development:

```bash
streamlit run streamlit_app.py
```

The app supports interactive text tools, CSV and Excel uploads, PDF operations,
document extraction, local knowledge search, HR generators, invoices, and
downloadable results. It is a local testing surface, not the final production
hosting architecture.

### Local enhancement stack

- PyMuPDF and pdfplumber provide layout-aware PDF text and table extraction.
- pandas and DuckDB provide fast column-level data profiling.
- email-validator, phonenumbers, and RapidFuzz improve validation and duplicate detection.
- dateparser normalizes contract dates and deadlines.
- ReportLab generates print-ready PDF invoices.

## Research and Spreadsheet Discovery Services

The PubMed, news, public-company, and patent services use public web data and
therefore require internet access while they run. NCBI requires a contact email
for PubMed Entrez requests. The Excel flattener and category lister run fully
locally. These services were adapted from the user's
`teamnoether_streamlit_app` into separate, reusable Python modules.

## Tools

| Tool | Script | Example |
| --- | --- | --- |
| Excel Splitter | `excel_splitter.py` | `python excel_splitter.py workbook.xlsx --output-dir split_excel` |
| PDF Merger | `pdf_merger.py` | `python pdf_merger.py a.pdf b.pdf --output merged.pdf` |
| PDF Compressor | `pdf_compressor.py` | `python pdf_compressor.py input.pdf --output compressed.pdf` |
| CSV Cleaner | `csv_cleaner.py` | `python csv_cleaner.py dirty.csv --output clean.csv --dedupe` |
| Bulk File Renamer | `bulk_file_renamer.py` | `python bulk_file_renamer.py ./files --pattern "Report_{num}{ext}" --dry-run` |
| Meeting Notes Generator | `meeting_notes_generator.py` | `python meeting_notes_generator.py transcript.txt --output notes.md` |
| Grammar Checker | `grammar_checker.py` | `python grammar_checker.py draft.txt --output corrected.txt` |
| Resume Formatter | `resume_formatter.py` | `python resume_formatter.py resume.txt --output resume.html` |
| Invoice Generator | `invoice_generator.py` | `python invoice_generator.py invoice.json --output invoice.html` |
| Email Template Generator | `email_template_generator.py` | `python email_template_generator.py welcome --vars name=Jasper company=Acme --output email.txt` |
| Organize Files by Type | `organize_files_by_type.py` | `python organize_files_by_type.py ./downloads --dry-run` |
| Data Extractor | `data_extractor.py` | `python data_extractor.py invoice.pdf --format json --output data.json` |
| HR Toolkit | `hr_toolkit.py` | `python hr_toolkit.py job-description --role "Data Analyst" --skills SQL Excel Python` |
| PDF Suite | `pdf_suite.py` | `python pdf_suite.py split report.pdf --output-dir pages` |
| AI Knowledge Assistant | `knowledge_assistant.py` | `python knowledge_assistant.py ./docs --question "What is the refund policy?"` |
| Excel Reverse Engineering | `excel_reverse_engineering.py` | `python excel_reverse_engineering.py workbook.xlsx --output excel_report.json` |
| Vendor Comparison | `vendor_comparison.py` | `python vendor_comparison.py --text "Vendor A INR 480000. Vendor B INR 410000."` |
| Government Forms | `government_forms.py` | `python government_forms.py --input filing_notes.txt --format md --output filing_packet.md` |
| Advanced Data Cleanup | `data_cleanup_advanced.py` | `python data_cleanup_advanced.py customers.csv --output cleanup_report.json` |
| Excel-to-System | `excel_to_system.py` | `python excel_to_system.py tracker.xlsx --output system_blueprint.json` |
| Audit Engine | `audit_engine.py` | `python audit_engine.py --input audit_notes.txt --output audit_package.json` |
| RFP Generator | `rfp_generator.py` | `python rfp_generator.py --input rfp.txt --format md --output response.md` |
| Invoice Matcher | `invoice_matcher.py` | `python invoice_matcher.py --invoice invoice.txt --po po.txt --receipt receipt.txt` |
| Process Recorder | `process_recorder.py` | `python process_recorder.py --input actions.txt --output sop.json` |
| Email-to-Workflow | `email_to_workflow.py` | `python email_to_workflow.py --input email.txt --output tasks.json` |
| Folder-to-Knowledge Base | `folder_to_knowledge_base.py` | `python folder_to_knowledge_base.py ./docs --output kb_plan.json` |
| Contract Analyzer | `contract_analyzer.py` | `python contract_analyzer.py --input contract.txt --output obligations.json` |
| Invoice-to-Accounting | `invoice_to_accounting.py` | `python invoice_to_accounting.py --input invoice.txt --output accounting.json` |
| SOP-to-Automation | `sop_to_automation.py` | `python sop_to_automation.py --input sop.txt --output automation_plan.json` |
| Policy Impact Analyzer | `policy_impact_analyzer.py` | `python policy_impact_analyzer.py --input policy_change.txt --output impact.json` |
| Activity-to-Training | `activity_to_training.py` | `python activity_to_training.py --input activity.txt --output training.json` |
| PubMed Research Extractor | `pubmed_research.py` | Use `search_pubmed()` from Python or Streamlit |
| Google News Search | `news_search.py` | Use `search_news()` from Python or Streamlit |
| Company Finance Lookup | `company_finance_lookup.py` | Use `lookup_company()` from Python or Streamlit |
| Patent Intelligence | `patent_intelligence.py` | Use `fetch_patents()` from Python or Streamlit |
| Excel Merge Flattener | `excel_flattener.py` | Use `flatten_workbook()` from Python or Streamlit |
| Category Lister | `category_lister.py` | Use `list_categories()` from Python or Streamlit |

## Second Batch Notes

- `organize_files_by_type.py` can move or copy files into folders like documents, spreadsheets, images, code, and archives.
- `data_extractor.py` supports PDF/text extraction now, image OCR with optional OCR dependencies, and exports CSV, JSON, or XLSX.
- `hr_toolkit.py` includes resume parsing, candidate ranking, job descriptions, interview questions, and evaluation templates.
- `pdf_suite.py` combines common PDF actions: merge, split, compress, rotate, and extract text.
- `knowledge_assistant.py` is a free local document chat MVP using keyword retrieval. Later this can become a paid AI version with embeddings, citations, user workspaces, and team permissions.

## Advanced Automation Notes

- `automation_common.py` is a shared helper module for advanced tools. Keep it in the same folder as the scripts.
- Most advanced tools accept either `--input path.txt` or `--text "direct text"` and can output JSON or Markdown with `--format json|md`.
- Excel tools need `openpyxl`. PDF text input needs `pypdf`.
- These scripts are MVP service cores: they create structured outputs now, and later can be upgraded with AI models, OCR, integrations, permissions, billing limits, and user workspaces.

## Service Notes

- Keep free tools limited by file size, number of pages, or daily usage.
- Advanced paid versions can add batch jobs, cloud storage, OCR, AI summaries, templates, branding, and team access.
- Custom private/public tools can reuse this folder pattern: one script, clear input schema, clear output file.
