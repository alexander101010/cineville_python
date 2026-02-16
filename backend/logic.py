"""
Cineville Technical Assignment

Reads:
- members.csv  (member_id,barcode)
- visits.csv   (visit_id,barcode,reservation_id)

Outputs:
- output.csv with rows: member_id,barcode,[visit_id1, visit_id2, ...]
- summary.json for serving to frontend

Also prints:
- Top 5 members by number of visits (member_id, amount_of_visits)
- Total number of walk-ins (visits without reservation_id)

Run:
  python3 backend/processor.py
  -OR-
  python3 backend/processor.py --members members.csv --visits visits.csv --output output.csv
"""

from __future__ import annotations

import csv
import json
import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ----------------------------------------------------------------------------------------
# Data models
# ----------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Visit:
    visit_id: str
    barcode: str
    reservation_id: Optional[str]


# ----------------------------------------------------------------------------------------
# Core functions
# ----------------------------------------------------------------------------------------
def load_members(file_path: str | Path) -> Dict[str, str]:
    """
    Load members.csv into a mapping: barcode -> member_id
    We do ensure barcodes are unique and non-empty, but more critical validation is done for visits.
    """
    path = Path(file_path)
    barcode_to_member: Dict[str, str] = {}

    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # For each row, we check that member_id and barcode are present, non-empty and unique.
        for line_no, row in enumerate(reader, start=2):  # header is line 1
            member_id = (row.get("member_id") or "").strip()
            barcode = (row.get("barcode") or "").strip()

            if not member_id or not barcode:
                logging.warning(
                    "Invalid member row (missing member_id or barcode). file=%s line=%d row=%r",
                    path.name, line_no, row
                )
                continue

            if barcode in barcode_to_member:
                logging.warning(
                    "Duplicate barcode in members.csv ignored. file=%s line=%d barcode=%s existing_member=%s new_member=%s",
                    path.name, line_no, barcode, barcode_to_member[barcode], member_id
                )
                continue

            
            barcode_to_member[barcode] = member_id

    return barcode_to_member


def load_visits(file_path: str | Path) -> List[Visit]:
    """
    Load visits.csv into a list[Visit].

    We do not fully validate here (that happens in validate_and_group_visits),
    but we normalize whitespace and treat empty reservation_id as None.
    """
    path = Path(file_path)
    visits: List[Visit] = []

    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for line_no, row in enumerate(reader, start=2): # header is line 1 again
            visit_id = (row.get("visit_id") or "").strip()
            barcode = (row.get("barcode") or "").strip()
            reservation_id = ((row.get("reservation_id") or "").strip()) or None

            if not visit_id:
                logging.warning(
                    "Invalid visit row (missing visit_id). file=%s line=%d row=%r",
                    path.name, line_no, row
                )
                continue

            visits.append(Visit(visit_id=visit_id, barcode=barcode, reservation_id=reservation_id))

    return visits


def validate_and_group_visits(
    members: Dict[str, str],
    visits: List[Visit],
) -> Tuple[Dict[Tuple[str, str], List[str]], int]:
    """
    Apply validation rules:
      - A visit must have a barcode
      - A visit must reference a known barcode

    Invalid data is logged and excluded.

    Returns:
      grouped_data: dict[(member_id, barcode)] -> [visit_id, ...]
      walk_in_count: number of valid visits where reservation_id is missing
    """
    grouped: Dict[Tuple[str, str], List[str]] = defaultdict(list)
    walk_in_count = 0

    for v in visits:
        if not v.barcode:
            logging.warning(
                "Invalid visit (missing barcode) excluded. visit_id=%s",
                v.visit_id
            )
            continue

        member_id = members.get(v.barcode)
        if not member_id:
            logging.warning(
                "Invalid visit (unknown barcode) excluded. visit_id=%s barcode=%s",
                v.visit_id, v.barcode
            )
            continue

        grouped[(member_id, v.barcode)].append(v.visit_id)

        if v.reservation_id is None:
            walk_in_count += 1

    return dict(grouped), walk_in_count


def write_output(file_path: str | Path, grouped_data: Dict[Tuple[str, str], List[str]]) -> None:
    """
    Write output CSV with format:
      member_id,barcode,[visit_id1, visit_id2, ...]
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as f:
        f.write("member_id,barcode,visits\n")

        # Stable ordering for debugging and tests
        for member_id, barcode in sorted(grouped_data):
            visit_ids = grouped_data[(member_id, barcode)]
            visits_repr = "[" + ", ".join(visit_ids) + "]"
            f.write(f"{member_id},{barcode},{visits_repr}\n")


def print_top_members(grouped_data: Dict[Tuple[str, str], List[str]], top_n: int = 5) -> None:
    """
    Bonus: Print top N members by number of visits. Top 5 are asked for, but make it configurable.
    Each line: member_id, amount_of_visits
    """
    visits_per_member: Dict[str, int] = defaultdict(int)

    print("--------------------------------------------")
    print(f"Top {top_n} members by visits:")

    for (member_id, _barcode), visit_ids in grouped_data.items():
        visits_per_member[member_id] += len(visit_ids)

    ranking = sorted(
        visits_per_member.items(),
        key=lambda item: (-item[1], item[0])  # desc by count, then member_id
    )[:top_n]

    for member_id, count in ranking:
        print(f"{member_id}, {count}")
    print("--------------------------------------------")


def print_total_walk_ins(walk_in_count: int) -> None:
    """
    Bonus: Print total number of walk-ins (valid visits with no reservation).
    """
    print("--------------------------------------------")
    print(f"Total walk-ins: {walk_in_count}")
    print("--------------------------------------------")



def build_summary(
    *,
    grouped_data: Dict[Tuple[str, str], List[str]],
    walk_in_count: int,
    top_n: int = 5,
) -> Dict[str, object]:
    visits_per_member: Dict[str, int] = defaultdict(int)
    total_valid_visits = 0

    for (member_id, _barcode), visit_ids in grouped_data.items():
        count = len(visit_ids)
        visits_per_member[member_id] += count
        total_valid_visits += count

    top_members = sorted(
        visits_per_member.items(),
        key=lambda item: (-item[1], item[0]),
    )[:top_n]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_valid_visits": total_valid_visits,
        "total_walk_ins": walk_in_count,
        "top_members": [
            {"member_id": member_id, "visit_count": count}
            for member_id, count in top_members
        ],
    }


def write_summary(file_path: str | Path, summary: Dict[str, object]) -> None:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
