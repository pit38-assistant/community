#!/usr/bin/env python3

# /// script
# requires-python = ">=3.12"
# dependencies = [
# ]
# ///

import argparse
import csv
import os
from datetime import datetime
from pathlib import Path
from typing import TextIO


BROKER = 'BUNQ'


def convert_bunq(infile: TextIO) -> list[dict]:
    """Convert bunq CSV to income row dicts."""
    reader = csv.DictReader(infile)
    rows = []

    for row in reader:
        description = row['Description'].strip()

        # Filter for interest payments only
        if 'bunq Payday' not in description:
            continue

        operation_datetime = datetime.strptime(row['Date'].strip(), '%Y-%m-%d')
        settlement_date = operation_datetime.date()

        # Parse amount (remove thousands separator)
        amount_str = row['Amount'].strip().replace(',', '')

        # Extract currency from description: "bunq Payday 2026-01-25 EUR"
        currency = description.split()[-1]

        symbol = f"{currency}-INT"
        rows.append({
            'broker': BROKER,
            'tx_id': f"{symbol}:{settlement_date.isoformat()}",
            'income_type': 'INTEREST',
            'symbol': symbol,
            'currency': currency,
            'gross_amount': amount_str,
            'wht_amount': '0',
            'operation_datetime': operation_datetime.isoformat(),
            'settlement_date': settlement_date.isoformat(),
        })

    return rows


def _write_csv(outfile: TextIO, rows: list[dict]) -> None:
    writer = csv.DictWriter(outfile, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=argparse.FileType('r'), help='Input bunq CSV file')
    parser.add_argument('--output', help='Output income CSV')

    args = parser.parse_args()

    income_rows = convert_bunq(args.input)
    args.input.close()

    if income_rows:
        stem = Path(args.input.name).stem
        suffix = os.urandom(3).hex()
        output_path = args.output or f'result_{stem}_{suffix}.csv'
        with open(output_path, 'w') as f:
            _write_csv(f, income_rows)
        print(f"Wrote {len(income_rows)} interest payment(s) → {output_path}")


if __name__ == '__main__':
    main()
