import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from services.nba_client import NBAClient
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

def create_player_card(player_name, player_vec, fit_result, analysis_type):
    """Create a player card using the working structure from the previous example."""
    
    # Get player info and scores
    if player_vec:
        age = int(player_vec.get('age', 0))
        height_in = int(player_vec.get('height_in', 0))
        weight_lb = int(player_vec.get('weight_lb', 0))
        position = player_vec.get('POSITION', 'Unknown')
        player_id = player_vec.get('PLAYER_ID', 0)
        
        # Convert height to feet and inches
        feet = height_in // 12
        inches = height_in % 12
        height_display = f"{feet}'{inches}\""
    else:
        age = 0
        height_in = 0
        weight_lb = 0
        position = 'Unknown'
        player_id = 0
        height_display = "N/A"
    
    # Get scores
    fit_score = fit_result.get('fit_score', 0)
    role_match = fit_result.get('role_match', 0)
    scheme_fit = fit_result.get('scheme_fit', 0)
    lineup_synergy = fit_result.get('lineup_synergy', 0)
    team_redundancy = fit_result.get('team_redundancy', 0)
    
    # Create custom CSS for the card (using the working structure)
    card_css = """
    <style>
    .player-card {
        background: #f5f5f5;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border: 1px solid #f0f0f0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .player-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    }
    .player-header {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
        gap: 15px;
        flex-wrap: nowrap;
    }
    .player-image {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #f0f0f0;
        flex-shrink: 0;
    }
    .player-info {
        flex: 1;
        min-width: 0;
        overflow: hidden;
    }
    .player-info h3 {
        margin: 0;
        color: #333;
        font-size: 18px;
        font-weight: 600;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .player-info p {
        margin: 5px 0 0 0;
        color: #666;
        font-size: 14px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 15px;
        margin-top: 15px;
    }
    .stat-item {
        text-align: center;
        padding: 10px;
        background: #e8e8e8;
        border-radius: 8px;
    }
    .stat-value {
        font-size: 20px;
        font-weight: bold;
        color: #2c3e50;
        margin: 0;
    }
    .stat-label {
        font-size: 12px;
        color: #7f8c8d;
        margin: 5px 0 0 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .main-score {
        text-align: center;
        margin: 20px 0;
    }
    .main-score-value {
        font-size: 48px;
        font-weight: bold;
        color: #2c3e50;
        margin: 0;
    }
    .main-score-label {
        font-size: 16px;
        color: #7f8c8d;
        margin: 5px 0 0 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    /* Hide Streamlit accessibility labels and internal text */
    [aria-label*="keyboard"],
    [aria-label*="arrow"],
    [data-testid*="keyboard"],
    [data-testid*="arrow"],
    .stMetric [aria-label*="keyboard"],
    .stMetric [aria-label*="arrow"] {
        display: none !important;
        visibility: hidden !important;
    }
    </style>
    """
    
    st.markdown(card_css, unsafe_allow_html=True)
    
    # Get player image URL
    image_url = get_player_image_url(player_id)
    
    # Create the card HTML (using the working structure)
    card_html = f"""
    <div class="player-card">
        <div class="player-header">
            <div class="image-container">
                <img src="{image_url}" alt="{player_name}" class="player-image" 
                     onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                <div class="no-image-placeholder" style="display: none; width: 60px; height: 60px; border-radius: 50%; background: #f0f0f0; margin-right: 15px; align-items: center; justify-content: center; color: #999; font-size: 12px;">No Image</div>
            </div>
            <div class="player-info">
                <h3>{player_name or 'Custom Player'}</h3>
                <p>{position} • {CURRENT_SEASON}</p>
            </div>
            <div class="main-score" style="margin-left: auto; text-align: right; padding-right: 10px; flex-shrink: 0; min-width: 120px;">
                <div class="main-score-value" style="font-size: 36px; margin: 0; line-height: 1;">{fit_score:.1f}</div>
                <div class="main-score-label" style="font-size: 12px; margin: 0; line-height: 1.2;">Overall Fit Score</div>
            </div>
        </div>
        <div class="stats-grid">
            <div class="stat-item">
                <p class="stat-value">{role_match:.1f}</p>
                <p class="stat-label">Role Match</p>
            </div>
            <div class="stat-item">
                <p class="stat-value">{scheme_fit:.1f}</p>
                <p class="stat-label">Scheme Fit</p>
            </div>
            <div class="stat-item">
                <p class="stat-value">{lineup_synergy:.1f}</p>
                <p class="stat-label">Synergy</p>
            </div>
            <div class="stat-item">
                <p class="stat-value">{100 - team_redundancy:.1f}</p>
                <p class="stat-label">Uniqueness</p>
            </div>
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

# Current NBA season constant
CURRENT_SEASON = "2024-25"

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

# Initialize NBA client
@st.cache_resource
def get_nba_client():
    return NBAClient()

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

# Build scheme vector
scheme_vec = build_scheme_vector(sliders)

# Scheme fit toggle
consider_scheme_fit = st.sidebar.checkbox("Consider Scheme Fit", value=True)

# Player source selection at the top
player_source = st.sidebar.radio("Player Source", ["NBA Player", "Custom Player"], key="player_source_radio")

st.sidebar.subheader("Player Selection")

# Team splits toggle
show_team_splits = st.sidebar.toggle("Show team splits", value=False)

nba_client = get_nba_client()
selected_player = None
selected_player_id = None
player_vec = None
player_stats_df = None

# Get active players for lineup selection (needed for both NBA and custom players)
with st.spinner("Loading active NBA players..."):
    try:
        st.write("🔍 Debug: Fetching active players from NBA API...")
        active_players_df = nba_client.get_active_players()
        player_names = active_players_df['full_name'].tolist() if not active_players_df.empty else []
        st.write(f"✅ Debug: Successfully loaded {len(player_names)} active players")
    except Exception as e:
        st.sidebar.error(f"❌ Error loading players: {str(e)}")
        st.write(f"🔍 Debug: Full error details: {str(e)}")
        active_players_df = pd.DataFrame()
        player_names = []

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
        selected_player_id = active_players_df[
            active_players_df['full_name'] == selected_player
        ]['id'].iloc[0]
        
        # Fetch player stats and build vector
        if selected_player_id:
            try:
                # Check if the method exists
                if not hasattr(nba_client, 'get_player_per_game'):
                    st.sidebar.error("NBA client is missing required method. Please redeploy the application with the latest code.")
                else:
                    st.write(f"🔍 Debug: Fetching stats for player ID {selected_player_id} for season {CURRENT_SEASON}")
                    player_stats_df = nba_client.get_player_per_game(selected_player_id, CURRENT_SEASON, include_splits=show_team_splits)
                    if not player_stats_df.empty:
                        st.write(f"✅ Debug: Successfully loaded player stats. Shape: {player_stats_df.shape}")
                        feature_engineer = FeatureEngineer()
                        # For NBA players, we want the TOT row or single row (not splits)
                        if show_team_splits:
                            # If showing splits, get the TOT row for the vector
                            tot_row = player_stats_df[player_stats_df['TEAM_ABBREVIATION'] == 'TOT']
                            if not tot_row.empty:
                                player_vec = feature_engineer.build_player_vector(tot_row)
                                st.write("✅ Debug: Built player vector from TOT row")
                            else:
                                # Use first row if no TOT
                                player_vec = feature_engineer.build_player_vector(player_stats_df.iloc[:1])
                                st.write("✅ Debug: Built player vector from first row (no TOT)")
                        else:
                            # Already have TOT or single row
                            player_vec = feature_engineer.build_player_vector(player_stats_df)
                            st.write("✅ Debug: Built player vector from single row")
                    else:
                        st.write("⚠️ Debug: No player stats data returned")
            except Exception as e:
                st.sidebar.error(f"Error fetching player stats: {str(e)}")
                # Add more detailed error information for debugging
                import traceback
                st.sidebar.error(f"Full error details: {traceback.format_exc()}")

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
    starting_lineup_names = st.sidebar.multiselect(
        "Starting Lineup (without candidate):",
        options=player_names,
        default=[],
        max_selections=4,
        help="Select up to 4 NBA players for the starting lineup (excluding the candidate player)",
        key="lineup_selection"
    )
    
    # Get starting lineup player IDs
    starting_lineup_ids = []
    if starting_lineup_names:
        for name in starting_lineup_names:
            player_id = active_players_df[
                active_players_df['full_name'] == name
            ]['id'].iloc[0]
            starting_lineup_ids.append(player_id)
else:
    # No roster selection when no player is selected
    starting_lineup_ids = []
    full_roster_ids = []

# Build roster summary if players are selected (works for both NBA and custom players)
roster_summary = None
if starting_lineup_ids:
    with st.spinner("Analyzing lineup..."):
        try:
            st.write(f"🔍 Debug: Analyzing roster with {len(starting_lineup_ids)} players")
            roster_summary = summarize_roster(starting_lineup_ids, [], CURRENT_SEASON)
            st.write("✅ Debug: Successfully analyzed roster")
        except Exception as e:
            st.sidebar.warning(f"❌ Error analyzing roster: {str(e)}")
            st.write(f"🔍 Debug: Roster analysis error: {str(e)}")
            roster_summary = None

# Score player fit
lineup_fit_result = None

if player_vec is not None:
    st.write("🔍 Debug: Starting player fit scoring...")
    if roster_summary:
        # Create lineup summary for fit analysis
        lineup_summary = {
            'lineup_vectors': roster_summary.get('lineup_vectors', []),
            'lineup_centroid': roster_summary.get('lineup_centroid', {}),
        }
        
        st.write(f"🔍 Debug: Scoring with roster context. Lineup vectors: {len(lineup_summary['lineup_vectors'])}")
        print(f"DEBUG: App - lineup_summary keys: {list(lineup_summary.keys())}")
        print(f"DEBUG: App - scheme_vec: {scheme_vec}")
        print(f"DEBUG: App - consider_scheme_fit: {consider_scheme_fit}")
        
        lineup_fit_result = score_player(player_vec, scheme_vec, lineup_summary, consider_scheme_fit)
        st.write("✅ Debug: Successfully scored player fit with roster context")
    else:
        # For custom players or when no roster is selected, score without roster context
        st.write("🔍 Debug: Scoring without roster context")
        print(f"DEBUG: App - No roster selected, scoring without roster context")
        print(f"DEBUG: App - scheme_vec: {scheme_vec}")
        print(f"DEBUG: App - consider_scheme_fit: {consider_scheme_fit}")
        
        lineup_fit_result = score_player(player_vec, scheme_vec, None, consider_scheme_fit)
        st.write("✅ Debug: Successfully scored player fit without roster context")


# Display lineup fit analysis with beautiful player card
if lineup_fit_result is not None:
    st.subheader("Lineup Fit Analysis")
    
    # Create beautiful player card
    create_player_card(selected_player, player_vec, lineup_fit_result, "Lineup Fit")
    
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
if selected_player and player_stats_df is not None and not player_stats_df.empty:
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
    <div class="season-stats-header">Season Stats{splits_text}</div>
    """, unsafe_allow_html=True)
    st.dataframe(player_stats_df, use_container_width=True)
    
    # Display radar chart for player vs scheme fit
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
elif selected_player and player_source == "NBA Player" and player_stats_df is not None and player_stats_df.empty:
    st.warning(f"No stats available for {selected_player} in the {CURRENT_SEASON} season")
elif selected_player and player_source == "NBA Player" and 'unique_seasons' in locals() and not unique_seasons:
    st.warning(f"No career data available for {selected_player}")
elif selected_player and player_source == "NBA Player" and player_stats_df is None:
    st.info("Loading player statistics...")

# Masthead at the bottom
st.markdown("""
<div style="text-align: center; margin-top: 3rem; padding: 1rem 0; border-top: 1px solid #e0e0e0;">
    <p style="font-size: 0.8rem; color: #888; margin: 0;">by Chloe Wong - 2025</p>
</div>
""", unsafe_allow_html=True)