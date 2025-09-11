import streamlit as st
from services.nba_client import NBAClient

# Page configuration
st.set_page_config(
    page_title="NBA Fit",
    page_icon="🏀",
    layout="wide"
)

# Title
st.title("NBA Fit — Team Contextual Player Valuation")

# Initialize NBA client
@st.cache_resource
def get_nba_client():
    return NBAClient()

# Sidebar with Pace slider
st.sidebar.header("Configuration")
pace = st.sidebar.slider("Pace", 0, 100, 50)

# Player selection
st.sidebar.subheader("Player Selection")
nba_client = get_nba_client()

# Get active players
with st.spinner("Loading active NBA players..."):
    try:
        active_players_df = nba_client.get_active_players()
        
        if not active_players_df.empty:
            # Create dropdown with player names
            player_names = active_players_df['full_name'].tolist()
            selected_player = st.sidebar.selectbox(
                "Select a player:",
                options=player_names,
                index=0
            )
            
            # Get the selected player's ID
            selected_player_id = active_players_df[
                active_players_df['full_name'] == selected_player
            ]['id'].iloc[0]
            
        else:
            st.sidebar.error("No active players found")
            selected_player = None
            selected_player_id = None
            
    except Exception as e:
        st.sidebar.error(f"Error loading players: {str(e)}")
        selected_player = None
        selected_player_id = None

# Display the pace value and selected player info on the main page
col1, col2 = st.columns(2)

with col1:
    st.write(f"Current Pace: {pace}")

with col2:
    if selected_player and selected_player_id:
        st.write(f"Selected Player: {selected_player}")
        st.write(f"Player ID: {selected_player_id}")
    else:
        st.write("No player selected")
