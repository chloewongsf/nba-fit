"""
Scoring module for NBA Fit analysis.
Contains functions to calculate overall fit scores from engineered features.
"""

import numpy as np
from typing import Dict, Any, Optional


def calculate_fit_score(
    features: Dict[str, float],
    scoring_weight: float = 0.3,
    defense_weight: float = 0.3,
    playmaking_weight: float = 0.4,
    **kwargs
) -> float:
    """
    Calculate overall fit score from engineered features.
    
    Args:
        features: Dictionary of engineered features
        scoring_weight: Weight for scoring features (0.0-1.0)
        defense_weight: Weight for defense features (0.0-1.0)
        playmaking_weight: Weight for playmaking features (0.0-1.0)
        **kwargs: Additional parameters for future use
        
    Returns:
        Overall fit score (0-100)
    """
    # Validate weights
    total_weight = scoring_weight + defense_weight + playmaking_weight
    if abs(total_weight - 1.0) > 0.01:  # Allow small floating point errors
        # Normalize weights if they don't sum to 1
        scoring_weight /= total_weight
        defense_weight /= total_weight
        playmaking_weight /= total_weight
    
    # Extract core features
    scoring_score = features.get('scoring', 0.0)
    defense_score = features.get('defense', 0.0)
    playmaking_score = features.get('playmaking', 0.0)
    
    # Calculate weighted average
    weighted_score = (
        scoring_score * scoring_weight +
        defense_score * defense_weight +
        playmaking_score * playmaking_weight
    )
    
    # Apply additional factors
    weighted_score = apply_additional_factors(weighted_score, features)
    
    # Ensure score is within bounds
    return max(0.0, min(100.0, weighted_score))


def apply_additional_factors(base_score: float, features: Dict[str, float]) -> float:
    """
    Apply additional factors to the base score.
    
    Args:
        base_score: Base weighted score
        features: All available features
        
    Returns:
        Adjusted score with additional factors
    """
    adjusted_score = base_score
    
    # Efficiency bonus/penalty
    efficiency = features.get('efficiency', 50.0)
    if efficiency > 75.0:
        adjusted_score *= 1.05  # 5% bonus for high efficiency
    elif efficiency < 45.0:
        adjusted_score *= 0.95  # 5% penalty for low efficiency
    
    # Versatility bonus
    versatility = features.get('versatility', 50.0)
    if versatility > 80.0:
        adjusted_score *= 1.03  # 3% bonus for high versatility
    
    # Team need fulfillment
    team_need = features.get('team_need', 50.0)
    if team_need > 80.0:
        adjusted_score *= 1.02  # 2% bonus for filling team needs
    
    return adjusted_score


def calculate_position_fit_score(
    player_position: str,
    team_needs: Dict[str, float],
    features: Dict[str, float]
) -> float:
    """
    Calculate position-specific fit score.
    
    Args:
        player_position: Player's primary position
        team_needs: Team's positional needs
        features: Player features
        
    Returns:
        Position-specific fit score (0-100)
    """
    # Position-specific weights
    position_weights = {
        'PG': {'playmaking': 0.5, 'scoring': 0.3, 'defense': 0.2},
        'SG': {'scoring': 0.4, 'defense': 0.3, 'playmaking': 0.3},
        'SF': {'scoring': 0.35, 'defense': 0.35, 'playmaking': 0.3},
        'PF': {'defense': 0.4, 'scoring': 0.35, 'playmaking': 0.25},
        'C': {'defense': 0.5, 'scoring': 0.3, 'playmaking': 0.2}
    }
    
    weights = position_weights.get(player_position, position_weights['SF'])
    
    # Calculate position-specific score
    position_score = (
        features.get('scoring', 0) * weights['scoring'] +
        features.get('defense', 0) * weights['defense'] +
        features.get('playmaking', 0) * weights['playmaking']
    )
    
    # Apply team need factor
    team_need_factor = team_needs.get(player_position, 0.5)
    position_score *= (1 + team_need_factor * 0.2)  # Up to 20% bonus
    
    return max(0.0, min(100.0, position_score))


def calculate_advanced_metrics(features: Dict[str, float]) -> Dict[str, float]:
    """
    Calculate advanced metrics from basic features.
    
    Args:
        features: Basic feature dictionary
        
    Returns:
        Dictionary of advanced metrics
    """
    advanced_metrics = {}
    
    # Overall impact score
    advanced_metrics['impact_score'] = (
        features.get('scoring', 0) * 0.3 +
        features.get('defense', 0) * 0.3 +
        features.get('playmaking', 0) * 0.4
    )
    
    # Consistency score (simulated)
    advanced_metrics['consistency'] = 75.0  # Placeholder
    
    # Clutch factor (simulated)
    advanced_metrics['clutch_factor'] = 70.0  # Placeholder
    
    # Leadership score (simulated)
    advanced_metrics['leadership'] = 65.0  # Placeholder
    
    return advanced_metrics


def get_score_interpretation(score: float) -> str:
    """
    Get human-readable interpretation of fit score.
    
    Args:
        score: Fit score (0-100)
        
    Returns:
        Interpretation string
    """
    if score >= 90:
        return "Exceptional fit - Perfect match for the team"
    elif score >= 80:
        return "Excellent fit - Great addition to the roster"
    elif score >= 70:
        return "Good fit - Solid player for the team"
    elif score >= 60:
        return "Decent fit - Could work with the right role"
    elif score >= 50:
        return "Average fit - Mixed results expected"
    elif score >= 40:
        return "Poor fit - Significant concerns about compatibility"
    else:
        return "Very poor fit - Not recommended for this team"


def calculate_confidence_interval(score: float, features: Dict[str, float]) -> tuple:
    """
    Calculate confidence interval for the fit score.
    
    Args:
        score: Calculated fit score
        features: Feature dictionary
        
    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    # Calculate uncertainty based on feature completeness and variance
    feature_count = len(features)
    feature_variance = np.var(list(features.values()))
    
    # Base uncertainty
    uncertainty = 5.0  # Base 5 point uncertainty
    
    # Adjust based on feature variance
    if feature_variance > 100:
        uncertainty += 3.0
    elif feature_variance < 25:
        uncertainty -= 1.0
    
    # Adjust based on feature count
    if feature_count < 5:
        uncertainty += 2.0
    
    lower_bound = max(0.0, score - uncertainty)
    upper_bound = min(100.0, score + uncertainty)
    
    return (lower_bound, upper_bound)
