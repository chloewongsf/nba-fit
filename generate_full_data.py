#!/usr/bin/env python3
"""
NBA Data Export Script

This script fetches all NBA data for the 2024-25 season and exports it to JSON files
for hosting on GitHub Pages. It creates the complete dataset needed by the NBA Fit app.
"""

import json
import os
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from nba_api.stats.endpoints import commonallplayers, playergamelog, commonplayerinfo
    NBA_API_AVAILABLE = True
except ImportError:
    logger.error("nba_api not available. Please install with: pip install nba_api")
    NBA_API_AVAILABLE = False

# Configuration
SEASON = "2024-25"
DATA_DIR = Path("data")
PLAYERS_DIR = DATA_DIR / "players"
MAX_PLAYERS = None  # Set to a number to limit players for testing, None for all
DELAY_BETWEEN_REQUESTS = 0.5  # Seconds to wait between API calls

def calculate_age_from_birthdate(birthdate_str: str) -> int:
    """Calculate age from birthdate string."""
    try:
        if pd.isna(birthdate_str) or not birthdate_str:
            return 0
        
        # Parse birthdate (format: "1988-03-14T00:00:00")
        birthdate = datetime.strptime(birthdate_str.split('T')[0], '%Y-%m-%d')
        today = datetime.now()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        return max(0, age)  # Ensure non-negative age
    except Exception as e:
        logger.warning(f"Failed to calculate age from birthdate '{birthdate_str}': {e}")
        return 0

def ensure_directories():
    """Create necessary directories."""
    DATA_DIR.mkdir(exist_ok=True)
    PLAYERS_DIR.mkdir(exist_ok=True)
    logger.info(f"✅ Created directories: {DATA_DIR} and {PLAYERS_DIR}")

def fetch_active_players() -> List[Dict]:
    """
    Fetch list of active NBA players.
    
    Returns:
        List[Dict]: List of player dictionaries with player_id and name
    """
    logger.info("🏀 Fetching active NBA players...")
    
    try:
        players_df = commonallplayers.CommonAllPlayers(is_only_current_season=1).get_data_frames()[0]
        
        players = []
        for _, row in players_df.iterrows():
            players.append({
                "player_id": int(row['PERSON_ID']),
                "name": row['DISPLAY_FIRST_LAST']
            })
        
        logger.info(f"✅ Fetched {len(players)} active players")
        return players
        
    except Exception as e:
        logger.error(f"❌ Failed to fetch active players: {e}")
        return []

def save_active_players(players: List[Dict]):
    """Save active players list to JSON file."""
    logger.info("💾 Saving active_players.json...")
    
    data = {"players": players}
    file_path = DATA_DIR / "active_players.json"
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"✅ Saved {len(players)} players to {file_path}")

def fetch_player_info(player_id: int, player_name: str) -> Optional[Dict]:
    """
    Fetch player biographical information.
    
    Args:
        player_id: NBA player ID
        player_name: Player name for logging
        
    Returns:
        Dict: Player info dictionary, or None if failed
    """
    try:
        player_info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
        info_df = player_info.get_data_frames()[0]
        
        if not info_df.empty:
            row = info_df.iloc[0]
            birthdate = row.get('BIRTHDATE', '')
            age = calculate_age_from_birthdate(birthdate)
            
            info = {
                "position": row.get('POSITION', 'Unknown'),
                "height": row.get('HEIGHT', 'Unknown'),
                "weight": row.get('WEIGHT', 'Unknown'),
                "age": age,
                "birthdate": birthdate,  # Add birthdate field for age calculation fallback
                "team": row.get('TEAM_NAME', 'Unknown'),
                "jersey": row.get('JERSEY', 'Unknown')
            }
            return info
        else:
            logger.warning(f"⚠️ No player info found for {player_name} ({player_id})")
            return None
            
    except Exception as e:
        logger.error(f"❌ Failed to fetch player info for {player_name} ({player_id}): {e}")
        return None

def save_player_info(player_id: int, player_name: str, info: Dict):
    """Save player info to JSON file."""
    file_path = PLAYERS_DIR / f"{player_id}_info.json"
    
    data = {"player_info": info}
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"✅ Saved player info for {player_name} ({player_id})")

def fetch_player_gamelog(player_id: int, player_name: str) -> Optional[List[Dict]]:
    """
    Fetch player game log data.
    
    Args:
        player_id: NBA player ID
        player_name: Player name for logging
        
    Returns:
        List[Dict]: List of game dictionaries, or None if failed
    """
    try:
        gamelog = playergamelog.PlayerGameLog(player_id=player_id, season=SEASON)
        games_df = gamelog.get_data_frames()[0]
        
        if games_df.empty:
            logger.warning(f"⚠️ No game log data for {player_name} ({player_id}) in {SEASON}")
            return []
        
        games = []
        for _, row in games_df.iterrows():
            game = {
                "GAME_DATE": row['GAME_DATE'],
                "MATCHUP": row['MATCHUP'],
                "MIN": float(row['MIN']) if pd.notna(row['MIN']) else 0.0,
                "FGM": int(row['FGM']),
                "FGA": int(row['FGA']),
                "FG3M": int(row['FG3M']),
                "FG3A": int(row['FG3A']),
                "FTM": int(row['FTM']),
                "FTA": int(row['FTA']),
                "OREB": int(row['OREB']),
                "DREB": int(row['DREB']),
                "REB": int(row['REB']),
                "AST": int(row['AST']),
                "STL": int(row['STL']),
                "BLK": int(row['BLK']),
                "TOV": int(row['TOV']),
                "PF": int(row['PF']),
                "PTS": int(row['PTS']),
                "PLUS_MINUS": int(row['PLUS_MINUS'])
            }
            games.append(game)
        
        logger.info(f"✅ Fetched {len(games)} games for {player_name} ({player_id})")
        return games
        
    except Exception as e:
        logger.error(f"❌ Failed to fetch game log for {player_name} ({player_id}): {e}")
        return None

def save_player_gamelog(player_id: int, player_name: str, games: List[Dict]):
    """Save player game log to JSON file."""
    file_path = PLAYERS_DIR / f"{player_id}_gamelog.json"
    
    data = {"games": games}
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"✅ Saved {len(games)} games for {player_name} ({player_id})")

def calculate_season_stats(games: List[Dict]) -> Dict:
    """
    Calculate season statistics from game log data.
    
    Args:
        games: List of game dictionaries
        
    Returns:
        Dict: Season statistics
    """
    if not games:
        return {}
    
    # Convert to DataFrame for easier calculations
    df = pd.DataFrame(games)
    
    # Calculate averages
    numeric_cols = ['MIN', 'FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA', 
                   'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'PLUS_MINUS']
    
    stats = {}
    
    # Calculate averages for numeric columns
    for col in numeric_cols:
        if col in df.columns:
            stats[f'{col}_avg'] = float(df[col].mean())
            stats[f'{col}_total'] = int(df[col].sum())
    
    # Calculate percentages
    if 'FGA' in df.columns and 'FGM' in df.columns:
        total_fga = df['FGA'].sum()
        total_fgm = df['FGM'].sum()
        stats['FG_PCT'] = float(total_fgm / total_fga) if total_fga > 0 else 0.0
    
    if 'FG3A' in df.columns and 'FG3M' in df.columns:
        total_fg3a = df['FG3A'].sum()
        total_fg3m = df['FG3M'].sum()
        stats['FG3_PCT'] = float(total_fg3m / total_fg3a) if total_fg3a > 0 else 0.0
    
    if 'FTA' in df.columns and 'FTM' in df.columns:
        total_fta = df['FTA'].sum()
        total_ftm = df['FTM'].sum()
        stats['FT_PCT'] = float(total_ftm / total_fta) if total_fta > 0 else 0.0
    
    # Add game count
    stats['games_played'] = len(games)
    
    return stats

def save_player_season_stats(player_id: int, player_name: str, stats: Dict):
    """Save player season stats to JSON file."""
    file_path = PLAYERS_DIR / f"{player_id}_season_stats.json"
    
    data = {"season_stats": stats}
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"✅ Saved season stats for {player_name} ({player_id})")

def process_player(player_id: int, player_name: str, skip_existing: bool = True) -> bool:
    """
    Process a single player: fetch and save all their data.
    
    Args:
        player_id: NBA player ID
        player_name: Player name for logging
        skip_existing: Whether to skip if files already exist
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"🔄 Processing {player_name} ({player_id})...")
    
    # Check if files already exist
    if skip_existing:
        info_file = PLAYERS_DIR / f"{player_id}_info.json"
        gamelog_file = PLAYERS_DIR / f"{player_id}_gamelog.json"
        stats_file = PLAYERS_DIR / f"{player_id}_season_stats.json"
        
        if all(f.exists() for f in [info_file, gamelog_file, stats_file]):
            logger.info(f"⏩ Skipping {player_name} ({player_id}) - files already exist")
            return True
    
    success = True
    
    # Fetch and save player info
    try:
        info = fetch_player_info(player_id, player_name)
        if info:
            save_player_info(player_id, player_name, info)
        else:
            success = False
    except Exception as e:
        logger.error(f"❌ Error processing player info for {player_name}: {e}")
        success = False
    
    # Add delay between requests
    time.sleep(DELAY_BETWEEN_REQUESTS)
    
    # Fetch and save game log
    try:
        games = fetch_player_gamelog(player_id, player_name)
        if games is not None:
            save_player_gamelog(player_id, player_name, games)
            
            # Calculate and save season stats
            stats = calculate_season_stats(games)
            if stats:
                save_player_season_stats(player_id, player_name, stats)
        else:
            success = False
    except Exception as e:
        logger.error(f"❌ Error processing game log for {player_name}: {e}")
        success = False
    
    # Add delay between requests
    time.sleep(DELAY_BETWEEN_REQUESTS)
    
    if success:
        logger.info(f"✅ Completed processing {player_name} ({player_id})")
    else:
        logger.warning(f"⚠️ Completed processing {player_name} ({player_id}) with some errors")
    
    return success

def main():
    """Main function to generate all NBA data."""
    if not NBA_API_AVAILABLE:
        logger.error("❌ NBA API not available. Please install nba_api and try again.")
        return 1
    
    logger.info("🚀 Starting NBA data generation for 2024-25 season...")
    logger.info("=" * 60)
    
    # Create directories
    ensure_directories()
    
    # Fetch active players
    players = fetch_active_players()
    if not players:
        logger.error("❌ No players fetched. Exiting.")
        return 1
    
    # Limit players if specified
    if MAX_PLAYERS:
        players = players[:MAX_PLAYERS]
        logger.info(f"🔢 Limited to first {MAX_PLAYERS} players for testing")
    
    # Save active players list
    save_active_players(players)
    
    # Process each player
    logger.info(f"🔄 Processing {len(players)} players...")
    logger.info("=" * 60)
    
    successful = 0
    failed = 0
    
    for i, player in enumerate(players, 1):
        player_id = player['player_id']
        player_name = player['name']
        
        logger.info(f"📊 Progress: {i}/{len(players)} - {player_name} ({player_id})")
        
        try:
            if process_player(player_id, player_name):
                successful += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"❌ Unexpected error processing {player_name}: {e}")
            failed += 1
        
        # Progress update every 10 players
        if i % 10 == 0:
            logger.info(f"📈 Progress: {i}/{len(players)} players processed ({successful} successful, {failed} failed)")
    
    # Final summary
    logger.info("=" * 60)
    logger.info("🎉 Data generation complete!")
    logger.info(f"📊 Summary:")
    logger.info(f"  ✅ Successful: {successful}")
    logger.info(f"  ❌ Failed: {failed}")
    logger.info(f"  📁 Total players: {len(players)}")
    
    # Show file structure
    logger.info(f"📁 Generated files in {DATA_DIR}:")
    logger.info(f"  - active_players.json")
    logger.info(f"  - players/ directory with {len(list(PLAYERS_DIR.glob('*.json')))} files")
    
    logger.info("\n💡 Next steps:")
    logger.info("  1. Review the generated JSON files")
    logger.info("  2. Create a GitHub repository (e.g., 'nba-fit-data')")
    logger.info("  3. Upload the data/ folder to the repository")
    logger.info("  4. Enable GitHub Pages in repository settings")
    logger.info("  5. Update config.py with your GitHub Pages URL")
    logger.info("  6. Deploy your NBA Fit app")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
