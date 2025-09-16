"""
NBA API client module for fetching player and team data.
This is a stub implementation that will be replaced with actual NBA API integration.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
import time
import random
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats
import sys
import os

# Add parent directory to path to import cache_manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cache_manager import CacheManager


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
        Get a DataFrame of active NBA players using the NBA API with caching.
        
        Returns:
            DataFrame with columns 'id' and 'full_name' for active players
        """
        # Try to get from cache first
        cached_players = self.cache_manager.get_cached_players()
        if cached_players is not None:
            return cached_players
        
        try:
            # Add timeout and retry logic for Streamlit Cloud
            import time
            time.sleep(0.1)  # Small delay to avoid rate limits
            
            print("🔍 Fetching active players from NBA API...")
            # Get all players from NBA API
            all_players = players.get_players()
            
            # Convert to DataFrame
            players_df = pd.DataFrame(all_players)
            
            # Filter for active players (is_active = True)
            active_players = players_df[players_df['is_active'] == True]
            
            # Select only id and full_name columns
            result_df = active_players[['id', 'full_name']].copy()
            
            # Reset index
            result_df = result_df.reset_index(drop=True)
            
            # Cache the result
            self.cache_manager.cache_players(result_df)
            
            print(f"✅ Successfully fetched {len(result_df)} active players from API")
            return result_df
            
        except Exception as e:
            # Fallback to cached data or fallback list if API call fails
            print(f"❌ Error fetching active players from API: {e}")
            
            # Try to get from cache even if expired
            cached_players = self.cache_manager.get_cached_players()
            if cached_players is not None:
                print("✅ Using expired cache data")
                return cached_players
            
            # Use fallback list
            print("✅ Using fallback player list")
            return self.cache_manager.get_fallback_players()

    def get_player_per_game(self, player_id: int, season: str, include_splits: bool = False) -> pd.DataFrame:
        """
        Get player per-game statistics for a specific season using the NBA API with caching.
        
        Args:
            player_id: NBA player ID
            season: NBA season (e.g., "2023-24")
            include_splits: If True, return all rows (team splits + TOT). If False, return only TOT row or single row.
            
        Returns:
            DataFrame with per-game statistics for the given season.
            If no rows match the season, returns data for the most recent season.
            By default, returns only the TOT row if present, otherwise the single row.
        """
        # Try to get from cache first
        cached_stats = self.cache_manager.get_cached_player_stats(player_id, season)
        if cached_stats is not None:
            return cached_stats
        
        try:
            # Add small delay to avoid rate limits on Streamlit Cloud
            import time
            time.sleep(0.2)
            
            print(f"🔍 Fetching stats for player {player_id} from NBA API...")
            # Get player career stats
            career_stats = playercareerstats.PlayerCareerStats(
                player_id=player_id,
                per_mode36="PerGame"
            )
            
            # Get the data
            career_data = career_stats.get_data_frames()[0]  # First DataFrame contains season stats
            
            if career_data.empty:
                print(f"No career data found for player {player_id}")
                # Try fallback stats
                fallback_stats = self.cache_manager.get_fallback_player_stats(player_id, season)
                if fallback_stats is not None:
                    return fallback_stats
                return pd.DataFrame()
            
            # Filter for the requested season
            season_data = career_data[career_data['SEASON_ID'] == season]
            
            # If no data for the requested season, get the most recent season
            if season_data.empty:
                # Sort by season and get the most recent
                career_data_sorted = career_data.sort_values('SEASON_ID', ascending=False)
                season_data = career_data_sorted.iloc[:1]  # Get the most recent season
                
                if not season_data.empty:
                    print(f"No data found for season {season}. Using most recent season: {season_data['SEASON_ID'].iloc[0]}")
            
            # Handle TOT row logic
            if include_splits:
                # Return all rows (team splits + TOT if present)
                result = season_data.reset_index(drop=True)
            else:
                # Check if there's a TOT row
                tot_row = season_data[season_data['TEAM_ABBREVIATION'] == 'TOT']
                
                if not tot_row.empty:
                    # Return just the TOT row
                    result = tot_row.reset_index(drop=True)
                else:
                    # Return the single row (or first row if multiple)
                    result = season_data.iloc[:1].reset_index(drop=True)
            
            # Cache the result
            self.cache_manager.cache_player_stats(player_id, season, result)
            
            print(f"✅ Successfully fetched stats for player {player_id} from API")
            return result
            
        except Exception as e:
            print(f"❌ Error fetching player per-game stats for player {player_id}: {e}")
            
            # Try to get from cache even if expired
            cached_stats = self.cache_manager.get_cached_player_stats(player_id, season)
            if cached_stats is not None:
                print("✅ Using expired cache data")
                return cached_stats
            
            # Try fallback stats
            fallback_stats = self.cache_manager.get_fallback_player_stats(player_id, season)
            if fallback_stats is not None:
                print("✅ Using fallback stats")
                return fallback_stats
            
            # Return empty DataFrame with expected columns for graceful handling
            print("⚠️ No data available, returning empty DataFrame")
            return pd.DataFrame(columns=['PLAYER_ID', 'SEASON_ID', 'TEAM_ABBREVIATION', 'PTS', 'REB', 'AST', 'FG_PCT', 'FG3_PCT', 'FT_PCT'])

    def validate_api_connection(self) -> bool:
        """
        Validate connection to NBA API.
        
        Returns:
            True if connection is successful, False otherwise
        """
        # Placeholder implementation
        # In real implementation, would make a test API call
        return True
