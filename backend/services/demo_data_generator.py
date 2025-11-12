"""Demo data generator for FIN-DASH.

Generates realistic sample financial data for demo mode including:
- Accounts (checking, savings, credit card, investment)
- Transactions (6 months of realistic spending patterns)
- Budgets (monthly budgets with 50/30/20 rule)
- Investments (sample portfolio with South African stocks)
- Recurring transactions (salary, bills, subscriptions)
- Categories (income and expense categories)
"""

import random
from datetime import datetime, timedelta, date
from typing import List, Dict, Any
from decimal import Decimal

from utils.ids import generate_transaction_id, generate_uuid


class DemoDataGenerator:
    """Generate realistic sample financial data for demo mode."""

    # South African banks
    SA_BANKS = ["FNB", "Capitec", "Standard Bank", "Nedbank", "Absa"]

    # South African stocks and ETFs
    SA_STOCKS = [
        {"symbol": "NPN", "name": "Naspers Ltd", "price": 3200.00, "type": "stock"},
        {
            "symbol": "SHP",
            "name": "Shoprite Holdings",
            "price": 180.00,
            "type": "stock",
        },
        {
            "symbol": "SBK",
            "name": "Standard Bank Group",
            "price": 145.00,
            "type": "stock",
        },
        {"symbol": "STX40", "name": "Satrix Top 40 ETF", "price": 85.00, "type": "etf"},
        {"symbol": "RES", "name": "Resilient REIT", "price": 12.00, "type": "stock"},
        {
            "symbol": "BTI",
            "name": "British American Tobacco",
            "price": 520.00,
            "type": "stock",
        },
        {"symbol": "AGL", "name": "Anglo American", "price": 380.00, "type": "stock"},
    ]

    # Transaction patterns (South African context)
    TRANSACTION_PATTERNS = {
        "income": [
            {
                "desc": "Salary - {company}",
                "amount_range": (35000, 55000),
                "frequency": "monthly",
                "day": 25,
            },
            {
                "desc": "Freelance - {client}",
                "amount_range": (3000, 15000),
                "frequency": "irregular",
            },
            {
                "desc": "Investment Dividend",
                "amount_range": (500, 2500),
                "frequency": "quarterly",
            },
        ],
        "recurring_expenses": [
            {
                "desc": "Rent - {landlord}",
                "amount_range": (8000, 15000),
                "frequency": "monthly",
                "day": 1,
                "category": "Housing",
            },
            {
                "desc": "Electricity - Eskom",
                "amount_range": (800, 1500),
                "frequency": "monthly",
                "day": 5,
                "category": "Utilities",
            },
            {
                "desc": "Water & Rates - Municipality",
                "amount_range": (400, 800),
                "frequency": "monthly",
                "day": 5,
                "category": "Utilities",
            },
            {
                "desc": "Internet - {isp}",
                "amount_range": (699, 999),
                "frequency": "monthly",
                "day": 10,
                "category": "Utilities",
            },
            {
                "desc": "Cell Phone - {provider}",
                "amount_range": (299, 799),
                "frequency": "monthly",
                "day": 10,
                "category": "Utilities",
            },
            {
                "desc": "Car Insurance - {insurer}",
                "amount_range": (1200, 2000),
                "frequency": "monthly",
                "day": 15,
                "category": "Insurance",
            },
            {
                "desc": "Medical Aid - {provider}",
                "amount_range": (2500, 4000),
                "frequency": "monthly",
                "day": 15,
                "category": "Healthcare",
            },
            {
                "desc": "Gym - Virgin Active",
                "amount_range": (550, 850),
                "frequency": "monthly",
                "day": 1,
                "category": "Health & Fitness",
            },
            {
                "desc": "Netflix Subscription",
                "amount_range": (99, 199),
                "frequency": "monthly",
                "day": 12,
                "category": "Entertainment",
            },
            {
                "desc": "Spotify Premium",
                "amount_range": (59, 119),
                "frequency": "monthly",
                "day": 15,
                "category": "Entertainment",
            },
            {
                "desc": "DSTV Subscription",
                "amount_range": (299, 899),
                "frequency": "monthly",
                "day": 1,
                "category": "Entertainment",
            },
        ],
        "variable_expenses": [
            {
                "desc": "Woolworths - Groceries",
                "amount_range": (300, 1200),
                "frequency": "weekly",
                "category": "Groceries",
            },
            {
                "desc": "Pick n Pay - Groceries",
                "amount_range": (400, 1500),
                "frequency": "weekly",
                "category": "Groceries",
            },
            {
                "desc": "Checkers - Groceries",
                "amount_range": (350, 1000),
                "frequency": "weekly",
                "category": "Groceries",
            },
            {
                "desc": "Uber - Transport",
                "amount_range": (50, 300),
                "frequency": "weekly",
                "category": "Transport",
            },
            {
                "desc": "Petrol - {station}",
                "amount_range": (400, 800),
                "frequency": "weekly",
                "category": "Transport",
            },
            {
                "desc": "{restaurant} - Dining",
                "amount_range": (150, 600),
                "frequency": "weekly",
                "category": "Dining Out",
            },
            {
                "desc": "Takealot - Online Shopping",
                "amount_range": (200, 2000),
                "frequency": "monthly",
                "category": "Shopping",
            },
            {
                "desc": "{store} - Clothing",
                "amount_range": (300, 1500),
                "frequency": "monthly",
                "category": "Shopping",
            },
            {
                "desc": "Clicks - Personal Care",
                "amount_range": (100, 500),
                "frequency": "monthly",
                "category": "Personal Care",
            },
            {
                "desc": "Dischem - Pharmacy",
                "amount_range": (150, 600),
                "frequency": "monthly",
                "category": "Healthcare",
            },
            {
                "desc": "Movie - {cinema}",
                "amount_range": (80, 250),
                "frequency": "monthly",
                "category": "Entertainment",
            },
            {
                "desc": "Coffee - {cafe}",
                "amount_range": (35, 80),
                "frequency": "weekly",
                "category": "Dining Out",
            },
        ],
    }

    # Placeholder names
    COMPANIES = ["ABC Corp", "XYZ Ltd", "Tech Solutions SA", "Digital Innovations"]
    CLIENTS = ["Client A", "Client B", "Startup Co", "Enterprise Inc"]
    LANDLORDS = ["Property Management Co", "Private Landlord"]
    ISPS = ["Vodacom Fibre", "Telkom", "Vumatel", "Openserve"]
    PROVIDERS = ["Vodacom", "MTN", "Cell C", "Telkom Mobile"]
    INSURERS = ["Discovery Insure", "OUTsurance", "Santam", "Hollard"]
    MEDICAL_AIDS = ["Discovery Health", "Bonitas", "Momentum Health", "Medshield"]
    PETROL_STATIONS = ["Shell", "Engen", "BP", "Sasol"]
    RESTAURANTS = ["Nando's", "Spur", "Ocean Basket", "Primi Piatti", "Col'Cacchio"]
    STORES = ["Woolworths", "Edgars", "Mr Price", "Zara", "H&M"]
    CINEMAS = ["Ster-Kinekor", "Nu Metro"]
    CAFES = ["Vida e Caffè", "Mugg & Bean", "Seattle Coffee Co"]

    def __init__(self):
        """Initialize demo data generator."""
        self.start_date = datetime.now() - timedelta(days=180)  # 6 months ago
        self.end_date = datetime.now()

    def _random_choice(self, items: List[str]) -> str:
        """Get random choice from list."""
        return random.choice(items)

    def _random_amount(self, min_val: float, max_val: float) -> float:
        """Generate random amount in range."""
        return round(random.uniform(min_val, max_val), 2)

    def _format_description(self, template: str) -> str:
        """Format description with random placeholders."""
        replacements = {
            "{company}": self._random_choice(self.COMPANIES),
            "{client}": self._random_choice(self.CLIENTS),
            "{landlord}": self._random_choice(self.LANDLORDS),
            "{isp}": self._random_choice(self.ISPS),
            "{provider}": self._random_choice(self.PROVIDERS),
            "{insurer}": self._random_choice(self.INSURERS),
            "{medical_aid}": self._random_choice(self.MEDICAL_AIDS),
            "{station}": self._random_choice(self.PETROL_STATIONS),
            "{restaurant}": self._random_choice(self.RESTAURANTS),
            "{store}": self._random_choice(self.STORES),
            "{cinema}": self._random_choice(self.CINEMAS),
            "{cafe}": self._random_choice(self.CAFES),
        }

        result = template
        for key, value in replacements.items():
            result = result.replace(key, value)
        return result

    def generate_categories(self) -> List[Dict[str, Any]]:
        """Generate default categories."""
        now = datetime.now().isoformat()

        categories = [
            # Income
            {
                "id": "cat_salary",
                "name": "Salary",
                "group": "income",
                "color": "#10b981",
                "icon": "Briefcase",
                "is_system": "true",
                "created_at": now,
            },
            {
                "id": "cat_freelance",
                "name": "Freelance",
                "group": "income",
                "color": "#059669",
                "icon": "Code",
                "is_system": "false",
                "created_at": now,
            },
            {
                "id": "cat_investment_income",
                "name": "Investment Income",
                "group": "income",
                "color": "#047857",
                "icon": "TrendingUp",
                "is_system": "false",
                "created_at": now,
            },
            # Needs
            {
                "id": "cat_housing",
                "name": "Housing",
                "group": "needs",
                "color": "#3b82f6",
                "icon": "Home",
                "is_system": "true",
                "created_at": now,
            },
            {
                "id": "cat_groceries",
                "name": "Groceries",
                "group": "needs",
                "color": "#2563eb",
                "icon": "ShoppingCart",
                "is_system": "true",
                "created_at": now,
            },
            {
                "id": "cat_utilities",
                "name": "Utilities",
                "group": "needs",
                "color": "#1d4ed8",
                "icon": "Zap",
                "is_system": "true",
                "created_at": now,
            },
            {
                "id": "cat_transport",
                "name": "Transport",
                "group": "needs",
                "color": "#1e40af",
                "icon": "Car",
                "is_system": "true",
                "created_at": now,
            },
            {
                "id": "cat_insurance",
                "name": "Insurance",
                "group": "needs",
                "color": "#1e3a8a",
                "icon": "Shield",
                "is_system": "true",
                "created_at": now,
            },
            {
                "id": "cat_healthcare",
                "name": "Healthcare",
                "group": "needs",
                "color": "#7c3aed",
                "icon": "Heart",
                "is_system": "true",
                "created_at": now,
            },
            # Wants
            {
                "id": "cat_dining",
                "name": "Dining Out",
                "group": "wants",
                "color": "#f59e0b",
                "icon": "Coffee",
                "is_system": "true",
                "created_at": now,
            },
            {
                "id": "cat_entertainment",
                "name": "Entertainment",
                "group": "wants",
                "color": "#d97706",
                "icon": "Film",
                "is_system": "true",
                "created_at": now,
            },
            {
                "id": "cat_shopping",
                "name": "Shopping",
                "group": "wants",
                "color": "#b45309",
                "icon": "ShoppingBag",
                "is_system": "true",
                "created_at": now,
            },
            {
                "id": "cat_fitness",
                "name": "Health & Fitness",
                "group": "wants",
                "color": "#92400e",
                "icon": "Activity",
                "is_system": "false",
                "created_at": now,
            },
            {
                "id": "cat_personal_care",
                "name": "Personal Care",
                "group": "wants",
                "color": "#ec4899",
                "icon": "Sparkles",
                "is_system": "false",
                "created_at": now,
            },
            # Savings
            {
                "id": "cat_savings",
                "name": "Savings",
                "group": "savings",
                "color": "#8b5cf6",
                "icon": "PiggyBank",
                "is_system": "true",
                "created_at": now,
            },
            {
                "id": "cat_investment",
                "name": "Investment",
                "group": "savings",
                "color": "#7c3aed",
                "icon": "TrendingUp",
                "is_system": "true",
                "created_at": now,
            },
        ]

        return categories

    def generate_accounts(self) -> List[Dict[str, Any]]:
        """Generate sample accounts."""
        now = datetime.now().isoformat()

        accounts = [
            {
                "id": "acc_checking",
                "name": f"{self._random_choice(self.SA_BANKS)} - Cheque Account",
                "type": "bank",
                "opening_balance": "25450.00",
                "is_active": "true",
                "created_at": now,
            },
            {
                "id": "acc_savings",
                "name": f"{self._random_choice(self.SA_BANKS)} - Savings Account",
                "type": "bank",
                "opening_balance": "87320.00",
                "is_active": "true",
                "created_at": now,
            },
            {
                "id": "acc_credit",
                "name": f"{self._random_choice(self.SA_BANKS)} - Credit Card",
                "type": "bank",
                "opening_balance": "-3240.00",
                "is_active": "true",
                "created_at": now,
            },
            {
                "id": "acc_investment",
                "name": "EasyEquities - Investment Account",
                "type": "investment",
                "opening_balance": "156890.00",
                "is_active": "true",
                "created_at": now,
            },
        ]

        return accounts

    def generate_transactions(
        self, accounts: List[Dict], categories: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Generate 6 months of realistic transactions."""
        transactions = []
        now_str = datetime.now().isoformat()

        # Create category lookup
        cat_lookup = {cat["name"]: cat["id"] for cat in categories}

        # Get account IDs
        checking_acc = "acc_checking"
        savings_acc = "acc_savings"
        credit_acc = "acc_credit"

        # Generate monthly salary (income)
        current_date = self.start_date
        while current_date <= self.end_date:
            # Salary on 25th of each month
            if current_date.day == 25:
                salary_amount = self._random_amount(40000, 50000)
                transactions.append(
                    {
                        "id": generate_transaction_id(),
                        "date": current_date.strftime("%Y-%m-%d"),
                        "description": self._format_description("Salary - {company}"),
                        "amount": str(salary_amount),
                        "category_id": cat_lookup.get("Salary", "cat_salary"),
                        "account_id": checking_acc,
                        "card_id": "",
                        "type": "income",
                        "currency": "ZAR",
                        "source": "demo",
                        "external_id": "",
                        "tags": "salary;income",
                        "created_at": now_str,
                        "updated_at": now_str,
                    }
                )

            current_date += timedelta(days=1)

        # Generate recurring monthly expenses
        for pattern in self.TRANSACTION_PATTERNS["recurring_expenses"]:
            current_date = self.start_date
            while current_date <= self.end_date:
                if current_date.day == pattern["day"]:
                    amount = -self._random_amount(*pattern["amount_range"])
                    cat_id = cat_lookup.get(pattern["category"], "")

                    # Use credit card for some expenses
                    account = credit_acc if random.random() < 0.3 else checking_acc

                    transactions.append(
                        {
                            "id": generate_transaction_id(),
                            "date": current_date.strftime("%Y-%m-%d"),
                            "description": self._format_description(pattern["desc"]),
                            "amount": str(amount),
                            "category_id": cat_id,
                            "account_id": account,
                            "card_id": "",
                            "type": "expense",
                            "currency": "ZAR",
                            "source": "demo",
                            "external_id": "",
                            "tags": "recurring",
                            "created_at": now_str,
                            "updated_at": now_str,
                        }
                    )

                current_date += timedelta(days=1)

        # Generate variable expenses (weekly/monthly)
        for pattern in self.TRANSACTION_PATTERNS["variable_expenses"]:
            if pattern["frequency"] == "weekly":
                # Generate 1-3 transactions per week
                current_date = self.start_date
                while current_date <= self.end_date:
                    if random.random() < 0.4:  # 40% chance per day
                        amount = -self._random_amount(*pattern["amount_range"])
                        cat_id = cat_lookup.get(pattern["category"], "")

                        # Use credit card for some expenses
                        account = credit_acc if random.random() < 0.4 else checking_acc

                        transactions.append(
                            {
                                "id": generate_transaction_id(),
                                "date": current_date.strftime("%Y-%m-%d"),
                                "description": self._format_description(
                                    pattern["desc"]
                                ),
                                "amount": str(amount),
                                "category_id": cat_id,
                                "account_id": account,
                                "card_id": "",
                                "type": "expense",
                                "currency": "ZAR",
                                "source": "demo",
                                "external_id": "",
                                "tags": "",
                                "created_at": now_str,
                                "updated_at": now_str,
                            }
                        )

                    current_date += timedelta(days=1)

            elif pattern["frequency"] == "monthly":
                # Generate 1-2 transactions per month
                current_date = self.start_date
                month_tracker = set()

                while current_date <= self.end_date:
                    month_key = (current_date.year, current_date.month)
                    if month_key not in month_tracker and random.random() < 0.05:
                        amount = -self._random_amount(*pattern["amount_range"])
                        cat_id = cat_lookup.get(pattern["category"], "")

                        # Use credit card for shopping
                        account = (
                            credit_acc
                            if "Shopping" in pattern["category"]
                            else checking_acc
                        )

                        transactions.append(
                            {
                                "id": generate_transaction_id(),
                                "date": current_date.strftime("%Y-%m-%d"),
                                "description": self._format_description(
                                    pattern["desc"]
                                ),
                                "amount": str(amount),
                                "category_id": cat_id,
                                "account_id": account,
                                "card_id": "",
                                "type": "expense",
                                "currency": "ZAR",
                                "source": "demo",
                                "external_id": "",
                                "tags": "",
                                "created_at": now_str,
                                "updated_at": now_str,
                            }
                        )
                        month_tracker.add(month_key)

                    current_date += timedelta(days=1)

        # Generate occasional freelance income
        for _ in range(random.randint(3, 8)):
            random_date = self.start_date + timedelta(days=random.randint(0, 180))
            amount = self._random_amount(3000, 15000)

            transactions.append(
                {
                    "id": generate_transaction_id(),
                    "date": random_date.strftime("%Y-%m-%d"),
                    "description": self._format_description("Freelance - {client}"),
                    "amount": str(amount),
                    "category_id": cat_lookup.get("Freelance", "cat_freelance"),
                    "account_id": checking_acc,
                    "card_id": "",
                    "type": "income",
                    "currency": "ZAR",
                    "source": "demo",
                    "external_id": "",
                    "tags": "freelance;income",
                    "created_at": now_str,
                    "updated_at": now_str,
                }
            )

        # Generate monthly savings transfers
        current_date = self.start_date
        while current_date <= self.end_date:
            if current_date.day == 26:  # Day after salary
                amount = self._random_amount(5000, 10000)

                # Expense from checking
                transactions.append(
                    {
                        "id": generate_transaction_id(),
                        "date": current_date.strftime("%Y-%m-%d"),
                        "description": "Transfer to Savings",
                        "amount": str(-amount),
                        "category_id": cat_lookup.get("Savings", "cat_savings"),
                        "account_id": checking_acc,
                        "card_id": "",
                        "type": "expense",
                        "currency": "ZAR",
                        "source": "demo",
                        "external_id": "",
                        "tags": "savings;transfer",
                        "created_at": now_str,
                        "updated_at": now_str,
                    }
                )

                # Income to savings
                transactions.append(
                    {
                        "id": generate_transaction_id(),
                        "date": current_date.strftime("%Y-%m-%d"),
                        "description": "Transfer from Checking",
                        "amount": str(amount),
                        "category_id": cat_lookup.get("Savings", "cat_savings"),
                        "account_id": savings_acc,
                        "card_id": "",
                        "type": "income",
                        "currency": "ZAR",
                        "source": "demo",
                        "external_id": "",
                        "tags": "savings;transfer",
                        "created_at": now_str,
                        "updated_at": now_str,
                    }
                )

            current_date += timedelta(days=1)

        # Sort by date
        transactions.sort(key=lambda x: x["date"])

        return transactions

    def generate_budgets(self) -> List[Dict[str, Any]]:
        """Generate monthly budgets for the last 6 months."""
        budgets = []
        now_str = datetime.now().isoformat()

        # Generate budgets for each month in the range
        current_date = self.start_date
        while current_date <= self.end_date:
            # One budget per month
            if current_date.day == 1:
                # 50/30/20 rule on ~R45,000 income
                total_income = 45000

                budgets.append(
                    {
                        "id": generate_uuid(),
                        "year": str(current_date.year),
                        "month": str(current_date.month),
                        "needs_planned": str(total_income * 0.50),  # R22,500
                        "wants_planned": str(total_income * 0.30),  # R13,500
                        "savings_planned": str(total_income * 0.20),  # R9,000
                        "notes": "Demo budget following 50/30/20 rule",
                        "created_at": now_str,
                        "updated_at": now_str,
                    }
                )

            current_date += timedelta(days=1)

        return budgets

    def generate_investments(self) -> List[Dict[str, Any]]:
        """Generate sample investment portfolio."""
        investments = []
        now_str = datetime.now().isoformat()
        today = datetime.now().strftime("%Y-%m-%d")

        # Select 5 random stocks from SA_STOCKS
        selected_stocks = random.sample(self.SA_STOCKS, min(5, len(self.SA_STOCKS)))

        for stock in selected_stocks:
            # Random quantity
            if stock["type"] == "etf":
                quantity = random.randint(100, 300)
            else:
                quantity = random.randint(5, 100)

            # Average cost slightly different from current price
            price_variance = random.uniform(0.85, 1.05)
            avg_cost = round(stock["price"] * price_variance, 2)

            investments.append(
                {
                    "id": generate_uuid(),
                    "symbol": stock["symbol"],
                    "name": stock["name"],
                    "type": stock["type"],
                    "currency": "ZAR",
                    "quantity": str(quantity),
                    "average_cost": str(avg_cost),
                    "current_price": str(stock["price"]),
                    "last_updated": today,
                    "notes": "Demo investment",
                    "created_at": now_str,
                    "updated_at": now_str,
                }
            )

        return investments

    def generate_recurring_transactions(
        self, accounts: List[Dict], categories: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Generate recurring transaction templates."""
        recurring = []
        now_str = datetime.now().isoformat()

        # Create category lookup
        cat_lookup = {cat["name"]: cat["id"] for cat in categories}

        # Get account IDs
        checking_acc = "acc_checking"
        savings_acc = "acc_savings"

        # Salary
        recurring.append(
            {
                "id": generate_uuid(),
                "name": self._format_description("Monthly Salary - {company}"),
                "amount": str(45000.00),
                "category_id": cat_lookup.get("Salary", "cat_salary"),
                "account_id": checking_acc,
                "type": "income",
                "frequency": "monthly",
                "start_date": self.start_date.strftime("%Y-%m-%d"),
                "end_date": "",
                "day_of_month": "25",
                "day_of_week": "",
                "is_active": "true",
                "last_generated": "",
                "next_due": "",
                "tags": "salary",
                "notes": "Monthly salary payment",
                "created_at": now_str,
                "updated_at": now_str,
            }
        )

        # Rent
        recurring.append(
            {
                "id": generate_uuid(),
                "name": self._format_description("Rent - {landlord}"),
                "amount": str(-12000.00),
                "category_id": cat_lookup.get("Housing", "cat_housing"),
                "account_id": checking_acc,
                "type": "expense",
                "frequency": "monthly",
                "start_date": self.start_date.strftime("%Y-%m-%d"),
                "end_date": "",
                "day_of_month": "1",
                "day_of_week": "",
                "is_active": "true",
                "last_generated": "",
                "next_due": "",
                "tags": "rent;housing",
                "notes": "Monthly rent payment",
                "created_at": now_str,
                "updated_at": now_str,
            }
        )

        # Utilities
        recurring.append(
            {
                "id": generate_uuid(),
                "name": "Electricity - Eskom",
                "amount": str(-1200.00),
                "category_id": cat_lookup.get("Utilities", "cat_utilities"),
                "account_id": checking_acc,
                "type": "expense",
                "frequency": "monthly",
                "start_date": self.start_date.strftime("%Y-%m-%d"),
                "end_date": "",
                "day_of_month": "5",
                "day_of_week": "",
                "is_active": "true",
                "last_generated": "",
                "next_due": "",
                "tags": "utilities",
                "notes": "Monthly electricity bill",
                "created_at": now_str,
                "updated_at": now_str,
            }
        )

        # Internet
        recurring.append(
            {
                "id": generate_uuid(),
                "name": self._format_description("Internet - {isp}"),
                "amount": str(-899.00),
                "category_id": cat_lookup.get("Utilities", "cat_utilities"),
                "account_id": checking_acc,
                "type": "expense",
                "frequency": "monthly",
                "start_date": self.start_date.strftime("%Y-%m-%d"),
                "end_date": "",
                "day_of_month": "10",
                "day_of_week": "",
                "is_active": "true",
                "last_generated": "",
                "next_due": "",
                "tags": "utilities;internet",
                "notes": "Monthly internet subscription",
                "created_at": now_str,
                "updated_at": now_str,
            }
        )

        # Gym
        recurring.append(
            {
                "id": generate_uuid(),
                "name": "Gym Membership - Virgin Active",
                "amount": str(-650.00),
                "category_id": cat_lookup.get("Health & Fitness", "cat_fitness"),
                "account_id": checking_acc,
                "type": "expense",
                "frequency": "monthly",
                "start_date": self.start_date.strftime("%Y-%m-%d"),
                "end_date": "",
                "day_of_month": "1",
                "day_of_week": "",
                "is_active": "true",
                "last_generated": "",
                "next_due": "",
                "tags": "fitness;health",
                "notes": "Monthly gym membership",
                "created_at": now_str,
                "updated_at": now_str,
            }
        )

        # Savings transfer
        recurring.append(
            {
                "id": generate_uuid(),
                "name": "Savings Transfer",
                "amount": str(-8000.00),
                "category_id": cat_lookup.get("Savings", "cat_savings"),
                "account_id": checking_acc,
                "type": "expense",
                "frequency": "monthly",
                "start_date": self.start_date.strftime("%Y-%m-%d"),
                "end_date": "",
                "day_of_month": "26",
                "day_of_week": "",
                "is_active": "true",
                "last_generated": "",
                "next_due": "",
                "tags": "savings",
                "notes": "Monthly savings transfer",
                "created_at": now_str,
                "updated_at": now_str,
            }
        )

        return recurring

    def generate_complete_dataset(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generate complete demo dataset with all data types."""
        print("Generating demo data...")

        # Generate in order (dependencies)
        categories = self.generate_categories()
        print(f"✓ Generated {len(categories)} categories")

        accounts = self.generate_accounts()
        print(f"✓ Generated {len(accounts)} accounts")

        transactions = self.generate_transactions(accounts, categories)
        print(f"✓ Generated {len(transactions)} transactions")

        budgets = self.generate_budgets()
        print(f"✓ Generated {len(budgets)} budgets")

        investments = self.generate_investments()
        print(f"✓ Generated {len(investments)} investments")

        recurring = self.generate_recurring_transactions(accounts, categories)
        print(f"✓ Generated {len(recurring)} recurring transactions")

        return {
            "categories": categories,
            "accounts": accounts,
            "transactions": transactions,
            "budgets": budgets,
            "investments": investments,
            "recurring_transactions": recurring,
        }


# Singleton instance
demo_generator = DemoDataGenerator()
