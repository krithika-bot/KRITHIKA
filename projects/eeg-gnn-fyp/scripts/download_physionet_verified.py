"""Download the EEGMMIDB motor-imagery EDFs and verify them with MNE's SHA-256 registry.

Example:
    python scripts/download_physionet_verified.py \
        --manifest results/full_cohort/provenance/edf_manifest.csv

The EDF recordings remain in the ignored local data directory; only the manifest is shareable.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from importlib.resources import files
from pathlib import Path

import requests

S3_BASE = "https://physionet-open.s3.amazonaws.com/eegmmidb/1.0.0"
EXCLUDED_SUBJECTS = {88, 89, 92, 100, 104}
RUNS = (4, 8, 12)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_registry() -> dict[str, str]:
    registry = files("mne").joinpath("data", "eegbci_checksums.txt")
    entries = {}
    for line in registry.read_text().splitlines():
        fields = line.split()
        if len(fields) == 2:
            entries[fields[0]] = fields[1]
    return entries


def fetch_one(subject: int, run: int, raw_root: Path, registry: dict[str, str]) -> dict:
    relative = f"S{subject:03d}/S{subject:03d}R{run:02d}.edf"
    expected = registry.get(relative)
    if expected is None:
        raise ValueError(f"No MNE checksum entry for {relative}")

    destination = raw_root / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and sha256_file(destination) == expected:
        pass
    else:
        temporary = destination.with_suffix(".edf.part")
        url = f"{S3_BASE}/{relative}"
        try:
            with requests.get(url, stream=True, timeout=(20, 120)) as response:
                response.raise_for_status()
                with temporary.open("wb") as f:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)
            actual = sha256_file(temporary)
            if actual != expected:
                raise ValueError(f"Checksum mismatch for {relative}: expected {expected}, got {actual}")
            temporary.replace(destination)
        finally:
            temporary.unlink(missing_ok=True)

    actual = sha256_file(destination)
    return {
        "participant_id": subject,
        "run": run,
        "file": relative,
        "source_url": f"{S3_BASE}/{relative}",
        "bytes": destination.stat().st_size,
        "sha256": actual,
        "mne_registry_match": actual == expected,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-root", default="data/raw/MNE-eegbci-data/files/eegmmidb/1.0.0")
    parser.add_argument("--manifest", default="results/full_cohort/provenance/edf_manifest.csv")
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("--workers must be at least 1")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    raw_root = Path(args.raw_root)
    manifest = Path(args.manifest)
    registry = load_registry()
    jobs = [(s, r) for s in range(1, 110) if s not in EXCLUDED_SUBJECTS for r in RUNS]
    records = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(fetch_one, s, r, raw_root, registry): (s, r) for s, r in jobs}
        for index, future in enumerate(as_completed(futures), start=1):
            subject, run = futures[future]
            record = future.result()
            records.append(record)
            logging.info("verified %d/%d: S%03d run %02d", index, len(jobs), subject, run)

    records.sort(key=lambda row: (row["participant_id"], row["run"]))
    manifest.parent.mkdir(parents=True, exist_ok=True)
    with manifest.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    logging.info("Wrote %d verified file records to %s", len(records), manifest)


if __name__ == "__main__":
    main()
