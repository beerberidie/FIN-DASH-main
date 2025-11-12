#!/usr/bin/env python3
"""
Seed FIN-DASH with real account data.

Usage:
    python backend/scripts/seed_real_data.py [--clear] [--dry-run] [--verbose]

Options:
    --clear     Clear existing data before seeding
    --dry-run   Show what would be created without creating
    --verbose   Show detailed output
"""

import argparse
import requests
import sys
from datetime import datetime
from typing import Dict, List, Any

API_BASE = "http://127.0.0.1:8777/api"


# Color codes for terminal output
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_success(msg: str):
    print(f"{Colors.GREEN}✓{Colors.ENDC} {msg}")


def print_error(msg: str):
    print(f"{Colors.RED}✗{Colors.ENDC} {msg}")


def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ{Colors.ENDC} {msg}")


def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠{Colors.ENDC} {msg}")


def check_api_status() -> bool:
    """Check if API is running."""
    try:
        response = requests.get(f"{API_BASE}/summary", timeout=5)
        return response.status_code in [200, 404]  # 404 is ok, means API is running
    except requests.exceptions.RequestException:
        return False


def create_accounts(dry_run: bool = False, verbose: bool = False) -> Dict[str, str]:
    """Create all accounts and return mapping of name to ID."""
    print_info("Creating accounts...")

    accounts = [
        {
            "name": "Easy Account",
            "type": "bank",
            "opening_balance": 181.0,
            "is_active": True,
        },
        {
            "name": "CreditCard",
            "type": "bank",
            "opening_balance": 0.0,  # Credit card account starts at 0
            "is_active": True,
        },
        {
            "name": "Ebucks",
            "type": "virtual",
            "opening_balance": 19731.0,  # eBucks points
            "is_active": True,
        },
        {
            "name": "Savings",
            "type": "bank",
            "opening_balance": 566.0,
            "is_active": True,
        },
        {
            "name": "Share Investor",
            "type": "investment",
            "opening_balance": 231.0,
            "is_active": True,
        },
    ]

    account_map = {}

    for account in accounts:
        if dry_run:
            print(
                f"  [DRY RUN] Would create account: {account['name']} ({account['type']}) - R{account['opening_balance']:.2f}"
            )
            account_map[account["name"]] = (
                f"acc_{account['name'].lower().replace(' ', '_')}"
            )
        else:
            try:
                response = requests.post(f"{API_BASE}/accounts", json=account)
                if response.status_code == 201:
                    data = response.json()
                    account_map[account["name"]] = data["id"]
                    if verbose:
                        print_success(
                            f"  Created account: {account['name']} (ID: {data['id']})"
                        )
                    else:
                        print_success(f"  Created account: {account['name']}")
                elif response.status_code == 400 and "already exists" in response.text:
                    print_warning(f"  Account already exists: {account['name']}")
                    # Try to get existing account ID
                    accounts_response = requests.get(f"{API_BASE}/accounts")
                    if accounts_response.status_code == 200:
                        existing_accounts = accounts_response.json()
                        for acc in existing_accounts:
                            if acc["name"] == account["name"]:
                                account_map[account["name"]] = acc["id"]
                                break
                else:
                    print_error(
                        f"  Failed to create account: {account['name']} - {response.text}"
                    )
            except Exception as e:
                print_error(f"  Error creating account {account['name']}: {str(e)}")

    return account_map


def create_categories(dry_run: bool = False, verbose: bool = False) -> Dict[str, str]:
    """Create all categories and return mapping of name to ID."""
    print_info("Creating categories...")

    # Define categories with their groups and colors
    categories = [
        # Expense categories
        {
            "name": "Food",
            "group": "needs",
            "color": "#ef4444",
            "icon": "UtensilsCrossed",
        },
        {"name": "Gifts", "group": "wants", "color": "#ec4899", "icon": "Gift"},
        {
            "name": "Health/Medical",
            "group": "needs",
            "color": "#10b981",
            "icon": "Heart",
        },
        {"name": "Home", "group": "needs", "color": "#8b5cf6", "icon": "Home"},
        {"name": "Transportation", "group": "needs", "color": "#f59e0b", "icon": "Car"},
        {"name": "Personal", "group": "wants", "color": "#06b6d4", "icon": "User"},
        {"name": "Pets", "group": "wants", "color": "#84cc16", "icon": "PawPrint"},
        {"name": "Utilities", "group": "needs", "color": "#6366f1", "icon": "Zap"},
        {"name": "Travel", "group": "wants", "color": "#14b8a6", "icon": "Plane"},
        {"name": "Debt", "group": "debt", "color": "#dc2626", "icon": "CreditCard"},
        {
            "name": "Other",
            "group": "wants",
            "color": "#64748b",
            "icon": "MoreHorizontal",
        },
        {"name": "Wifi", "group": "needs", "color": "#3b82f6", "icon": "Wifi"},
        {"name": "Gap Cover", "group": "needs", "color": "#059669", "icon": "Shield"},
        {
            "name": "YouTube Premium",
            "group": "wants",
            "color": "#dc2626",
            "icon": "Youtube",
        },
        {
            "name": "YouTube Music",
            "group": "wants",
            "color": "#f97316",
            "icon": "Music",
        },
        {"name": "Spotify", "group": "wants", "color": "#22c55e", "icon": "Music"},
        {"name": "Netflix", "group": "wants", "color": "#ef4444", "icon": "Tv"},
        {
            "name": "Bike Insurance",
            "group": "needs",
            "color": "#f59e0b",
            "icon": "Bike",
        },
        {
            "name": "Bank Charges",
            "group": "needs",
            "color": "#6366f1",
            "icon": "Building",
        },
        {
            "name": "Cell Phone",
            "group": "needs",
            "color": "#8b5cf6",
            "icon": "Smartphone",
        },
        {
            "name": "Liberty (Insurance)",
            "group": "needs",
            "color": "#0ea5e9",
            "icon": "Shield",
        },
        # Income categories
        {"name": "Paycheck", "group": "income", "color": "#10b981", "icon": "Wallet"},
        {
            "name": "Savings",
            "group": "savings",
            "color": "#3b82f6",
            "icon": "PiggyBank",
        },
        {"name": "Bonus", "group": "income", "color": "#22c55e", "icon": "TrendingUp"},
        {"name": "Interest", "group": "income", "color": "#06b6d4", "icon": "Percent"},
        {
            "name": "Other Income",
            "group": "income",
            "color": "#84cc16",
            "icon": "DollarSign",
        },
        {
            "name": "Custom Category",
            "group": "income",
            "color": "#64748b",
            "icon": "Circle",
        },
    ]

    category_map = {}

    for category in categories:
        if dry_run:
            print(
                f"  [DRY RUN] Would create category: {category['name']} ({category['group']})"
            )
            category_map[category["name"]] = (
                f"cat_{category['name'].lower().replace(' ', '_').replace('/', '_')}"
            )
        else:
            try:
                response = requests.post(f"{API_BASE}/categories", json=category)
                if response.status_code == 201:
                    data = response.json()
                    category_map[category["name"]] = data["id"]
                    if verbose:
                        print_success(
                            f"  Created category: {category['name']} (ID: {data['id']})"
                        )
                    else:
                        print_success(f"  Created category: {category['name']}")
                elif response.status_code == 400 and "already exists" in response.text:
                    print_warning(f"  Category already exists: {category['name']}")
                    # Try to get existing category ID
                    categories_response = requests.get(f"{API_BASE}/categories")
                    if categories_response.status_code == 200:
                        existing_categories = categories_response.json()
                        for cat in existing_categories:
                            if cat["name"] == category["name"]:
                                category_map[category["name"]] = cat["id"]
                                break
                else:
                    print_error(
                        f"  Failed to create category: {category['name']} - {response.text}"
                    )
            except Exception as e:
                print_error(f"  Error creating category {category['name']}: {str(e)}")

    return category_map


def create_credit_card(
    account_map: Dict[str, str], dry_run: bool = False, verbose: bool = False
) -> bool:
    """Create credit card linked to CreditCard account."""
    print_info("Creating credit card...")

    # Get CreditCard account ID
    creditcard_account_id = account_map.get("CreditCard")

    if not creditcard_account_id:
        print_error("  CreditCard account not found")
        return False

    card = {
        "name": "Standard Bank Credit Card",
        "card_type": "credit",
        "last_four_digits": "1234",
        "account_id": creditcard_account_id,
        "issuer": "Standard Bank",
        "available_balance": 6946.0,
        "current_balance": -1053.0,
        "credit_limit": 8000.0,
        "expiry_month": 12,
        "expiry_year": 2027,
        "is_active": True,
        "color": "#dc2626",
        "icon": "CreditCard",
    }

    if dry_run:
        print(f"  [DRY RUN] Would create card: {card['name']}")
        print(f"    Available: R{card['available_balance']:.2f}")
        print(f"    Current Balance: R{card['current_balance']:.2f}")
        print(f"    Credit Limit: R{card['credit_limit']:.2f}")
        return True
    else:
        try:
            response = requests.post(f"{API_BASE}/cards", json=card)
            if response.status_code == 201:
                data = response.json()
                if verbose:
                    print_success(f"  Created card: {card['name']} (ID: {data['id']})")
                    print(f"    Available: R{card['available_balance']:.2f}")
                    print(f"    Current Balance: R{card['current_balance']:.2f}")
                else:
                    print_success(f"  Created card: {card['name']}")
                return True
            elif response.status_code == 400 and "already exists" in response.text:
                print_warning(f"  Card already exists: {card['name']}")
                return True
            else:
                print_error(f"  Failed to create card: {response.text}")
                return False
        except Exception as e:
            print_error(f"  Error creating card: {str(e)}")
            return False


def create_budget(dry_run: bool = False, verbose: bool = False) -> bool:
    """Create budget for current month."""
    print_info("Creating budget for October 2025...")

    # Calculate totals
    needs_total = (
        2000.00
        + 2017.00
        + 2000.00
        + 2000.00
        + 500.00
        + 300.00
        + 138.00
        + 338.00
        + 150.00
        + 250.00
        + 700.00
    )  # 10,393
    wants_total = (
        0.00 + 3000.00 + 0.00 + 0.00 + 100.00 + 60.00 + 90.00 + 159.00
    )  # 3,409
    savings_total = 0.00

    budget = {
        "year": 2025,
        "month": 10,
        "needs_planned": needs_total,
        "wants_planned": wants_total,
        "savings_planned": savings_total,
        "notes": "Initial budget setup - October 2025",
    }

    if dry_run:
        print(f"  [DRY RUN] Would create budget:")
        print(f"    Needs: R{budget['needs_planned']:.2f}")
        print(f"    Wants: R{budget['wants_planned']:.2f}")
        print(f"    Savings: R{budget['savings_planned']:.2f}")
        print(
            f"    Total: R{budget['needs_planned'] + budget['wants_planned'] + budget['savings_planned']:.2f}"
        )
        return True
    else:
        try:
            response = requests.post(f"{API_BASE}/budgets", json=budget)
            if response.status_code == 201:
                if verbose:
                    print_success(f"  Created budget for October 2025")
                    print(f"    Needs: R{budget['needs_planned']:.2f}")
                    print(f"    Wants: R{budget['wants_planned']:.2f}")
                    print(f"    Savings: R{budget['savings_planned']:.2f}")
                else:
                    print_success(
                        f"  Created budget: R{budget['needs_planned'] + budget['wants_planned']:.2f} total"
                    )
                return True
            elif response.status_code == 400 and "already exists" in response.text:
                print_warning(f"  Budget already exists for October 2025")
                return True
            else:
                print_error(f"  Failed to create budget: {response.text}")
                return False
        except Exception as e:
            print_error(f"  Error creating budget: {str(e)}")
            return False


def verify_data(verbose: bool = False) -> bool:
    """Verify that all data was created correctly."""
    print_info("Verifying data...")

    try:
        # Check accounts
        accounts_response = requests.get(f"{API_BASE}/accounts")
        if accounts_response.status_code == 200:
            accounts = accounts_response.json()
            print_success(f"  Found {len(accounts)} accounts")
            if verbose:
                for acc in accounts:
                    print(f"    - {acc['name']}: R{acc['opening_balance']:.2f}")

        # Check categories
        categories_response = requests.get(f"{API_BASE}/categories")
        if categories_response.status_code == 200:
            categories = categories_response.json()
            print_success(f"  Found {len(categories)} categories")

        # Check budgets
        budgets_response = requests.get(f"{API_BASE}/budgets")
        if budgets_response.status_code == 200:
            budgets = budgets_response.json()
            print_success(f"  Found {len(budgets)} budget(s)")

        return True
    except Exception as e:
        print_error(f"  Verification failed: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Seed FIN-DASH with real account data")
    parser.add_argument(
        "--clear", action="store_true", help="Clear existing data before seeding"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created without creating",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    print(f"\n{Colors.BOLD}FIN-DASH Data Seeding Script{Colors.ENDC}\n")

    # Check API status
    print_info("Checking API status...")
    if not check_api_status():
        print_error("API is not running! Please start the backend server first.")
        print_info("Run: python start.py")
        sys.exit(1)
    print_success("API is running")

    if args.dry_run:
        print_warning("DRY RUN MODE - No data will be created\n")

    # Create data
    account_map = create_accounts(dry_run=args.dry_run, verbose=args.verbose)
    print()

    category_map = create_categories(dry_run=args.dry_run, verbose=args.verbose)
    print()

    create_credit_card(account_map, dry_run=args.dry_run, verbose=args.verbose)
    print()

    create_budget(dry_run=args.dry_run, verbose=args.verbose)
    print()

    # Verify data
    if not args.dry_run:
        verify_data(verbose=args.verbose)
        print()

    print(f"{Colors.GREEN}{Colors.BOLD}✓ Data seeding complete!{Colors.ENDC}\n")

    if not args.dry_run:
        print_info("Summary:")
        print(f"  - 5 accounts created")
        print(f"  - 1 credit card created")
        print(f"  - 27 categories created")
        print(f"  - 1 budget created (October 2025)")
        print(f"\n{Colors.BLUE}Next steps:{Colors.ENDC}")
        print(f"  1. Open FIN-DASH: http://localhost:8080")
        print(f"  2. View your accounts, cards, and budget")
        print(f"  3. Start adding transactions or import bank statements\n")


if __name__ == "__main__":
    main()
