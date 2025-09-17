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

def fetch_and_save(player_id: int, season: str = DEFAULT_SEASON, max_retries: int = 3, overwrite: bool = False) -> bool:
    """
    Fetch game log data for a single player and save as CSV with retry mechanism.
    
    Args:
        player_id: NBA player ID
        season: NBA season (e.g., "2024-25")
        max_retries: Maximum number of retry attempts
        overwrite: If True, overwrite existing CSV files
        
    Returns:
        True if successful, False otherwise
    """
    # Check if CSV already exists
    normalized_season = normalize_season(season)
    filename = f"{player_id}_{normalized_season}.csv"
    filepath = os.path.join(DATA_DIR, filename)
    
    if os.path.exists(filepath) and not overwrite:
        print(f"⏩ Skipping {player_id}, file already exists")
        return True  # Return True since we have the data
    
    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                print(f"🔄 Retry {attempt}/{max_retries} for player {player_id}...")
                time.sleep(2)  # Longer delay on retry
            
            # Fetch game log data
            log = playergamelog.PlayerGameLog(player_id=player_id, season=season)
            df = log.get_data_frames()[0]
            
            if df.empty:
                print(f"⚠️ No game log data found for player {player_id} in {season}")
                return False
            
            # Save to CSV
            df.to_csv(filepath, index=False)
            print(f"✅ Saved {len(df)} games to {filepath}")
            
            # Delay between requests to avoid rate limiting
            time.sleep(1)
            return True
            
        except Exception as e:
            error_msg = str(e).lower()
            if attempt < max_retries:
                if any(keyword in error_msg for keyword in ['timeout', 'connection', 'network', 'rate']):
                    print(f"⚠️ Attempt {attempt + 1} failed for player {player_id}: {e}")
                    continue
                else:
                    print(f"❌ Non-retryable error for player {player_id}: {e}")
                    return False
            else:
                print(f"❌ Failed to fetch player {player_id} after {max_retries + 1} attempts: {e}")
                return False
    
    return False

def fetch_all_players(season: str = DEFAULT_SEASON, max_players: Optional[int] = None, chunk_size: int = 50, overwrite: bool = False) -> dict:
    """
    Fetch game log data for all active players with chunking and progress tracking.
    
    Args:
        season: NBA season (e.g., "2024-25")
        max_players: Maximum number of players to fetch (None for all)
        chunk_size: Number of players to process in each chunk
        overwrite: If True, overwrite existing CSV files
        
    Returns:
        Dictionary with success/failure counts
    """
    print(f"🏀 Fetching game logs for all active players in {season}...")
    print(f"📦 Chunk size: {chunk_size} players per chunk")
    
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
        print(f"📦 Will process in {chunk_size} chunks")
        
        success_count = 0
        failed_count = 0
        total_chunks = (len(players_df) + chunk_size - 1) // chunk_size
        
        # Process players in chunks
        for chunk_idx in range(0, len(players_df), chunk_size):
            chunk_end = min(chunk_idx + chunk_size, len(players_df))
            chunk_df = players_df.iloc[chunk_idx:chunk_end]
            chunk_num = (chunk_idx // chunk_size) + 1
            
            print(f"\n{'='*60}")
            print(f"📦 Processing Chunk {chunk_num}/{total_chunks}")
            print(f"📊 Players {chunk_idx + 1}-{chunk_end} of {len(players_df)}")
            print(f"{'='*60}")
            
            chunk_success = 0
            chunk_failed = 0
            
            for i, row in chunk_df.iterrows():
                player_id = row["PERSON_ID"]
                player_name = row["DISPLAY_FIRST_LAST"]
                global_index = i + 1
                
                print(f"\n[{global_index}/{len(players_df)}] Fetching player {global_index} of {len(players_df)} ({player_id}) - {player_name}")
                
                if fetch_and_save(player_id, season, overwrite=overwrite):
                    chunk_success += 1
                    success_count += 1
                else:
                    chunk_failed += 1
                    failed_count += 1
            
            # Chunk summary
            print(f"\n📦 Chunk {chunk_num} Complete:")
            print(f"✅ Success: {chunk_success}")
            print(f"❌ Failed: {chunk_failed}")
            print(f"📊 Total: {chunk_success + chunk_failed}")
            
            # Overall progress
            processed = chunk_end
            print(f"\n📈 Overall Progress: {processed}/{len(players_df)} players processed")
            print(f"✅ Total Success: {success_count}")
            print(f"❌ Total Failed: {failed_count}")
            
            # Save progress after each chunk
            if chunk_num < total_chunks:
                print(f"💾 Progress saved. Ready for next chunk...")
                print(f"🔄 You can restart the script and it will continue from where it left off")
        
        print(f"\n🎉 All chunks complete!")
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

def fetch_popular_players(season: str = DEFAULT_SEASON, overwrite: bool = False) -> dict:
    """
    Fetch game log data for a curated list of popular players.
    
    Args:
        season: NBA season (e.g., "2024-25")
        overwrite: If True, overwrite existing CSV files
        
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
        
        if fetch_and_save(player_id, season, overwrite=overwrite):
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
    parser.add_argument("--chunk-size", type=int, default=50, help="Chunk size for processing players (default: 50)")
    parser.add_argument("--retries", type=int, default=3, help="Number of retries for failed requests (default: 3)")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing CSV files (default: skip existing files)")
    
    args = parser.parse_args()
    
    print("🚀 NBA Data Fetcher")
    print("=" * 60)
    print(f"📅 Season: {args.season}")
    print(f"📁 Data directory: {DATA_DIR}")
    print(f"📦 Chunk size: {args.chunk_size}")
    print(f"🔄 Max retries: {args.retries}")
    print(f"⏱️  Delay between requests: 1 second")
    print(f"📝 Overwrite existing files: {'Yes' if args.overwrite else 'No (skip existing)'}")
    print("=" * 60)
    print()
    
    if args.all:
        # Fetch all active players
        print("🏀 Fetching ALL active players...")
        print("⚠️  This may take a long time and make many API requests!")
        print("💡 Use --max to limit the number of players")
        print()
        
        results = fetch_all_players(args.season, args.max, args.chunk_size, args.overwrite)
    elif args.popular:
        # Fetch popular players
        print("⭐ Fetching popular players...")
        results = fetch_popular_players(args.season, args.overwrite)
    elif args.players:
        # Fetch specific players
        print(f"🎯 Fetching {len(args.players)} specific players...")
        success_count = 0
        failed_count = 0
        
        for i, player_id in enumerate(args.players):
            print(f"\n[{i+1}/{len(args.players)}] Fetching player {i+1} of {len(args.players)} ({player_id})")
            if fetch_and_save(player_id, args.season, args.retries, args.overwrite):
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
        
        for i, player_id in enumerate(example_players):
            print(f"\n[{i+1}/{len(example_players)}] Fetching player {i+1} of {len(example_players)} ({player_id})")
            if fetch_and_save(player_id, args.season, args.retries, args.overwrite):
                success_count += 1
            else:
                failed_count += 1
        
        results = {
            "success": success_count,
            "failed": failed_count,
            "total": success_count + failed_count
        }
    
    print("\n" + "=" * 60)
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
        
        # Show some example files
        import glob
        csv_files = glob.glob(os.path.join(DATA_DIR, f"*_{normalize_season(args.season)}.csv"))
        if csv_files:
            print(f"\n📁 Example files created:")
            for file in csv_files[:5]:  # Show first 5 files
                print(f"   - {os.path.basename(file)}")
            if len(csv_files) > 5:
                print(f"   ... and {len(csv_files) - 5} more files")
    
    print(f"\n🎉 Fetch complete!")

if __name__ == "__main__":
    main()
