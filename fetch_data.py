"""
NBA Data Fetcher Script

This script fetches player game log data from the NBA API and saves it as CSV files
in the data/ directory. The Streamlit app then loads from these CSV files.

Usage:
    python3 fetch_data.py                    # Fetch specific players
    python3 fetch_data.py --all              # Fetch all active players
    python3 fetch_data.py --all --max 100    # Fetch up to 100 players
"""

from nba_api.stats.endpoints import playergamelog, commonallplayers
import pandas as pd
import os
import time
import argparse
from typing import Optional

DATA_DIR = "data"
DEFAULT_SEASON = "2024-25"

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def normalize_season(season: str) -> str:
    """
    Normalize season format for filename (e.g., 2024-25 -> 2024_25)
    
    Args:
        season: Season in format like "2024-25"
        
    Returns:
        Normalized season for filename like "2024_25"
    """
    return season.replace('-', '_')

def fetch_and_save(player_id: int, season: str = DEFAULT_SEASON) -> bool:
    """
    Fetch game log data for a single player and save as CSV.
    
    Args:
        player_id: NBA player ID
        season: NBA season (e.g., "2024-25")
        
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"📊 Fetching game log for player {player_id} ({season})...")
        
        # Fetch game log data
        log = playergamelog.PlayerGameLog(player_id=player_id, season=season)
        df = log.get_data_frames()[0]
        
        if df.empty:
            print(f"⚠️ No game log data found for player {player_id} in {season}")
            return False
        
        # Normalize season for filename
        normalized_season = normalize_season(season)
        filename = f"{player_id}_{normalized_season}.csv"
        filepath = os.path.join(DATA_DIR, filename)
        
        # Save to CSV
        df.to_csv(filepath, index=False)
        print(f"✅ Saved {len(df)} games to {filepath}")
        
        # Small delay to be respectful to the API
        time.sleep(0.2)
        return True
        
    except Exception as e:
        print(f"❌ Failed to fetch player {player_id}: {e}")
        return False

def fetch_all_players(season: str = DEFAULT_SEASON, max_players: Optional[int] = None) -> dict:
    """
    Fetch game log data for all active players.
    
    Args:
        season: NBA season (e.g., "2024-25")
        max_players: Maximum number of players to fetch (None for all)
        
    Returns:
        Dictionary with success/failure counts
    """
    print(f"🏀 Fetching game logs for all active players in {season}...")
    
    try:
        # Get list of active players
        print("📋 Getting list of active players...")
        players_df = commonallplayers.CommonAllPlayers(is_only_current_season=1).get_data_frames()[0]
        
        if players_df.empty:
            print("❌ No active players found")
            return {"success": 0, "failed": 0, "total": 0}
        
        total_players = len(players_df)
        if max_players:
            total_players = min(total_players, max_players)
            players_df = players_df.head(max_players)
        
        print(f"📊 Found {len(players_df)} active players to process")
        
        success_count = 0
        failed_count = 0
        
        for i, row in players_df.iterrows():
            player_id = row["PERSON_ID"]
            player_name = row["DISPLAY_FIRST_LAST"]
            
            print(f"\n[{i+1}/{len(players_df)}] Processing {player_name} (ID: {player_id})")
            
            if fetch_and_save(player_id, season):
                success_count += 1
            else:
                failed_count += 1
            
            # Progress update every 10 players
            if (i + 1) % 10 == 0:
                print(f"📈 Progress: {i+1}/{len(players_df)} players processed")
        
        print(f"\n🎉 Fetch complete!")
        print(f"✅ Successfully fetched: {success_count} players")
        print(f"❌ Failed to fetch: {failed_count} players")
        print(f"📊 Total processed: {success_count + failed_count} players")
        
        return {
            "success": success_count,
            "failed": failed_count,
            "total": success_count + failed_count
        }
        
    except Exception as e:
        print(f"❌ Error fetching all players: {e}")
        return {"success": 0, "failed": 0, "total": 0}

def fetch_popular_players(season: str = DEFAULT_SEASON) -> dict:
    """
    Fetch game log data for a curated list of popular players.
    
    Args:
        season: NBA season (e.g., "2024-25")
        
    Returns:
        Dictionary with success/failure counts
    """
    # Curated list of popular/important players
    popular_player_ids = [
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
        1630173, # Precious Achiuwa
        2544,    # LeBron James
        201935,  # Damian Lillard
        201142,  # Kevin Durant
        203507,  # Karl-Anthony Towns
    ]
    
    print(f"⭐ Fetching game logs for {len(popular_player_ids)} popular players in {season}...")
    
    success_count = 0
    failed_count = 0
    
    for i, player_id in enumerate(popular_player_ids):
        print(f"\n[{i+1}/{len(popular_player_ids)}] Processing player ID {player_id}")
        
        if fetch_and_save(player_id, season):
            success_count += 1
        else:
            failed_count += 1
    
    print(f"\n🎉 Popular players fetch complete!")
    print(f"✅ Successfully fetched: {success_count} players")
    print(f"❌ Failed to fetch: {failed_count} players")
    
    return {
        "success": success_count,
        "failed": failed_count,
        "total": success_count + failed_count
    }

def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(description="Fetch NBA player game log data")
    parser.add_argument("--season", default=DEFAULT_SEASON, help=f"NBA season (default: {DEFAULT_SEASON})")
    parser.add_argument("--all", action="store_true", help="Fetch all active players")
    parser.add_argument("--popular", action="store_true", help="Fetch popular players only")
    parser.add_argument("--max", type=int, help="Maximum number of players to fetch (with --all)")
    parser.add_argument("--players", nargs="+", type=int, help="Specific player IDs to fetch")
    
    args = parser.parse_args()
    
    print("🚀 NBA Data Fetcher")
    print("=" * 50)
    print(f"📅 Season: {args.season}")
    print(f"📁 Data directory: {DATA_DIR}")
    print()
    
    if args.all:
        # Fetch all active players
        results = fetch_all_players(args.season, args.max)
    elif args.popular:
        # Fetch popular players
        results = fetch_popular_players(args.season)
    elif args.players:
        # Fetch specific players
        print(f"🎯 Fetching {len(args.players)} specific players...")
        success_count = 0
        failed_count = 0
        
        for player_id in args.players:
            if fetch_and_save(player_id, args.season):
                success_count += 1
            else:
                failed_count += 1
        
        results = {
            "success": success_count,
            "failed": failed_count,
            "total": success_count + failed_count
        }
    else:
        # Default: fetch a few example players
        print("🎯 Fetching example players (use --all, --popular, or --players for more options)...")
        example_players = [201939, 1630173]  # Curry and Achiuwa
        
        success_count = 0
        failed_count = 0
        
        for player_id in example_players:
            if fetch_and_save(player_id, args.season):
                success_count += 1
            else:
                failed_count += 1
        
        results = {
            "success": success_count,
            "failed": failed_count,
            "total": success_count + failed_count
        }
    
    print("\n" + "=" * 50)
    print("📊 Final Results:")
    print(f"✅ Successful: {results['success']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"📈 Total: {results['total']}")
    
    if results['success'] > 0:
        print(f"\n💡 Next steps:")
        print(f"1. Check the {DATA_DIR}/ directory for new CSV files")
        print(f"2. Commit the new files to your repository:")
        print(f"   git add {DATA_DIR}/")
        print(f"   git commit -m 'Update player data for {args.season}'")
        print(f"   git push")
        print(f"3. Your Streamlit app will now load from these CSV files!")

if __name__ == "__main__":
    main()
