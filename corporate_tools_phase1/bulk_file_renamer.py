"""Rename many files using a numbered pattern."""

from __future__ import annotations

import argparse
from pathlib import Path


def rename_files(folder: Path, pattern: str, start: int = 1, dry_run: bool = False) -> list[tuple[Path, Path]]:
    files = sorted(path for path in folder.iterdir() if path.is_file())
    planned: list[tuple[Path, Path]] = []

    for index, file_path in enumerate(files, start=start):
        new_name = pattern.format(num=index, name=file_path.stem, ext=file_path.suffix)
        target = file_path.with_name(new_name)
        if target.exists() and target != file_path:
            raise FileExistsError(f"Target already exists: {target}")
        planned.append((file_path, target))

    if not dry_run:
        for source, target in planned:
            source.rename(target)

    return planned


def main() -> None:
    parser = argparse.ArgumentParser(description="Bulk rename files.")
    parser.add_argument("folder", type=Path)
    parser.add_argument("--pattern", required=True, help='Example: "Report_{num}{ext}"')
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    for source, target in rename_files(args.folder, args.pattern, args.start, args.dry_run):
        print(f"{source.name} -> {target.name}")


if __name__ == "__main__":
    main()

