"""
Configuration settings for NBA Fit app.

This module contains configuration settings for data sources and URLs.
"""

import os

# GitHub Pages base URL for data files
# Change this to your GitHub Pages URL
DEFAULT_BASE_DATA_URL = "https://chloewongsf.github.io/nba-fit-data/"

# Get base URL from environment variable or use default
BASE_DATA_URL = os.getenv('NBA_DATA_BASE_URL', DEFAULT_BASE_DATA_URL)

# Ensure URL ends with slash
if not BASE_DATA_URL.endswith('/'):
    BASE_DATA_URL += '/'

# Data file paths
DATA_PATHS = {
    'active_players': 'active_players.json',
    'player_gamelog': 'players/{player_id}_gamelog.json',
    'player_info': 'players/{player_id}_info.json',
    'player_season_stats': 'players/{player_id}_season_stats.json'
}

def get_data_url(data_type: str, **kwargs) -> str:
    """
    Get the full URL for a data file.
    
    Args:
        data_type: Type of data file (key from DATA_PATHS)
        **kwargs: Format parameters for the path (e.g., player_id)
        
    Returns:
        str: Full URL to the data file
    """
    if data_type not in DATA_PATHS:
        raise ValueError(f"Unknown data type: {data_type}")
    
    path_template = DATA_PATHS[data_type]
    path = path_template.format(**kwargs)
    
    return BASE_DATA_URL + path

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Cache settings
CACHE_TTL = {
    'active_players': 86400,  # 24 hours
    'player_gamelog': 900,    # 15 minutes
    'player_info': 3600,      # 1 hour
    'player_season_stats': 900  # 15 minutes
}
