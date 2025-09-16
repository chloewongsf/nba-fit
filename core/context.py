"""
Context module for NBA Fit analysis.
Contains functions to build scheme vectors from team context and sliders.
"""

import numpy as np
from typing import Dict, Any, List
from services.nba_client import NBAClient
from core.features import FeatureEngineer


def build_scheme_vector(sliders: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a scheme vector from slider inputs.
    
    Args:
        sliders: Dictionary containing slider values with keys like:
                - pace: Team pace preference
                - three_point_volume: Three-point shooting volume
                - switchability: Defensive switching preference
                - rim_pressure: Rim pressure/defense intensity
                - ball_movement: Ball movement preference
                - off_glass: Offensive rebounding emphasis
                - drop_vs_switch: Drop coverage vs switch preference
                - foul_avoidance: Foul avoidance emphasis
    
    Returns:
        Dictionary containing the scheme vector (passthrough for now)
    """
    # For now, just return the sliders as a passthrough
    # Future implementations can add transformations, normalizations, etc.
    return sliders.copy()


def summarize_roster(lineup_ids: List[int], bench_ids: List[int], season: str) -> Dict[str, Any]:
    """
    Summarize a roster by fetching player stats and computing feature vectors.
    
    Args:
        lineup_ids: List of NBA player IDs for starting lineup
        bench_ids: List of NBA player IDs for bench players
        season: NBA season (e.g., "2023-24")
        
    Returns:
        Dictionary containing lineup_vectors, bench_vectors, full_roster_vectors,
        lineup_centroid, and team_centroid
    """
    nba_client = NBAClient()
    feature_engineer = FeatureEngineer()
    
    def process_player_list(player_ids: List[int]) -> List[Dict[str, Any]]:
        """Helper function to process a list of player IDs and return vectors."""
        vectors = []
        for player_id in player_ids:
            try:
                # Get player stats for the season
                player_stats_df = nba_client.get_player_per_game(player_id, season)
                
                if not player_stats_df.empty:
                    # Build player vector
                    player_vector = feature_engineer.build_player_vector(player_stats_df)
                    vectors.append(player_vector)
                else:
                    print(f"No stats found for player {player_id} in season {season}")
                    
            except Exception as e:
                print(f"Error processing player {player_id}: {e}")
                continue
        return vectors
    
    # Process lineup and bench players separately
    lineup_vectors = process_player_list(lineup_ids)
    bench_vectors = process_player_list(bench_ids)
    
    # Combine for full roster
    full_roster_vectors = lineup_vectors + bench_vectors
    
    def compute_centroid(vectors: List[Dict[str, Any]]) -> Dict[str, float]:
        """Helper function to compute centroid from a list of vectors."""
        if not vectors:
            return {}
        
        # Get all unique keys from all vectors
        all_keys = set()
        for vector in vectors:
            all_keys.update(vector.keys())
        
        # Compute average for each key (only numeric values)
        centroid = {}
        for key in all_keys:
            values = []
            for vector in vectors:
                value = vector.get(key, 0.0)
                # Only include numeric values (int, float, or numeric strings)
                if isinstance(value, (int, float)) or (isinstance(value, str) and value.replace('.', '').replace('-', '').isdigit()):
                    values.append(float(value))
                # Skip non-numeric values like 'POSITION', 'PLAYER_ID', etc.
            
            if values:  # Only compute mean if we have numeric values
                centroid[key] = np.mean(values)
            else:
                # For non-numeric keys, use the most common value or skip
                centroid[key] = 0.0  # Default value for non-numeric keys
        
        return centroid
    
    # Compute centroids
    lineup_centroid = compute_centroid(lineup_vectors)
    team_centroid = compute_centroid(full_roster_vectors)
    
    return {
        'lineup_vectors': lineup_vectors,
        'bench_vectors': bench_vectors,
        'full_roster_vectors': full_roster_vectors,
        'lineup_centroid': lineup_centroid,
        'team_centroid': team_centroid
    }
