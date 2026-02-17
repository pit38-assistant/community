#!/usr/bin/env python3
import argparse
import csv
from datetime import datetime
from decimal import Decimal
from typing import TextIO


BROKER = 'T212'


def convert_trading212(infile: TextIO, trades_file: TextIO, income_file: TextIO) -> tuple[int, int]:
    """Convert Trading 212 CSV to manual trade and income CSV formats.

    Returns:
        Tuple of (trades_converted, income_converted).
    """
    trades_converted = 0
    income_converted = 0

    trade_rows = []
    income_rows = []

    reader = csv.DictReader(infile)

    for row in reader:
        action = row['Action'].strip()

        if action in ('Market buy', 'Market sell'):
            trade_row = _convert_trade_row(row)
            trade_rows.append(trade_row)
            trades_converted += 1

        elif action == 'Interest on cash':
            income_row = _convert_interest_row(row)
            income_rows.append(income_row)
            income_converted += 1

        elif action.startswith('Dividend'):
            income_row = _convert_dividend_row(row)
            income_rows.append(income_row)
            income_converted += 1

    if trade_rows:
        _write_trades_csv(trades_file, trade_rows)

    if income_rows:
        _write_income_csv(income_file, income_rows)

    return trades_converted, income_converted


def _convert_trade_row(row: dict) -> dict:
    action = row['Action'].strip()
    direction = 'BUY' if action == 'Market buy' else 'SELL'

    isin = row['ISIN'].strip()
    symbol = row['Ticker'].strip()
    tx_id = row['ID'].strip()

    operation_datetime = _parse_datetime(row['Time'].strip())
    settlement_date = operation_datetime.date()

    quantity = row['No. of shares'].strip()
    price_original = Decimal(row['Price / share'].strip())
    total = Decimal(row['Total'].strip())
    settlement_currency = row['Currency (Total)'].strip()
    exchange_rate = Decimal(row['Exchange rate'].strip())
    price = price_original / exchange_rate

    # FX conversion fee
    commission_str = row.get('Currency conversion fee', '').strip()
    commission = commission_str if commission_str else '0'

    # Calculate amount (gross before commission)
    total_dec = Decimal(total)
    commission_dec = Decimal(commission)
    if direction == 'SELL':
        amount = total_dec + commission_dec
    else:
        amount = total_dec - commission_dec

    country = isin[:2] if len(isin) >= 2 else ''

    return {
        'broker': BROKER,
        'tx_id': tx_id,
        'direction': direction,
        'symbol': symbol,
        'isin': isin,
        'country': country,
        'currency': settlement_currency,
        'price': str(price),
        'quantity': quantity,
        'amount': str(amount),
        'commission': commission,
        'operation_datetime': operation_datetime.isoformat(),
        'settlement_date': settlement_date.isoformat(),
    }


def _convert_interest_row(row: dict) -> dict:
    operation_datetime = _parse_datetime(row['Time'].strip())
    settlement_date = operation_datetime.date()
    gross_amount = row['Total'].strip()
    currency = row['Currency (Total)'].strip()
    tx_id = row['ID'].strip()

    return {
        'broker': BROKER,
        'tx_id': tx_id,
        'income_type': 'INTEREST',
        'symbol': f"{currency}-INT",
        'currency': currency,
        'gross_amount': gross_amount,
        'wht_amount': '0',
        'operation_datetime': operation_datetime.isoformat(),
        'settlement_date': settlement_date.isoformat(),
    }


def _convert_dividend_row(row: dict) -> dict:
    operation_datetime = _parse_datetime(row['Time'].strip())
    settlement_date = operation_datetime.date()
    symbol = row['Ticker'].strip()
    tx_id = row['ID'].strip()

    gross_amount = row['Total'].strip()
    settlement_currency = row['Currency (Total)'].strip()

    # Withholding tax conversion
    wht_str = row.get('Withholding tax', '').strip()
    wht_currency_str = row.get('Currency (Withholding tax)', '').strip()
    exchange_rate_str = row['Exchange rate'].strip()

    if wht_str:
        wht_original = Decimal(wht_str)
        exchange_rate = Decimal(exchange_rate_str)
        # Convert WHT to settlement currency if different
        if wht_currency_str and wht_currency_str != settlement_currency:
            wht_amount = wht_original * exchange_rate
        else:
            wht_amount = wht_original
    else:
        wht_amount = Decimal('0')

    return {
        'broker': BROKER,
        'tx_id': tx_id,
        'income_type': 'DIVIDEND',
        'symbol': symbol,
        'currency': settlement_currency,
        'gross_amount': gross_amount,
        'wht_amount': str(wht_amount),
        'operation_datetime': operation_datetime.isoformat(),
        'settlement_date': settlement_date.isoformat(),
    }


def _parse_datetime(datetime_str: str) -> datetime:
    """Parse Trading 212 datetime: 2025-07-22 10:06:57 or 2025-07-22 10:06:57.358"""
    try:
        return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')


def _write_trades_csv(outfile: TextIO, rows: list[dict]) -> None:
    fieldnames = list(rows[0].keys())
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def _write_income_csv(outfile: TextIO, rows: list[dict]) -> None:
    fieldnames = list(rows[0].keys())
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=argparse.FileType('r'), help='Input Trading 212 CSV file')
    parser.add_argument('trades_output', type=argparse.FileType('w'), help='Output trades')
    parser.add_argument('income_output', type=argparse.FileType('w'), help='Output income')

    args = parser.parse_args()

    trades_count, income_count = convert_trading212(
        args.input, args.trades_output, args.income_output
    )

    if args.trades_output:
        print(f"✓ Converted {trades_count} trade(s)")
        print(f"✓ Trades written to: {args.trades_output.name}")

    if args.income_output:
        print(f"✓ Converted {income_count} income record(s)")
        print(f"✓ Income written to: {args.income_output.name}")


if __name__ == '__main__':
    main()
