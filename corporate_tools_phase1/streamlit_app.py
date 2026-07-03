"""Streamlit test bench for the corporate tools platform."""

from __future__ import annotations

import io
import html
import json
import sys
import tempfile
import zipfile
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from activity_to_training import training_material
from audit_engine import audit_package
from auth import render_account, require_login
from category_lister import list_categories
from company_finance_lookup import lookup_company
from contract_analyzer import analyze_contract
from csv_cleaner import clean_csv
from data_cleanup_advanced import cleanup_csv
from data_extractor import extract_data
from email_template_generator import TEMPLATES, generate_email
from email_to_workflow import email_workflow
from excel_reverse_engineering import analyze_workbook
from excel_flattener import flatten_workbook
from excel_splitter import split_excel
from excel_to_system import plan_system
from folder_to_knowledge_base import build_kb_plan
from government_forms import generate_forms_packet
from grammar_checker import grammar_check
from hr_toolkit import (
    employee_evaluation_template,
    generate_job_description,
    generate_questions,
    parse_resume,
)
from invoice_generator import generate_invoice, generate_invoice_pdf
from invoice_matcher import invoice_match
from invoice_to_accounting import accounting_entries
from knowledge_assistant import answer_question, build_index
from meeting_notes_generator import generate_notes
from news_search import search_news
from patent_intelligence import fetch_patents
from pdf_suite import compress, extract_text, merge, rotate, split
from policy_impact_analyzer import policy_impact
from process_recorder import process_document
from pubmed_research import search_pubmed
from resume_formatter import resume_to_html
from rfp_generator import rfp_response
from sop_to_automation import sop_automation
from vendor_comparison import compare_vendors


st.set_page_config(page_title="Corporate Tools", page_icon="⚡", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;600&family=Sora:wght@500;600;700&display=swap');
    :root {
      --ct-page: #f5f7fb;
      --ct-sidebar: #ffffff;
      --ct-surface: #ffffff;
      --ct-surface-2: #f1f4f9;
      --ct-surface-3: #e8edf5;
      --ct-text: #172033;
      --ct-secondary: #58677e;
      --ct-muted: #7e8ba0;
      --ct-border: #dce3ed;
      --ct-border-strong: #c6d0df;
      --ct-accent: #5b5fe9;
      --ct-accent-light: #4f52c9;
      --ct-accent-bg: #ececff;
      --ct-success: #0d7654;
      --ct-success-bg: #e8f7f1;
      --ct-amber: #a46300;
      --ct-amber-bg: #fff7dc;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --ct-page: #0b1120;
        --ct-sidebar: #0a0e1a;
        --ct-surface: #111a2e;
        --ct-surface-2: #16213a;
        --ct-surface-3: #1c2740;
        --ct-text: #f1f5f9;
        --ct-secondary: #94a3b8;
        --ct-muted: #697895;
        --ct-border: #22304d;
        --ct-border-strong: #2e3f63;
        --ct-accent: #6366f1;
        --ct-accent-light: #a5a8f5;
        --ct-accent-bg: #1a1b3d;
        --ct-success: #6ee7b7;
        --ct-success-bg: #0d2a22;
        --ct-amber: #fbbf24;
        --ct-amber-bg: #2e2410;
      }
    }
    * { letter-spacing: 0; }
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp {
      background:
        radial-gradient(circle at 78% -10%, color-mix(in srgb, var(--ct-accent) 17%, transparent), transparent 31rem),
        radial-gradient(circle at 22% 105%, color-mix(in srgb, #8b5cf6 10%, transparent), transparent 28rem),
        var(--ct-page);
      color: var(--ct-text);
    }
    header[data-testid="stHeader"] { background: transparent; }
    .block-container { max-width: 1240px; padding: 2.5rem 2.8rem 5rem; }

    [data-testid="stSidebar"] {
      background: color-mix(in srgb, var(--ct-sidebar) 94%, transparent);
      border-right: 1px solid var(--ct-border);
      backdrop-filter: blur(18px);
    }
    [data-testid="stSidebar"] > div:first-child { padding: 1.85rem 1.2rem; }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] p { color: var(--ct-secondary); }
    .ct-brand { display: flex; align-items: center; gap: .75rem; margin: .1rem 0 1.65rem; }
    .ct-brand-mark {
      display: grid; place-items: center; width: 2.35rem; height: 2.35rem; flex: 0 0 auto;
      border-radius: 12px; color: white; font: 700 1rem 'Sora', sans-serif;
      background: linear-gradient(135deg, var(--ct-accent), #8b5cf6);
      box-shadow: 0 8px 22px color-mix(in srgb, var(--ct-accent) 32%, transparent);
    }
    .ct-brand-copy strong { display: block; color: var(--ct-text); font: 700 1.02rem 'Sora', sans-serif; }
    .ct-brand-copy span { color: var(--ct-muted); font-size: .72rem; }

    div[data-baseweb="input"], div[data-baseweb="select"] > div {
      background: var(--ct-surface-2); border-color: var(--ct-border); border-radius: 12px;
      transition: border-color .2s ease, box-shadow .2s ease, background .2s ease;
    }
    div[data-baseweb="input"] input, div[data-baseweb="select"] * { color: var(--ct-text); }
    div[data-baseweb="input"]:focus-within, div[data-baseweb="select"] > div:focus-within {
      border-color: var(--ct-accent); box-shadow: 0 0 0 3px color-mix(in srgb, var(--ct-accent) 20%, transparent);
    }

    .tool-header { position: relative; margin: .35rem 0 1.8rem; animation: ctBoot .55s cubic-bezier(.2,.8,.2,1) both; }
    .tool-header::after { content: ''; position: absolute; width: 9rem; height: 9rem; right: 3%; top: -5rem; border-radius: 50%; background: var(--ct-accent); filter: blur(75px); opacity: .13; pointer-events: none; }
    .tool-kicker { display: inline-flex; align-items: center; gap: .45rem; color: var(--ct-accent-light); font: 600 .7rem 'Sora', sans-serif; letter-spacing: .12em; text-transform: uppercase; margin-bottom: .7rem; }
    .tool-kicker::before { content: ''; width: 1.5rem; height: 2px; border-radius: 2px; background: linear-gradient(90deg, var(--ct-accent), #8b5cf6); }
    .tool-title-row { display: flex; align-items: center; flex-wrap: wrap; gap: .75rem; }
    .build-tag { display: inline-flex; align-items: center; gap: .38rem; padding: .38rem .65rem; border: 1px solid color-mix(in srgb, var(--ct-amber) 35%, transparent); border-radius: 999px; background: var(--ct-amber-bg); color: var(--ct-amber); font: 600 .65rem 'Sora', sans-serif; letter-spacing: .05em; text-transform: uppercase; white-space: nowrap; }
    .build-tag::before { content: ''; width: .42rem; height: .42rem; border-radius: 50%; background: currentColor; animation: ctTagPulse 1.8s ease-in-out infinite; }
    .tool-header h1 { color: var(--ct-text); font: 700 clamp(2rem, 4vw, 3rem)/1.08 'Sora', sans-serif; letter-spacing: -.04em; margin: 0; }
    .tool-header p { color: var(--ct-secondary); font-size: .98rem; line-height: 1.65; margin: .7rem 0 0; max-width: 680px; }
    @keyframes ctBoot { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
    @keyframes ctShimmer { to { background-position: 200% center; } }
    @keyframes ctFloat { 50% { transform: translateY(-3px); } }
    @keyframes ctTagPulse { 50% { opacity: .35; box-shadow: 0 0 0 4px color-mix(in srgb, var(--ct-amber) 12%, transparent); } }

    .status-note { color: var(--ct-secondary); background: var(--ct-success-bg); border: 1px solid color-mix(in srgb, var(--ct-success) 25%, transparent); padding: .85rem .9rem; border-radius: 12px; font-size: .75rem; line-height: 1.45; }
    .status-note strong { color: var(--ct-success); }
    div[data-testid="stMetric"] {
      position: relative; overflow: hidden; background: color-mix(in srgb, var(--ct-surface) 92%, transparent);
      border: 1px solid var(--ct-border); padding: 1.25rem 1.35rem; border-radius: 16px;
      box-shadow: 0 10px 35px color-mix(in srgb, #000 7%, transparent);
      transition: border-color .25s ease, transform .25s ease, box-shadow .25s ease;
      animation: ctBoot .55s .08s cubic-bezier(.2,.8,.2,1) both;
    }
    div[data-testid="stMetric"]::after { content: ''; position: absolute; inset: 0; background: linear-gradient(110deg, transparent 35%, color-mix(in srgb, var(--ct-accent) 9%, transparent), transparent 65%); background-size: 200% 100%; opacity: 0; transition: opacity .25s; }
    div[data-testid="stMetric"]:hover { border-color: color-mix(in srgb, var(--ct-accent) 55%, var(--ct-border)); transform: translateY(-4px); box-shadow: 0 16px 40px color-mix(in srgb, var(--ct-accent) 14%, transparent); }
    div[data-testid="stMetric"]:hover::after { opacity: 1; animation: ctShimmer 1.2s linear; }
    div[data-testid="stMetric"] label { color: var(--ct-muted); text-transform: uppercase; font-size: .72rem; }
    div[data-testid="stMetricValue"] { color: var(--ct-text); font: 600 2rem 'Sora', sans-serif; letter-spacing: -.03em; }

    .st-key-tool_panel { background: color-mix(in srgb, var(--ct-surface) 94%, transparent); border: 1px solid var(--ct-border) !important; border-radius: 18px !important; padding: 1.65rem 1.75rem; margin-top: 1.7rem; box-shadow: 0 18px 55px color-mix(in srgb, #000 8%, transparent); animation: ctBoot .55s .15s cubic-bezier(.2,.8,.2,1) both; }
    .stButton > button, .stDownloadButton > button, .stFormSubmitButton > button { min-height: 2.75rem; border-radius: 12px; border: 1px solid var(--ct-border-strong); font-weight: 600; transition: transform .15s ease, box-shadow .2s ease, border-color .2s ease, background .2s ease; }
    .stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] { background: linear-gradient(135deg, var(--ct-accent), #7c3aed); color: white; border-color: transparent; box-shadow: 0 8px 20px color-mix(in srgb, var(--ct-accent) 25%, transparent); }
    .stButton > button:hover, .stDownloadButton > button:hover, .stFormSubmitButton > button:hover { border-color: var(--ct-accent); transform: translateY(-2px); box-shadow: 0 8px 24px color-mix(in srgb, var(--ct-accent) 24%, transparent); }
    .stButton > button:active, .stDownloadButton > button:active, .stFormSubmitButton > button:active { transform: scale(.98); }
    [data-baseweb="tab-list"] { border-bottom: 1px solid var(--ct-border); gap: 1.3rem; }
    [data-baseweb="tab"] { color: var(--ct-muted); }
    [aria-selected="true"][data-baseweb="tab"] { color: var(--ct-text); }
    [data-testid="stDataFrame"], [data-testid="stFileUploaderDropzone"] { border-color: var(--ct-border); border-radius: 14px; }
    [data-testid="stFileUploaderDropzone"] { background: var(--ct-surface-2); transition: border-color .2s ease, background .2s ease; }
    [data-testid="stFileUploaderDropzone"]:hover { border-color: var(--ct-accent); background: var(--ct-accent-bg); }
    [data-testid="stExpander"] { background: var(--ct-surface-2); border-color: var(--ct-border); border-radius: 12px; overflow: hidden; }
    [data-testid="stAlert"] { border-radius: 12px; }
    hr { border-color: var(--ct-border) !important; }
    ::-webkit-scrollbar { width: 9px; height: 9px; }
    ::-webkit-scrollbar-thumb { background: var(--ct-border-strong); border-radius: 9px; border: 2px solid var(--ct-page); }

    .news-item { background: var(--ct-surface); border: 1px solid var(--ct-border); border-radius: 12px; padding: 1rem 1.1rem; margin-bottom: .65rem; transition: border-color .18s ease, background .18s ease, transform .18s ease; animation: ctBoot .35s ease both; }
    .news-item:hover { border-color: var(--ct-accent); background: var(--ct-surface-2); transform: translateX(3px); }
    .news-item a { color: var(--ct-accent-light); font-weight: 600; text-decoration: none; }
    .news-item a:hover { text-decoration: underline; }
    .news-meta { color: var(--ct-muted); font: .72rem 'JetBrains Mono', monospace; margin-top: .4rem; }

    .st-key-auth_shell { max-width: 1120px; margin: 4vh auto 0; }
    .st-key-auth_visual { position: relative; overflow: hidden; min-height: 620px; padding: 0; border: 1px solid color-mix(in srgb, var(--ct-accent) 28%, transparent); border-radius: 28px; background: #080d32; box-shadow: 0 25px 70px color-mix(in srgb, #11184f 25%, transparent); }
    .auth-art { width: 100%; height: 430px; margin: 0; overflow: hidden; }
    .auth-art img { display: block; width: 100%; height: 100%; object-fit: cover; object-position: center 54%; mask-image: linear-gradient(to bottom, black 68%, transparent 100%); }
    .auth-visual-copy { position: relative; z-index: 1; padding: 0 2rem 1.7rem; color: #fff; }
    .auth-visual-copy span { color: #a5b4fc; font: 600 .68rem 'Sora', sans-serif; letter-spacing: .12em; text-transform: uppercase; }
    .auth-visual-copy h2 { max-width: 430px; margin: .55rem 0 .65rem; color: #fff; font: 700 2rem/1.15 'Sora', sans-serif; letter-spacing: -.04em; }
    .auth-visual-copy p { max-width: 470px; margin: 0; color: #aeb8dc; font-size: .86rem; line-height: 1.6; }
    .auth-features { display: flex; flex-wrap: wrap; gap: .55rem; margin-top: 1.1rem; }
    .auth-features b { padding: .42rem .65rem; border: 1px solid rgba(165,180,252,.18); border-radius: 999px; background: rgba(99,102,241,.12); color: #dbe3ff; font-size: .66rem; font-weight: 600; }
    .auth-hero { max-width: 430px; margin: 0 0 1.4rem; text-align: left; animation: ctBoot .55s cubic-bezier(.2,.8,.2,1) both; }
    .auth-mark { display: grid; place-items: center; width: 3.3rem; height: 3.3rem; margin: 0 0 1.2rem; border-radius: 16px; background: linear-gradient(135deg, var(--ct-accent), #8b5cf6); color: white; font: 700 1.3rem 'Sora', sans-serif; box-shadow: 0 12px 30px color-mix(in srgb, var(--ct-accent) 32%, transparent); animation: ctFloat 4s ease-in-out infinite; }
    .auth-hero .tool-kicker::before { display: none; }
    .auth-hero h1 { color: var(--ct-text); font: 700 2.45rem 'Sora', sans-serif; letter-spacing: -.045em; margin: .2rem 0 .5rem; }
    .auth-hero p { color: var(--ct-secondary); line-height: 1.6; margin: 0; }
    .auth-byline { margin-top: .65rem; color: var(--ct-muted); font: 500 .72rem 'Sora', sans-serif; letter-spacing: .04em; }
    .st-key-login_form { max-width: 430px; margin: 0; padding: 1.5rem 1.6rem; border: 1px solid var(--ct-border); border-radius: 18px; background: color-mix(in srgb, var(--ct-surface) 94%, transparent); box-shadow: 0 20px 55px color-mix(in srgb, #000 10%, transparent); animation: ctBoot .55s .08s cubic-bezier(.2,.8,.2,1) both; }
    [data-testid="stFormSubmitButton"] > button { background: linear-gradient(135deg, var(--ct-accent), #7c3aed) !important; border-color: transparent !important; color: white !important; }
    .account-note { display: flex; justify-content: space-between; align-items: center; margin: .7rem 0; color: var(--ct-muted); font-size: .72rem; }
    .account-note strong { color: var(--ct-text); font-size: .76rem; }

    @media (max-width: 760px) {
      .block-container { padding: 1.5rem 1rem 3rem; }
      .tool-header h1 { font-size: 1.8rem; }
      .st-key-tool_panel { padding: 1rem; }
      .st-key-auth_shell { margin-top: 2vh; }
      .st-key-auth_visual { display: none; }
      .auth-hero { margin: 5vh auto 1.25rem; text-align: center; }
      .auth-mark { margin-left: auto; margin-right: auto; }
      .auth-hero .tool-kicker { justify-content: center; }
      .st-key-login_form { margin: 0 auto; }
    }
    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after { animation-duration: .01ms !important; animation-iteration-count: 1 !important; transition-duration: .01ms !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

current_user = require_login()

TEXT_TOOLS = {
    "Vendor Comparison": ("Procurement", "Compare proposals, pricing, features, and risks.", compare_vendors),
    "Government Forms": ("Compliance", "Create a filing preparation packet from business details.", generate_forms_packet),
    "Audit Engine": ("Compliance", "Turn audit notes into an evidence and control package.", audit_package),
    "RFP Generator": ("Sales", "Structure an RFP response from requirements and company knowledge.", rfp_response),
    "Process Recorder": ("Operations", "Convert recorded actions into an SOP and checklist.", process_document),
    "Email-to-Workflow": ("Automation", "Convert an email into tasks, approvals, and workflow steps.", email_workflow),
    "Contract Analyzer": ("Legal", "Extract obligations, dates, risks, and renewal signals.", analyze_contract),
    "Invoice-to-Accounting": ("Finance", "Create an accounting-entry plan from invoice text.", accounting_entries),
    "SOP-to-Automation": ("Automation", "Convert a procedure into an executable automation blueprint.", sop_automation),
    "Policy Impact Analyzer": ("Compliance", "Identify affected teams, systems, documents, and controls.", policy_impact),
    "Activity-to-Training": ("HR", "Generate onboarding and training material from employee activity.", training_material),
}

TOOLS = {
    "CSV Cleaner": ("Data", "Normalize headers, trim values, remove blank rows, and deduplicate."),
    "Advanced Data Cleanup": ("Data", "Validate, normalize, deduplicate, and review business data."),
    "Excel Splitter": ("Spreadsheets", "Split one workbook into a file for every worksheet."),
    "Excel Reverse Engineering": ("Spreadsheets", "Explain formulas, dependencies, errors, and workbook structure."),
    "Excel-to-System": ("Spreadsheets", "Turn a workbook into a database and workflow blueprint."),
    "PDF Suite": ("Documents", "Merge, split, compress, rotate, or extract text from PDFs."),
    "Data Extractor": ("Documents", "Extract structured data from PDFs, images, receipts, and statements."),
    "Knowledge Assistant": ("Knowledge", "Ask questions across uploaded documents using local retrieval."),
    "Folder-to-Knowledge Base": ("Knowledge", "Inventory uploaded files and plan a searchable knowledge base."),
    "Meeting Notes Generator": ("Writing", "Create structured notes, decisions, and actions from a transcript."),
    "Grammar Checker": ("Writing", "Apply lightweight grammar, capitalization, and spacing fixes."),
    "Resume Formatter": ("HR", "Convert a plain-text resume into a polished HTML document."),
    "HR Toolkit": ("HR", "Parse resumes, generate job descriptions, questions, and evaluations."),
    "Invoice Generator": ("Finance", "Create a downloadable HTML invoice."),
    "Invoice Matcher": ("Finance", "Compare invoice, purchase order, and receipt values."),
    "Email Template Generator": ("Writing", "Generate reusable business email templates."),
    "File Organizer & Renamer": ("Files", "Preview organized folders and batch-renamed files."),
    "PubMed Research Extractor": ("Research", "Find publications and institutional author contacts from PubMed."),
    "Google News Search": ("Research", "Find recent topic and company coverage through Google News RSS."),
    "Company Finance Lookup": ("Research", "Look up public-company symbols, exchanges, and profiles."),
    "Patent Intelligence": ("Research", "Collect inventor, assignee, status, and PDF metadata for patents."),
    "Excel Merge Flattener": ("Spreadsheets", "Unmerge Excel ranges and fill every cell with the merged value."),
    "Category Lister": ("Spreadsheets", "Extract a clean, unique category list from an Excel workbook."),
    **{name: (category, description) for name, (category, description, _) in TEXT_TOOLS.items()},
}

READY_TOOLS = {
    "Category Lister",
    "Excel Merge Flattener",
    "Patent Intelligence",
    "Company Finance Lookup",
    "Google News Search",
    "PubMed Research Extractor",
    "PDF Suite",
    "Excel Splitter",
}

DEFAULT_TOOL = "Company Finance Lookup"


def save_upload(upload, folder: Path) -> Path:
    path = folder / Path(upload.name).name
    path.write_bytes(upload.getvalue())
    return path


def download_json(data: object, name: str = "result.json") -> None:
    st.download_button("Download JSON", json.dumps(data, indent=2, default=str), name, "application/json")


def finance_value(value: object, currency: str = "") -> str:
    """Format Yahoo Finance values for compact overview metrics."""
    if value in (None, "", "N/A"):
        return "—"
    if isinstance(value, (int, float)):
        prefix = f"{currency} " if currency else ""
        absolute = abs(value)
        if absolute >= 1_000_000_000_000:
            return f"{prefix}{value / 1_000_000_000_000:.2f}T"
        if absolute >= 1_000_000_000:
            return f"{prefix}{value / 1_000_000_000:.2f}B"
        if absolute >= 1_000_000:
            return f"{prefix}{value / 1_000_000:.2f}M"
        if isinstance(value, int):
            return f"{prefix}{value:,}"
        return f"{prefix}{value:,.2f}"
    return str(value)


def show_yahoo_module(info: dict, module: str, title: str) -> None:
    data = info.get(module)
    if data:
        with st.expander(title):
            st.json(data, expanded=True)


def render_result(data: object) -> None:
    if isinstance(data, (dict, list)):
        st.json(data, expanded=True)
        download_json(data)
    else:
        st.text_area("Result", str(data), height=360)
        st.download_button("Download result", str(data), "result.txt", "text/plain")


def table_downloads(records: list[dict], basename: str, link_columns: dict[str, str] | None = None) -> None:
    import pandas as pd

    frame = pd.DataFrame(records)
    if frame.empty:
        st.info("No matching records were returned. Try broadening the query or filters.")
        return
    column_config = {column: st.column_config.LinkColumn(label) for column, label in (link_columns or {}).items() if column in frame.columns}
    st.dataframe(frame, use_container_width=True, hide_index=True, column_config=column_config)
    excel = io.BytesIO()
    with pd.ExcelWriter(excel, engine="xlsxwriter") as writer:
        frame.to_excel(writer, index=False, sheet_name="Results")
        worksheet = writer.sheets["Results"]
        for index, column in enumerate(frame.columns):
            width = min(max(len(str(column)) + 2, frame[column].astype(str).map(len).max() + 2), 55)
            worksheet.set_column(index, index, width)
    excel.seek(0)
    excel_col, csv_col, json_col = st.columns(3)
    excel_col.download_button("Download Excel", excel.getvalue(), f"{basename}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    csv_col.download_button("Download CSV", frame.to_csv(index=False), f"{basename}.csv", "text/csv", use_container_width=True)
    json_col.download_button("Download JSON", frame.to_json(orient="records", indent=2), f"{basename}.json", "application/json", use_container_width=True)


def text_tool(name: str) -> None:
    _, _, runner = TEXT_TOOLS[name]
    sample = st.text_area("Business input", height=280, placeholder="Paste source text, notes, requirements, or document content here...")
    if st.button("Run tool", type="primary", disabled=not sample.strip()):
        with st.spinner("Building structured result..."):
            render_result(runner(sample))


def csv_tools(name: str) -> None:
    upload = st.file_uploader("Upload CSV", type=["csv"])
    dedupe = st.checkbox("Remove duplicate rows", value=True)
    if upload and st.button("Clean data", type="primary"):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            source = save_upload(upload, folder)
            if name == "Advanced Data Cleanup":
                render_result(cleanup_csv(source))
            else:
                output = folder / "cleaned.csv"
                clean_csv(source, output, dedupe=dedupe)
                st.success("CSV cleaned successfully.")
                st.download_button("Download cleaned CSV", output.read_bytes(), "cleaned.csv", "text/csv")


def excel_tools(name: str) -> None:
    upload = st.file_uploader("Upload Excel workbook", type=["xlsx"])
    if upload and st.button("Analyze workbook" if name != "Excel Splitter" else "Split workbook", type="primary"):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            source = save_upload(upload, folder)
            if name == "Excel Reverse Engineering":
                render_result(analyze_workbook(source))
            elif name == "Excel-to-System":
                render_result(plan_system(source))
            else:
                outputs = split_excel(source, folder / "sheets")
                bundle = io.BytesIO()
                with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as archive:
                    for output in outputs:
                        archive.write(output, output.name)
                st.success(f"Created {len(outputs)} worksheet files.")
                st.download_button("Download worksheet ZIP", bundle.getvalue(), "split_workbook.zip", "application/zip")


def pdf_tool() -> None:
    action = st.segmented_control("Operation", ["Merge", "Split", "Compress", "Rotate", "Extract text"], default="Merge")
    multiple = action == "Merge"
    uploads = st.file_uploader("Upload PDF files" if multiple else "Upload PDF", type=["pdf"], accept_multiple_files=multiple)
    degrees = st.selectbox("Rotation", [90, 180, 270], disabled=action != "Rotate")
    ready = bool(uploads)
    if st.button("Process PDF", type="primary", disabled=not ready):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            files = [save_upload(item, folder) for item in uploads] if multiple else [save_upload(uploads, folder)]
            if action == "Merge":
                output = merge(files, folder / "merged.pdf")
            elif action == "Compress":
                output = compress(files[0], folder / "compressed.pdf")
            elif action == "Rotate":
                output = rotate(files[0], folder / "rotated.pdf", degrees)
            elif action == "Extract text":
                output = extract_text(files[0], folder / "extracted.txt")
            else:
                pages = split(files[0], folder / "pages")
                bundle = io.BytesIO()
                with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as archive:
                    for page in pages:
                        archive.write(page, page.name)
                st.download_button("Download pages ZIP", bundle.getvalue(), "pdf_pages.zip", "application/zip")
                return
            mime = "text/plain" if output.suffix == ".txt" else "application/pdf"
            st.download_button(f"Download {output.name}", output.read_bytes(), output.name, mime)


def extraction_tool() -> None:
    uploads = st.file_uploader("Upload business documents", type=["pdf", "png", "jpg", "jpeg", "txt"], accept_multiple_files=True)
    output_format = st.selectbox("Output format", ["json", "csv", "xlsx"])
    if st.button("Extract data", type="primary", disabled=not uploads):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            inputs = [save_upload(item, folder) for item in uploads]
            output = folder / f"extracted.{output_format}"
            extract_data(inputs, output, output_format)
            mime = {"json": "application/json", "csv": "text/csv", "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}[output_format]
            if output_format == "json":
                st.json(json.loads(output.read_text(encoding="utf-8")))
            st.download_button("Download extracted data", output.read_bytes(), output.name, mime)


def knowledge_tool(plan_only: bool = False) -> None:
    uploads = st.file_uploader("Upload documents", type=["txt", "md", "pdf"], accept_multiple_files=True)
    question = st.text_input("Question", disabled=plan_only, placeholder="What do these documents say about...")
    label = "Build knowledge-base plan" if plan_only else "Ask documents"
    if st.button(label, type="primary", disabled=not uploads or (not plan_only and not question.strip())):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            paths = [save_upload(item, folder) for item in uploads]
            if plan_only:
                render_result(build_kb_plan(folder))
            else:
                st.markdown(answer_question(build_index(paths), question))


def writing_tool(name: str) -> None:
    text = st.text_area("Source text", height=300)
    if st.button("Generate", type="primary", disabled=not text.strip()):
        if name == "Grammar Checker":
            result = grammar_check(text)
            render_result(result)
        elif name == "Meeting Notes Generator":
            render_result(generate_notes(text))
        else:
            html = resume_to_html(text)
            st.components.v1.html(html, height=500, scrolling=True)
            st.download_button("Download formatted resume", html, "resume.html", "text/html")


def hr_tool() -> None:
    action = st.segmented_control("HR workflow", ["Resume parser", "Job description", "Interview questions", "Evaluation"], default="Resume parser")
    if action == "Resume parser":
        text = st.text_area("Resume text", height=300)
        if st.button("Parse resume", type="primary", disabled=not text.strip()):
            render_result(parse_resume(text))
        return
    role = st.text_input("Role", "Data Analyst")
    skills = st.text_input("Skills, comma separated", "SQL, Excel, Python")
    level = st.selectbox("Level", ["Junior", "Mid-level", "Senior", "Lead"], disabled=action != "Job description")
    if st.button("Generate", type="primary", disabled=not role.strip()):
        skill_list = [item.strip() for item in skills.split(",") if item.strip()]
        if action == "Job description":
            render_result(generate_job_description(role, level, skill_list))
        elif action == "Interview questions":
            render_result(generate_questions(role, skill_list, 12))
        else:
            render_result(employee_evaluation_template(role))


def invoice_generator_tool() -> None:
    left, right = st.columns(2)
    with left:
        number = st.text_input("Invoice number", "INV-1001")
        business = st.text_input("Business name", "Your Company")
        client = st.text_input("Client", "Acme Corp")
        date = st.date_input("Invoice date")
    with right:
        description = st.text_input("Item description", "Consulting services")
        quantity = st.number_input("Quantity", min_value=1.0, value=1.0)
        price = st.number_input("Unit price", min_value=0.0, value=1000.0)
        tax = st.number_input("Tax rate", min_value=0.0, max_value=1.0, value=0.18, step=0.01)
    if st.button("Generate invoice", type="primary"):
        data = {"invoice_number": number, "date": str(date), "business_name": business, "client_name": client, "tax_rate": tax, "items": [{"description": description, "quantity": quantity, "unit_price": price}]}
        html = generate_invoice(data)
        pdf = generate_invoice_pdf(data)
        st.components.v1.html(html, height=620, scrolling=True)
        html_col, pdf_col = st.columns(2)
        html_col.download_button("Download HTML", html, f"{number}.html", "text/html")
        pdf_col.download_button("Download PDF", pdf, f"{number}.pdf", "application/pdf")


def invoice_matcher_tool() -> None:
    invoice = st.text_area("Invoice", height=160)
    po = st.text_area("Purchase order", height=160)
    receipt = st.text_area("Delivery receipt", height=160)
    if st.button("Match documents", type="primary", disabled=not (invoice and po and receipt)):
        render_result(invoice_match(invoice, po, receipt))


def email_tool() -> None:
    template = st.selectbox("Template", sorted(TEMPLATES))
    name = st.text_input("Recipient", "Alex")
    company = st.text_input("Company", "Acme")
    topic = st.text_input("Topic", "our proposal")
    sender = st.text_input("Sender", "Team")
    if st.button("Generate email", type="primary"):
        result = generate_email(template, {"name": name, "company": company, "topic": topic, "sender": sender, "invoice_number": "INV-1001", "due_date": "Friday", "time_option": "Tuesday at 2 PM"})
        render_result(result)


def file_preview_tool() -> None:
    uploads = st.file_uploader("Choose files", accept_multiple_files=True)
    pattern = st.text_input("Rename pattern", "Document_{num}{ext}")
    if uploads:
        categories = {"pdf": "Documents", "docx": "Documents", "xlsx": "Spreadsheets", "csv": "Spreadsheets", "png": "Images", "jpg": "Images", "zip": "Archives"}
        preview = []
        for index, item in enumerate(uploads, 1):
            suffix = Path(item.name).suffix
            target = pattern.replace("{num}", str(index)).replace("{ext}", suffix)
            preview.append({"original": item.name, "category": categories.get(suffix.lstrip(".").lower(), "Other"), "new_name": target})
        st.dataframe(preview, use_container_width=True)
        st.caption("Preview mode keeps browser uploads unchanged. Server deployment can enable direct folder operations.")


def research_tool(name: str) -> None:
    if name == "PubMed Research Extractor":
        query = st.text_area("PubMed query", value='("workflow automation") AND 2024:2026[Date - Publication]', height=120)
        email = st.text_input("Contact email required by NCBI", placeholder="you@company.com")
        countries = st.multiselect("Affiliation countries", ["United States", "USA", "United Kingdom", "India", "Canada", "Australia", "Germany", "France", "China", "Japan"], default=[])
        limit = st.number_input("Maximum publications", min_value=10, max_value=1000, value=100, step=10)
        if st.button("Search PubMed", type="primary", disabled=not (query.strip() and email.strip())):
            with st.status("Searching PubMed and preparing the table...", expanded=False) as status:
                result = search_pubmed(query, email, countries, limit=int(limit))
                status.update(label=f"Found {result['result_count']} author records", state="complete")
            records = result["records"]
            for record in records:
                record["pubmed_url"] = f"https://pubmed.ncbi.nlm.nih.gov/{record['pmid']}/" if record.get("pmid") else ""
                record["doi_url"] = f"https://doi.org/{record['doi']}" if record.get("doi") else ""
            count_col, article_col, institution_col = st.columns(3)
            count_col.metric("Author records", len(records))
            article_col.metric("Unique articles", len({item.get("pmid") for item in records}))
            institution_col.metric("Institutions", len({item.get("institution") for item in records}))
            results_tab, raw_tab = st.tabs(["Results table", "Raw response"])
            with results_tab:
                table_downloads(records, "pubmed_results", {"pubmed_url": "PubMed", "doi_url": "DOI"})
            with raw_tab:
                st.json(result, expanded=False)
    elif name == "Google News Search":
        query = st.text_input("Topic, company, or keyword", "business automation")
        limit = st.slider("Maximum articles", 1, 30, 10)
        if st.button("Search news", type="primary", disabled=not query.strip()):
            with st.spinner("Finding recent coverage..."):
                result = search_news(query, limit)
            articles = result["articles"]
            st.success(f"Found {len(articles)} articles for {query}.")
            links_tab, table_tab = st.tabs(["Clickable articles", "Export table"])
            with links_tab:
                for article in articles:
                    title = html.escape(article.get("title", "Untitled article"))
                    link = html.escape(article.get("link", ""), quote=True)
                    source = html.escape(article.get("source", ""))
                    published = html.escape(article.get("published", ""))
                    st.markdown(f'<div class="news-item"><a href="{link}" target="_blank">{title}</a><div class="news-meta">{source} &nbsp; {published}</div></div>', unsafe_allow_html=True)
            with table_tab:
                table_downloads(articles, "google_news_results", {"link": "Open article"})
    elif name == "Company Finance Lookup":
        company = st.text_input("Company name", "Microsoft")
        if st.button("Look up company", type="primary", disabled=not company.strip()):
            with st.spinner("Looking up public company data..."):
                result = lookup_company(company)
            matches = result["matches"]
            if not matches:
                st.warning(f"No public company was found for {company}.")
                return

            info = result["company_info"]
            profile = info.get("assetProfile", {})
            price = info.get("price", {})
            summary = info.get("summaryDetail", {})
            financial = info.get("financialData", {})
            company_name = price.get("longName") or matches[0].get("name") or company
            symbol = result["symbol"]
            currency = price.get("currency", "")

            st.subheader(f"{company_name} ({symbol})")
            st.caption("Detailed company information supplied by Yahoo Finance")
            metric_cols = st.columns(4)
            metric_cols[0].metric("Market price", finance_value(price.get("regularMarketPrice"), currency))
            metric_cols[1].metric("Market cap", finance_value(summary.get("marketCap"), currency))
            metric_cols[2].metric("Revenue", finance_value(financial.get("totalRevenue"), currency))
            metric_cols[3].metric("Employees", finance_value(profile.get("fullTimeEmployees")))

            overview_tab, finance_tab, statements_tab, ownership_tab, raw_tab = st.tabs(
                ["Company overview", "Market & financials", "Statements & trends", "Ownership & filings", "Complete Yahoo data"]
            )
            with overview_tab:
                if profile.get("longBusinessSummary"):
                    st.markdown("#### Business summary")
                    st.write(profile["longBusinessSummary"])
                overview = {
                    "Sector": profile.get("sector"),
                    "Industry": profile.get("industry"),
                    "Country": profile.get("country"),
                    "City": profile.get("city"),
                    "Website": profile.get("website"),
                    "Phone": profile.get("phone"),
                    "Exchange": price.get("exchangeName") or matches[0].get("exchange"),
                    "Quote type": price.get("quoteType") or matches[0].get("type"),
                }
                st.table({"Field": list(overview), "Value": [value or "—" for value in overview.values()]})
                show_yahoo_module(info, "assetProfile", "Full company profile")
                show_yahoo_module(info, "calendarEvents", "Corporate calendar")
            with finance_tab:
                for module, title in (
                    ("price", "Price and exchange data"),
                    ("summaryDetail", "Trading and valuation summary"),
                    ("financialData", "Financial performance"),
                    ("defaultKeyStatistics", "Key statistics"),
                    ("quoteType", "Security details"),
                ):
                    show_yahoo_module(info, module, title)
            with statements_tab:
                for module, title in (
                    ("incomeStatementHistory", "Annual income statements"),
                    ("incomeStatementHistoryQuarterly", "Quarterly income statements"),
                    ("balanceSheetHistory", "Annual balance sheets"),
                    ("balanceSheetHistoryQuarterly", "Quarterly balance sheets"),
                    ("cashflowStatementHistory", "Annual cash-flow statements"),
                    ("cashflowStatementHistoryQuarterly", "Quarterly cash-flow statements"),
                    ("earnings", "Earnings"),
                    ("earningsHistory", "Earnings history"),
                    ("earningsTrend", "Earnings trend"),
                    ("recommendationTrend", "Analyst recommendations"),
                ):
                    show_yahoo_module(info, module, title)
            with ownership_tab:
                for module, title in (
                    ("majorHoldersBreakdown", "Major holders"),
                    ("institutionOwnership", "Institutional ownership"),
                    ("fundOwnership", "Fund ownership"),
                    ("insiderHolders", "Insider holders"),
                    ("insiderTransactions", "Insider transactions"),
                    ("netSharePurchaseActivity", "Share purchase activity"),
                    ("secFilings", "SEC filings"),
                    ("upgradeDowngradeHistory", "Upgrades and downgrades"),
                ):
                    show_yahoo_module(info, module, title)
            with raw_tab:
                st.json(info, expanded=False)
                download_json(result, f"{symbol}_yahoo_finance.json")
    else:
        raw = st.text_area("Patent document numbers", placeholder="US12345678B2\nEP1234567A1", height=180)
        numbers = [value.strip() for value in raw.replace(",", "\n").splitlines() if value.strip()]
        fetch_depth = st.radio(
            "Fetch depth",
            ["Quick", "Standard", "Complete", "Custom"],
            index=1,
            horizontal=True,
            help="Quick returns the core profile only. Deeper modes parse more sections and may take longer.",
        )
        group_labels = {
            "Translate names and assignees": "translations",
            "Legal events, assignments and litigation": "legal",
            "Classifications, landscapes and keywords": "classifications",
            "Claims": "claims",
            "Patent family and priority applications": "family",
            "Patent and non-patent citations": "citations",
            "Similar and related documents": "related",
            "Full description and drawing links": "full_text_media",
        }
        standard_groups = {"translations", "legal", "classifications", "family", "citations"}
        if fetch_depth == "Quick":
            detail_groups = set()
            st.caption("Fastest: title, abstract, inventors, assignees, status, dates, expiration and links.")
        elif fetch_depth == "Standard":
            detail_groups = standard_groups
            st.caption("Recommended: core profile plus translations, legal history, classifications, family and citations.")
        elif fetch_depth == "Complete":
            detail_groups = set(group_labels.values())
            st.caption("Everything available, including claims, full description and drawing links.")
        else:
            chosen_groups = st.multiselect("Choose optional detail groups", list(group_labels), default=["Legal events, assignments and litigation"])
            detail_groups = {group_labels[label] for label in chosen_groups}
        if st.button("Fetch patents", type="primary", disabled=not numbers):
            with st.spinner(f"Collecting {fetch_depth.lower()} patent data..."):
                result = fetch_patents(numbers, detail_groups)
            patents = result["patents"]
            summary_records = []
            for patent in patents:
                summary_records.append({
                    "document_number": patent.get("document_number", ""),
                    "document_number_used": patent.get("document_number_used", ""),
                    "availability": patent.get("availability", ""),
                    "title": patent.get("title", ""),
                    "inventors": "; ".join(patent.get("inventors", [])),
                    "inventors_translated": "; ".join(patent.get("inventors_translated", [])),
                    "original_assignees": "; ".join(patent.get("assignees_original", [])),
                    "current_assignees": "; ".join(patent.get("assignees_current", [])),
                    "translated_assignees": "; ".join(patent.get("assignees_translated", [])),
                    "legal_status": patent.get("legal_status", ""),
                    "application_number": patent.get("application_number", ""),
                    "priority_date": patent.get("priority_date", ""),
                    "filing_date": patent.get("filing_date", ""),
                    "publication_date": patent.get("publication_date", ""),
                    "grant_date": patent.get("grant_date", ""),
                    "adjusted_expiration": patent.get("adjusted_expiration", ""),
                    "anticipated_expiration": patent.get("anticipated_expiration", ""),
                    "claim_count": patent.get("claim_count", ""),
                    "classification_count": len(patent.get("classifications", [])),
                    "family_application_count": len(patent.get("family_applications", [])),
                    "patent_citation_count": len(patent.get("patent_citations", [])),
                    "cited_by_count": len(patent.get("cited_by", [])),
                    "legal_event_count": len(patent.get("legal_events", [])),
                    "pdf": patent.get("pdf", ""),
                    "google_patents_url": patent.get("google_patents_url", ""),
                })
            summary_tab, details_tab = st.tabs(["Patent summary & exports", "Selected details"])
            with summary_tab:
                table_downloads(
                    summary_records,
                    "patent_intelligence",
                    {"pdf": "Patent PDF", "google_patents_url": "Google Patents"},
                )
            with details_tab:
                st.caption(f"Fetched optional groups: {', '.join(result['detail_groups_fetched']) or 'none (Quick mode)'}")
                download_json(result, "patent_intelligence_complete.json")
                for patent in patents:
                    label = f"{patent.get('document_number', 'Patent')} — {patent.get('legal_status') or patent.get('availability', '')}"
                    with st.expander(label):
                        if patent.get("abstract"):
                            st.markdown("#### Abstract")
                            st.write(patent["abstract"])
                        events = patent.get("legal_events", [])
                        if events:
                            st.markdown("#### Legal-event history")
                            st.dataframe(events, use_container_width=True, hide_index=True)
                        st.markdown("#### Complete record")
                        st.json(patent, expanded=False)


def spreadsheet_discovery_tool(name: str) -> None:
    upload = st.file_uploader("Upload Excel workbook", type=["xlsx"])
    if upload and st.button("Flatten workbook" if name == "Excel Merge Flattener" else "Extract categories", type="primary"):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            source = save_upload(upload, folder)
            if name == "Excel Merge Flattener":
                output = folder / "flattened_workbook.xlsx"
                result = flatten_workbook(source, output)
                st.json(result)
                st.download_button("Download flattened workbook", output.read_bytes(), output.name, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            else:
                result = list_categories(source)
                st.metric("Unique categories", result["category_count"])
                st.dataframe({"Category": result["categories"]}, use_container_width=True)
                st.download_button("Download category list", "Category\n" + "\n".join(result["categories"]), "categories.csv", "text/csv")


with st.sidebar:
    st.markdown("<div class='ct-brand'><div class='ct-brand-mark'>N</div><div class='ct-brand-copy'><strong>Corporate Tools</strong><span>Work smarter, in one place</span></div></div>", unsafe_allow_html=True)
    search = st.text_input("Search tools", placeholder="invoice, PDF, HR...")
    categories = ["All"] + sorted({category for category, _ in TOOLS.values()})
    category = st.selectbox("Category", categories)
    filtered = [name for name, (group, _) in TOOLS.items() if (category == "All" or group == category) and search.lower() in name.lower()]
    if not filtered:
        st.warning("No matching tools")
        filtered = list(TOOLS)
    selection_key = f"tool_{category}_{search.strip().lower()}"
    default_index = filtered.index(DEFAULT_TOOL) if category == "All" and not search.strip() and DEFAULT_TOOL in filtered else 0
    selected = st.selectbox(
        "Tool",
        filtered,
        index=default_index,
        key=selection_key,
        format_func=lambda name: name if name in READY_TOOLS else f"{name} · In build",
    )
    st.divider()
    st.markdown("<div class='status-note'><strong>● Privacy-first workspace</strong><br>Your files stay within this session.</div>", unsafe_allow_html=True)

    render_account(current_user)

group, description = TOOLS[selected]
build_tag = "" if selected in READY_TOOLS else "<span class='build-tag'>In build</span>"
st.markdown(
    f"<div class='tool-header'><div class='tool-kicker'>{html.escape(group)} workspace</div>"
    f"<div class='tool-title-row'><h1>{html.escape(selected)}</h1>{build_tag}</div>"
    f"<p>{html.escape(description)}</p></div>",
    unsafe_allow_html=True,
)

metric1, metric2 = st.columns(2)
metric1.metric("Available tools", len(TOOLS))
metric2.metric("Category", group)

with st.container(border=True, key="tool_panel"):
    try:
        if selected in TEXT_TOOLS:
            text_tool(selected)
        elif selected in {"CSV Cleaner", "Advanced Data Cleanup"}:
            csv_tools(selected)
        elif selected in {"Excel Splitter", "Excel Reverse Engineering", "Excel-to-System"}:
            excel_tools(selected)
        elif selected == "PDF Suite":
            pdf_tool()
        elif selected == "Data Extractor":
            extraction_tool()
        elif selected == "Knowledge Assistant":
            knowledge_tool()
        elif selected == "Folder-to-Knowledge Base":
            knowledge_tool(plan_only=True)
        elif selected in {"Meeting Notes Generator", "Grammar Checker", "Resume Formatter"}:
            writing_tool(selected)
        elif selected == "HR Toolkit":
            hr_tool()
        elif selected == "Invoice Generator":
            invoice_generator_tool()
        elif selected == "Invoice Matcher":
            invoice_matcher_tool()
        elif selected == "Email Template Generator":
            email_tool()
        elif selected == "File Organizer & Renamer":
            file_preview_tool()
        elif selected in {"PubMed Research Extractor", "Google News Search", "Company Finance Lookup", "Patent Intelligence"}:
            research_tool(selected)
        elif selected in {"Excel Merge Flattener", "Category Lister"}:
            spreadsheet_discovery_tool(selected)
    except Exception as exc:
        st.error(f"The tool could not complete this test: {exc}")
        st.caption("Check optional PDF, Excel, or OCR dependencies when processing those file types.")
