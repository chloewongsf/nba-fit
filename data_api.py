"""
NBA Data API Layer

This module provides a clean interface to load NBA data from JSON files
hosted on GitHub Pages, with proper caching for the Streamlit app.
"""

import time
import logging
import streamlit as st
import pandas as pd
import requests
from typing import Dict, Optional
from config import get_data_url, CACHE_TTL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_SEASON = "2024-25"

def load_json(url: str) -> Dict:
    """
    Load JSON data from a URL.
    
    Args:
        url: URL to fetch JSON from
        
    Returns:
        Dict: JSON data
        
    Raises:
        requests.RequestException: If the request fails
    """
    try:
        logger.debug(f"Fetching JSON from: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch JSON from {url}: {e}")
        raise

@st.cache_data(ttl=CACHE_TTL['active_players'])
def get_active_players_df():
    """
    Get list of active NBA players from JSON file.
    
    Returns:
        pd.DataFrame: DataFrame with columns 'player_id' and 'name'
    """
    try:
        url = get_data_url('active_players')
        data = load_json(url)
        
        if 'players' in data:
            players = data['players']
            df = pd.DataFrame(players)
            logger.info(f"✅ Loaded {len(df)} active players from JSON")
            return df
        else:
            logger.warning("No 'players' key in JSON data")
            return pd.DataFrame(columns=['player_id', 'name'])
            
    except Exception as e:
        logger.error(f"Failed to fetch active players: {e}")
        st.error(f"Failed to load active players: {str(e)}")
        return pd.DataFrame(columns=['player_id', 'name'])

@st.cache_data(ttl=CACHE_TTL['player_gamelog'])
def fetch_player_gamelog(player_id: int, season: str = DEFAULT_SEASON) -> pd.DataFrame:
    """
    Fetch player game log data from JSON file.
    
    Args:
        player_id: NBA player ID
        season: NBA season (e.g., "2024-25")
        
    Returns:
        pd.DataFrame: Player game log data
        
    Raises:
        RuntimeError: If JSON file not found or invalid
    """
    try:
        url = get_data_url('player_gamelog', player_id=player_id)
        data = load_json(url)
        
        if 'games' in data:
            games = data['games']
            df = pd.DataFrame(games)
            logger.info(f"✅ Loaded {len(df)} games for player {player_id}")
            return df
        else:
            logger.warning(f"No 'games' key in JSON data for player {player_id}")
            return pd.DataFrame()
            
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            logger.warning(f"No game log data found for player {player_id}")
            return pd.DataFrame()
        else:
            raise
    except Exception as e:
        logger.error(f"Failed to fetch game log for player {player_id}: {e}")
        raise RuntimeError(f"Failed to load game log for player {player_id}: {e}")

def get_player_df(player_id: int, season: str = DEFAULT_SEASON) -> pd.DataFrame:
    """
    Get player game log data with session state caching to prevent refetches
    on slider changes.
    
    Args:
        player_id: NBA player ID
        season: NBA season (e.g., "2024-25")
        
    Returns:
        pd.DataFrame: Player game log data
    """
    key = f"player_{player_id}_{season}"
    if key not in st.session_state:
        with st.spinner(f"Loading game log for player {player_id} in {season}..."):
            try:
                st.session_state[key] = fetch_player_gamelog(player_id, season)
            except RuntimeError as e:
                st.error(str(e))
                st.session_state[key] = pd.DataFrame()
    
    return st.session_state[key]

def _parse_height_to_inches(height_str: str) -> int:
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

@st.cache_data(ttl=CACHE_TTL['player_info'])
def get_player_info(player_id: int) -> dict:
    """
    Get player biographical information from JSON file.
    
    Args:
        player_id: NBA player ID
        
    Returns:
        dict: Player info including position, height, weight, etc.
    """
    try:
        url = get_data_url('player_info', player_id=player_id)
        data = load_json(url)
        
        if 'player_info' in data:
            info = data['player_info']
            
            # Parse height to inches if it's in string format
            if 'height' in info and isinstance(info['height'], str):
                info['height_inches'] = _parse_height_to_inches(info['height'])
            
            logger.info(f"✅ Loaded player info for {player_id}")
            return info
        else:
            logger.warning(f"No 'player_info' key in JSON data for player {player_id}")
            return _get_default_player_info()
            
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            logger.warning(f"No player info found for player {player_id}")
            return _get_default_player_info()
        else:
            raise
    except Exception as e:
        logger.error(f"Failed to fetch player info for {player_id}: {e}")
        return _get_default_player_info()

def _get_default_player_info() -> dict:
    """Get default player info when JSON file not found."""
    return {
        'position': 'Unknown',
        'height': 'Unknown',
        'weight': 'Unknown',
        'age': 0,
        'team': 'Unknown',
        'jersey': 'Unknown'
    }

def get_player_season_stats(player_id: int, season: str = DEFAULT_SEASON) -> dict:
    """
    Get player season averages from game log data.
    
    Args:
        player_id: NBA player ID
        season: NBA season (e.g., "2024-25")
        
    Returns:
        dict: Season averages and totals
    """
    game_log_df = get_player_df(player_id, season)
    
    if game_log_df.empty:
        return {}
    
    # Calculate season averages
    numeric_cols = ['MIN', 'FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA', 
                   'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'PLUS_MINUS']
    
    season_stats = {}
    
    # Calculate averages for numeric columns
    for col in numeric_cols:
        if col in game_log_df.columns:
            season_stats[f'{col}_avg'] = game_log_df[col].mean()
            season_stats[f'{col}_total'] = game_log_df[col].sum()
    
    # Calculate percentages
    if 'FGA' in game_log_df.columns and 'FGM' in game_log_df.columns:
        total_fga = game_log_df['FGA'].sum()
        total_fgm = game_log_df['FGM'].sum()
        season_stats['FG_PCT'] = total_fgm / total_fga if total_fga > 0 else 0
    
    if 'FG3A' in game_log_df.columns and 'FG3M' in game_log_df.columns:
        total_fg3a = game_log_df['FG3A'].sum()
        total_fg3m = game_log_df['FG3M'].sum()
        season_stats['FG3_PCT'] = total_fg3m / total_fg3a if total_fg3a > 0 else 0
    
    if 'FTA' in game_log_df.columns and 'FTM' in game_log_df.columns:
        total_fta = game_log_df['FTA'].sum()
        total_ftm = game_log_df['FTM'].sum()
        season_stats['FT_PCT'] = total_ftm / total_fta if total_fta > 0 else 0
    
    # Add game count
    season_stats['games_played'] = len(game_log_df)
    
    # Add player info
    player_info = get_player_info(player_id)
    season_stats.update(player_info)
    
    return season_stats

def get_player_season_averages_df(player_id: int, season: str = DEFAULT_SEASON) -> pd.DataFrame:
    """
    Get player season averages as a DataFrame for display.
    
    Args:
        player_id: NBA player ID
        season: NBA season (e.g., "2024-25")
        
    Returns:
        pd.DataFrame: Season averages in a format suitable for display
    """
    season_stats = get_player_season_stats(player_id, season)
    
    if not season_stats:
        return pd.DataFrame()
    
    # Create a DataFrame with season averages
    averages_data = {
        'MIN': [season_stats.get('MIN_avg', 0)],
        'FGM': [season_stats.get('FGM_avg', 0)],
        'FGA': [season_stats.get('FGA_avg', 0)],
        'FG_PCT': [season_stats.get('FG_PCT', 0)],
        'FG3M': [season_stats.get('FG3M_avg', 0)],
        'FG3A': [season_stats.get('FG3A_avg', 0)],
        'FG3_PCT': [season_stats.get('FG3_PCT', 0)],
        'FTM': [season_stats.get('FTM_avg', 0)],
        'FTA': [season_stats.get('FTA_avg', 0)],
        'FT_PCT': [season_stats.get('FT_PCT', 0)],
        'OREB': [season_stats.get('OREB_avg', 0)],
        'DREB': [season_stats.get('DREB_avg', 0)],
        'REB': [season_stats.get('REB_avg', 0)],
        'AST': [season_stats.get('AST_avg', 0)],
        'STL': [season_stats.get('STL_avg', 0)],
        'BLK': [season_stats.get('BLK_avg', 0)],
        'TOV': [season_stats.get('TOV_avg', 0)],
        'PF': [season_stats.get('PF_avg', 0)],
        'PTS': [season_stats.get('PTS_avg', 0)],
        'PLUS_MINUS': [season_stats.get('PLUS_MINUS_avg', 0)]
    }
    
    df = pd.DataFrame(averages_data)
    
    # Round to appropriate decimal places
    df = df.round({
        'MIN': 1,
        'FGM': 1,
        'FGA': 1,
        'FG_PCT': 3,
        'FG3M': 1,
        'FG3A': 1,
        'FG3_PCT': 3,
        'FTM': 1,
        'FTA': 1,
        'FT_PCT': 3,
        'OREB': 1,
        'DREB': 1,
        'REB': 1,
        'AST': 1,
        'STL': 1,
        'BLK': 1,
        'TOV': 1,
        'PF': 1,
        'PTS': 1,
        'PLUS_MINUS': 1
    })
    
    return df

def get_data_status() -> Dict:
    """
    Get current data source status and configuration.
    
    Returns:
        dict: Data source status information
    """
    from config import BASE_DATA_URL
    
    return {
        'data_source': 'GitHub Pages JSON',
        'base_url': BASE_DATA_URL,
        'cache_enabled': True,
        'cache_ttl': CACHE_TTL
    }