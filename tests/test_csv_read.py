#!/usr/bin/env python3
"""Test CSV reading."""
import sys
import os

# Change to backend directory so relative paths work
os.chdir('backend')
sys.path.insert(0, os.getcwd())

from services.csv_manager import csv_manager

accounts = csv_manager.read_csv("accounts.csv")
print(f"Found {len(accounts)} accounts:")
for acc in accounts:
    print(f"  - {acc.get('id')}: {acc.get('name')}")

