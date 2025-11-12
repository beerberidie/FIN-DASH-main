"""Portfolio analytics and performance calculation service."""

from typing import List, Dict
from collections import defaultdict

from models.investment import PortfolioSummary, InvestmentPerformance
from services.investment_service import investment_service


class PortfolioService:
    """Service for portfolio analytics and performance metrics."""

    def get_portfolio_summary(self, base_currency: str = "USD") -> PortfolioSummary:
        """
        Get comprehensive portfolio summary with performance metrics.

        Args:
            base_currency: Base currency for reporting (default: USD)

        Returns:
            PortfolioSummary object with all metrics
        """
        investments = investment_service.list_investments()

        if not investments:
            return PortfolioSummary(
                total_investments=0,
                total_value=0.0,
                total_cost=0.0,
                total_profit_loss=0.0,
                total_profit_loss_percentage=0.0,
                currency=base_currency,
                by_type={},
                top_performers=[],
                worst_performers=[],
            )

        # Calculate performance for each investment
        performances: List[InvestmentPerformance] = []
        for inv in investments:
            try:
                perf = investment_service.get_investment_performance(inv.id)
                performances.append(perf)
            except Exception:
                continue

        # Calculate totals
        total_value = sum(p.current_value for p in performances)
        total_cost = sum(p.total_cost for p in performances)
        total_profit_loss = total_value - total_cost
        total_profit_loss_percentage = (
            (total_profit_loss / total_cost * 100) if total_cost > 0 else 0
        )

        # Group by type for asset allocation
        by_type = self._calculate_asset_allocation(performances, total_value)

        # Get top and worst performers
        sorted_by_performance = sorted(
            performances, key=lambda p: p.profit_loss_percentage, reverse=True
        )

        top_performers = [
            {
                "symbol": p.symbol,
                "name": p.name,
                "profit_loss": p.profit_loss,
                "profit_loss_percentage": p.profit_loss_percentage,
                "current_value": p.current_value,
            }
            for p in sorted_by_performance[:5]
        ]

        worst_performers = [
            {
                "symbol": p.symbol,
                "name": p.name,
                "profit_loss": p.profit_loss,
                "profit_loss_percentage": p.profit_loss_percentage,
                "current_value": p.current_value,
            }
            for p in sorted_by_performance[-5:]
        ]

        return PortfolioSummary(
            total_investments=len(performances),
            total_value=total_value,
            total_cost=total_cost,
            total_profit_loss=total_profit_loss,
            total_profit_loss_percentage=total_profit_loss_percentage,
            currency=base_currency,
            by_type=by_type,
            top_performers=top_performers,
            worst_performers=worst_performers,
        )

    def _calculate_asset_allocation(
        self, performances: List[InvestmentPerformance], total_value: float
    ) -> Dict[str, Dict]:
        """
        Calculate asset allocation by investment type.

        Args:
            performances: List of investment performances
            total_value: Total portfolio value

        Returns:
            Dictionary with allocation by type
        """
        allocation = defaultdict(
            lambda: {
                "count": 0,
                "total_value": 0.0,
                "total_cost": 0.0,
                "profit_loss": 0.0,
                "percentage": 0.0,
            }
        )

        for perf in performances:
            inv_type = perf.type
            allocation[inv_type]["count"] += 1
            allocation[inv_type]["total_value"] += perf.current_value
            allocation[inv_type]["total_cost"] += perf.total_cost
            allocation[inv_type]["profit_loss"] += perf.profit_loss

        # Calculate percentages
        for inv_type in allocation:
            type_value = allocation[inv_type]["total_value"]
            allocation[inv_type]["percentage"] = (
                (type_value / total_value * 100) if total_value > 0 else 0
            )

        return dict(allocation)

    def get_asset_allocation(self) -> Dict[str, float]:
        """
        Get simple asset allocation percentages by type.

        Returns:
            Dictionary mapping investment type to percentage
        """
        summary = self.get_portfolio_summary()

        return {
            inv_type: data["percentage"] for inv_type, data in summary.by_type.items()
        }

    def get_total_portfolio_value(self, base_currency: str = "USD") -> float:
        """
        Get total portfolio value.

        Args:
            base_currency: Base currency for reporting

        Returns:
            Total portfolio value
        """
        summary = self.get_portfolio_summary(base_currency)
        return summary.total_value

    def get_portfolio_profit_loss(self, base_currency: str = "USD") -> Dict[str, float]:
        """
        Get portfolio profit/loss metrics.

        Args:
            base_currency: Base currency for reporting

        Returns:
            Dictionary with profit/loss metrics
        """
        summary = self.get_portfolio_summary(base_currency)

        return {
            "total_cost": summary.total_cost,
            "total_value": summary.total_value,
            "profit_loss": summary.total_profit_loss,
            "profit_loss_percentage": summary.total_profit_loss_percentage,
            "currency": base_currency,
        }

    def get_investments_by_type(
        self, investment_type: str
    ) -> List[InvestmentPerformance]:
        """
        Get all investments of a specific type with performance metrics.

        Args:
            investment_type: Type of investment (stock, etf, crypto, etc.)

        Returns:
            List of InvestmentPerformance objects
        """
        investments = investment_service.list_investments(type_filter=investment_type)

        performances = []
        for inv in investments:
            try:
                perf = investment_service.get_investment_performance(inv.id)
                performances.append(perf)
            except Exception:
                continue

        # Sort by current value descending
        performances.sort(key=lambda p: p.current_value, reverse=True)

        return performances


# Singleton instance
portfolio_service = PortfolioService()
