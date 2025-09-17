"""
NBA Data API Layer

This module provides a clean interface to the NBA API with proper caching
and error handling for the Streamlit app.
"""

import time
import streamlit as st
import pandas as pd
from nba_api.stats.endpoints import commonallplayers, playergamelog

DEFAULT_SEASON = "2024-25"

@st.cache_data(ttl=86400)  # 24h cache
def get_active_players_df():
    """
    Get list of active NBA players for the current season.
    
    Returns:
        pd.DataFrame: DataFrame with columns 'player_id' and 'name'
    """
    try:
        df = commonallplayers.CommonAllPlayers(is_only_current_season=1).get_data_frames()[0]
        return df[["PERSON_ID", "DISPLAY_FIRST_LAST"]].rename(
            columns={"PERSON_ID": "player_id", "DISPLAY_FIRST_LAST": "name"}
        )
    except Exception as e:
        st.error(f"Failed to fetch active players: {str(e)}")
        return pd.DataFrame(columns=["player_id", "name"])

@st.cache_data(ttl=900)  # 15 min cache per player/season
def fetch_player_gamelog(player_id: int, season: str = DEFAULT_SEASON) -> pd.DataFrame:
    """
    Fetch player game log data with retry logic and caching.
    
    Args:
        player_id: NBA player ID
        season: NBA season (e.g., "2024-25")
        
    Returns:
        pd.DataFrame: Player game log data
        
    Raises:
        RuntimeError: If API fails after 3 retries
    """
    # retry wrapper to tolerate transient issues
    last_err = None
    for i in range(3):
        try:
            # nba_api sets headers for stats.nba.com internally
            log = playergamelog.PlayerGameLog(player_id=player_id, season=season, timeout=30)
            dfs = log.get_data_frames()
            if dfs and len(dfs[0]) > 0:
                return dfs[0]
            else:
                # return empty but valid DF to avoid crashes
                return pd.DataFrame()
        except Exception as e:
            last_err = e
            if i < 2:  # Don't sleep on last attempt
                time.sleep(0.3)
    
    raise RuntimeError(f"NBA API failed after 3 tries for {player_id} {season}: {last_err}")

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
    # keep a copy in session so sliders don't trigger new cache keys
    key = f"player_{player_id}_{season}"
    if key not in st.session_state:
        with st.spinner(f"Loading game log for player {player_id} in {season}..."):
            try:
                st.session_state[key] = fetch_player_gamelog(player_id, season)
            except RuntimeError as e:
                st.error(str(e))
                st.session_state[key] = pd.DataFrame()
    
    return st.session_state[key]

@st.cache_data(ttl=3600)  # 1 hour cache for player info
def get_player_info(player_id: int) -> dict:
    """
    Get player biographical information from NBA API.
    
    Args:
        player_id: NBA player ID
        
    Returns:
        dict: Player info including position, height, weight, etc.
    """
    try:
        from nba_api.stats.endpoints import commonplayerinfo
        player_info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
        info_df = player_info.get_data_frames()[0]
        
        if not info_df.empty:
            row = info_df.iloc[0]
            return {
                'position': row.get('POSITION', 'Unknown'),
                'height': row.get('HEIGHT', 'Unknown'),
                'weight': row.get('WEIGHT', 'Unknown'),
                'age': row.get('AGE', 0),
                'team': row.get('TEAM_NAME', 'Unknown'),
                'jersey': row.get('JERSEY', 'Unknown')
            }
        else:
            return {
                'position': 'Unknown',
                'height': 'Unknown', 
                'weight': 'Unknown',
                'age': 0,
                'team': 'Unknown',
                'jersey': 'Unknown'
            }
    except Exception as e:
        print(f"Error fetching player info for {player_id}: {e}")
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

