# NBA Fit 🏀

A Streamlit application for analyzing NBA player-team fit using advanced analytics and machine learning techniques.

## Features

- **Player Analysis**: Comprehensive player statistics and performance metrics
- **Team Assessment**: Team needs and roster analysis
- **Fit Scoring**: Advanced algorithms to calculate player-team compatibility
- **Interactive UI**: User-friendly interface with real-time analysis
- **Visualizations**: Charts and graphs for better insights

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd nba-fit
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

To run the NBA Fit application:

```bash
streamlit run app.py
```

The application will start and be available at `http://localhost:8501` in your web browser.

## How to Use

1. **Configure Team Scheme**: Use the sliders in the sidebar to define your team's playing style:
   - Pace: Team's preferred pace of play
   - 3PT Volume: Emphasis on three-point shooting
   - Switchability: Defensive switching preferences
   - Rim Pressure: Rim protection and pressure
   - Ball Movement: Ball movement and passing emphasis
   - Offensive Glass: Offensive rebounding priority
   - Drop vs Switch: Defensive coverage preferences
   - Foul Avoidance: Foul discipline emphasis

2. **Scheme Fit Toggle**: By default, Scheme Fit is included in player evaluation. You can disable it with the "Consider Scheme Fit" checkbox if you only want to evaluate roster fit without scheme alignment.

3. **Select Player**: Choose between NBA Player or Custom Player:
   - **NBA Player**: Select from active NBA players and view their statistics
   - **Custom Player**: Input custom player statistics manually

4. **Configure Roster**: Select starting lineup and bench players to analyze fit within team context

5. **Analyze Fit**: The application automatically calculates:
   - **Role Match**: How well the player fits their role archetype
   - **Scheme Fit**: How well the player matches the team's scheme (when enabled)
   - **Lineup Synergy**: Complementarity with starting lineup
   - **Team Redundancy**: Similarity to existing roster players
   - **Upside**: Age-based potential

6. **Review Results**: Examine the detailed breakdown, visualizations, and fit scores

## Project Structure

```
nba-fit/
├── app.py                 # Main Streamlit application
├── core/
│   ├── __init__.py
│   ├── features.py        # Feature engineering module
│   ├── scoring.py         # Scoring algorithms with scheme fit toggle
│   └── context.py         # Team context and roster analysis
├── services/
│   ├── __init__.py
│   └── nba_client.py      # NBA API client
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Components

### Core Modules

- **`features.py`**: Contains the `FeatureEngineer` class for processing player and team data into meaningful features, including custom player input support
- **`scoring.py`**: Implements advanced scoring algorithms with scheme fit toggle, role match, lineup synergy, and team redundancy calculations
- **`context.py`**: Handles team context building and roster analysis for comprehensive fit evaluation

### Services

- **`nba_client.py`**: NBA API client for fetching active players and career statistics with season filtering

### Main Application

- **`app.py`**: Streamlit application with interactive UI featuring scheme configuration, player selection, roster analysis, and comprehensive fit scoring with visualizations

## Dependencies

- **Streamlit**: Web application framework
- **NBA API**: Python library for accessing NBA statistics
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **Requests**: HTTP library for API calls
- **Plotly**: Interactive visualizations

## Development

This is currently a scaffold with placeholder implementations. To make it fully functional:

1. Implement real NBA API integration in `services/nba_client.py`
2. Enhance feature engineering algorithms in `core/features.py`
3. Improve scoring algorithms in `core/scoring.py`
4. Add more sophisticated visualizations
5. Implement data caching and optimization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Disclaimer

This application is for educational and analytical purposes. The NBA API integration is currently a placeholder implementation. For production use, proper API authentication and rate limiting should be implemented.
