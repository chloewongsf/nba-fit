"""
Feature engineering module for NBA Fit analysis.
Contains functions to create and process features from player and team data.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional


class FeatureEngineer:
    """
    Feature engineering class for NBA player-team fit analysis.
    """
    
    def __init__(self):
        """Initialize the feature engineer."""
        self.feature_weights = {
            'scoring': 0.3,
            'defense': 0.3,
            'playmaking': 0.4
        }
    
    def create_features(self, player_data: Dict[str, Any], team_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Create features from player and team data.
        
        Args:
            player_data: Dictionary containing player statistics
            team_data: Dictionary containing team statistics
            
        Returns:
            Dictionary of engineered features
        """
        features = {}
        
        # Scoring features
        features['scoring'] = self._calculate_scoring_feature(player_data, team_data)
        
        # Defense features
        features['defense'] = self._calculate_defense_feature(player_data, team_data)
        
        # Playmaking features
        features['playmaking'] = self._calculate_playmaking_feature(player_data, team_data)
        
        # Additional advanced features
        features['efficiency'] = self._calculate_efficiency_feature(player_data)
        features['versatility'] = self._calculate_versatility_feature(player_data)
        features['team_need'] = self._calculate_team_need_feature(player_data, team_data)
        
        return features
    
    def _calculate_scoring_feature(self, player_data: Dict[str, Any], team_data: Dict[str, Any]) -> float:
        """
        Calculate scoring-related features.
        
        Args:
            player_data: Player statistics
            team_data: Team statistics
            
        Returns:
            Scoring feature score (0-100)
        """
        # Placeholder implementation - in real app, would use actual NBA stats
        base_score = 75.0
        
        # Simulate some variation based on player name length (demo purposes)
        if 'player_name' in player_data:
            name_factor = len(player_data['player_name']) * 2
            base_score += name_factor
        
        # Team scoring need (placeholder)
        team_scoring_need = team_data.get('scoring_need', 0.5)
        scoring_fit = base_score * (1 + team_scoring_need)
        
        return min(100.0, max(0.0, scoring_fit))
    
    def _calculate_defense_feature(self, player_data: Dict[str, Any], team_data: Dict[str, Any]) -> float:
        """
        Calculate defense-related features.
        
        Args:
            player_data: Player statistics
            team_data: Team statistics
            
        Returns:
            Defense feature score (0-100)
        """
        # Placeholder implementation
        base_score = 70.0
        
        # Simulate defensive rating based on player data
        if 'player_name' in player_data:
            name_factor = hash(player_data['player_name']) % 20
            base_score += name_factor
        
        # Team defensive need
        team_defense_need = team_data.get('defense_need', 0.3)
        defense_fit = base_score * (1 + team_defense_need)
        
        return min(100.0, max(0.0, defense_fit))
    
    def _calculate_playmaking_feature(self, player_data: Dict[str, Any], team_data: Dict[str, Any]) -> float:
        """
        Calculate playmaking-related features.
        
        Args:
            player_data: Player statistics
            team_data: Team statistics
            
        Returns:
            Playmaking feature score (0-100)
        """
        # Placeholder implementation
        base_score = 65.0
        
        # Simulate playmaking ability
        if 'player_name' in player_data:
            name_factor = (hash(player_data['player_name']) % 15) + 5
            base_score += name_factor
        
        # Team playmaking need
        team_playmaking_need = team_data.get('playmaking_need', 0.4)
        playmaking_fit = base_score * (1 + team_playmaking_need)
        
        return min(100.0, max(0.0, playmaking_fit))
    
    def _calculate_efficiency_feature(self, player_data: Dict[str, Any]) -> float:
        """
        Calculate player efficiency metrics.
        
        Args:
            player_data: Player statistics
            
        Returns:
            Efficiency score (0-100)
        """
        # Placeholder for efficiency calculations
        # In real implementation, would calculate PER, TS%, etc.
        return 72.5
    
    def _calculate_versatility_feature(self, player_data: Dict[str, Any]) -> float:
        """
        Calculate player versatility metrics.
        
        Args:
            player_data: Player statistics
            
        Returns:
            Versatility score (0-100)
        """
        # Placeholder for versatility calculations
        # In real implementation, would analyze position flexibility, skill diversity
        return 68.0
    
    def _calculate_team_need_feature(self, player_data: Dict[str, Any], team_data: Dict[str, Any]) -> float:
        """
        Calculate how well player fills team needs.
        
        Args:
            player_data: Player statistics
            team_data: Team statistics
            
        Returns:
            Team need fulfillment score (0-100)
        """
        # Placeholder for team need analysis
        # In real implementation, would analyze roster gaps, playing style fit
        return 75.0
    
    def normalize_features(self, features: Dict[str, float]) -> Dict[str, float]:
        """
        Normalize features to 0-100 scale.
        
        Args:
            features: Raw feature dictionary
            
        Returns:
            Normalized feature dictionary
        """
        normalized = {}
        for key, value in features.items():
            # Ensure values are within 0-100 range
            normalized[key] = max(0.0, min(100.0, value))
        
        return normalized
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance weights.
        
        Returns:
            Dictionary of feature importance weights
        """
        return self.feature_weights.copy()
