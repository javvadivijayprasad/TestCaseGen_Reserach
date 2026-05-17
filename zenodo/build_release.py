"""Build the RAITG Zenodo release bundle.

Produces a single ZIP file under zenodo/dist/ containing:
  - datasets/    (312-requirement corpora)
  - results/runs/ (per-requirement run logs)
  - tables/      (aggregate + per-domain CSVs)
  - figures/     (PNGs used by the paper)
  - repo/        (three reference applications)
  - scripts/     (experiment pipeline)
  - paper/       (.tex source + compiled PDF if present)
  - README.md    (from zenodo/README_zenodo.md)
  - LICENSE      (from zenodo/LICENSE)
  - CITATION.cff (from zenodo/CITATION.cff)
  - requirements.txt

Usage:
    python zenodo/build_release.py
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZENODO = ROOT / "zenodo"
DIST = ZENODO / "dist"
VERSION = "1.0.0"
RELEASE_NAME = f"raitg-v{VERSION}"

# What to include, and what to map it to inside the archive
INCLUDE = {
    "datasets": "datasets",
    "results/runs": "results/runs",                        # Sonnet 4.6 main run
    "results_haiku/runs": "results_haiku/runs",            # Haiku 4.5 multi-model run
    "results_haiku/tables": "results_haiku/tables",
    "tables": "tables",
    "figures": "figures",
    "repo": "repo",
    "scripts": "scripts",
    "requirements.txt": "requirements.txt",
}

# Intentionally NOT including the paper PDF or LaTeX source in the Zenodo
# release. This matches the established convention of the research series
# (e.g., zenodo.19682733 for the Software Defect Prediction Dataset), which
# ships only the dataset + code + reference artefacts needed to reproduce
# the results. The paper itself is distributed through the journal /
# preprint channel.
PAPER_SOURCES: list[str] = []


def sha256sum(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_tree(src: Path, dst: Path, *, exclude_suffixes=(".pyc",),
              exclude_names=("__pycache__", ".DS_Store")) -> None:
    if src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return
    for root, dirs, files in os.walk(src):
        # filter dirs in place
        dirs[:] = [d for d in dirs if d not in exclude_names]
        rel = Path(root).relative_to(src)
        target_dir = dst / rel
        target_dir.mkdir(parents=True, exist_ok=True)
        for f in files:
            if f in exclude_names:
                continue
            if any(f.endswith(sfx) for sfx in exclude_suffixes):
                continue
            shutil.copy2(Path(root) / f, target_dir / f)


def main() -> int:
    DIST.mkdir(parents=True, exist_ok=True)
    staged = DIST / RELEASE_NAME
    if staged.exists():
        shutil.rmtree(staged)
    staged.mkdir(parents=True)

    # 1. Core artefact folders
    manifest: list[dict] = []
    for src_rel, dst_rel in INCLUDE.items():
        src = ROOT / src_rel
        if not src.exists():
            print(f"[warn] missing: {src_rel}")
            continue
        dst = staged / dst_rel
        copy_tree(src, dst)
        print(f"  included: {src_rel}  →  {dst_rel}")

    # 2. Paper sources are deliberately omitted (see PAPER_SOURCES comment).
    for name in PAPER_SOURCES:
        src = ROOT / name
        if src.exists():
            (staged / "paper").mkdir(exist_ok=True)
            shutil.copy2(src, staged / "paper" / name)
            print(f"  included: {name}  →  paper/{name}")

    # 3. Zenodo release docs
    for name in ("README_zenodo.md", "LICENSE", "CITATION.cff"):
        src = ZENODO / name
        if not src.exists():
            print(f"[fatal] missing required release doc: {name}")
            return 1
        final = "README.md" if name == "README_zenodo.md" else name
        shutil.copy2(src, staged / final)

    # 4. SHA-256 manifest of the entire bundle
    for p in sorted(staged.rglob("*")):
        if p.is_file():
            rel = p.relative_to(staged).as_posix()
            if rel.endswith("MANIFEST.sha256"):
                continue
            manifest.append({
                "path": rel,
                "size": p.stat().st_size,
                "sha256": sha256sum(p),
            })
    (staged / "MANIFEST.sha256").write_text(
        "\n".join(f"{m['sha256']}  {m['path']}" for m in manifest) + "\n"
    )

    # 5. Release summary
    summary = {
        "release": RELEASE_NAME,
        "version": VERSION,
        "file_count": len(manifest),
        "total_bytes": sum(m["size"] for m in manifest),
    }
    (staged / "RELEASE_INFO.json").write_text(json.dumps(summary, indent=2))
    print(f"\nStaged {len(manifest)} files "
          f"({summary['total_bytes']/1e6:.2f} MB) under {staged}")

    # 6. Build ZIP
    zip_path = DIST / f"{RELEASE_NAME}.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED,
                         compresslevel=6) as zf:
        for root, _, files in os.walk(staged):
            for f in files:
                abs_path = Path(root) / f
                arcname = abs_path.relative_to(staged.parent).as_posix()
                zf.write(abs_path, arcname)
    print(f"\nZIP: {zip_path}  ({zip_path.stat().st_size/1e6:.2f} MB)")
    print(f"SHA-256 of ZIP: {sha256sum(zip_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
