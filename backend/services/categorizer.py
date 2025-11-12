"""Auto-categorization service for transactions."""

import re
from typing import Dict, List, Tuple, Optional
from services.csv_manager import csv_manager


class Categorizer:
    """Service for auto-categorizing transactions based on merchant patterns."""

    # South African merchant patterns mapped to categories
    MERCHANT_PATTERNS = {
        # Groceries (Needs)
        "cat_needs_groceries": [
            r"pick\s*n\s*pay",
            r"pnp\s",
            r"woolworths",
            r"woolies",
            r"checkers",
            r"shoprite",
            r"spar",
            r"boxer",
            r"usave",
            r"food\s*lover",
            r"makro",
            r"game\s*store",
            r"cambridge",
        ],
        # Transport (Needs)
        "cat_needs_transport": [
            r"uber",
            r"bolt",
            r"taxify",
            r"gautrain",
            r"metrorail",
            r"shell",
            r"engen",
            r"bp\s",
            r"caltex",
            r"sasol",
            r"total",
            r"petrol",
            r"fuel",
            r"garage",
            r"filling\s*station",
        ],
        # Utilities (Needs)
        "cat_needs_utilities": [
            r"eskom",
            r"city\s*power",
            r"municipality",
            r"rates",
            r"water\s*bill",
            r"electricity",
            r"prepaid",
        ],
        # Data/Airtime (Needs)
        "cat_needs_data": [
            r"vodacom",
            r"mtn",
            r"cell\s*c",
            r"telkom",
            r"rain",
            r"airtime",
            r"data\s*bundle",
            r"recharge",
        ],
        # Eating Out (Wants)
        "cat_wants_dining": [
            r"nando",
            r"kfc",
            r"mcdonald",
            r"steers",
            r"wimpy",
            r"spur",
            r"ocean\s*basket",
            r"mugg\s*&\s*bean",
            r"vida",
            r"seattle",
            r"restaurant",
            r"cafe",
            r"coffee",
            r"pizza",
            r"burger",
            r"takeaway",
            r"uber\s*eats",
            r"mr\s*d",
            r"order\s*in",
        ],
        # Entertainment (Wants)
        "cat_wants_entertainment": [
            r"ster\s*kinekor",
            r"nu\s*metro",
            r"cinema",
            r"movie",
            r"netflix",
            r"showmax",
            r"dstv",
            r"multichoice",
            r"spotify",
            r"apple\s*music",
            r"youtube\s*premium",
            r"playstation",
            r"xbox",
            r"steam",
            r"game",
        ],
        # Subscriptions (Wants)
        "cat_wants_subscriptions": [
            r"subscription",
            r"monthly\s*fee",
            r"membership",
            r"gym",
            r"virgin\s*active",
            r"planet\s*fitness",
        ],
        # Shopping (Wants)
        "cat_wants_shopping": [
            r"takealot",
            r"superbalist",
            r"zando",
            r"spree",
            r"mr\s*price",
            r"edgars",
            r"woolworths\s*fashion",
            r"truworths",
            r"foschini",
            r"ackermans",
            r"pep",
            r"clicks",
            r"dis-chem",
            r"amazon",
            r"shein",
        ],
        # Savings
        "cat_savings_goals": [
            r"savings",
            r"investment",
            r"unit\s*trust",
            r"easy\s*equities",
            r"satrix",
            r"tfsa",
        ],
        # Debt Payments
        "cat_debt_credit_card": [
            r"credit\s*card",
            r"visa",
            r"mastercard",
            r"amex",
        ],
        "cat_debt_loan": [
            r"loan\s*payment",
            r"personal\s*loan",
            r"home\s*loan",
            r"vehicle\s*finance",
            r"capitec\s*loan",
            r"african\s*bank",
        ],
        # Income
        "cat_income_salary": [
            r"salary",
            r"payroll",
            r"wages",
            r"income",
        ],
        "cat_income_freelance": [
            r"freelance",
            r"consulting",
            r"contract",
            r"invoice",
        ],
    }

    # Keyword patterns for generic categorization
    KEYWORD_PATTERNS = {
        "cat_needs_rent": [r"rent", r"lease", r"landlord"],
        "cat_needs_groceries": [r"grocery", r"supermarket", r"food"],
        "cat_needs_transport": [r"transport", r"taxi", r"bus", r"train"],
        "cat_needs_utilities": [r"utility", r"water", r"electric"],
        "cat_wants_dining": [r"restaurant", r"food", r"eat", r"dine"],
        "cat_wants_entertainment": [r"entertainment", r"movie", r"show"],
        "cat_savings_emergency": [r"emergency", r"savings"],
        "cat_debt_credit_card": [r"credit", r"card"],
        "cat_income_salary": [r"salary", r"pay", r"wage"],
    }

    def __init__(self):
        """Initialize categorizer."""
        self.user_patterns: Dict[str, List[str]] = {}
        self._load_user_patterns()

    def _load_user_patterns(self):
        """Load user's historical categorization patterns."""
        try:
            transactions = csv_manager.read_all("transactions.csv")

            # Build patterns from user's manual categorizations
            category_descriptions: Dict[str, List[str]] = {}

            for tx in transactions:
                category_id = tx.get("category_id", "")
                description = tx.get("description", "").lower()

                if category_id and description:
                    if category_id not in category_descriptions:
                        category_descriptions[category_id] = []
                    category_descriptions[category_id].append(description)

            # Extract common words from descriptions per category
            for category_id, descriptions in category_descriptions.items():
                if len(descriptions) >= 2:  # Need at least 2 examples
                    # Extract unique words (simple approach)
                    words = set()
                    for desc in descriptions:
                        words.update(desc.split())

                    # Filter out common words
                    common_words = {
                        "the",
                        "a",
                        "an",
                        "and",
                        "or",
                        "but",
                        "in",
                        "on",
                        "at",
                        "to",
                        "for",
                    }
                    meaningful_words = [
                        w for w in words if len(w) > 3 and w not in common_words
                    ]

                    if meaningful_words:
                        self.user_patterns[category_id] = meaningful_words[
                            :10
                        ]  # Top 10

        except Exception:
            # If loading fails, continue with default patterns
            pass

    def categorize(self, description: str, amount: float) -> Tuple[str, float]:
        """
        Categorize a transaction based on description and amount.

        Args:
            description: Transaction description
            amount: Transaction amount (negative for expenses)

        Returns:
            Tuple of (category_id, confidence_score)
            confidence_score: 0.0 to 1.0 (0.8+ = high, 0.5-0.8 = medium, <0.5 = low)
        """
        description_lower = description.lower()

        # Income detection (positive amounts)
        if amount > 0:
            return self._categorize_income(description_lower)

        # Expense categorization (negative amounts)
        return self._categorize_expense(description_lower, abs(amount))

    def _categorize_income(self, description: str) -> Tuple[str, float]:
        """Categorize income transactions."""
        # Check merchant patterns
        for category_id, patterns in self.MERCHANT_PATTERNS.items():
            if not category_id.startswith("cat_income_"):
                continue

            for pattern in patterns:
                if re.search(pattern, description, re.IGNORECASE):
                    return (category_id, 0.9)

        # Check keyword patterns
        for category_id, patterns in self.KEYWORD_PATTERNS.items():
            if not category_id.startswith("cat_income_"):
                continue

            for pattern in patterns:
                if re.search(pattern, description, re.IGNORECASE):
                    return (category_id, 0.7)

        # Default to salary for income
        return ("cat_income_salary", 0.5)

    def _categorize_expense(self, description: str, amount: float) -> Tuple[str, float]:
        """Categorize expense transactions."""
        # 1. Check user's learned patterns first (highest priority)
        user_match = self._check_user_patterns(description)
        if user_match:
            return user_match

        # 2. Check merchant patterns (high confidence)
        merchant_match = self._check_merchant_patterns(description)
        if merchant_match:
            return merchant_match

        # 3. Check keyword patterns (medium confidence)
        keyword_match = self._check_keyword_patterns(description)
        if keyword_match:
            return keyword_match

        # 4. Amount-based heuristics (low confidence)
        amount_match = self._categorize_by_amount(amount)
        if amount_match:
            return amount_match

        # 5. Default to uncategorized
        return ("cat_needs_groceries", 0.3)  # Low confidence default

    def _check_user_patterns(self, description: str) -> Optional[Tuple[str, float]]:
        """Check against user's learned patterns."""
        for category_id, words in self.user_patterns.items():
            for word in words:
                if word in description:
                    return (category_id, 0.85)
        return None

    def _check_merchant_patterns(self, description: str) -> Optional[Tuple[str, float]]:
        """Check against known merchant patterns."""
        for category_id, patterns in self.MERCHANT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, description, re.IGNORECASE):
                    return (category_id, 0.9)
        return None

    def _check_keyword_patterns(self, description: str) -> Optional[Tuple[str, float]]:
        """Check against keyword patterns."""
        for category_id, patterns in self.KEYWORD_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, description, re.IGNORECASE):
                    return (category_id, 0.6)
        return None

    def _categorize_by_amount(self, amount: float) -> Optional[Tuple[str, float]]:
        """Categorize based on amount heuristics."""
        # Large amounts might be rent
        if amount > 3000:
            return ("cat_needs_rent", 0.4)

        # Medium amounts might be groceries
        if amount > 200:
            return ("cat_needs_groceries", 0.4)

        # Small amounts might be transport or dining
        if amount < 100:
            return ("cat_needs_transport", 0.3)

        return None

    def get_confidence_label(self, confidence: float) -> str:
        """Get human-readable confidence label."""
        if confidence >= 0.8:
            return "High"
        elif confidence >= 0.5:
            return "Medium"
        else:
            return "Low"


# Global categorizer instance
categorizer = Categorizer()
