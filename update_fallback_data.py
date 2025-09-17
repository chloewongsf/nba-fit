#!/usr/bin/env python3
"""
Script to update fallback CSV data with fresh NBA API data.
Run this locally to pull fresh stats and save them to CSV files.
"""

import pandas as pd
import time
from services.nba_client import NBAClient
from fallback_data_manager import FallbackDataManager
import os


def update_active_players():
    """Update the active players CSV with fresh data from NBA API."""
    print("🔄 Updating active players data...")
    
    client = NBAClient()
    fallback_manager = FallbackDataManager()
    
    try:
        # Get fresh data from NBA API
        print("📡 Fetching fresh active players from NBA API...")
        players_df = client.get_active_players()
        
        if not players_df.empty:
            # Save to fallback CSV
            fallback_manager.save_players_to_csv(players_df)
            print(f"✅ Successfully updated active players CSV with {len(players_df)} players")
        else:
            print("⚠️ No players data received from API")
            
    except Exception as e:
        print(f"❌ Error updating active players: {e}")


def update_player_stats():
    """Update player stats CSV with fresh data for popular players."""
    print("🔄 Updating player stats data...")
    
    client = NBAClient()
    fallback_manager = FallbackDataManager()
    
    # Popular NBA players to update
    popular_players = [
        (201939, "Stephen Curry"),
        (203110, "Draymond Green"), 
        (203999, "Nikola Jokic"),
        (201142, "Kevin Durant"),
        (201935, "Damian Lillard"),
        (203507, "Karl-Anthony Towns"),
        (203954, "Joel Embiid"),
        (201566, "Russell Westbrook"),
        (202681, "Giannis Antetokounmpo"),
        (203076, "Anthony Davis"),
        (201935, "Damian Lillard"),
        (203507, "Karl-Anthony Towns"),
        (203954, "Joel Embiid"),
        (201566, "Russell Westbrook"),
        (202681, "Giannis Antetokounmpo"),
    ]
    
    seasons = ["2023-24", "2024-25"]
    
    updated_count = 0
    error_count = 0
    
    for player_id, player_name in popular_players:
        for season in seasons:
            try:
                print(f"📊 Fetching stats for {player_name} ({player_id}) for {season}...")
                
                # Get fresh stats from NBA API
                stats_df = client.get_player_per_game(player_id, season)
                
                if not stats_df.empty:
                    # Save to fallback CSV
                    fallback_manager.save_player_stats_to_csv(stats_df)
                    updated_count += 1
                    print(f"  ✅ Updated stats for {player_name} in {season}")
                else:
                    print(f"  ⚠️ No stats available for {player_name} in {season}")
                
                # Small delay to avoid rate limits
                time.sleep(1)
                
            except Exception as e:
                error_count += 1
                print(f"  ❌ Error updating {player_name} in {season}: {e}")
                time.sleep(2)  # Longer delay on error
    
    print(f"\n📊 Stats update complete!")
    print(f"✅ Successfully updated: {updated_count} player-season combinations")
    print(f"❌ Errors encountered: {error_count}")


def show_data_status():
    """Show the current status of fallback data files."""
    print("📁 Current fallback data status:")
    
    data_dir = "data"
    if not os.path.exists(data_dir):
        print("❌ No data directory found")
        return
    
    # Check active players CSV
    players_csv = os.path.join(data_dir, "active_players.csv")
    if os.path.exists(players_csv):
        try:
            df = pd.read_csv(players_csv)
            print(f"✅ active_players.csv: {len(df)} players")
        except Exception as e:
            print(f"❌ active_players.csv: Error reading file - {e}")
    else:
        print("❌ active_players.csv: Not found")
    
    # Check player stats CSV
    stats_csv = os.path.join(data_dir, "player_stats.csv")
    if os.path.exists(stats_csv):
        try:
            df = pd.read_csv(stats_csv)
            print(f"✅ player_stats.csv: {len(df)} records")
            # Show unique players and seasons
            unique_players = df['PLAYER_ID'].nunique()
            unique_seasons = df['SEASON_ID'].nunique()
            print(f"   📊 {unique_players} unique players, {unique_seasons} unique seasons")
        except Exception as e:
            print(f"❌ player_stats.csv: Error reading file - {e}")
    else:
        print("❌ player_stats.csv: Not found")


def main():
    """Main function to update all fallback data."""
    print("🚀 NBA Fallback Data Update Script")
    print("=" * 50)
    
    # Show current status
    show_data_status()
    print()
    
    # Update active players
    update_active_players()
    print()
    
    # Update player stats
    update_player_stats()
    print()
    
    # Show final status
    print("📁 Final data status:")
    show_data_status()
    
    print("\n🎉 Update complete!")
    print("💡 You can now commit the updated CSV files to your repository")


if __name__ == "__main__":
    main()
