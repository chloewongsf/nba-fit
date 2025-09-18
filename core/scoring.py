"""
Scoring module for NBA Fit analysis.
Contains functions to score player-team fit using various algorithms.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any

# Define player role feature keys for redundancy calculation
ROLE_FEATURE_KEYS = [
    "three_rate", "ft_rate", "ast_pct", "tov_pct", "stl_pct", 
    "blk_pct", "dreb_pct", "catch_shoot", "pullup", "rim_rate", 
    "switchability", "rim_protect", "age", "height_in", "weight_lb"
]

# Define role archetype names for redundancy calculation
ROLE_ARCHETYPE_NAMES = ["shooter", "playmaker", "rim_protector", "stretch_big", "switchable_wing"]


def target_value(k: str, t01: float, players_df: pd.DataFrame) -> float:
    """
    Map slider 0-100 to the 20th-80th percentile range of that feature.
    
    Args:
        k: Feature key
        t01: Slider value (0-100) normalized to 0-1
        players_df: DataFrame of player features for percentile calculation
        
    Returns:
        Target value in the 20th-80th percentile range
    """
    lo = players_df[k].quantile(0.20)
    hi = players_df[k].quantile(0.80)
    return lo + t01 * (hi - lo)


def distance_score(diffs: np.ndarray, weights: np.ndarray = None, sigma: float = 0.6) -> float:
    """
    Compute distance-based score with relaxed tolerance.
    
    Args:
        diffs: Array of differences between player and target values
        weights: Optional weights for each feature
        sigma: Tolerance parameter (higher = more forgiving)
        
    Returns:
        Score between 0-100
    """
    if weights is None:
        weights = np.ones(len(diffs))
    
    # Weighted squared differences
    weighted_diffs = weights * (diffs ** 2)
    
    # Apply exponential decay with relaxed tolerance
    score = 100 * np.exp(-np.sum(weighted_diffs) / (2 * sigma ** 2))
    
    return max(0.0, min(100.0, score))


def scheme_fit_score(player_vec: Dict[str, Any], scheme_vec: Dict[str, Any], 
                    players_df: pd.DataFrame) -> float:
    """
    Compute scheme fit score using distance-based scoring with realistic ranges.
    
    Args:
        player_vec: Player feature vector
        scheme_vec: Scheme preference vector (slider values 0-100)
        players_df: DataFrame of player features for percentile calculation
        
    Returns:
        Scheme fit score (0-100)
    """
    # Define feature weights (importance of each feature)
    feature_weights = {
        'pace': 1.0,
        'three_point_volume': 1.2,
        'switchability': 1.1,
        'rim_pressure': 1.0,
        'ball_movement': 1.1,
        'off_glass': 0.9,
        'drop_vs_switch': 0.8,
        'foul_avoidance': 0.7
    }
    
    diffs = []
    weights = []
    
    for key in feature_weights.keys():
        if key in player_vec and key in scheme_vec and key in players_df.columns:
            # Get player value
            player_val = float(player_vec[key])
            
            # Convert scheme slider (0-100) to target value using percentiles
            scheme_slider = float(scheme_vec[key]) / 100.0  # Normalize to 0-1
            target_val = target_value(key, scheme_slider, players_df)
            
            # Calculate difference
            diff = abs(player_val - target_val)
            diffs.append(diff)
            weights.append(feature_weights[key])
    
    if not diffs:
        return 50.0  # Default if no matching features
    
    # Compute distance score with relaxed tolerance (sigma = 0.6)
    diffs_array = np.array(diffs)
    weights_array = np.array(weights)
    
    s = distance_score(diffs_array, weights_array, sigma=0.6)
    
    # Calculate overall mismatch for bonus/floor logic
    mismatch = np.mean(diffs_array)
    
    # Floor and bonus scaling
    if mismatch < 0.1:
        s = max(s, 85.0)  # Boost well-fit players to at least 85
    
    # Ensure no scheme score < 30
    s = max(30.0, s)
    
    return s


def normalize_feature_value(feature, value):
    """
    Normalize a feature value to [0, 1] range based on realistic NBA ranges.
    
    Args:
        feature: Feature name
        value: Raw feature value
        
    Returns:
        Normalized value between 0 and 1
    """
    if feature == "three_rate":
        return min(value, 0.5) / 0.5  # Cap at 50% 3PT rate
    elif feature == "ast_pct":
        return min(value, 30.0) / 30.0  # Cap at 30% assist rate
    elif feature == "tov_pct":
        return max(0, (15.0 - value) / 15.0)  # Invert: lower TOV% is better
    elif feature == "blk_pct":
        return min(value, 5.0) / 5.0  # Cap at 5 blocks per game
    elif feature == "stl_pct":
        return min(value, 3.0) / 3.0  # Cap at 3 steals per game
    elif feature == "dreb_pct":
        return min(value, 12.0) / 12.0  # Cap at 12 defensive rebounds
    elif feature == "rim_protect":
        return min(value, 1.0)  # Already normalized
    elif feature == "catch_shoot":
        return min(value, 1.0)  # Already normalized
    elif feature == "pullup":
        return min(value, 1.0)  # Already normalized
    elif feature == "switchability":
        return min(value, 1.0)  # Already normalized
    elif feature == "height_in":
        return max(0, (value - 70) / 20)  # Normalize height (70-90 inches)
    elif feature == "ft_rate":
        return min(value, 0.4) / 0.4  # Cap at 40% FT rate
    else:
        return min(value, 1.0)  # Default normalization


def calculate_role_vector(player_vec):
    """
    Calculate dynamic role vector for a player based on weighted combinations of real stats.
    
    Args:
        player_vec: Dictionary containing player characteristics
        
    Returns:
        Dictionary with dynamic role scores for each archetype
    """
    # Extract and normalize feature values
    three_rate = normalize_feature_value("three_rate", float(player_vec.get("three_rate", 0.0) or 0.0))
    catch_shoot = normalize_feature_value("catch_shoot", float(player_vec.get("catch_shoot", 0.0) or 0.0))
    pullup = normalize_feature_value("pullup", float(player_vec.get("pullup", 0.0) or 0.0))
    ft_rate = normalize_feature_value("ft_rate", float(player_vec.get("ft_rate", 0.0) or 0.0))
    ast_pct = normalize_feature_value("ast_pct", float(player_vec.get("ast_pct", 0.0) or 0.0))
    dreb_pct = normalize_feature_value("dreb_pct", float(player_vec.get("dreb_pct", 0.0) or 0.0))
    tov_pct = normalize_feature_value("tov_pct", float(player_vec.get("tov_pct", 0.0) or 0.0))
    blk_pct = normalize_feature_value("blk_pct", float(player_vec.get("blk_pct", 0.0) or 0.0))
    rim_protect = normalize_feature_value("rim_protect", float(player_vec.get("rim_protect", 0.0) or 0.0))
    height_in = normalize_feature_value("height_in", float(player_vec.get("height_in", 0.0) or 0.0))
    switchability = normalize_feature_value("switchability", float(player_vec.get("switchability", 0.0) or 0.0))
    stl_pct = normalize_feature_value("stl_pct", float(player_vec.get("stl_pct", 0.0) or 0.0))
    
    # Calculate dynamic archetype scores based on weighted combinations
    role_vector = {
        "shooter": (
            0.35 * three_rate +
            0.25 * catch_shoot +
            0.25 * pullup +
            0.15 * ft_rate
        ),
        "playmaker": (
            0.5 * ast_pct +
            0.25 * dreb_pct +
            0.25 * tov_pct  # tov_pct is already inverted (lower is better)
        ),
        "rim_protector": (
            0.6 * blk_pct +
            0.4 * rim_protect
        ),
        "stretch_big": (
            0.4 * three_rate +
            0.3 * catch_shoot +
            0.3 * height_in
        ),
        "switchable_wing": (
            0.5 * switchability +
            0.25 * stl_pct +
            0.25 * dreb_pct
        )
    }
    
    # Ensure all scores are in [0, 1] range
    for archetype in role_vector:
        role_vector[archetype] = max(0.0, min(1.0, role_vector[archetype]))
    
    return role_vector


def get_top_archetypes(role_vector, n=2):
    """
    Get the top N archetypes for a player based on their role vector.
    
    Args:
        role_vector: Dictionary with archetype scores
        n: Number of top archetypes to return
        
    Returns:
        List of tuples (archetype_name, score) sorted by score descending
    """
    sorted_archetypes = sorted(role_vector.items(), key=lambda x: x[1], reverse=True)
    return sorted_archetypes[:n]


def get_position(player_vec):
    """
    Get player position using NBA API data with validation and fallbacks.
    
    Args:
        player_vec: Player vector containing position info, stats, and role vector
        
    Returns:
        str: Player position (PG, SG, SF, PF, C)
    """
    height = player_vec.get('height_in', 78)
    # Ensure height is an integer
    try:
        height = int(height)
    except (ValueError, TypeError):
        height = 78  # Default fallback
    player_id = player_vec.get('PLAYER_ID')
    
    # Known position corrections for players where NBA API is wrong
    known_positions = {
        201939: 'PG',  # Stephen Curry - API says Guard but he's a point guard
        203999: 'C',   # Nikola Jokić - API says Center but he's a center
        203110: 'PF',  # Draymond Green - API is giving wrong ID but he's a forward
        201142: 'SF',  # Kevin Durant - API says Forward but he's more of a wing
        203081: 'PG',  # Damian Lillard - API says Guard but he's a point guard
        2544: 'SF',    # LeBron James - API says Forward but he's a wing
        202691: 'SG',  # Klay Thompson - API says Guard but he's a shooting guard
        203954: 'C',   # Joel Embiid - API says Center-Forward but he's a center
        203952: 'SF',  # Andrew Wiggins - API says Forward but he's a wing
    }
    
    # Check known positions first
    if player_id in known_positions:
        position = known_positions[player_id]
        print(f"DEBUG: Player {player_id} using known position: {position}")
        return position
    
    # Try NBA API position with validation
    position = player_vec.get('POSITION', None)
    if position:
        position_lower = position.lower()
        
        # Validate NBA API position against height and stats
        if 'guard' in position_lower and 'forward' not in position_lower:
            # Pure guard - validate this makes sense
            if height >= 82:  # Guards shouldn't be 6'10"+
                # Likely wrong - use role-based inference
                pass
            else:
                # For guards, use assist rate to distinguish PG vs SG
                # PGs are primary playmakers (high assists), SGs are primary scorers (high shooting)
                ast_pct = player_vec.get('ast_pct', 0.0)
                
                if ast_pct >= 25:  # High assist rate = point guard
                    return 'PG'
                else:  # Lower assist rate = shooting guard
                    return 'SG'
                
        elif 'forward' in position_lower and 'guard' not in position_lower and 'center' not in position_lower:
            # Pure forward - validate height
            if height < 75:  # Forwards shouldn't be under 6'3"
                # Likely wrong - use role-based inference
                pass
            else:
                return 'SF' if height < 81 else 'PF'
                
        elif 'center' in position_lower:
            # Center - validate height
            if height < 78:  # Centers shouldn't be under 6'6"
                # Likely wrong - use role-based inference
                pass
            else:
                return 'C'
                
        elif 'guard' in position_lower and 'forward' in position_lower:
            # Guard-Forward (combo guard)
            return 'SG'
        elif 'forward' in position_lower and 'center' in position_lower:
            # Forward-Center (combo big)
            return 'PF' if height < 82 else 'C'
    
    # Fallback: infer from role vector and stats
    role_vector = calculate_role_vector(player_vec)
    dominant_archetype = max(role_vector, key=role_vector.get)
    
    # Map archetypes to positions with height validation
    if dominant_archetype in ['shooter', 'playmaker']:
        # Guards - validate height
        if height >= 82:  # Too tall for guard
            return 'SF' if height < 85 else 'PF'
        # Use assist rate to distinguish PG vs SG
        ast_pct = player_vec.get('ast_pct', 0.0)
        
        if ast_pct >= 25:  # High assist rate = point guard
            return 'PG'
        else:  # Lower assist rate = shooting guard
            return 'SG'
        
    elif dominant_archetype == 'switchable_wing':
        return 'SF'
        
    elif dominant_archetype in ['rim_protector', 'stretch_big']:
        # Bigs - validate height
        if height < 78:  # Too short for big
            return 'SF'
        return 'PF' if height < 82 else 'C'
    
    # Final fallback: height-based with reasonable bounds
    if height < 75:  # Under 6'3"
        return 'PG'
    elif height < 78:  # 6'3" to 6'6"
        return 'SG'
    elif height < 81:  # 6'6" to 6'9"
        return 'SF'
    elif height < 84:  # 6'9" to 7'0"
        return 'PF'
    else:  # 7'0" and above
        return 'C'


def get_dominant_archetype(role_vector, player_vector):
    """
    Refined dominant archetype assignment with thresholds and contextual tie-breaking.
    
    Args:
        role_vector: Dict with archetype scores (shooter, playmaker, rim_protector, stretch_big, switchable_wing)
        player_vector: Dict with player features including height_in, three_rate, ast_pct, etc.
    
    Returns:
        tuple: (archetype_name, strength)
    """
    height = player_vector.get('height_in', 78)
    three_rate = player_vector.get('three_rate', 0.0)
    ast_pct = player_vector.get('ast_pct', 0.0)
    catch_shoot = player_vector.get('catch_shoot', 0.0)
    
    print(f"DEBUG: get_dominant_archetype - Raw role vector: {role_vector}")
    print(f"DEBUG: get_dominant_archetype - Player context: height={height}, three_rate={three_rate:.3f}, ast_pct={ast_pct:.3f}")
    
    # Apply thresholds and tie-breakers
    shooter_score = role_vector.get('shooter', 0.0)
    playmaker_score = role_vector.get('playmaker', 0.0)
    rim_protector_score = role_vector.get('rim_protector', 0.0)
    stretch_big_score = role_vector.get('stretch_big', 0.0)
    switchable_wing_score = role_vector.get('switchable_wing', 0.0)
    
    # 1. Shooter threshold: high shooter score + high three-point indicators
    if shooter_score >= 0.5 and (three_rate > 0.3 or catch_shoot > 0.4):
        print(f"DEBUG: Shooter threshold triggered - shooter_score={shooter_score:.3f}, three_rate={three_rate:.3f}")
        return ('shooter', shooter_score)
    
    # 2. Playmaker threshold: high playmaker score + high assist rate
    if playmaker_score >= 0.5 and ast_pct > 0.25:
        print(f"DEBUG: Playmaker threshold triggered - playmaker_score={playmaker_score:.3f}, ast_pct={ast_pct:.3f}")
        return ('playmaker', playmaker_score)
    
    # 3. Big archetypes: require height > 6'6" (78 inches)
    if height >= 78:
        # Rim Protector: high rim_protector score
        if rim_protector_score >= 0.5:
            print(f"DEBUG: Rim Protector threshold triggered - rim_protector_score={rim_protector_score:.3f}, height={height}")
            return ('rim_protector', rim_protector_score)
        
        # Stretch Big: high stretch_big score
        if stretch_big_score >= 0.5:
            print(f"DEBUG: Stretch Big threshold triggered - stretch_big_score={stretch_big_score:.3f}, height={height}")
            return ('stretch_big', stretch_big_score)
    
    # 4. Switchable Wing: high score + no other archetype dominates by >= 0.1
    if switchable_wing_score >= 0.6:
        max_other = max([shooter_score, playmaker_score, rim_protector_score, stretch_big_score])
        if switchable_wing_score - max_other >= 0.1:
            print(f"DEBUG: Switchable Wing threshold triggered - switchable_wing_score={switchable_wing_score:.3f}, max_other={max_other:.3f}")
            return ('switchable_wing', switchable_wing_score)
    
    # 5. Guard vs Big heuristics for tie-breaking
    if height < 78:  # Guards
        if shooter_score > playmaker_score:
            print(f"DEBUG: Guard heuristic - shooter chosen: {shooter_score:.3f} vs {playmaker_score:.3f}")
            return ('shooter', shooter_score)
        else:
            print(f"DEBUG: Guard heuristic - playmaker chosen: {playmaker_score:.3f} vs {shooter_score:.3f}")
            return ('playmaker', playmaker_score)
    
    elif height >= 82:  # Bigs
        if rim_protector_score > stretch_big_score:
            print(f"DEBUG: Big heuristic - rim_protector chosen: {rim_protector_score:.3f} vs {stretch_big_score:.3f}")
            return ('rim_protector', rim_protector_score)
        else:
            print(f"DEBUG: Big heuristic - stretch_big chosen: {stretch_big_score:.3f} vs {rim_protector_score:.3f}")
            return ('stretch_big', stretch_big_score)
    
    else:  # Wings (78-82 inches)
        # For wings, prefer switchable_wing if it's competitive
        if switchable_wing_score >= 0.4:
            print(f"DEBUG: Wing heuristic - switchable_wing chosen: {switchable_wing_score:.3f}")
            return ('switchable_wing', switchable_wing_score)
        elif shooter_score > playmaker_score:
            print(f"DEBUG: Wing heuristic - shooter chosen: {shooter_score:.3f} vs {playmaker_score:.3f}")
            return ('shooter', shooter_score)
        else:
            print(f"DEBUG: Wing heuristic - playmaker chosen: {playmaker_score:.3f} vs {shooter_score:.3f}")
            return ('playmaker', playmaker_score)
    
    # Fallback: return the highest scoring archetype
    dominant_archetype = max(role_vector, key=role_vector.get)
    strength = role_vector[dominant_archetype]
    print(f"DEBUG: Fallback - max archetype chosen: {dominant_archetype} with strength {strength:.3f}")
    return (dominant_archetype, strength)


def compute_team_redundancy(candidate_vec, teammate_vecs, scheme=None):
    """
    Compute team redundancy using simple position overlap matrix.
    
    Args:
        candidate_vec: Player vector of the candidate player
        teammate_vecs: List of teammate player vectors
        scheme: Optional scheme vector (unused in this simplified version)
        
    Returns:
        Redundancy score (0-100): 100 = worst (identical positions), 0 = best (no overlap)
    """
    import numpy as np

    # Simple position overlap matrix
    # 100 = worst (identical positions, full redundancy)
    # 0 = best (no overlap at all, fully complementary)
    POSITION_OVERLAP = {
        "PG": {"PG": 100, "SG": 70, "SF": 40, "PF": 20, "C": 10},
        "SG": {"PG": 70, "SG": 100, "SF": 60, "PF": 30, "C": 20},
        "SF": {"PG": 40, "SG": 60, "SF": 100, "PF": 70, "C": 40},
        "PF": {"PG": 20, "SG": 30, "SF": 70, "PF": 100, "C": 80},
        "C":  {"PG": 10, "SG": 20, "SF": 40, "PF": 80, "C": 100}
    }

    # Get candidate position
    candidate_pos = get_position(candidate_vec)
    cand_id = candidate_vec.get("PLAYER_ID")
    
    print(f"DEBUG: Candidate ID={cand_id}, position={candidate_pos}")

    # Collect pairwise redundancies for each teammate (exclude candidate/self)
    pairwise_redundancies = []

    for i, tv in enumerate(teammate_vecs or []):
        # skip same object or same id if available
        if tv is candidate_vec:
            print(f"DEBUG: Redundancy - skipping teammate {i+1}: same object as candidate")
            continue
        if cand_id is not None and tv.get("PLAYER_ID") == cand_id:
            print(f"DEBUG: Redundancy - skipping teammate {i+1}: same PLAYER_ID as candidate ({cand_id})")
            continue

        # Get teammate position
        teammate_pos = get_position(tv)
        teammate_id = tv.get("PLAYER_ID")
        
        # Look up redundancy from position matrix
        redundancy = POSITION_OVERLAP[candidate_pos][teammate_pos]
        print(f"DEBUG: Candidate position={candidate_pos}, Teammate ID={teammate_id} position={teammate_pos} → redundancy={redundancy}")
        
        pairwise_redundancies.append(redundancy)

    if not pairwise_redundancies:
        # no teammates → neutral low redundancy
        team_redundancy = 0.0
        print("DEBUG: Redundancy - no valid teammates found, using neutral redundancy: 0.0")
    else:
        # Team redundancy calculation: average of all pairwise redundancies
        team_redundancy = float(np.mean(pairwise_redundancies))
        print(f"DEBUG: Redundancy - pairwise redundancies: {[f'{r:.1f}' for r in pairwise_redundancies]}, average redundancy: {team_redundancy:.1f}")

    # ---------- debugging ----------
    print(f"DEBUG: Team Redundancy = {team_redundancy:.1f} (100=worst overlap, 0=complementary/unique roles)")
    return team_redundancy


def score_player(player_vec: Dict[str, Any], scheme_vec: Dict[str, Any], roster_summary: Dict[str, Any] = None, consider_scheme_fit: bool = True) -> Dict[str, float]:
    """
    Score player-team fit using multiple components and weighted scoring.
    
    Args:
        player_vec: Dictionary containing player characteristics
        scheme_vec: Dictionary containing team scheme preferences
        roster_summary: Dictionary containing roster_vectors and roster_centroid (optional)
        consider_scheme_fit: Whether to include scheme fit in the overall score (default: True)
        
    Returns:
        Dictionary with detailed breakdown of fit components
    """
    # Map scheme sliders to player features for comparison
    scheme_to_player_mapping = {
        'pace': 'ft_rate',  # High pace = more possessions = more free throw attempts
        'three_point_volume': 'three_rate',  # High 3PT volume = high 3PT rate
        'switchability': 'switchability',  # Direct match
        'rim_pressure': 'rim_rate',  # High rim pressure = high rim rate
        'ball_movement': 'ast_pct',  # High ball movement = more assists/playmaking
        'off_glass': 'dreb_pct',  # Offensive glass = defensive rebounding
        'drop_vs_switch': 'switchability',  # Switch defense = switchability
        'foul_avoidance': 'tov_pct'  # Foul avoidance = low turnovers (inverted)
    }
    
    
    # Define player feature keys for role match
    player_feature_keys = [
        'three_rate', 'ft_rate', 'ast_pct', 'tov_pct', 
        'stl_pct', 'blk_pct', 'dreb_pct', 'switchability', 'rim_protect'
    ]
    
    # Helper function for cosine similarity
    def cosine_similarity(vec1, vec2):
        """Compute cosine similarity between two vectors."""
        if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
            return 0.0
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    # 1. Role Match: Lineup-relative calculation (0-100 scale)
    # Measures how well player fits the role defined by the current lineup centroid
    # This is dynamic - stars like Stephen Curry score highly in lineups that fit his style,
    # but lower if inserted into mismatched rosters (e.g., defensive-minded lineups)
    # 0 = very dissimilar to lineup, 100 = perfect similarity to lineup
    role_match = 0.0  # Default to no match when no roster context
    if roster_summary and roster_summary.get('lineup_centroid'):
        lineup_centroid = roster_summary['lineup_centroid']
        print(f"DEBUG: Role Match - lineup_centroid keys: {list(lineup_centroid.keys())}")
        print(f"DEBUG: Role Match - player_vec keys: {list(player_vec.keys())}")
        
        # Extract player features and lineup centroid features
        player_features = []
        centroid_features = []
        
        for key in player_feature_keys:
            player_val = player_vec.get(key, 0.0)
            centroid_val = lineup_centroid.get(key, 0.0)
            
            # Normalize features to 0-1 scale for consistent similarity calculation
            if key in ['three_rate', 'ft_rate', 'switchability', 'rim_protect']:
                # Already 0-1 scale
                player_features.append(float(player_val))
                centroid_features.append(float(centroid_val))
            else:
                # Normalize other features to 0-1 scale
                player_features.append(float(player_val) / 100.0)
                centroid_features.append(float(centroid_val) / 100.0)
        
        # Compute cosine similarity between player and lineup centroid
        # This measures how similar the player is to the average characteristics of the lineup
        player_array = np.array(player_features)
        centroid_array = np.array(centroid_features)
        similarity = cosine_similarity(player_array, centroid_array)
        
        # Linear scaling: cosine similarity (-1 to 1) → (0 to 100)
        # -1 → 0, 0 → 50, 1 → 100
        role_match = (similarity + 1) * 50
        role_match = np.clip(role_match, 0, 100)
        print(f"DEBUG: Role Match - similarity: {similarity:.3f}, final score: {role_match:.1f}")
    
    # 2. Scheme Fit: Cosine distance-based calculation (0-100 scale)
    # Measures how well player matches the team's scheme preferences
    # Only exact alignment yields 100, sliders at 50 represent neutral midpoint
    # 0 = perfect mismatch, 100 = perfect match
    if consider_scheme_fit:
        # Extract overlapping features between player and scheme
        player_scheme_values = []
        scheme_values = []
        
        for scheme_key, player_key in scheme_to_player_mapping.items():
            if scheme_key in scheme_vec and player_key in player_vec:
                scheme_val = float(scheme_vec[scheme_key])  # Slider value 0-100
                player_val = float(player_vec[player_key])  # Player feature value
                
                # Normalize player values to 0-100 scale for comparison
                if player_key == 'three_rate':
                    player_val = player_val * 100  # Convert 0-1 to 0-100
                elif player_key == 'ft_rate':
                    player_val = player_val * 100  # Convert 0-1 to 0-100
                elif player_key == 'rim_rate':
                    player_val = player_val * 100  # Convert 0-1 to 0-100
                elif player_key == 'switchability':
                    player_val = player_val * 100  # Convert 0-1 to 0-100
                elif player_key == 'tov_pct':
                    # Invert turnovers for foul avoidance (lower turnovers = better)
                    player_val = max(0, 100 - player_val * 2)  # Scale and invert
                
                player_scheme_values.append(player_val)
                scheme_values.append(scheme_val)
        
        if player_scheme_values and scheme_values:
            # Compute cosine similarity and convert to distance-based score
            # Cosine similarity range: -1 to 1
            similarity = cosine_similarity(np.array(player_scheme_values), np.array(scheme_values))
            
            # Linear scaling: cosine similarity (-1 to 1) → (0 to 100)
            # -1 → 0, 0 → 50, 1 → 100
            scheme_fit = (similarity + 1) * 50
            scheme_fit = np.clip(scheme_fit, 0, 100)
            
            print(f"DEBUG: Scheme Fit - player values: {[f'{v:.1f}' for v in player_scheme_values]}")
            print(f"DEBUG: Scheme Fit - scheme values: {[f'{v:.1f}' for v in scheme_values]}")
            print(f"DEBUG: Scheme Fit - similarity: {similarity:.3f}, final score: {scheme_fit:.1f}")
        else:
            # No overlapping features, use neutral value
            scheme_fit = 50.0
            print(f"DEBUG: Scheme Fit - no overlapping features, using default: {scheme_fit}")
    else:
        # If scheme fit is disabled, set to neutral value
        scheme_fit = 50.0
        print(f"DEBUG: Scheme Fit - disabled, using default: {scheme_fit}")
    
    # 3. Lineup Synergy: Measure how well player complements teammates (0-100 scale)
    # Higher synergy = more complementary roles, lower synergy = too similar roles
    lineup_synergy = 0.0  # Default to no synergy when no roster context
    if roster_summary and roster_summary.get('lineup_vectors'):
        lineup_vectors = roster_summary['lineup_vectors']
        if lineup_vectors:
            # Use position-based complementarity matrix for synergy calculation
            candidate_pos = get_position(player_vec)
            lineup_synergies = []
            
            for lineup_vec in lineup_vectors:
                lineup_pos = get_position(lineup_vec)
                
                # Define position complementarity matrix (higher = more complementary)
                # This is the inverse of the redundancy matrix
                POSITION_SYNERGY = {
                    "PG": {"PG": 0, "SG": 80, "SF": 60, "PF": 40, "C": 20},
                    "SG": {"PG": 80, "SG": 0, "SF": 70, "PF": 50, "C": 30},
                    "SF": {"PG": 60, "SG": 70, "SF": 0, "PF": 80, "C": 60},
                    "PF": {"PG": 40, "SG": 50, "SF": 80, "PF": 0, "C": 90},
                    "C":  {"PG": 20, "SG": 30, "SF": 60, "PF": 90, "C": 0}
                }
                
                # Get synergy score from matrix
                synergy_score = POSITION_SYNERGY.get(candidate_pos, {}).get(lineup_pos, 50)
                lineup_synergies.append(synergy_score)
            
            # Average synergy across all teammates
            lineup_synergy = np.mean(lineup_synergies)
            lineup_synergy = np.clip(lineup_synergy, 0, 100)
            
            print(f"DEBUG: Lineup Synergy - candidate position: {candidate_pos}")
            print(f"DEBUG: Lineup Synergy - teammate synergies: {lineup_synergies}, final score: {lineup_synergy:.1f}")
    else:
        print(f"DEBUG: Lineup Synergy - no lineup vectors available, using default: {lineup_synergy}")
    
    # 4. Team Redundancy: Measure role overlap with teammates (0-100 scale)
    # 0 = great (unique/complementary roles, no redundancy)
    # 100 = terrible (roles overlap/identical)
    team_redundancy = compute_team_redundancy(player_vec, roster_summary.get('lineup_vectors', []) if roster_summary else [], scheme_vec if consider_scheme_fit else None)
    
    # 5. Upside: Dynamic age-based potential (0-100 scale)
    # Formula: 100 - (age - 20) * 2
    # Age 20 = 100, Age 25 = 90, Age 30 = 80, Age 35 = 70, Age 40 = 60
    
    # Debug: Check what's actually in the player vector
    age = float(player_vec.get("age", 27))  # default if missing
    
    # Fix upside calculation to be more realistic and handle age=0 case
    if age == 0:
        # If age is unknown, use neutral upside (50)
        upside = 50.0
    else:
        # More realistic upside formula: peak at 22, decline more gradually
        # Age 22: 100, Age 25: 90, Age 30: 70, Age 35: 50, Age 37: 42, Age 40: 30
        # Uses a gentler decline curve that doesn't hit 0 until much later
        if age <= 22:
            upside = 100.0
        elif age <= 30:
            # Gentle decline from 22-30: 100 to 70
            upside = 100 - (age - 22) * 3.75
        elif age <= 40:
            # Slower decline from 30-40: 70 to 30
            upside = 70 - (age - 30) * 4
        else:
            # Very slow decline after 40: minimum 20
            upside = max(20, 30 - (age - 40) * 1)
        
        upside = np.clip(upside, 0, 100)
    
    
    # 6. Compute fit score using weighted combination of all components (0-100 scale)
    # Rebalanced weights: Role Match 30%, Scheme Fit 20%, Synergy 25%, Redundancy 15%, Upside 10%
    # This ensures upside contributes but doesn't dominate results
    if consider_scheme_fit:
        # Include all 5 components with rebalanced weighting
        # Perfect alignment: (100*0.3 + 100*0.2 + 100*0.25 + 100*0.15 + 100*0.1) = 100
        # Redundancy is inverted: high redundancy (bad overlap) → low contribution, low redundancy (good unique roles) → high contribution
        fit_score = (
            role_match * 0.30 +                    # Role Match: 30%
            scheme_fit * 0.20 +                    # Scheme Fit: 20%
            lineup_synergy * 0.25 +                # Lineup Synergy: 25%
            (100 - team_redundancy) * 0.15 +       # Team Redundancy (inverted): 15% (redundancy 0 → 100, redundancy 100 → 0)
            upside * 0.10                          # Upside: 10%
        )
    else:
        # Exclude scheme fit, rebalance remaining 4 components
        # Perfect alignment: (100*0.375 + 100*0.3125 + 100*0.1875 + 100*0.125) = 100
        # Redundancy is inverted: high redundancy (bad overlap) → low contribution, low redundancy (good unique roles) → high contribution
        fit_score = (
            role_match * 0.375 +                   # Role Match: 37.5%
            lineup_synergy * 0.3125 +              # Lineup Synergy: 31.25%
            (100 - team_redundancy) * 0.1875 +     # Team Redundancy (inverted): 18.75%
            upside * 0.125                         # Upside: 12.5%
        )
    
    # Ensure fit_score is within bounds (0-100)
    fit_score = np.clip(fit_score, 0, 100)
    
    # Debug logging for all components before final aggregation
    print("=" * 60)
    print("DEBUG: SCORING COMPONENTS BEFORE FINAL AGGREGATION")
    print("DEBUG: Note: Redundancy represents 'badness' - higher values = more role overlap")
    print("=" * 60)
    print(f"DEBUG: Role Match = {role_match:.1f}, Scheme Fit = {scheme_fit:.1f}, Lineup Synergy = {lineup_synergy:.1f}, Redundancy = {team_redundancy:.1f} (100=identical/overlapping roles, 0=complementary/unique roles), Upside = {upside:.1f}")
    print(f"DEBUG: Redundancy value being passed to UI: {team_redundancy:.1f}")
    print(f"DEBUG: Consider Scheme Fit: {consider_scheme_fit}")
    print("=" * 60)
    print(f"DEBUG: Final Fit Score: {fit_score:.1f}")
    print("=" * 60)
    
    # Determine archetype for internal use (not displayed in UI)
    def determine_archetype(player_vec):
        """Determine player archetype based on priority ordering."""
        ast_pct = player_vec.get('ast_pct', 0.0)
        blk_pct = player_vec.get('blk_pct', 0.0)
        three_rate = player_vec.get('three_rate', 0.0) * 100  # Scale to 0-100
        stl_pct = player_vec.get('stl_pct', 0.0)
        rim_protect = player_vec.get('rim_protect', 0.0) * 100
        dreb_pct = player_vec.get('dreb_pct', 0.0)
        
        # Priority ordering (check in order)
        # 1. Rim Protector (blk_pct > 3.5 or rim_protect > 0.5)
        if blk_pct > 3.5 or rim_protect > 50.0:
            return "Rim Protector"
        
        # 2. 3&D Wing (three_rate > 0.35 and stl_pct > 1.5)
        elif three_rate > 35.0 and stl_pct > 1.5:
            return "3&D Wing"
        
        # 3. Playmaking Big (ast_pct > 20 and (dreb_pct > 15 or blk_pct > 2) and three_rate < 0.25)
        elif ast_pct > 20.0 and (dreb_pct > 15.0 or blk_pct > 2.0) and three_rate < 25.0:
            return "Playmaking Big"
        
        # 4. Creator (ast_pct > 25 and three_rate > 0.3)
        elif ast_pct > 25.0 and three_rate > 30.0:
            return "Creator"
        
        # 5. Shot Creator (midrange-heavy scorers: high volume, low 3P rate, moderate playmaking)
        elif player_vec.get('FGA', 0) > 15.0 and three_rate < 25.0 and 15.0 <= ast_pct <= 30.0:
            return "Shot Creator"
        
        # 6. Scoring Wing (elite scorers: high volume OR high 3P rate, but not primary creators or playmaking bigs)
        elif (player_vec.get('FGA', 0) > 15.0 or three_rate > 25.0) and ast_pct < 30.0:
            return "Scoring Wing"
        
        # 7. Default
        else:
            return "Utility / Glue"
    
    archetype = determine_archetype(player_vec)
    
    return {
        'fit_score': fit_score,
        'role_match': role_match,
        'scheme_fit': scheme_fit,
        'lineup_synergy': lineup_synergy,
        'team_redundancy': team_redundancy,
        'upside': upside,
        'archetype': archetype
    }