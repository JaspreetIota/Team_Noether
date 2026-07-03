"""Convert document folders into searchable knowledge base plans."""

from __future__ import annotations

import argparse
from pathlib import Path
from automation_common import top_keywords, write_output


def build_kb_plan(folder: Path) -> dict:
    docs = []
    combined = ""
    for file_path in sorted(folder.iterdir()):
        if file_path.is_file() and file_path.suffix.lower() in {".txt", ".md", ".csv", ".json"}:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            combined += "\n" + text
            docs.append({"file": file_path.name, "keywords": top_keywords(text, 8)})
    return {
        "tool": "Folder-to-Knowledge Base",
        "folder": str(folder),
        "documents_indexed": len(docs),
        "document_taxonomy": docs,
        "global_keywords": top_keywords(combined, 20),
        "recommended_structure": ["Policies", "Processes", "FAQs", "Templates", "Reference data"],
        "launch_plan": ["Upload documents", "Clean names", "Index content", "Set permissions", "Enable search/chat"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Create knowledge base plan from folder.")
    parser.add_argument("folder", type=Path)
    parser.add_argument("--output", type=Path, default=Path("folder_to_knowledge_base.json"))
    parser.add_argument("--format", choices=["json", "md"], default="json")
    args = parser.parse_args()
    print(write_output(build_kb_plan(args.folder), args.output, args.format))


if __name__ == "__main__":
    main()

