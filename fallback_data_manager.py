"""
Fallback data manager for NBA player data when API is blocked.
"""

import pandas as pd
import os
from typing import Dict, Any, Optional, List
import streamlit as st


class FallbackDataManager:
    """Manages fallback CSV data when NBA API is unavailable."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.ensure_data_dir()
    
    def ensure_data_dir(self):
        """Ensure data directory exists."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def get_fallback_players(self) -> pd.DataFrame:
        """Get fallback active players data from CSV."""
        csv_path = os.path.join(self.data_dir, "active_players.csv")
        
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                st.write(f"📁 Loaded {len(df)} players from fallback CSV")
                return df
            except Exception as e:
                st.error(f"❌ Error loading fallback players CSV: {e}")
                return self._get_hardcoded_players()
        else:
            st.warning("⚠️ No fallback players CSV found, using hardcoded data")
            return self._get_hardcoded_players()
    
    def get_fallback_player_stats(self, player_id: int, season: str) -> Optional[pd.DataFrame]:
        """Get fallback player stats from CSV."""
        csv_path = os.path.join(self.data_dir, "player_stats.csv")
        
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                # Filter for the specific player and season
                filtered_df = df[(df['PLAYER_ID'] == player_id) & (df['SEASON_ID'] == season)]
                
                if not filtered_df.empty:
                    st.write(f"📁 Loaded stats for player {player_id} from fallback CSV")
                    return filtered_df
                else:
                    st.warning(f"⚠️ No fallback stats found for player {player_id} in {season}")
                    return None
            except Exception as e:
                st.error(f"❌ Error loading fallback stats CSV: {e}")
                return None
        else:
            st.warning("⚠️ No fallback stats CSV found")
            return None
    
    def _get_hardcoded_players(self) -> pd.DataFrame:
        """Get hardcoded fallback players when CSV is not available."""
        hardcoded_players = pd.DataFrame({
            'id': [
                201939,  # Stephen Curry
                203110,  # Draymond Green
                203999,  # Nikola Jokic
                201142,  # Kevin Durant
                201935,  # Damian Lillard
                203507,  # Karl-Anthony Towns
                203954,  # Joel Embiid
                201566,  # Russell Westbrook
                202681,  # Giannis Antetokounmpo
                203076,  # Anthony Davis
                201935,  # Damian Lillard
                203507,  # Karl-Anthony Towns
                203954,  # Joel Embiid
                201566,  # Russell Westbrook
                202681,  # Giannis Antetokounmpo
                201142,  # Kevin Durant
                201939,  # Stephen Curry
                203110,  # Draymond Green
                203999,  # Nikola Jokic
                201935,  # Damian Lillard
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
                'Giannis Antetokounmpo',
                'Anthony Davis',
                'Damian Lillard',
                'Karl-Anthony Towns',
                'Joel Embiid',
                'Russell Westbrook',
                'Giannis Antetokounmpo',
                'Kevin Durant',
                'Stephen Curry',
                'Draymond Green',
                'Nikola Jokic',
                'Damian Lillard',
            ]
        })
        
        # Remove duplicates
        hardcoded_players = hardcoded_players.drop_duplicates(subset=['id'])
        st.write(f"📁 Using hardcoded fallback with {len(hardcoded_players)} players")
        return hardcoded_players
    
    def save_players_to_csv(self, players_df: pd.DataFrame):
        """Save players data to fallback CSV."""
        csv_path = os.path.join(self.data_dir, "active_players.csv")
        try:
            players_df.to_csv(csv_path, index=False)
            st.success(f"✅ Saved {len(players_df)} players to fallback CSV")
        except Exception as e:
            st.error(f"❌ Error saving players CSV: {e}")
    
    def save_player_stats_to_csv(self, stats_df: pd.DataFrame):
        """Save player stats data to fallback CSV."""
        csv_path = os.path.join(self.data_dir, "player_stats.csv")
        try:
            # Append to existing CSV or create new one
            if os.path.exists(csv_path):
                existing_df = pd.read_csv(csv_path)
                combined_df = pd.concat([existing_df, stats_df], ignore_index=True)
                # Remove duplicates based on PLAYER_ID and SEASON_ID
                combined_df = combined_df.drop_duplicates(subset=['PLAYER_ID', 'SEASON_ID'], keep='last')
                combined_df.to_csv(csv_path, index=False)
                st.success(f"✅ Updated player stats CSV with {len(stats_df)} new records")
            else:
                stats_df.to_csv(csv_path, index=False)
                st.success(f"✅ Created new player stats CSV with {len(stats_df)} records")
        except Exception as e:
            st.error(f"❌ Error saving player stats CSV: {e}")
    
    def get_fallback_stats_for_player(self, player_id: int, season: str) -> Optional[pd.DataFrame]:
        """Get fallback stats for a specific player, with hardcoded fallback."""
        # Try CSV first
        csv_stats = self.get_fallback_player_stats(player_id, season)
        if csv_stats is not None:
            return csv_stats
        
        # Fall back to hardcoded stats for popular players
        hardcoded_stats = self._get_hardcoded_player_stats(player_id, season)
        if hardcoded_stats is not None:
            st.write(f"📁 Using hardcoded fallback stats for player {player_id}")
            return hardcoded_stats
        
        return None
    
    def _get_hardcoded_player_stats(self, player_id: int, season: str) -> Optional[pd.DataFrame]:
        """Get hardcoded fallback stats for popular players."""
        # Sample stats for popular players
        hardcoded_stats = {
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
            },
            203999: {  # Nikola Jokic
                'PLAYER_ID': 203999,
                'SEASON_ID': season,
                'TEAM_ABBREVIATION': 'DEN',
                'PLAYER_AGE': 29,
                'GP': 75,
                'GS': 75,
                'MIN': 35.2,
                'FGM': 9.8,
                'FGA': 18.1,
                'FG_PCT': 0.541,
                'FG3M': 1.2,
                'FG3A': 3.4,
                'FG3_PCT': 0.353,
                'FTM': 4.8,
                'FTA': 5.6,
                'FT_PCT': 0.857,
                'OREB': 2.8,
                'DREB': 9.2,
                'REB': 12.0,
                'AST': 9.8,
                'STL': 1.3,
                'BLK': 0.9,
                'TOV': 3.5,
                'PF': 2.8,
                'PTS': 25.6
            }
        }
        
        if player_id in hardcoded_stats:
            stats_dict = hardcoded_stats[player_id].copy()
            stats_dict['SEASON_ID'] = season  # Update season
            return pd.DataFrame([stats_dict])
        
        return None
