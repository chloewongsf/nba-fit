#!/usr/bin/env python3
"""
Cache warming script to pre-populate popular NBA players' data.
Run this script to cache data for common players before deployment.
"""

from services.nba_client import NBAClient
import time

def warm_cache():
    """Pre-populate cache with popular NBA players."""
    client = NBAClient()
    
    # Popular NBA players to cache
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
    
    print("🔥 Warming cache with popular NBA players...")
    
    # Cache active players first
    print("📋 Caching active players list...")
    try:
        players_df = client.get_active_players()
        print(f"✅ Cached {len(players_df)} active players")
    except Exception as e:
        print(f"❌ Error caching active players: {e}")
    
    # Cache player stats
    print("📊 Caching player stats...")
    cached_count = 0
    for player_id, player_name in popular_players:
        for season in seasons:
            try:
                print(f"  Caching {player_name} ({player_id}) for {season}...")
                stats_df = client.get_player_per_game(player_id, season)
                if not stats_df.empty:
                    cached_count += 1
                    print(f"    ✅ Cached stats for {player_name}")
                else:
                    print(f"    ⚠️ No stats available for {player_name} in {season}")
                
                # Small delay to avoid rate limits
                time.sleep(0.5)
                
            except Exception as e:
                print(f"    ❌ Error caching {player_name}: {e}")
    
    print(f"\n🎉 Cache warming complete! Cached stats for {cached_count} player-season combinations.")
    
    # Show cache status
    import os
    if os.path.exists("cache"):
        cache_files = os.listdir("cache")
        print(f"📁 Cache directory now has {len(cache_files)} files")
    else:
        print("📁 No cache directory found")

if __name__ == "__main__":
    warm_cache()
