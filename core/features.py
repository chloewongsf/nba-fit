"""
Feature engineering module for NBA Fit analysis.
Contains functions to create and process features from player and team data.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from datetime import date, datetime
from nba_api.stats.endpoints import commonplayerinfo


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
            2544: 40,    # LeBron James
            203081: 25,  # Luka Doncic
            201142: 35,  # Kevin Durant
            1629029: 26, # Zion Williamson
            203999: 26,  # Jayson Tatum
            201566: 35,  # Russell Westbrook
            201939: 35,  # Stephen Curry (alternative ID)
            203507: 30,  # Giannis Antetokounmpo
            201980: 34,  # James Harden
            202681: 33,  # Kyrie Irving
            203954: 29,  # Joel Embiid
            201935: 36,  # Stephen Curry (primary ID)
            203999: 26,  # Jayson Tatum
            1629029: 26, # Zion Williamson
            203507: 30,  # Giannis Antetokounmpo
            201142: 35,  # Kevin Durant
            2544: 40,    # LeBron James
            203081: 25,  # Luka Doncic
        }
    
    def get_player_age(self, player_id: int) -> int:
        """
        Get the real age of a player by fetching their birth date from NBA API.
        
        Args:
            player_id: NBA player ID
            
        Returns:
            Player's current age in years
        """
        try:
            print(f"DEBUG: Fetching age for player ID: {player_id}")
            
            # Get player info from NBA API with timeout
            import time
            start_time = time.time()
            info = commonplayerinfo.CommonPlayerInfo(player_id=player_id).get_normalized_dict()
            end_time = time.time()
            print(f"DEBUG: API call took {end_time - start_time:.2f} seconds")
            
            print(f"DEBUG: API response keys: {list(info.keys())}")
            
            # Extract birth date from the response
            if 'CommonPlayerInfo' in info and len(info['CommonPlayerInfo']) > 0:
                player_info = info['CommonPlayerInfo'][0]
                print(f"DEBUG: Player info keys: {list(player_info.keys())}")
                
                dob_str = player_info.get('BIRTHDATE', '')
                print(f"DEBUG: Raw DOB string: '{dob_str}'")
                
                if dob_str:
                    # Parse the birth date
                    # Handle different date formats
                    if 'T' in dob_str:
                        # Format: '1988-03-14T00:00:00'
                        dob = datetime.strptime(dob_str.split('T')[0], "%Y-%m-%d").date()
                    else:
                        # Format: '03/14/1988'
                        dob = datetime.strptime(dob_str, "%m/%d/%Y").date()
                    
                    # Calculate current age
                    today = date.today()
                    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                    
                    print(f"DEBUG: Player {player_id} DOB: {dob_str} Age: {age}")
                    
                    return age
                else:
                    print(f"DEBUG: No BIRTHDATE found for player {player_id}")
                    return 26
            else:
                print(f"DEBUG: No CommonPlayerInfo found for player {player_id}")
                return 26
            
        except Exception as e:
            print(f"DEBUG: Error fetching age for player {player_id}: {e}")
            import traceback
            traceback.print_exc()
            
            # Try fallback dictionary for well-known players
            if player_id in self.known_player_ages:
                fallback_age = self.known_player_ages[player_id]
                print(f"DEBUG: Using fallback age {fallback_age} for player {player_id}")
                return fallback_age
            
            # Last resort: simulated age based on player ID
            simulated_age = 20 + (player_id % 20)  # Age range: 20-39
            print(f"DEBUG: Using simulated age {simulated_age} for player {player_id} (last resort)")
            return simulated_age
    
    def test_nba_api(self, player_id: int = 201935) -> bool:
        """
        Test if NBA API is accessible by trying to fetch a known player (Stephen Curry).
        
        Args:
            player_id: Player ID to test with (default: Stephen Curry)
            
        Returns:
            True if API is accessible, False otherwise
        """
        try:
            print(f"DEBUG: Testing NBA API with player ID: {player_id}")
            info = commonplayerinfo.CommonPlayerInfo(player_id=player_id).get_normalized_dict()
            print(f"DEBUG: API test successful, response keys: {list(info.keys())}")
            return True
        except Exception as e:
            print(f"DEBUG: NBA API test failed: {e}")
            return False
    
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

    def build_player_vector(self, stats_df: pd.DataFrame) -> Dict[str, float]:
        """
        Build a player vector from per-game statistics.
        
        Args:
            stats_df: DataFrame containing a single row of per-game stats (TOT or single-team)
            
        Returns:
            Dictionary containing computed player metrics and placeholders
        """
        if stats_df.empty:
            return {}
        
        # Get the first (and only) row
        row = stats_df.iloc[0]
        
        # Compute derived metrics
        player_vector = {}
        
        # Three-point rate
        fga = row.get('FGA', 0)
        fg3a = row.get('FG3A', 0)
        if fga > 0:
            player_vector['three_rate'] = fg3a / fga
        else:
            player_vector['three_rate'] = 0.0
        
        # Free throw rate
        fta = row.get('FTA', 0)
        if fga > 0:
            player_vector['ft_rate'] = fta / fga
        else:
            player_vector['ft_rate'] = 0.0
        
        # Assist percentage (rough proxy)
        ast = row.get('AST', 0)
        player_vector['ast_pct'] = ast * 5
        
        # Turnover percentage (rough proxy)
        tov = row.get('TOV', 0)
        player_vector['tov_pct'] = tov * 3
        
        # Steal percentage
        stl = row.get('STL', 0)
        player_vector['stl_pct'] = stl * 2
        
        # Block percentage
        blk = row.get('BLK', 0)
        player_vector['blk_pct'] = blk * 2.5
        
        # Defensive rebound percentage (fallback to total rebounds)
        dreb = row.get('DREB', None)
        if dreb is not None:
            player_vector['dreb_pct'] = dreb * 3
        else:
            reb = row.get('REB', 0)
            player_vector['dreb_pct'] = reb * 3
        
        # Placeholder metrics (to be replaced with real data later)
        player_vector['catch_shoot'] = 0.30
        player_vector['pullup'] = 0.15
        player_vector['rim_rate'] = 0.25
        player_vector['switchability'] = 0.5
        player_vector['rim_protect'] = 0.3
        
        # Bio data (use from stats if available, otherwise placeholders)
        # Get real age from NBA API using player's birth date
        player_id = row.get('PLAYER_ID', 0)
        print(f"DEBUG: Building player vector for player_id: {player_id}")
        
        # Test API first
        if not hasattr(self, '_api_tested'):
            self._api_tested = True
            api_works = self.test_nba_api()
            print(f"DEBUG: NBA API test result: {api_works}")
        
        real_age = self.get_player_age(player_id)
        print(f"DEBUG: Retrieved age {real_age} for player_id {player_id}")
        
        player_vector['age'] = real_age
        player_vector['height_in'] = row.get('HEIGHT_IN', 78)
        player_vector['weight_lb'] = row.get('WEIGHT_LB', 215)
        
        # Add PLAYER_ID for redundancy calculation
        player_vector['PLAYER_ID'] = player_id
        
        # Get position from NBA API
        try:
            player_info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
            info_df = player_info.get_data_frames()[0]
            if not info_df.empty:
                position = info_df.iloc[0].get('POSITION', '')
                player_vector['POSITION'] = position
                print(f"DEBUG: Retrieved position '{position}' for player_id {player_id}")
            else:
                player_vector['POSITION'] = None
                print(f"DEBUG: No position data found for player_id {player_id}")
        except Exception as e:
            player_vector['POSITION'] = None
            print(f"DEBUG: Error fetching position for player_id {player_id}: {e}")
        
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
