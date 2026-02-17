#!/usr/bin/env python3
import argparse
import csv
import sys
from datetime import datetime
from typing import TextIO


BROKER = 'BUNQ'


def convert_bunq(infile: TextIO, outfile: TextIO) -> int:
    """Convert bunq CSV to manual income CSV format.

    Returns:
        Number of rows converted.
    """
    rows_converted = 0
    reader = csv.DictReader(infile)

    # Prepare output rows
    output_rows = []

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
        output_row = {
            'broker': BROKER,
            'tx_id': f"{symbol}:{settlement_date.isoformat()}",
            'income_type': 'INTEREST',
            'symbol': symbol,
            'currency': currency,
            'gross_amount': amount_str,
            'wht_amount': '0',
            'operation_datetime': operation_datetime.isoformat(),
            'settlement_date': settlement_date.isoformat(),
        }

        output_rows.append(output_row)
        rows_converted += 1

    if output_rows:
        fieldnames = list(output_rows[0].keys())
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    return rows_converted


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=argparse.FileType('r'), help='Input bunq CSV file')
    parser.add_argument('output', type=argparse.FileType('w'), help='Output')

    args = parser.parse_args()

    try:
        count = convert_bunq(args.input, args.output)
        print(f"✓ Converted {count} interest payment(s)")
        print(f"✓ Output written to: {args.output.name}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        args.input.close()
        args.output.close()


if __name__ == '__main__':
    main()
