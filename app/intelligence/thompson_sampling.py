"""
Thompson Sampling - Bayesian approach for cold-start campaign optimization.

Thompson Sampling helps optimize budget allocation when there's limited historical data
by balancing exploration (trying uncertain options) with exploitation (using proven winners).
"""
import numpy as np
from typing import List, Dict, Any, Tuple
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)


class ThompsonSampling:
    """
    Thompson Sampling for multi-armed bandit problem in campaign optimization.
    
    Each campaign is an "arm" and we want to allocate budget to maximize ROAS.
    Uses Beta distribution for modeling success probability.
    """
    
    def __init__(self, alpha_prior: float = 1.0, beta_prior: float = 1.0):
        """
        Initialize Thompson Sampling with Beta prior.
        
        Args:
            alpha_prior: Prior successes (optimistic prior encourages exploration)
            beta_prior: Prior failures
        """
        self.alpha_prior = alpha_prior
        self.beta_prior = beta_prior
    
    def select_campaigns_for_budget_increase(
        self,
        campaigns: List[Dict[str, Any]],
        total_additional_budget: float,
        num_samples: int = 10000
    ) -> Dict[str, float]:
        """
        Use Thompson Sampling to allocate additional budget across campaigns.
        
        Args:
            campaigns: List of campaign data with performance metrics
            total_additional_budget: Total budget to allocate
            num_samples: Number of Monte Carlo samples
        
        Returns:
            Dictionary mapping campaign_id to additional budget amount
        """
        if not campaigns or total_additional_budget <= 0:
            return {}
        
        # Build Beta distributions for each campaign
        campaign_distributions = []
        
        for campaign in campaigns:
            metrics = campaign.get("current_metrics", {})
            
            # Use conversions as successes, clicks as trials
            conversions = metrics.get("conversions", 0)
            clicks = metrics.get("clicks", 0)
            
            if clicks == 0:
                # New campaign with no data - use priors
                alpha = self.alpha_prior
                beta = self.beta_prior
            else:
                # Update with observed data
                alpha = self.alpha_prior + conversions
                beta = self.beta_prior + (clicks - conversions)
            
            campaign_distributions.append({
                "campaign_id": campaign["campaign_id"],
                "campaign_name": campaign.get("name", "Unknown"),
                "alpha": alpha,
                "beta": beta,
                "current_budget": campaign.get("daily_budget", 0),
                "current_roas": metrics.get("roas", 0)
            })
        
        # Sample from each distribution and count wins
        win_counts = {c["campaign_id"]: 0 for c in campaign_distributions}
        
        for _ in range(num_samples):
            samples = []
            for dist in campaign_distributions:
                # Sample from Beta distribution
                sample = np.random.beta(dist["alpha"], dist["beta"])
                samples.append((dist["campaign_id"], sample))
            
            # Find winner of this sample
            winner_id = max(samples, key=lambda x: x[1])[0]
            win_counts[winner_id] += 1
        
        # Allocate budget proportional to win probability
        budget_allocation = {}
        total_wins = sum(win_counts.values())
        
        for campaign_id, wins in win_counts.items():
            win_probability = wins / total_wins if total_wins > 0 else 0
            allocated_budget = total_additional_budget * win_probability
            
            # Only allocate if probability is significant (> 1%)
            if win_probability > 0.01:
                budget_allocation[campaign_id] = round(allocated_budget, 2)
        
        logger.info(
            "thompson_sampling_allocation",
            num_campaigns=len(campaigns),
            total_budget=total_additional_budget,
            allocations=len(budget_allocation)
        )
        
        return budget_allocation
    
    def calculate_exploration_bonus(
        self,
        campaign: Dict[str, Any]
    ) -> float:
        """
        Calculate exploration bonus for a campaign.
        
        Higher bonus for campaigns with more uncertainty (fewer data points).
        
        Args:
            campaign: Campaign data
        
        Returns:
            Exploration bonus factor (0-1)
        """
        metrics = campaign.get("current_metrics", {})
        clicks = metrics.get("clicks", 0)
        
        # Exploration bonus decreases as we gather more data
        # Using logarithmic decay
        if clicks == 0:
            return 1.0  # Maximum exploration for new campaigns
        
        # Bonus decreases logarithmically with data
        # After 1000 clicks, bonus is ~0.5
        # After 10000 clicks, bonus is ~0.25
        bonus = 1.0 / (1 + np.log10(clicks + 1) / 2)
        
        return max(0.0, min(1.0, bonus))
    
    def get_confidence_interval(
        self,
        campaign: Dict[str, Any],
        confidence: float = 0.95
    ) -> Tuple[float, float]:
        """
        Get confidence interval for campaign conversion rate.
        
        Args:
            campaign: Campaign data
            confidence: Confidence level (e.g., 0.95 for 95%)
        
        Returns:
            Tuple of (lower_bound, upper_bound) for conversion rate
        """
        metrics = campaign.get("current_metrics", {})
        conversions = metrics.get("conversions", 0)
        clicks = metrics.get("clicks", 0)
        
        if clicks == 0:
            return (0.0, 1.0)  # Complete uncertainty
        
        # Calculate Beta distribution parameters
        alpha = self.alpha_prior + conversions
        beta = self.beta_prior + (clicks - conversions)
        
        # Calculate percentiles
        lower_percentile = (1 - confidence) / 2
        upper_percentile = 1 - lower_percentile
        
        from scipy import stats
        lower_bound = stats.beta.ppf(lower_percentile, alpha, beta)
        upper_bound = stats.beta.ppf(upper_percentile, alpha, beta)
        
        return (lower_bound, upper_bound)
    
    def should_explore(
        self,
        campaign: Dict[str, Any],
        threshold: float = 0.3
    ) -> bool:
        """
        Determine if campaign should explore (make bold moves).
        
        Args:
            campaign: Campaign data
            threshold: Exploration bonus threshold
        
        Returns:
            True if campaign should explore
        """
        exploration_bonus = self.calculate_exploration_bonus(campaign)
        return exploration_bonus > threshold
    
    def rank_campaigns_by_potential(
        self,
        campaigns: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Rank campaigns by potential (considering both performance and uncertainty).
        
        Args:
            campaigns: List of campaigns
        
        Returns:
            Sorted list of campaigns with potential scores
        """
        ranked = []
        
        for campaign in campaigns:
            metrics = campaign.get("current_metrics", {})
            current_roas = metrics.get("roas", 0)
            
            # Calculate upper bound of confidence interval (optimistic estimate)
            _, upper_ci = self.get_confidence_interval(campaign)
            
            # Exploration bonus
            exploration_bonus = self.calculate_exploration_bonus(campaign)
            
            # Potential score combines current performance with uncertainty
            # Higher uncertainty = higher potential (might be a hidden gem)
            potential_score = current_roas + (exploration_bonus * 2.0)
            
            ranked.append({
                "campaign_id": campaign["campaign_id"],
                "campaign_name": campaign.get("name", "Unknown"),
                "current_roas": current_roas,
                "exploration_bonus": exploration_bonus,
                "potential_score": potential_score,
                "confidence_upper": upper_ci
            })
        
        # Sort by potential score (descending)
        ranked.sort(key=lambda x: x["potential_score"], reverse=True)
        
        return ranked
