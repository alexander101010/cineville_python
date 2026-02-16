import csv
from collections.abc import Iterable
from typing import TextIO

# fn expects an opened text file object (thus arguments of TextIO) and yields dicts with string keys and values, normalizing missing columns to empty strings
def read_csv_dicts(file: TextIO) -> Iterable[dict[str, str]]:
    reader = csv.DictReader(file)
    for row in reader:
        # Normalize None to empty string for missing columns
        yield {key: (value or "") for key, value in row.items()}


def write_output_csv(file: TextIO, rows: Iterable[tuple[str, str, str]]) -> None:
    # The assignment expects the visits list to appear without CSV quoting.
    for member_id, barcode, visits in rows:
        file.write(f"{member_id},{barcode},{visits}\n")
