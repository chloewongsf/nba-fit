"""
Cache manager for NBA player data to handle API rate limits and failures.
"""

import pandas as pd
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import hashlib


class CacheManager:
    """Manages caching of NBA player data to handle API failures."""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.ensure_cache_dir()
    
    def ensure_cache_dir(self):
        """Ensure cache directory exists."""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _get_cache_key(self, data_type: str, **kwargs) -> str:
        """Generate a cache key for the given parameters."""
        key_string = f"{data_type}_{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str, extension: str = "json") -> str:
        """Get the full path for a cache file."""
        return os.path.join(self.cache_dir, f"{cache_key}.{extension}")
    
    def _is_cache_valid(self, cache_path: str, max_age_hours: int = 24) -> bool:
        """Check if cache file is still valid (not expired)."""
        if not os.path.exists(cache_path):
            return False
        
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        expiry_time = file_time + timedelta(hours=max_age_hours)
        
        return datetime.now() < expiry_time
    
    def get_cached_players(self) -> Optional[pd.DataFrame]:
        """Get cached active players data."""
        cache_key = self._get_cache_key("active_players")
        cache_path = self._get_cache_path(cache_key, "csv")
        
        if self._is_cache_valid(cache_path, max_age_hours=24):
            try:
                df = pd.read_csv(cache_path)
                print(f"✅ Loaded {len(df)} players from cache")
                return df
            except Exception as e:
                print(f"❌ Error loading cached players: {e}")
                return None
        
        return None
    
    def cache_players(self, players_df: pd.DataFrame):
        """Cache active players data."""
        cache_key = self._get_cache_key("active_players")
        cache_path = self._get_cache_path(cache_key, "csv")
        
        try:
            players_df.to_csv(cache_path, index=False)
            print(f"✅ Cached {len(players_df)} players to {cache_path}")
        except Exception as e:
            print(f"❌ Error caching players: {e}")
    
    def get_cached_player_stats(self, player_id: int, season: str) -> Optional[pd.DataFrame]:
        """Get cached player stats data."""
        cache_key = self._get_cache_key("player_stats", player_id=player_id, season=season)
        cache_path = self._get_cache_path(cache_key, "csv")
        
        if self._is_cache_valid(cache_path, max_age_hours=12):
            try:
                df = pd.read_csv(cache_path)
                print(f"✅ Loaded stats for player {player_id} from cache")
                return df
            except Exception as e:
                print(f"❌ Error loading cached stats: {e}")
                return None
        
        return None
    
    def cache_player_stats(self, player_id: int, season: str, stats_df: pd.DataFrame):
        """Cache player stats data."""
        cache_key = self._get_cache_key("player_stats", player_id=player_id, season=season)
        cache_path = self._get_cache_path(cache_key, "csv")
        
        try:
            stats_df.to_csv(cache_path, index=False)
            print(f"✅ Cached stats for player {player_id} to {cache_path}")
        except Exception as e:
            print(f"❌ Error caching player stats: {e}")
    
    def get_fallback_players(self) -> pd.DataFrame:
        """Get a fallback list of popular NBA players when API fails."""
        fallback_players = pd.DataFrame({
            'id': [
                201939,  # Stephen Curry
                203110,  # Draymond Green
                203999,  # Nikola Jokic
                201142,  # Kevin Durant
                201935,  # Damian Lillard
                203507,  # Karl-Anthony Towns
                203954,  # Joel Embiid
                201566,  # Russell Westbrook
                201935,  # Damian Lillard
                202681,  # Giannis Antetokounmpo
                203076,  # Anthony Davis
                201142,  # Kevin Durant
                201939,  # Stephen Curry
                203110,  # Draymond Green
                203999,  # Nikola Jokic
                201935,  # Damian Lillard
                203507,  # Karl-Anthony Towns
                203954,  # Joel Embiid
                201566,  # Russell Westbrook
                202681,  # Giannis Antetokounmpo
            ],
            'full_name': [
                'Stephen Curry',
                'Draymond Green', 
                'Nikola Jokic',
                'Kevin Durant',
                'Damian Lillard',
                'Karl-Anthony Towns',
                'Joel Embiid',
                'Russell Westbrook',
                'Damian Lillard',
                'Giannis Antetokounmpo',
                'Anthony Davis',
                'Kevin Durant',
                'Stephen Curry',
                'Draymond Green',
                'Nikola Jokic',
                'Damian Lillard',
                'Karl-Anthony Towns',
                'Joel Embiid',
                'Russell Westbrook',
                'Giannis Antetokounmpo',
            ]
        })
        
        # Remove duplicates
        fallback_players = fallback_players.drop_duplicates(subset=['id'])
        print(f"✅ Using fallback list with {len(fallback_players)} players")
        return fallback_players
    
    def get_fallback_player_stats(self, player_id: int, season: str) -> Optional[pd.DataFrame]:
        """Get fallback player stats for popular players."""
        # Sample stats for popular players (these would be real data in production)
        fallback_stats = {
            201939: {  # Stephen Curry
                'PLAYER_ID': 201939,
                'SEASON_ID': season,
                'TEAM_ABBREVIATION': 'GSW',
                'PLAYER_AGE': 35,
                'GP': 70,
                'GS': 70,
                'MIN': 32.7,
                'FGM': 8.2,
                'FGA': 18.1,
                'FG_PCT': 0.453,
                'FG3M': 4.8,
                'FG3A': 11.4,
                'FG3_PCT': 0.421,
                'FTM': 4.1,
                'FTA': 4.5,
                'FT_PCT': 0.911,
                'OREB': 0.8,
                'DREB': 4.1,
                'REB': 4.9,
                'AST': 5.0,
                'STL': 0.9,
                'BLK': 0.4,
                'TOV': 3.2,
                'PF': 2.1,
                'PTS': 25.3
            },
            203110: {  # Draymond Green
                'PLAYER_ID': 203110,
                'SEASON_ID': season,
                'TEAM_ABBREVIATION': 'GSW',
                'PLAYER_AGE': 33,
                'GP': 65,
                'GS': 65,
                'MIN': 32.5,
                'FGM': 3.8,
                'FGA': 8.2,
                'FG_PCT': 0.463,
                'FG3M': 0.8,
                'FG3A': 2.4,
                'FG3_PCT': 0.333,
                'FTM': 1.8,
                'FTA': 2.4,
                'FT_PCT': 0.750,
                'OREB': 1.8,
                'DREB': 6.2,
                'REB': 8.0,
                'AST': 6.8,
                'STL': 1.0,
                'BLK': 0.8,
                'TOV': 2.8,
                'PF': 3.2,
                'PTS': 10.2
            }
        }
        
        if player_id in fallback_stats:
            stats_dict = fallback_stats[player_id].copy()
            stats_dict['SEASON_ID'] = season  # Update season
            df = pd.DataFrame([stats_dict])
            print(f"✅ Using fallback stats for player {player_id}")
            return df
        
        return None
    
    def clear_old_cache(self, max_age_hours: int = 48):
        """Clear cache files older than specified hours."""
        if not os.path.exists(self.cache_dir):
            return
        
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        cleared_count = 0
        
        for filename in os.listdir(self.cache_dir):
            file_path = os.path.join(self.cache_dir, filename)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_time < cutoff_time:
                    try:
                        os.remove(file_path)
                        cleared_count += 1
                    except Exception as e:
                        print(f"❌ Error removing old cache file {filename}: {e}")
        
        if cleared_count > 0:
            print(f"✅ Cleared {cleared_count} old cache files")
