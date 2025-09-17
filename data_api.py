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

def clear_player_cache(player_id: int = None, season: str = None):
    """
    Clear cached player data from session state.
    
    Args:
        player_id: Specific player ID to clear (None for all)
        season: Specific season to clear (None for all)
    """
    if player_id is not None and season is not None:
        key = f"player_{player_id}_{season}"
        if key in st.session_state:
            del st.session_state[key]
    else:
        # Clear all player cache keys
        keys_to_remove = [key for key in st.session_state.keys() if key.startswith("player_")]
        for key in keys_to_remove:
            del st.session_state[key]
