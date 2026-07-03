"""Organize files into folders by file type."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


CATEGORIES = {
    "documents": {".pdf", ".doc", ".docx", ".txt", ".md", ".rtf"},
    "spreadsheets": {".csv", ".xls", ".xlsx", ".ods"},
    "presentations": {".ppt", ".pptx", ".key"},
    "images": {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tiff"},
    "videos": {".mp4", ".mov", ".avi", ".mkv", ".webm"},
    "audio": {".mp3", ".wav", ".aac", ".flac", ".m4a"},
    "archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "code": {".py", ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".json", ".xml"},
}


def category_for(file_path: Path) -> str:
    extension = file_path.suffix.lower()
    for category, extensions in CATEGORIES.items():
        if extension in extensions:
            return category
    return "others"


def unique_target(target: Path) -> Path:
    if not target.exists():
        return target

    counter = 2
    while True:
        candidate = target.with_name(f"{target.stem}_{counter}{target.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def organize_files(folder: Path, copy: bool = False, dry_run: bool = False) -> list[tuple[Path, Path]]:
    planned: list[tuple[Path, Path]] = []
    for file_path in sorted(folder.iterdir()):
        if not file_path.is_file():
            continue
        destination_dir = folder / category_for(file_path)
        target = unique_target(destination_dir / file_path.name)
        planned.append((file_path, target))

    if dry_run:
        return planned

    for source, target in planned:
        target.parent.mkdir(parents=True, exist_ok=True)
        if copy:
            shutil.copy2(source, target)
        else:
            shutil.move(str(source), str(target))

    return planned


def main() -> None:
    parser = argparse.ArgumentParser(description="Organize files into type-based folders.")
    parser.add_argument("folder", type=Path)
    parser.add_argument("--copy", action="store_true", help="Copy files instead of moving them")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without moving files")
    args = parser.parse_args()

    for source, target in organize_files(args.folder, args.copy, args.dry_run):
        print(f"{source.name} -> {target.parent.name}/{target.name}")


if __name__ == "__main__":
    main()

