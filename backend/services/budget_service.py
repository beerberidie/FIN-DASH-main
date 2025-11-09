"""Budget calculation and analysis service."""
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict

from services.csv_manager import csv_manager
from services.calculator import calculator
from models.budget import BUDGET_FIELDNAMES
from models.transaction import TRANSACTION_FIELDNAMES


class BudgetService:
    """Service for budget calculations and analysis."""
    
    def calculate_actual_spending(self, year: int, month: int) -> Dict[str, float]:
        """
        Calculate actual spending per category for a given month.
        
        Args:
            year: Year (e.g., 2025)
            month: Month (1-12)
            
        Returns:
            Dictionary mapping category_id to actual spending amount
        """
        # Get all transactions for the month
        transactions = csv_manager.read_csv('transactions.csv')
        
        # Filter transactions for the specified month
        spending_by_category = defaultdict(float)
        
        for tx in transactions:
            tx_date = datetime.fromisoformat(tx['date'])
            if tx_date.year == year and tx_date.month == month:
                category_id = tx.get('category_id', '')
                amount = float(tx['amount'])
                
                # Only count expenses (negative amounts)
                if amount < 0:
                    spending_by_category[category_id] += abs(amount)
        
        return dict(spending_by_category)
    
    def calculate_budget_status(self, budget_id: str) -> Dict[str, Any]:
        """
        Calculate budget status with actual vs planned comparison.
        
        Args:
            budget_id: Budget ID
            
        Returns:
            Dictionary with budget status including utilization percentage
        """
        budgets = csv_manager.read_csv('budgets.csv')
        budget = next((b for b in budgets if b['id'] == budget_id), None)
        
        if not budget:
            return None
        
        year = int(budget['year'])
        month = int(budget['month'])
        
        # Get actual spending
        actual_spending = self.calculate_actual_spending(year, month)
        
        # Calculate totals by group
        categories = csv_manager.read_csv('categories.csv')
        category_map = {cat['id']: cat for cat in categories}
        
        group_actual = defaultdict(float)
        for cat_id, amount in actual_spending.items():
            if cat_id in category_map:
                group = category_map[cat_id]['group']
                group_actual[group] += amount
        
        # Build status
        status = {
            'id': budget['id'],
            'year': year,
            'month': month,
            'needs_planned': float(budget['needs_planned']),
            'needs_actual': group_actual.get('needs', 0.0),
            'wants_planned': float(budget['wants_planned']),
            'wants_actual': group_actual.get('wants', 0.0),
            'savings_planned': float(budget['savings_planned']),
            'savings_actual': group_actual.get('savings', 0.0),
            'total_planned': float(budget['needs_planned']) + float(budget['wants_planned']) + float(budget['savings_planned']),
            'total_actual': sum(group_actual.values()),
        }
        
        # Calculate utilization percentages
        status['needs_utilization'] = (status['needs_actual'] / status['needs_planned'] * 100) if status['needs_planned'] > 0 else 0
        status['wants_utilization'] = (status['wants_actual'] / status['wants_planned'] * 100) if status['wants_planned'] > 0 else 0
        status['savings_utilization'] = (status['savings_actual'] / status['savings_planned'] * 100) if status['savings_planned'] > 0 else 0
        status['total_utilization'] = (status['total_actual'] / status['total_planned'] * 100) if status['total_planned'] > 0 else 0
        
        # Identify over-budget categories
        status['over_budget'] = {
            'needs': status['needs_actual'] > status['needs_planned'],
            'wants': status['wants_actual'] > status['wants_planned'],
            'savings': status['savings_actual'] > status['savings_planned'],
        }
        
        return status
    
    def get_current_month_budget(self) -> Dict[str, Any]:
        """
        Get budget for the current month.
        
        Returns:
            Budget status for current month, or None if not found
        """
        now = datetime.now()
        budgets = csv_manager.read_csv('budgets.csv')
        
        # Find budget for current month
        current_budget = next(
            (b for b in budgets if int(b['year']) == now.year and int(b['month']) == now.month),
            None
        )
        
        if not current_budget:
            return None
        
        return self.calculate_budget_status(current_budget['id'])
    
    def get_category_breakdown(self, year: int, month: int) -> List[Dict[str, Any]]:
        """
        Get detailed spending breakdown by category for a month.
        
        Args:
            year: Year
            month: Month
            
        Returns:
            List of categories with actual spending and budget allocation
        """
        # Get actual spending
        actual_spending = self.calculate_actual_spending(year, month)
        
        # Get categories
        categories = csv_manager.read_csv('categories.csv')
        
        # Get budget for the month
        budgets = csv_manager.read_csv('budgets.csv')
        budget = next(
            (b for b in budgets if int(b['year']) == year and int(b['month']) == month),
            None
        )
        
        breakdown = []
        for cat in categories:
            cat_id = cat['id']
            actual = actual_spending.get(cat_id, 0.0)
            
            # Calculate allocated budget based on category group
            allocated = 0.0
            if budget:
                group = cat['group']
                if group == 'needs':
                    allocated = float(budget['needs_planned'])
                elif group == 'wants':
                    allocated = float(budget['wants_planned'])
                elif group == 'savings':
                    allocated = float(budget['savings_planned'])
            
            breakdown.append({
                'category_id': cat_id,
                'category_name': cat['name'],
                'group': cat['group'],
                'actual': actual,
                'allocated': allocated,
                'utilization': (actual / allocated * 100) if allocated > 0 else 0,
                'over_budget': actual > allocated if allocated > 0 else False,
            })
        
        # Sort by actual spending (highest first)
        breakdown.sort(key=lambda x: x['actual'], reverse=True)
        
        return breakdown


# Singleton instance
budget_service = BudgetService()

