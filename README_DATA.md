# NBA Fit Data Management

This document explains how to generate, host, and update the JSON data files used by the NBA Fit app.

## Overview

The NBA Fit app now uses static JSON files hosted on GitHub Pages instead of making direct API calls to the NBA API. This approach:

- ✅ **Eliminates API blocking issues** - No more timeout problems on cloud platforms
- ✅ **Improves performance** - Faster loading with cached JSON files
- ✅ **Reduces API usage** - Only fetch data when updating, not on every app load
- ✅ **Works everywhere** - No proxy configuration needed
- ✅ **Easy deployment** - Simple GitHub Pages setup

## Data Structure

The app expects JSON files in the following structure:

```
data/
├── active_players.json
└── players/
    ├── {player_id}_gamelog.json
    ├── {player_id}_info.json
    └── {player_id}_season_stats.json
```

When hosted on GitHub Pages, this becomes:

```
https://username.github.io/nba-fit-data/
├── index.html              # Landing page (prevents 404 errors)
├── active_players.json
└── players/
    ├── 201939_gamelog.json
    ├── 201939_info.json
    ├── 201939_season_stats.json
    ├── 203110_gamelog.json
    ├── 203110_info.json
    ├── 203110_season_stats.json
    └── ...
```

## JSON File Formats

### 1. `active_players.json`
```json
{
  "players": [
    {
      "player_id": 201939,
      "name": "Stephen Curry"
    },
    {
      "player_id": 203110,
      "name": "Draymond Green"
    }
  ]
}
```

### 2. `players/{player_id}_gamelog.json`
```json
{
  "games": [
    {
      "GAME_DATE": "2024-10-15",
      "MATCHUP": "GSW vs. LAL",
      "MIN": 32.5,
      "FGM": 8,
      "FGA": 18,
      "FG3M": 4,
      "FG3A": 11,
      "FTM": 4,
      "FTA": 4,
      "REB": 4,
      "AST": 6,
      "STL": 1,
      "BLK": 0,
      "TOV": 2,
      "PF": 1,
      "PTS": 24,
      "PLUS_MINUS": 8
    }
  ]
}
```

### 3. `players/{player_id}_info.json`
```json
{
  "player_info": {
    "position": "Guard",
    "height": "6-2",
    "weight": "185",
    "age": 35,
    "team": "Warriors",
    "jersey": "30"
  }
}
```

### 4. `players/{player_id}_season_stats.json`
```json
{
  "season_stats": {
    "MIN_avg": 32.1,
    "PTS_avg": 24.5,
    "REB_avg": 4.4,
    "AST_avg": 6.0,
    "FG_PCT": 0.448,
    "FG3_PCT": 0.397,
    "FT_PCT": 0.920,
    "games_played": 70
  }
}
```

## Quick Start Guide

### Step 1: Generate NBA Data Locally

Run the data generation script to fetch all NBA data:

```bash
# Install required dependencies
pip install nba_api pandas

# Generate all NBA data for 2024-25 season
python3 generate_full_data.py
```

This will create a `data/` folder with all the JSON files needed.

### Step 2: Create GitHub Repository for Data

1. **Create a new GitHub repository:**
   - Go to GitHub and create a new repository
   - Name it `nba-fit-data` (or your preferred name)
   - Make it public (required for free GitHub Pages)
   - Don't initialize with README (we'll add files manually)

2. **Upload the data folder:**
   ```bash
   # Clone your new repository
   git clone https://github.com/yourusername/nba-fit-data.git
   cd nba-fit-data
   
   # Copy the generated data folder and index file
   cp -r /path/to/nba-fit/data/ .
   cp /path/to/nba-fit/index.html .
   
   # Commit and push
   git add .
   git commit -m "Add NBA data JSON files and index page"
   git push origin main
   ```

3. **Enable GitHub Pages:**
   - Go to your repository on GitHub
   - Click Settings → Pages
   - Source: Deploy from a branch
   - Branch: `main`
   - Folder: `/ (root)`
   - Click Save

4. **Get your GitHub Pages URL:**
   - Your data will be available at: `https://yourusername.github.io/nba-fit-data/`
   - Note this URL - you'll need it for the next step

### Step 3: Configure the NBA Fit App

Update the `config.py` file in your NBA Fit app:

```python
# config.py
DEFAULT_BASE_DATA_URL = "https://yourusername.github.io/nba-fit-data/"
```

Or set the environment variable:
```bash
export NBA_DATA_BASE_URL="https://yourusername.github.io/nba-fit-data/"
```

### Step 4: Deploy Your NBA Fit App

Your NBA Fit app will now load data from GitHub Pages instead of the NBA API:

```bash
streamlit run app.py
```

You should see:
- ✅ "Data source: GitHub Pages JSON" in the sidebar
- 📊 "Loaded X active players" message
- No API timeout errors

## Detailed Setup Instructions

### Step 1: Generate JSON Data

The `generate_full_data.py` script will:

1. **Fetch active players** from the NBA API
2. **For each player, fetch:**
   - Player biographical information
   - Game log data for the 2024-25 season
   - Calculate season statistics
3. **Save all data** in the correct JSON format
4. **Create the directory structure** needed by the app

**Script Features:**
- ✅ **Progress tracking** - Shows which player is being processed
- ✅ **Error handling** - Continues if individual players fail
- ✅ **Skip existing files** - Won't re-download if files already exist
- ✅ **Rate limiting** - Adds delays between API calls
- ✅ **Comprehensive logging** - Shows detailed progress and errors

**Usage:**
```bash
# Generate all data (this may take 30-60 minutes)
python3 generate_full_data.py

# For testing, you can limit the number of players by editing the script
# Set MAX_PLAYERS = 10 in generate_full_data.py for quick testing
```

### Step 2: Upload to GitHub Pages

1. **Create the GitHub repository:**
   ```bash
   # Create a new repository on GitHub (e.g., nba-fit-data)
   # Then clone it locally
   git clone https://github.com/yourusername/nba-fit-data.git
   cd nba-fit-data
   ```

2. **Copy the generated data and index file:**
   ```bash
   # Copy the data folder from your NBA Fit project
   cp -r /path/to/nba-fit/data/ .
   
   # Copy the index.html file for GitHub Pages
   cp /path/to/nba-fit/index.html .
   
   # Commit and push
   git add .
   git commit -m "Add NBA data JSON files and index page for 2024-25 season"
   git push origin main
   ```

3. **Enable GitHub Pages:**
   - Go to your repository on GitHub
   - Settings → Pages
   - Source: Deploy from a branch
   - Branch: `main`
   - Folder: `/ (root)`
   - Save

4. **Wait for deployment** (usually takes 2-5 minutes)

### Step 3: Configure the NBA Fit App

Update the `config.py` file with your GitHub Pages URL:

```python
# config.py
DEFAULT_BASE_DATA_URL = "https://yourusername.github.io/nba-fit-data/"
```

Or set the environment variable:
```bash
export NBA_DATA_BASE_URL="https://yourusername.github.io/nba-fit-data/"
```

## Updating Data

To update the data files:

1. **Run the generation script again** to fetch fresh data
2. **Commit and push** the updated JSON files
3. **GitHub Pages will automatically update** (may take a few minutes)

## Testing

Test your setup by running the app:

```bash
streamlit run app.py
```

You should see:
- ✅ "Data source: GitHub Pages JSON" in the sidebar
- 📊 "Loaded X active players" message
- No API timeout errors

## Troubleshooting

### Common Issues

1. **"Failed to load JSON data"**
   - Check that GitHub Pages is enabled and deployed
   - Verify the base URL in `config.py` is correct
   - Ensure JSON files are in the correct format

2. **"No 'players' key in JSON data"**
   - Check that `active_players.json` has the correct structure
   - Verify the JSON is valid (use a JSON validator)

3. **"404 Not Found" for player data**
   - Ensure the `players/` directory exists
   - Check that player JSON files are named correctly
   - Verify the player ID matches the filename

### Debug Mode

Enable debug logging to see detailed information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Best Practices

1. **Regular Updates**: Update data weekly or after major NBA events
2. **Error Handling**: The generation script should handle API failures gracefully
3. **Rate Limiting**: Add delays between API calls to avoid being blocked
4. **Backup**: Keep a backup of your JSON files
5. **Validation**: Validate JSON files before uploading

## File Sizes

Typical file sizes:
- `active_players.json`: ~50KB (500+ players)
- `players/{id}_gamelog.json`: ~10-50KB per player (depending on games played)
- `players/{id}_info.json`: ~200 bytes per player

Total repository size: ~10-50MB depending on how many players you include.

## Security

- GitHub Pages is public by default
- No sensitive data should be included in JSON files
- Consider using a private repository if needed (requires GitHub Pro)

## Performance

- JSON files are cached by the app for 15 minutes to 24 hours
- GitHub Pages provides global CDN for fast loading
- Much faster than direct API calls
- No rate limiting issues
