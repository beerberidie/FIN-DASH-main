"""Card service for managing payment cards."""
from typing import Dict, List, Any
from collections import defaultdict
from datetime import datetime

from services.csv_manager import csv_manager


class CardService:
    """Service for card-related operations."""
    
    def calculate_card_balance(self, card_id: str) -> Dict[str, float]:
        """
        Calculate current balance for a card based on transactions.
        
        Args:
            card_id: Card ID
            
        Returns:
            Dictionary with available_balance and current_balance
        """
        # Get card
        cards = csv_manager.read_csv('cards.csv')
        card = next((c for c in cards if c['id'] == card_id), None)
        
        if not card:
            return {'available_balance': 0.0, 'current_balance': 0.0}
        
        # Get transactions for this card
        transactions = csv_manager.read_csv('transactions.csv')
        card_transactions = [tx for tx in transactions if tx.get('card_id') == card_id]
        
        # Calculate balance from transactions
        balance = 0.0
        for tx in card_transactions:
            amount = float(tx.get('amount', 0))
            balance += amount
        
        # For credit cards, calculate available credit
        card_type = card.get('card_type', 'debit')
        credit_limit = float(card.get('credit_limit', 0)) if card.get('credit_limit') else 0.0
        
        if card_type == 'credit':
            # For credit cards:
            # - current_balance is negative (amount owed)
            # - available_balance is credit_limit - abs(current_balance)
            current_balance = balance  # Should be negative
            available_balance = credit_limit + current_balance  # Add because current_balance is negative
        else:
            # For debit/prepaid cards:
            # - current_balance is the actual balance
            # - available_balance is the same as current_balance
            current_balance = balance
            available_balance = balance
        
        return {
            'available_balance': available_balance,
            'current_balance': current_balance
        }
    
    def get_card_analytics(self, card_id: str) -> Dict[str, Any]:
        """
        Get spending analytics for a card.
        
        Args:
            card_id: Card ID
            
        Returns:
            Dictionary with analytics data
        """
        # Get transactions for this card
        transactions = csv_manager.read_csv('transactions.csv')
        card_transactions = [tx for tx in transactions if tx.get('card_id') == card_id]
        
        if not card_transactions:
            return {
                'card_id': card_id,
                'total_transactions': 0,
                'total_spent': 0.0,
                'average_transaction': 0.0,
                'spending_by_category': {},
                'monthly_spending': {},
                'credit_utilization': 0.0
            }
        
        # Calculate totals
        total_spent = 0.0
        spending_by_category = defaultdict(float)
        monthly_spending = defaultdict(float)
        
        for tx in card_transactions:
            amount = float(tx.get('amount', 0))
            
            # Only count expenses (negative amounts)
            if amount < 0:
                total_spent += abs(amount)
                
                # By category
                category_id = tx.get('category_id', 'uncategorized')
                spending_by_category[category_id] += abs(amount)
                
                # By month
                tx_date = tx.get('date', '')
                if tx_date:
                    month = tx_date[:7]  # YYYY-MM
                    monthly_spending[month] += abs(amount)
        
        # Calculate average
        expense_count = sum(1 for tx in card_transactions if float(tx.get('amount', 0)) < 0)
        average_transaction = total_spent / expense_count if expense_count > 0 else 0.0
        
        # Calculate credit utilization
        cards = csv_manager.read_csv('cards.csv')
        card = next((c for c in cards if c['id'] == card_id), None)
        credit_utilization = 0.0
        
        if card and card.get('card_type') == 'credit':
            credit_limit = float(card.get('credit_limit', 0)) if card.get('credit_limit') else 0.0
            current_balance = float(card.get('current_balance', 0))
            
            if credit_limit > 0:
                # Utilization is (amount owed / credit limit) * 100
                credit_utilization = (abs(current_balance) / credit_limit) * 100
        
        return {
            'card_id': card_id,
            'total_transactions': len(card_transactions),
            'total_spent': total_spent,
            'average_transaction': average_transaction,
            'spending_by_category': dict(spending_by_category),
            'monthly_spending': dict(monthly_spending),
            'credit_utilization': credit_utilization
        }
    
    def validate_card_account_link(self, card_id: str, account_id: str) -> bool:
        """
        Validate that a card is linked to the specified account.
        
        Args:
            card_id: Card ID
            account_id: Account ID
            
        Returns:
            True if card is linked to account, False otherwise
        """
        cards = csv_manager.read_csv('cards.csv')
        card = next((c for c in cards if c['id'] == card_id), None)
        
        if not card:
            return False
        
        return card.get('account_id') == account_id
    
    def get_cards_by_account(self, account_id: str) -> List[Dict]:
        """
        Get all cards linked to an account.
        
        Args:
            account_id: Account ID
            
        Returns:
            List of cards
        """
        cards = csv_manager.read_csv('cards.csv')
        return [card for card in cards if card.get('account_id') == account_id]
    
    def update_card_balances(self, card_id: str) -> Dict[str, float]:
        """
        Update card balances based on transactions.
        
        Args:
            card_id: Card ID
            
        Returns:
            Updated balances
        """
        balances = self.calculate_card_balance(card_id)
        
        # Update card in CSV
        cards = csv_manager.read_csv('cards.csv')
        for i, card in enumerate(cards):
            if card['id'] == card_id:
                card['available_balance'] = str(balances['available_balance'])
                card['current_balance'] = str(balances['current_balance'])
                card['updated_at'] = datetime.now().isoformat()
                cards[i] = card
                break
        
        # Write back to CSV
        from models.card import CARD_FIELDNAMES
        csv_manager.write_csv('cards.csv', cards, CARD_FIELDNAMES)
        
        return balances


# Global instance
card_service = CardService()

