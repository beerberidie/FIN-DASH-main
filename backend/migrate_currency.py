"""Migration script to add currency field to existing transactions."""

import csv
from pathlib import Path


def migrate_transactions():
    """Add currency column to transactions.csv with default value 'ZAR'."""
    data_dir = Path(__file__).parent.parent / "data"
    transactions_file = data_dir / "transactions.csv"

    if not transactions_file.exists():
        print("No transactions.csv file found. Skipping migration.")
        return

    # Read existing transactions
    with open(transactions_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        transactions = list(reader)

    # Check if currency field already exists
    if "currency" in fieldnames:
        print("Currency field already exists in transactions.csv. No migration needed.")
        return

    # Add currency field after 'type'
    new_fieldnames = []
    for field in fieldnames:
        new_fieldnames.append(field)
        if field == "type":
            new_fieldnames.append("currency")

    # Add currency='ZAR' to all existing transactions
    for tx in transactions:
        tx["currency"] = "ZAR"

    # Write back to file
    with open(transactions_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(transactions)

    print(
        f"✓ Successfully migrated {len(transactions)} transactions to include currency field (default: ZAR)"
    )


if __name__ == "__main__":
    migrate_transactions()
