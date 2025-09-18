"""
Feature engineering module for NBA Fit analysis.
Contains functions to create and process features from player and team data.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from datetime import date, datetime


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
        
        # Fallback ages for well-known players (as of 2024-25 season)
        self.known_player_ages = {
            201935: 36,  # Stephen Curry
            201939: 36,  # Stephen Curry (alternative ID)
            2544: 40,    # LeBron James
            203081: 25,  # Luka Doncic
            201142: 35,  # Kevin Durant
            1629029: 26, # Zion Williamson
            203999: 26,  # Jayson Tatum
            201566: 35,  # Russell Westbrook
            203507: 30,  # Giannis Antetokounmpo
            201980: 34,  # James Harden
            202681: 33,  # Kyrie Irving
            203954: 29,  # Joel Embiid
            1630173: 25, # Precious Achiuwa
            203110: 34,  # Draymond Green
            202691: 34,  # Klay Thompson
            203952: 30,  # Andrew Wiggins
        }
    
    def _parse_height_to_inches(self, height_str: str) -> int:
        """
        Parse height from "6-6" format to total inches.
        
        Args:
            height_str: Height string in format like "6-6" or "6'6\""
            
        Returns:
            int: Total height in inches
        """
        try:
            # Handle different formats: "6-6", "6'6\"", "6'6", "6 6"
            height_str = str(height_str).strip()
            
            # Replace common separators with dash
            height_str = height_str.replace("'", "-").replace('"', "").replace(" ", "-")
            
            # Split by dash
            parts = height_str.split("-")
            if len(parts) >= 2:
                feet = int(parts[0])
                inches = int(parts[1])
                return feet * 12 + inches
            else:
                # Try to parse as single number (assume inches)
                return int(height_str)
        except (ValueError, TypeError, IndexError):
            # Default fallback
            return 78  # 6'6"
    
    def get_player_age(self, player_id: int, season_stats: Dict = None) -> int:
        """
        Get player age from season stats or fallback to known ages.
        
        Args:
            player_id: NBA player ID
            season_stats: Dictionary containing player season stats with age info
            
        Returns:
            Player age in years
        """
        # Try to get age from season stats first
        if season_stats and 'age' in season_stats and season_stats['age'] > 0:
            print(f"DEBUG: Retrieved age {season_stats['age']} for player_id {player_id}")
            return season_stats['age']
        
        # Try to calculate from birthdate in season stats
        if season_stats and 'birthdate' in season_stats:
            try:
                birthdate_str = season_stats['birthdate']
                if birthdate_str:
                    birthdate = datetime.strptime(birthdate_str.split('T')[0], '%Y-%m-%d')
                    today = date.today()
                    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
                    print(f"DEBUG: Calculated age {age} from birthdate for player_id {player_id}")
                    return max(0, age)
            except Exception as e:
                print(f"DEBUG: Error calculating age from birthdate for player {player_id}: {e}")
        
        # Fallback to known ages
        if player_id in self.known_player_ages:
            print(f"DEBUG: Using known age {self.known_player_ages[player_id]} for player_id {player_id}")
            return self.known_player_ages[player_id]
        
        # Default fallback age
        print(f"DEBUG: Using default age 25 for player_id {player_id}")
        return 25
    
    
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

    def build_player_vector(self, stats_df: pd.DataFrame, season_stats: Dict = None, player_id: int = None) -> Dict[str, float]:
        """
        Build a player vector from game log statistics.
        
        Args:
            stats_df: DataFrame containing game log data (multiple rows, one per game)
            season_stats: Dictionary containing season averages and player info
            
        Returns:
            Dictionary containing computed player metrics and placeholders
        """
        if stats_df.empty:
            return {}
        
        # Calculate season averages from game log data
        player_vector = {}
        
        # Three-point rate (from season averages)
        total_fga = stats_df['FGA'].sum() if 'FGA' in stats_df.columns else 0
        total_fg3a = stats_df['FG3A'].sum() if 'FG3A' in stats_df.columns else 0
        if total_fga > 0:
            player_vector['three_rate'] = total_fg3a / total_fga
        else:
            player_vector['three_rate'] = 0.0
        
        # Free throw rate (from season averages)
        total_fta = stats_df['FTA'].sum() if 'FTA' in stats_df.columns else 0
        if total_fga > 0:
            player_vector['ft_rate'] = total_fta / total_fga
        else:
            player_vector['ft_rate'] = 0.0
        
        # Assist percentage (from season averages)
        avg_ast = stats_df['AST'].mean() if 'AST' in stats_df.columns else 0
        player_vector['ast_pct'] = avg_ast * 5
        
        # Turnover percentage (from season averages)
        avg_tov = stats_df['TOV'].mean() if 'TOV' in stats_df.columns else 0
        player_vector['tov_pct'] = avg_tov * 3
        
        # Steal percentage (from season averages)
        avg_stl = stats_df['STL'].mean() if 'STL' in stats_df.columns else 0
        player_vector['stl_pct'] = avg_stl * 2
        
        # Block percentage (from season averages)
        avg_blk = stats_df['BLK'].mean() if 'BLK' in stats_df.columns else 0
        player_vector['blk_pct'] = avg_blk * 2.5
        
        # Defensive rebound percentage (from season averages)
        if 'DREB' in stats_df.columns:
            avg_dreb = stats_df['DREB'].mean()
            player_vector['dreb_pct'] = avg_dreb * 3
        elif 'REB' in stats_df.columns:
            avg_reb = stats_df['REB'].mean()
            player_vector['dreb_pct'] = avg_reb * 3
        else:
            player_vector['dreb_pct'] = 0.0
        
        # Placeholder metrics (to be replaced with real data later)
        player_vector['catch_shoot'] = 0.30
        player_vector['pullup'] = 0.15
        player_vector['rim_rate'] = 0.25
        player_vector['switchability'] = 0.5
        player_vector['rim_protect'] = 0.3
        
        # Bio data (use from season stats if available, otherwise placeholders)
        if player_id is None:
            player_id = stats_df.iloc[0].get('PLAYER_ID', 0) if not stats_df.empty else 0
        print(f"DEBUG: Building player vector for player_id: {player_id}")
        
        # Get age from season stats or fallback
        real_age = self.get_player_age(player_id, season_stats)
        print(f"DEBUG: Retrieved age {real_age} for player_id {player_id}")
        
        player_vector['age'] = real_age
        
        # Get height and weight from season stats
        if season_stats:
            # Use parsed height if available, otherwise parse it
            if 'height_inches' in season_stats:
                player_vector['height_in'] = season_stats['height_inches']
            else:
                # Fallback: parse height from string format
                height_str = season_stats.get('height', '6-6')
                player_vector['height_in'] = self._parse_height_to_inches(height_str)
            
            # Parse weight from string to int
            weight_str = season_stats.get('weight', '215')
            try:
                player_vector['weight_lb'] = int(weight_str)
            except (ValueError, TypeError):
                player_vector['weight_lb'] = 215
        else:
            player_vector['height_in'] = 78
            player_vector['weight_lb'] = 215
        
        # Add PLAYER_ID for redundancy calculation
        player_vector['PLAYER_ID'] = player_id
        
        # Get position from season stats or fallback
        if season_stats and 'position' in season_stats:
            position = season_stats['position']
            player_vector['POSITION'] = position
            print(f"DEBUG: Retrieved position '{position}' from season stats for player_id {player_id}")
        else:
            # Fallback to known positions for well-known players
            known_positions = {
                201935: 'PG',  # Stephen Curry
                2544: 'SF',    # LeBron James
                203081: 'PG',  # Luka Doncic
                201142: 'SF',  # Kevin Durant
                203999: 'SF',  # Jayson Tatum
                203507: 'PF',  # Giannis Antetokounmpo
                201980: 'PG',  # James Harden
                202681: 'PG',  # Kyrie Irving
                203954: 'C',   # Joel Embiid
            }
            position = known_positions.get(player_id, 'SF')  # Default to SF
            player_vector['POSITION'] = position
            print(f"DEBUG: Using fallback position '{position}' for player_id {player_id}")
        
        return player_vector

    def build_custom_vector(self, inputs: Dict[str, Any]) -> Dict[str, float]:
        """
        Build a player vector from manual input values.
        
        Args:
            inputs: Dictionary containing manual input values with keys like:
                   - FGA, FG3A, FTA, AST, TOV, STL, BLK, REB, DREB
                   - AGE, HEIGHT_IN, WEIGHT_LB
                   - Any other per-game stat keys
                   
        Returns:
            Dictionary containing computed player metrics and placeholders
        """
        # Compute derived metrics
        player_vector = {}
        
        # Three-point rate
        fga = inputs.get('FGA', 0)
        fg3a = inputs.get('FG3A', 0)
        if fga > 0:
            player_vector['three_rate'] = fg3a / fga
        else:
            player_vector['three_rate'] = 0.0
        
        # Free throw rate
        fta = inputs.get('FTA', 0)
        if fga > 0:
            player_vector['ft_rate'] = fta / fga
        else:
            player_vector['ft_rate'] = 0.0
        
        # Assist percentage (rough proxy)
        ast = inputs.get('AST', 0)
        player_vector['ast_pct'] = ast * 5
        
        # Turnover percentage (rough proxy)
        tov = inputs.get('TOV', 0)
        player_vector['tov_pct'] = tov * 3
        
        # Steal percentage
        stl = inputs.get('STL', 0)
        player_vector['stl_pct'] = stl * 2
        
        # Block percentage
        blk = inputs.get('BLK', 0)
        player_vector['blk_pct'] = blk * 2.5
        
        # Defensive rebound percentage (fallback to total rebounds)
        dreb = inputs.get('DREB', None)
        if dreb is not None:
            player_vector['dreb_pct'] = dreb * 3
        else:
            reb = inputs.get('REB', 0)
            player_vector['dreb_pct'] = reb * 3
        
        # Placeholder metrics (to be replaced with real data later)
        player_vector['catch_shoot'] = 0.30
        player_vector['pullup'] = 0.15
        player_vector['rim_rate'] = 0.25
        player_vector['switchability'] = 0.5
        player_vector['rim_protect'] = 0.3
        
        # Bio data (use from inputs if available, otherwise placeholders)
        player_vector['age'] = inputs.get('AGE', 26)
        player_vector['height_in'] = inputs.get('HEIGHT_IN', 78)
        player_vector['weight_lb'] = inputs.get('WEIGHT_LB', 215)
        
        # Add PLAYER_ID for custom players (use a unique negative ID)
        player_vector['PLAYER_ID'] = inputs.get('PLAYER_ID', -999)  # Custom player ID
        
        # Add position for custom players (if provided)
        player_vector['POSITION'] = inputs.get('POSITION', None)
        
        return player_vector
