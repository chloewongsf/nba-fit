"""
NBA API client module for fetching player and team data.
This is a stub implementation that will be replaced with actual NBA API integration.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
import time
import random
import sys
import os

# Add parent directory to path to import cache_manager and fallback_data_manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cache_manager import CacheManager
from fallback_data_manager import FallbackDataManager


class NBAClient:
    """
    NBA API client for fetching player and team statistics.
    Currently contains placeholder implementations.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the NBA client.
        
        Args:
            api_key: Optional API key for NBA API access
        """
        self.api_key = api_key
        self.base_url = "https://stats.nba.com/stats/"
        self.headers = {
            'User-Agent': 'NBA-Fit-App/1.0',
            'Accept': 'application/json'
        }
        self.cache_manager = CacheManager()
        self.fallback_manager = FallbackDataManager()
    
    def get_player_stats(self, player_name: str, season: str = "2023-24") -> Dict[str, Any]:
        """
        Get player statistics for a given player.
        
        Args:
            player_name: Name of the player
            season: NBA season (e.g., "2023-24")
            
        Returns:
            Dictionary containing player statistics
        """
        # Placeholder implementation - returns mock data
        # In real implementation, would call NBA API
        
        # Simulate API delay
        time.sleep(0.5)
        
        # Generate mock player data based on name
        mock_data = {
            'player_name': player_name,
            'season': season,
            'team': 'LAL',  # Placeholder
            'position': 'SF',
            'games_played': 65,
            'minutes_per_game': 35.2,
            'points_per_game': 25.8,
            'rebounds_per_game': 7.2,
            'assists_per_game': 6.8,
            'steals_per_game': 1.2,
            'blocks_per_game': 0.8,
            'field_goal_percentage': 0.485,
            'three_point_percentage': 0.365,
            'free_throw_percentage': 0.812,
            'player_efficiency_rating': 24.5,
            'true_shooting_percentage': 0.578,
            'usage_rate': 28.3,
            'win_shares': 8.2,
            'box_plus_minus': 5.8,
            'value_over_replacement': 3.2,
            'scoring_need': random.uniform(0.2, 0.8),
            'defense_need': random.uniform(0.2, 0.8),
            'playmaking_need': random.uniform(0.2, 0.8)
        }
        
        return mock_data
    
    def get_team_stats(self, team_name: str, season: str = "2023-24") -> Dict[str, Any]:
        """
        Get team statistics for a given team.
        
        Args:
            team_name: Name of the team
            season: NBA season (e.g., "2023-24")
            
        Returns:
            Dictionary containing team statistics
        """
        # Placeholder implementation - returns mock data
        time.sleep(0.3)
        
        # Team name mapping
        team_mapping = {
            'Lakers': 'LAL',
            'Warriors': 'GSW',
            'Celtics': 'BOS',
            'Heat': 'MIA',
            'Bucks': 'MIL',
            'Nuggets': 'DEN',
            'Suns': 'PHX',
            '76ers': 'PHI'
        }
        
        team_code = team_mapping.get(team_name, 'LAL')
        
        mock_data = {
            'team_name': team_name,
            'team_code': team_code,
            'season': season,
            'wins': 45,
            'losses': 37,
            'win_percentage': 0.549,
            'points_per_game': 115.2,
            'points_allowed_per_game': 112.8,
            'rebounds_per_game': 44.8,
            'assists_per_game': 26.5,
            'steals_per_game': 7.8,
            'blocks_per_game': 5.2,
            'field_goal_percentage': 0.468,
            'three_point_percentage': 0.356,
            'free_throw_percentage': 0.789,
            'pace': 98.5,
            'offensive_rating': 115.8,
            'defensive_rating': 112.3,
            'net_rating': 3.5,
            'scoring_need': random.uniform(0.1, 0.9),
            'defense_need': random.uniform(0.1, 0.9),
            'playmaking_need': random.uniform(0.1, 0.9)
        }
        
        return mock_data
    
    def get_player_list(self, season: str = "2023-24") -> List[Dict[str, Any]]:
        """
        Get list of all NBA players for a season.
        
        Args:
            season: NBA season
            
        Returns:
            List of player dictionaries
        """
        # Placeholder implementation
        mock_players = [
            {'id': 1, 'name': 'LeBron James', 'team': 'LAL', 'position': 'SF'},
            {'id': 2, 'name': 'Stephen Curry', 'team': 'GSW', 'position': 'PG'},
            {'id': 3, 'name': 'Kevin Durant', 'team': 'PHX', 'position': 'SF'},
            {'id': 4, 'name': 'Giannis Antetokounmpo', 'team': 'MIL', 'position': 'PF'},
            {'id': 5, 'name': 'Jayson Tatum', 'team': 'BOS', 'position': 'SF'},
            {'id': 6, 'name': 'Luka Doncic', 'team': 'DAL', 'position': 'PG'},
            {'id': 7, 'name': 'Joel Embiid', 'team': 'PHI', 'position': 'C'},
            {'id': 8, 'name': 'Nikola Jokic', 'team': 'DEN', 'position': 'C'},
        ]
        
        return mock_players
    
    def get_team_list(self) -> List[Dict[str, Any]]:
        """
        Get list of all NBA teams.
        
        Returns:
            List of team dictionaries
        """
        mock_teams = [
            {'id': 1, 'name': 'Lakers', 'code': 'LAL', 'conference': 'West'},
            {'id': 2, 'name': 'Warriors', 'code': 'GSW', 'conference': 'West'},
            {'id': 3, 'name': 'Celtics', 'code': 'BOS', 'conference': 'East'},
            {'id': 4, 'name': 'Heat', 'code': 'MIA', 'conference': 'East'},
            {'id': 5, 'name': 'Bucks', 'code': 'MIL', 'conference': 'East'},
            {'id': 6, 'name': 'Nuggets', 'code': 'DEN', 'conference': 'West'},
            {'id': 7, 'name': 'Suns', 'code': 'PHX', 'conference': 'West'},
            {'id': 8, 'name': '76ers', 'code': 'PHI', 'conference': 'East'},
        ]
        
        return mock_teams
    
    def get_player_comparison(self, player1: str, player2: str, season: str = "2023-24") -> Dict[str, Any]:
        """
        Compare two players' statistics.
        
        Args:
            player1: First player name
            player2: Second player name
            season: NBA season
            
        Returns:
            Dictionary containing comparison data
        """
        player1_stats = self.get_player_stats(player1, season)
        player2_stats = self.get_player_stats(player2, season)
        
        comparison = {
            'player1': player1_stats,
            'player2': player2_stats,
            'comparison_metrics': {
                'points_difference': player1_stats['points_per_game'] - player2_stats['points_per_game'],
                'rebounds_difference': player1_stats['rebounds_per_game'] - player2_stats['rebounds_per_game'],
                'assists_difference': player1_stats['assists_per_game'] - player2_stats['assists_per_game'],
            }
        }
        
        return comparison
    
    def search_players(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for players by name.
        
        Args:
            query: Search query
            
        Returns:
            List of matching players
        """
        all_players = self.get_player_list()
        query_lower = query.lower()
        
        matching_players = [
            player for player in all_players
            if query_lower in player['name'].lower()
        ]
        
        return matching_players
    
    def get_team_roster(self, team_name: str, season: str = "2023-24") -> List[Dict[str, Any]]:
        """
        Get team roster for a given team and season.
        
        Args:
            team_name: Name of the team
            season: NBA season
            
        Returns:
            List of players on the team
        """
        # Placeholder implementation
        team_code = {
            'Lakers': 'LAL',
            'Warriors': 'GSW',
            'Celtics': 'BOS',
            'Heat': 'MIA',
            'Bucks': 'MIL',
            'Nuggets': 'DEN',
            'Suns': 'PHX',
            '76ers': 'PHI'
        }.get(team_name, 'LAL')
        
        # Mock roster data
        mock_roster = [
            {'name': f'Player {i}', 'position': ['PG', 'SG', 'SF', 'PF', 'C'][i % 5], 'team': team_code}
            for i in range(15)
        ]
        
        return mock_roster
    
    def get_active_players(self) -> pd.DataFrame:
        """
        Get a DataFrame of active NBA players from cached CSV files.
        
        Returns:
            DataFrame with columns 'id' and 'full_name' for active players
        """
        import streamlit as st
        
        # Try to get from cache first
        cached_players = self.cache_manager.get_cached_players()
        if cached_players is not None:
            st.write("📁 Loaded active players from cache")
            return cached_players
        
        # Use fallback CSV data
        st.write("📁 Loading active players from fallback CSV")
        return self.fallback_manager.get_fallback_players()

    def get_player_per_game(self, player_id: int, season: str, include_splits: bool = False) -> pd.DataFrame:
        """
        Get player per-game statistics from cached CSV files.
        
        Args:
            player_id: NBA player ID
            season: NBA season (e.g., "2024-25")
            include_splits: If True, return all rows (team splits + TOT). If False, return only TOT row or single row.
            
        Returns:
            DataFrame with per-game statistics for the given season.
        """
        import streamlit as st
        import os
        
        # Try to get from cache first
        cached_stats = self.cache_manager.get_cached_player_stats(player_id, season)
        if cached_stats is not None:
            st.write(f"📁 Loaded stats for player {player_id} from cache")
            return cached_stats
        
        # Try to load from individual player CSV files
        # Support both season formats: 2024-25 and 2024_25
        season_formats = [season, season.replace('-', '_')]
        tried_files = []
        
        for season_format in season_formats:
            csv_path = os.path.join("data", f"{player_id}_{season_format}.csv")
            tried_files.append(csv_path)
            
            if os.path.exists(csv_path):
                try:
                    st.write(f"📁 Loading stats for player {player_id} from CSV: {csv_path}")
                    df = pd.read_csv(csv_path)
                    
                    if not df.empty:
                        # Convert game log data to per-game stats format
                        # Calculate per-game averages from game log data
                        per_game_stats = self._convert_game_log_to_per_game(df, player_id, season)
                        st.write(f"✅ Successfully loaded and converted stats for player {player_id}")
                        return per_game_stats
                    else:
                        st.warning(f"⚠️ Empty CSV file for player {player_id}")
                        
                except Exception as e:
                    st.error(f"❌ Error reading CSV for player {player_id}: {e}")
                    continue
        
        # Try fallback CSV data
        fallback_stats = self.fallback_manager.get_fallback_stats_for_player(player_id, season)
        if fallback_stats is not None:
            st.write(f"📁 Using fallback CSV data for player {player_id}")
            return fallback_stats
        
        # No data available - show which files were tried
        st.warning(f"⚠️ No cached stats available for player {player_id} and season {season}")
        st.warning(f"🔍 Tried files: {', '.join(tried_files)}")
        return pd.DataFrame(columns=['PLAYER_ID', 'SEASON_ID', 'TEAM_ABBREVIATION', 'PTS', 'REB', 'AST', 'FG_PCT', 'FG3_PCT', 'FT_PCT'])
    
    def _convert_game_log_to_per_game(self, game_log_df: pd.DataFrame, player_id: int, season: str) -> pd.DataFrame:
        """
        Convert game log data to per-game statistics format.
        
        Args:
            game_log_df: DataFrame with game log data
            player_id: NBA player ID
            season: NBA season
            
        Returns:
            DataFrame with per-game statistics
        """
        if game_log_df.empty:
            return pd.DataFrame()
        
        # Calculate per-game averages
        per_game_stats = {
            'PLAYER_ID': player_id,
            'SEASON_ID': season,
            'TEAM_ABBREVIATION': game_log_df['MATCHUP'].iloc[0].split(' ')[0] if 'MATCHUP' in game_log_df.columns else 'UNK',
            'PLAYER_AGE': 25,  # Default age
            'GP': len(game_log_df),
            'GS': len(game_log_df),  # Assume all games started
            'MIN': game_log_df['MIN'].mean() if 'MIN' in game_log_df.columns else 0,
            'FGM': game_log_df['FGM'].mean() if 'FGM' in game_log_df.columns else 0,
            'FGA': game_log_df['FGA'].mean() if 'FGA' in game_log_df.columns else 0,
            'FG_PCT': game_log_df['FG_PCT'].mean() if 'FG_PCT' in game_log_df.columns else 0,
            'FG3M': game_log_df['FG3M'].mean() if 'FG3M' in game_log_df.columns else 0,
            'FG3A': game_log_df['FG3A'].mean() if 'FG3A' in game_log_df.columns else 0,
            'FG3_PCT': game_log_df['FG3_PCT'].mean() if 'FG3_PCT' in game_log_df.columns else 0,
            'FTM': game_log_df['FTM'].mean() if 'FTM' in game_log_df.columns else 0,
            'FTA': game_log_df['FTA'].mean() if 'FTA' in game_log_df.columns else 0,
            'FT_PCT': game_log_df['FT_PCT'].mean() if 'FT_PCT' in game_log_df.columns else 0,
            'OREB': game_log_df['OREB'].mean() if 'OREB' in game_log_df.columns else 0,
            'DREB': game_log_df['DREB'].mean() if 'DREB' in game_log_df.columns else 0,
            'REB': game_log_df['REB'].mean() if 'REB' in game_log_df.columns else 0,
            'AST': game_log_df['AST'].mean() if 'AST' in game_log_df.columns else 0,
            'STL': game_log_df['STL'].mean() if 'STL' in game_log_df.columns else 0,
            'BLK': game_log_df['BLK'].mean() if 'BLK' in game_log_df.columns else 0,
            'TOV': game_log_df['TOV'].mean() if 'TOV' in game_log_df.columns else 0,
            'PF': game_log_df['PF'].mean() if 'PF' in game_log_df.columns else 0,
            'PTS': game_log_df['PTS'].mean() if 'PTS' in game_log_df.columns else 0
        }
        
        return pd.DataFrame([per_game_stats])

    def validate_api_connection(self) -> bool:
        """
        Validate connection to NBA API.
        
        Returns:
            True if connection is successful, False otherwise
        """
        # Placeholder implementation
        # In real implementation, would make a test API call
        return True
