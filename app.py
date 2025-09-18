import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import os
from data_api import get_active_players_df, get_player_df, get_player_season_stats, get_player_season_averages_df
from core.features import FeatureEngineer
from core.context import build_scheme_vector, summarize_roster
from core.scoring import score_player

# Set Inter font for the entire app
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Apply Inter font to all elements */
* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}

/* Specific styling for Streamlit components */
.stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    font-weight: 600 !important;
}

p, div, span {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}

/* Hide Streamlit accessibility labels that show up as text */
[aria-label*="keyboard"],
[aria-label*="arrow"],
[data-testid*="keyboard"],
[data-testid*="arrow"] {
    display: none !important;
    visibility: hidden !important;
}

/* Hide sidebar collapse button */
[data-testid="stSidebar"] button[aria-label="Close sidebar"] {
    display: none !important;
}

/* Alternative selector for sidebar close button */
.stSidebar .stButton button[aria-label*="Close"],
.stSidebar .stButton button[aria-label*="close"] {
    display: none !important;
}

/* Hide expander arrows specifically */
.stExpander [data-testid="stExpanderToggleIcon"],
.stExpander .streamlit-expanderHeader .streamlit-expanderToggleIcon,
.stExpander .streamlit-expanderHeader::after {
    display: none !important;
    visibility: hidden !important;
}

/* Hide any text content that contains keyboard_arrow_down */
* {
    font-size: inherit;
}

/* More aggressive hiding of expander elements */
.stExpander .streamlit-expanderHeader {
    position: relative;
}

.stExpander .streamlit-expanderHeader::before,
.stExpander .streamlit-expanderHeader::after {
    display: none !important;
}

/* Hide any SVG icons or text that might be showing keyboard_arrow_down */
.stExpander svg,
.stExpander [class*="icon"],
.stExpander [class*="arrow"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

def get_player_image_url(player_id):
    """Get NBA.com player image URL"""
    return f"https://cdn.nba.com/headshots/nba/latest/260x190/{player_id}.png"

def create_player_card_v6(player_name, player_id, season_stats, fit_result, analysis_type):
    """Create a player card using Streamlit native components - NO HTML - FORCE REFRESH."""
    
    # Get player info from season stats
    if season_stats:
        age = season_stats.get('age', 0)
        # Fix age if it's 0 by calculating from birthdate
        if age == 0 and 'birthdate' in season_stats:
            try:
                from datetime import datetime
                birthdate_str = season_stats.get('birthdate', '')
                if birthdate_str:
                    birthdate = datetime.strptime(birthdate_str.split('T')[0], '%Y-%m-%d')
                    today = datetime.now()
                    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
                    age = max(0, age)
            except:
                age = 0
        height = season_stats.get('height', 'Unknown')
        weight = season_stats.get('weight', 'Unknown')
        position = season_stats.get('position', 'Unknown')
        team = season_stats.get('team', 'Unknown')
        jersey = season_stats.get('jersey', 'Unknown')
        
        # Get season averages
        pts_avg = season_stats.get('PTS_avg', 0)
        reb_avg = season_stats.get('REB_avg', 0)
        ast_avg = season_stats.get('AST_avg', 0)
        fg_pct = season_stats.get('FG_PCT', 0)
        fg3_pct = season_stats.get('FG3_PCT', 0)
        ft_pct = season_stats.get('FT_PCT', 0)
        games_played = season_stats.get('games_played', 0)
        
        # Format percentages
        fg_pct_display = f"{fg_pct:.1%}" if fg_pct > 0 else "N/A"
        fg3_pct_display = f"{fg3_pct:.1%}" if fg3_pct > 0 else "N/A"
        ft_pct_display = f"{ft_pct:.1%}" if ft_pct > 0 else "N/A"
    else:
        age = 0
        height = 'Unknown'
        weight = 'Unknown'
        position = 'Unknown'
        team = 'Unknown'
        jersey = 'Unknown'
        pts_avg = 0
        reb_avg = 0
        ast_avg = 0
        fg_pct_display = "N/A"
        fg3_pct_display = "N/A"
        ft_pct_display = "N/A"
        games_played = 0
    
    # Get scores
    fit_score = fit_result.get('fit_score', 0)
    role_match = fit_result.get('role_match', 0)
    scheme_fit = fit_result.get('scheme_fit', 0)
    lineup_synergy = fit_result.get('lineup_synergy', 0)
    team_redundancy = fit_result.get('team_redundancy', 0)
    upside = fit_result.get('upside', 0)
    
    # Create player card using Streamlit native components
    # Player header
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        if player_id > 0:
            st.image(get_player_image_url(player_id), width=80)
        else:
            st.write("No Image")
    
    with col2:
        st.write(f"**{player_name}**")
        st.write(f"{position} • {team} #{jersey}")
        st.write(f"{height} • {weight} • Age {age}")
        st.write(f"Games: {games_played}")
    
    with col3:
        st.metric("Overall Fit", f"{fit_score:.1f}")
    
    st.divider()
    
    # Fit scores in big boxes (prominent)
    st.write("**Fit Analysis**")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Role Match", f"{role_match:.1f}")
    with col2:
        st.metric("Scheme Fit", f"{scheme_fit:.1f}")
    with col3:
        st.metric("Lineup Synergy", f"{lineup_synergy:.1f}")
    with col4:
        st.metric("Team Redundancy", f"{team_redundancy:.1f}")
    with col5:
        st.metric("Upside", f"{upside:.1f}")
    
    st.divider()
    
    # Player stats in small text
    st.write("**Season Stats**")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.write(f"PPG: {pts_avg:.1f}")
    with col2:
        st.write(f"RPG: {reb_avg:.1f}")
    with col3:
        st.write(f"APG: {ast_avg:.1f}")
    with col4:
        st.write(f"FG%: {fg_pct_display}")
    with col5:
        st.write(f"3P%: {fg3_pct_display}")
    with col6:
        st.write(f"FT%: {ft_pct_display}")

# Current NBA season constant

# Helper function to create human-readable feature labels
def get_feature_labels():
    """Map internal feature keys to human-readable labels."""
    return {
        'three_rate': 'Three-Point Rate',
        'ft_rate': 'Free Throw Rate', 
        'ast_pct': 'Assist %',
        'tov_pct': 'Turnover %',
        'stl_pct': 'Steal %',
        'blk_pct': 'Block %',
        'dreb_pct': 'Defensive Rebound %',
        'switchability': 'Switchability',
        'rim_protect': 'Rim Protection',
        'catch_shoot': 'Catch & Shoot',
        'pullup': 'Pull-up Shooting',
        'rim_rate': 'Rim Rate',
        'age': 'Age',
        'height_in': 'Height (inches)',
        'weight_lb': 'Weight (lbs)'
    }

def format_feature_value(value, feature_key):
    """Format feature values based on their type."""
    if feature_key in ['age', 'height_in', 'weight_lb']:
        return f"{int(round(value))}"
    elif feature_key in ['three_rate', 'ft_rate', 'switchability', 'rim_protect', 'catch_shoot', 'pullup', 'rim_rate']:
        return f"{value:.2f}"
    else:
        return f"{value:.1f}"

def create_centroid_table(centroid_data, title):
    """Create a formatted table for centroid/average characteristics."""
    if not centroid_data:
        return None
    
    feature_labels = get_feature_labels()
    
    # Create DataFrame with feature labels and values
    data = []
    for key, value in centroid_data.items():
        if key in feature_labels:
            label = feature_labels[key]
            formatted_value = format_feature_value(value, key)
            data.append({'Feature': label, 'Average': formatted_value})
    
    if not data:
        return None
    
    df = pd.DataFrame(data)
    return df

# Page configuration
st.set_page_config(
    page_title="NBA Fit",
    page_icon="🏀",
    layout="wide"
)

# Title
st.title("NBA Fit")
st.markdown("""
<style>
.custom-subheader {
    margin-top: -0.5rem !important;
    margin-bottom: 0 !important;
    font-size: 1.1rem !important;
    color: #666 !important;
    font-weight: 400 !important;
}
</style>
<div class="custom-subheader">
<h5>Team Contextual Player Valuation</h5>
</div>
""", unsafe_allow_html=True)

# Floating separator line
st.markdown("""
<div style="margin: 20px 0;">
    <div style="width: 100%; height: 2px; background-color: #e0e0e0; border-radius: 1px;"></div>
</div>
""", unsafe_allow_html=True)

# Cache scheme vector computation
@st.cache_data
def compute_scheme_vector(pace, three_point_volume, switchability, rim_pressure, 
                         ball_movement, off_glass, drop_vs_switch, foul_avoidance):
    """Cache scheme vector computation to avoid recomputing on every slider change."""
    from core.context import build_scheme_vector
    return build_scheme_vector({
        'pace': pace,
        'three_point_volume': three_point_volume,
        'switchability': switchability,
        'rim_pressure': rim_pressure,
        'ball_movement': ball_movement,
        'off_glass': off_glass,
        'drop_vs_switch': drop_vs_switch,
        'foul_avoidance': foul_avoidance
    })

# Load active players from JSON data
with st.spinner("Loading active NBA players from JSON data..."):
    try:
        active_players_df = get_active_players_df()
        player_names = active_players_df['name'].tolist() if not active_players_df.empty else []
        name_to_id = dict(zip(active_players_df['name'], active_players_df['player_id']))
        
        if active_players_df.empty:
            st.sidebar.warning("⚠️ Unable to load NBA players from JSON data.")
            st.sidebar.info("💡 The JSON data files may not be available. Try refreshing the page, or use the Custom Player option below.")
        else:
            # Show data source status
            from data_api import get_data_status
            data_status = get_data_status()
            st.sidebar.success(f"✅ Data source: {data_status['data_source']}")
            st.sidebar.info(f"📊 Loaded {len(active_players_df)} active players")
    except Exception as e:
        st.sidebar.error(f"❌ Error loading players: {str(e)}")
        st.sidebar.warning("⚠️ Unable to load JSON data. Please check your internet connection or try refreshing the page.")
        st.sidebar.info("💡 You can still use the Custom Player option below to test the fit analysis.")
        active_players_df = pd.DataFrame()
        player_names = []
        name_to_id = {}

# Sidebar with scheme sliders
st.sidebar.markdown("### Team Scheme Configuration")

# Create all sliders
pace = st.sidebar.slider("Pace", 0, 100, 50)
three_point_volume = st.sidebar.slider("3PT Volume", 0, 100, 50)
switchability = st.sidebar.slider("Switchability", 0, 100, 50)
rim_pressure = st.sidebar.slider("Rim Pressure", 0, 100, 50)
ball_movement = st.sidebar.slider("Ball Movement", 0, 100, 50)
off_glass = st.sidebar.slider("Offensive Glass", 0, 100, 50)
drop_vs_switch = st.sidebar.slider("Drop vs Switch", 0, 100, 50)
foul_avoidance = st.sidebar.slider("Foul Avoidance", 0, 100, 50)

# Collect sliders into dictionary
sliders = {
    'pace': pace,
    'three_point_volume': three_point_volume,
    'switchability': switchability,
    'rim_pressure': rim_pressure,
    'ball_movement': ball_movement,
    'off_glass': off_glass,
    'drop_vs_switch': drop_vs_switch,
    'foul_avoidance': foul_avoidance
}

# Build scheme vector using cached function
scheme_vec = compute_scheme_vector(pace, three_point_volume, switchability, rim_pressure, 
                                  ball_movement, off_glass, drop_vs_switch, foul_avoidance)

# Scheme fit toggle
consider_scheme_fit = st.sidebar.checkbox("Consider Scheme Fit", value=True)


# Use current season only - no user selection needed
CURRENT_SEASON = "2024-25"

# Player source selection at the top
player_source = st.sidebar.radio("Player Source", ["NBA Player", "Custom Player"], key="player_source_radio")

st.sidebar.subheader("Player Selection")

# Team splits toggle
show_team_splits = st.sidebar.toggle("Show team splits", value=False)

selected_player = None
selected_player_id = None
player_vec = None
player_stats_df = None

# Active players are loaded using new data API above

if player_source == "NBA Player":
    # NBA Player selection
    if player_names:
        selected_player = st.sidebar.selectbox(
            "Select a player:",
            options=player_names,
            index=0,
            key="nba_player_selectbox"
        )
        
        # Get the selected player's ID
        selected_player_id = name_to_id.get(selected_player)
        
        # Fetch player stats and build vector
        if selected_player_id:
            try:
                # Load player stats using new data API with session state caching
                player_stats_df = get_player_df(selected_player_id, CURRENT_SEASON)
                if not player_stats_df.empty:
                    # Get season stats for this player to pass to build_player_vector
                    season_stats = get_player_season_stats(selected_player_id, CURRENT_SEASON)
                    feature_engineer = FeatureEngineer()
                    # Pass the full game log data to build_player_vector
                    # The method will calculate season averages from all games
                    player_vec = feature_engineer.build_player_vector(player_stats_df, season_stats, selected_player_id)
                else:
                    st.sidebar.warning(f"⚠️ No game data available for {selected_player} in {CURRENT_SEASON}")
                    st.sidebar.info("💡 This player may not have played this season or the NBA API may be experiencing issues.")
            except Exception as e:
                st.sidebar.error(f"❌ Error loading player stats: {str(e)}")
                st.sidebar.warning("⚠️ The NBA API may be experiencing issues. Please try again in a few minutes.")

else:  # Custom Player
    st.sidebar.subheader("Custom Player Stats")
    
    # Input fields for custom player stats
    custom_name = st.sidebar.text_input("Name", value="Custom Player")
    custom_age = st.sidebar.number_input("Age", min_value=18, max_value=45, value=26)
    custom_height = st.sidebar.number_input("Height (inches)", min_value=60, max_value=90, value=78)
    custom_weight = st.sidebar.number_input("Weight (lbs)", min_value=150, max_value=350, value=215)
    
    st.sidebar.subheader("Shooting Stats")
    custom_fg_pct = st.sidebar.number_input("FG%", min_value=0.0, max_value=1.0, value=0.45, step=0.01, format="%.3f")
    custom_fga = st.sidebar.number_input("FGA", min_value=0.0, value=12.0, step=0.1)
    custom_fg3_pct = st.sidebar.number_input("3P%", min_value=0.0, max_value=1.0, value=0.35, step=0.01, format="%.3f")
    custom_fg3a = st.sidebar.number_input("3PA", min_value=0.0, value=4.0, step=0.1)
    custom_ft_pct = st.sidebar.number_input("FT%", min_value=0.0, max_value=1.0, value=0.80, step=0.01, format="%.3f")
    custom_fta = st.sidebar.number_input("FTA", min_value=0.0, value=3.0, step=0.1)
    
    st.sidebar.subheader("Other Stats")
    custom_oreb = st.sidebar.number_input("OREB", min_value=0.0, value=1.5, step=0.1)
    custom_dreb = st.sidebar.number_input("DREB", min_value=0.0, value=4.5, step=0.1)
    custom_ast = st.sidebar.number_input("AST", min_value=0.0, value=5.0, step=0.1)
    custom_stl = st.sidebar.number_input("STL", min_value=0.0, value=1.0, step=0.1)
    custom_blk = st.sidebar.number_input("BLK", min_value=0.0, value=0.5, step=0.1)
    custom_tov = st.sidebar.number_input("TOV", min_value=0.0, value=2.5, step=0.1)
    
    # Submit button for custom player
    submit_custom = st.sidebar.button("Submit Custom Player", type="primary", key="submit_custom_button")
    
    # Only process custom player when submit button is pressed
    if submit_custom:
        # Create custom player input dictionary
        custom_player_inputs = {
            'PLAYER_NAME': custom_name,
            'FG_PCT': custom_fg_pct,
            'FGA': custom_fga,
            'FG3_PCT': custom_fg3_pct,
            'FG3A': custom_fg3a,
            'FT_PCT': custom_ft_pct,
            'FTA': custom_fta,
            'OREB': custom_oreb,
            'DREB': custom_dreb,
            'AST': custom_ast,
            'STL': custom_stl,
            'BLK': custom_blk,
            'TOV': custom_tov,
            'AGE': custom_age,
            'HEIGHT_IN': custom_height,
            'WEIGHT_LB': custom_weight
        }
        
        selected_player = custom_name
        
        # Build custom player vector
        feature_engineer = FeatureEngineer()
        player_vec = feature_engineer.build_custom_vector(custom_player_inputs)
        
        # Store in session state so it persists
        st.session_state.custom_player_vec = player_vec
        st.session_state.custom_player_name = custom_name
        st.session_state.custom_player_submitted = True
    else:
        # Use session state if available, otherwise set to None
        player_vec = st.session_state.get('custom_player_vec', None)
        selected_player = st.session_state.get('custom_player_name', None)
    
    # For custom players, we don't have a stats DataFrame to display
    player_stats_df = None

# Lineup selection (for both NBA players and custom players)
if selected_player:
    st.sidebar.subheader("Lineup Analysis")
    
    # Starting lineup selection (4 players, excluding candidate)
    # Filter out the candidate player from lineup options
    lineup_options = [name for name in player_names if name != selected_player]
    starting_lineup_names = st.sidebar.multiselect(
        "Starting Lineup (without candidate):",
        options=lineup_options,
        default=[],
        max_selections=4,
        help="Select up to 4 NBA players for the starting lineup (excluding the candidate player)",
        key="lineup_selection"
    )
    
    # Get starting lineup player IDs
    starting_lineup_ids = []
    if starting_lineup_names:
        print(f"DEBUG: App - Selected lineup names: {starting_lineup_names}")
        for name in starting_lineup_names:
            player_id = name_to_id.get(name)
            if player_id:
                starting_lineup_ids.append(player_id)
        print(f"DEBUG: App - Starting lineup IDs: {starting_lineup_ids}")
    else:
        print("DEBUG: App - No lineup names selected")
    
    # Build roster summary if players are selected
    roster_summary = None
    if starting_lineup_ids:
        try:
            from core.context import summarize_roster
            from core.features import FeatureEngineer
            
            feature_engineer = FeatureEngineer()
            lineup_vectors = []
            
            for player_id in starting_lineup_ids:
                try:
                    player_stats_df = get_player_df(player_id, CURRENT_SEASON)
                    if not player_stats_df.empty:
                        # Get season stats for this player to pass to build_player_vector
                        try:
                            player_season_stats = get_player_season_stats(player_id, CURRENT_SEASON)
                            lineup_player_vec = feature_engineer.build_player_vector(player_stats_df, player_season_stats, player_id)
                            lineup_vectors.append(lineup_player_vec)
                        except Exception as e:
                            print(f"Error getting season stats for player {player_id}: {e}")
                            # Fallback without season stats
                            lineup_player_vec = feature_engineer.build_player_vector(player_stats_df, None, player_id)
                            lineup_vectors.append(lineup_player_vec)
                except Exception as e:
                    print(f"Error loading player {player_id}: {e}")
                    continue
            
            if lineup_vectors:
                print(f"DEBUG: App - Created {len(lineup_vectors)} lineup vectors")
                print(f"DEBUG: App - First lineup vector keys: {list(lineup_vectors[0].keys()) if lineup_vectors else 'None'}")
                print(f"DEBUG: App - Lineup vector PLAYER_IDs: {[vec.get('PLAYER_ID') for vec in lineup_vectors]}")
                roster_summary = summarize_roster(lineup_vectors)
                print(f"DEBUG: App - Roster summary keys: {list(roster_summary.keys()) if roster_summary else 'None'}")
            else:
                print("DEBUG: App - No lineup vectors created")
                roster_summary = None
        except Exception as e:
            st.sidebar.warning(f"❌ Error analyzing roster: {str(e)}")
            print(f"DEBUG: App - Roster analysis error: {str(e)}")
            roster_summary = None
    
    # Score player fit
    lineup_fit_result = None
    
    if player_vec is not None:
        if roster_summary:
            # Create lineup summary for fit analysis
            lineup_summary = {
                'lineup_vectors': roster_summary.get('lineup_vectors', []),
                'lineup_centroid': roster_summary.get('lineup_centroid', {}),
            }
            
            print(f"DEBUG: App - lineup_summary keys: {list(lineup_summary.keys())}")
            print(f"DEBUG: App - lineup_vectors count: {len(lineup_summary.get('lineup_vectors', []))}")
            print(f"DEBUG: App - scheme_vec: {scheme_vec}")
            print(f"DEBUG: App - consider_scheme_fit: {consider_scheme_fit}")
            
            print(f"DEBUG: App - About to score player {player_vec.get('PLAYER_ID')} against lineup with {len(lineup_summary.get('lineup_vectors', []))} teammates")
            lineup_fit_result = score_player(player_vec, scheme_vec, lineup_summary, consider_scheme_fit)
        else:
            # For custom players or when no roster is selected, score without roster context
            print(f"DEBUG: App - No roster selected, scoring without roster context")
            print(f"DEBUG: App - scheme_vec: {scheme_vec}")
            print(f"DEBUG: App - consider_scheme_fit: {consider_scheme_fit}")
            
            lineup_fit_result = score_player(player_vec, scheme_vec, None, consider_scheme_fit)
    
    # Display lineup fit analysis with beautiful player card
    if lineup_fit_result is not None:
        st.subheader("Lineup Fit Analysis")
        
        # Create beautiful player card with NBA API data
        if player_source == "NBA Player" and selected_player_id:
            season_stats = get_player_season_stats(selected_player_id, CURRENT_SEASON)
            create_player_card_v6(selected_player, selected_player_id, season_stats, lineup_fit_result, "Lineup Fit")
        else:
            # For custom players, use placeholder data
            create_player_card_v6(selected_player, 0, {}, lineup_fit_result, "Lineup Fit")
        
        
        # Show visualization message for custom players
        if player_source == "Custom Player":
            st.info("📊 Visualizations are not currently available for custom players. This feature will be added in a future update.")
        
        # Display lineup summary if available
        if roster_summary:
            # Display lineup analysis
            if roster_summary.get('lineup_vectors'):
                st.markdown("---")  # Add a clean separator
                st.subheader("Lineup Analysis")
                lineup_players_count = len(roster_summary['lineup_vectors'])
                if player_vec is not None:
                    total_analyzing = lineup_players_count + 1
                    st.write(f"Analyzing {total_analyzing} starting lineup players ({lineup_players_count} selected + 1 candidate)")
                else:
                    st.write(f"Analyzing {lineup_players_count} starting lineup players")
                
                # Show starting lineup centroid
                if roster_summary.get('lineup_centroid'):
                    centroid_df = create_centroid_table(roster_summary['lineup_centroid'], "Starting Lineup")
                    if centroid_df is not None:
                        st.dataframe(centroid_df, use_container_width=True, hide_index=True, height=400)
                
                # Add download button for CSV
                csv_data = centroid_df.to_csv(index=False)
                st.download_button(
                    label="Download Starting Lineup Data (CSV)",
                    data=csv_data,
                    file_name="starting_lineup_characteristics.csv",
                    mime="text/csv"
                )
    

# Display player stats if available
if selected_player and player_source == "NBA Player" and selected_player_id:
    # Use NBA API data for season averages
    season_averages_df = get_player_season_averages_df(selected_player_id, CURRENT_SEASON)
    if not season_averages_df.empty:
        st.markdown(f"""
        <style>
        .season-stats-header {{
            font-size: 1.05rem !important;
            font-weight: 600 !important;
            margin-top: 2rem !important;
            margin-bottom: 0.5rem !important;
        }}
        </style>
        <div class="season-stats-header">Candidate's Season Stats</div>
        """, unsafe_allow_html=True)
        st.dataframe(season_averages_df, use_container_width=True)
elif selected_player and player_stats_df is not None and not player_stats_df.empty:
    # Fallback for custom players or when NBA API data not available
    splits_text = " (with team splits)" if show_team_splits else ""
    st.markdown(f"""
    <style>
    .season-stats-header {{
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        margin-top: 2rem !important;
        margin-bottom: 0.5rem !important;
    }}
    </style>
    <div class="season-stats-header">Candidate's Season Stats{splits_text}</div>
    """, unsafe_allow_html=True)
    st.dataframe(player_stats_df, use_container_width=True)

# Display radar chart for player vs scheme fit (for all players)
if player_vec is not None:
    # Define the features to display in radar chart
    radar_features = [
        'three_rate', 'ft_rate', 'ast_pct', 'tov_pct', 
        'stl_pct', 'blk_pct', 'dreb_pct', 'switchability', 'rim_protect'
    ]
    
    # Normalize features to 0-100 scale
    def normalize_feature(value, feature_name):
        if feature_name in ['three_rate', 'ft_rate', 'switchability', 'rim_protect']:
            # These are already 0-1 scale, convert to 0-100
            return min(100, max(0, value * 100))
        else:
            # These are already in appropriate ranges, just ensure 0-100
            return min(100, max(0, value))
    
    # Extract and normalize player values
    player_values = []
    scheme_values = []
    
    for feature in radar_features:
        player_val = player_vec.get(feature, 0)
        scheme_val = scheme_vec.get(feature, 0)
        
        player_values.append(normalize_feature(player_val, feature))
        scheme_values.append(normalize_feature(scheme_val, feature))
    
    # Create radar chart
    fig = go.Figure()
    
    # Add player vector (blue)
    fig.add_trace(go.Scatterpolar(
        r=player_values,
        theta=radar_features,
        fill='toself',
        name='Player',
        line_color='blue',
        fillcolor='rgba(0, 100, 255, 0.3)'
    ))
    
    # Add scheme vector (red)
    fig.add_trace(go.Scatterpolar(
        r=scheme_values,
        theta=radar_features,
        fill='toself',
        name='Scheme',
        line_color='red',
        fillcolor='rgba(255, 0, 0, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title="Player vs Scheme Fit",
        height=500
    )
    
    # Display radar chart and fit score breakdown side by side
    if lineup_fit_result is not None:
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Prepare data for bar chart
            breakdown_data = {
                'Component': ['Role Match', 'Scheme Fit', 'Lineup Synergy', 'Team Redundancy', 'Upside'],
                'Score': [
                    lineup_fit_result['role_match'],
                    lineup_fit_result['scheme_fit'],
                    lineup_fit_result['lineup_synergy'],
                    100 - lineup_fit_result['team_redundancy'],  # Invert redundancy for display
                    lineup_fit_result['upside']
                ]
            }
            
            # Create horizontal bar chart
            fig_bar = px.bar(
                x=breakdown_data['Score'],
                y=breakdown_data['Component'],
                orientation='h',
                title="Fit Score Components",
                labels={'x': 'Score (0-100)', 'y': 'Component'},
                color=breakdown_data['Score'],
                color_continuous_scale='RdYlGn'
            )
            
            fig_bar.update_layout(
                height=500,
                showlegend=False,
                xaxis=dict(range=[0, 100])
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.plotly_chart(fig, use_container_width=True)
    
    # Handle cases where no stats are available
    if selected_player and player_source == "NBA Player" and player_stats_df is not None and player_stats_df.empty:
        st.warning(f"No stats available for {selected_player} in the {CURRENT_SEASON} season")
    if selected_player and player_source == "NBA Player" and 'unique_seasons' in locals() and not unique_seasons:
        st.warning(f"No career data available for {selected_player}")
    if selected_player and player_source == "NBA Player" and player_stats_df is None:
        st.info("Loading player statistics...")

# Masthead at the bottom
st.markdown("""
<div style="text-align: center; margin-top: 3rem; padding: 1rem 0; border-top: 1px solid #e0e0e0;">
    <p style="font-size: 0.8rem; color: #888; margin: 0;">by Chloe Wong - 2025</p>
</div>
""", unsafe_allow_html=True)