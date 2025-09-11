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

1. **Enter Player Name**: Type the name of the NBA player you want to analyze
2. **Select Team**: Choose the team you want to evaluate the fit for
3. **Adjust Parameters**: Use the sliders to weight different aspects of the analysis:
   - Scoring Weight: Importance of scoring ability
   - Defense Weight: Importance of defensive skills
   - Playmaking Weight: Importance of playmaking ability
4. **Analyze**: Click "Analyze Fit" to get the compatibility score
5. **Review Results**: Examine the detailed breakdown and visualizations

## Project Structure

```
nba-fit/
├── app.py                 # Main Streamlit application
├── core/
│   ├── __init__.py
│   ├── features.py        # Feature engineering module
│   └── scoring.py         # Scoring algorithms
├── services/
│   ├── __init__.py
│   └── nba_client.py      # NBA API client (stub)
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Components

### Core Modules

- **`features.py`**: Contains the `FeatureEngineer` class for processing player and team data into meaningful features
- **`scoring.py`**: Implements scoring algorithms including `calculate_fit_score()` and advanced metrics

### Services

- **`nba_client.py`**: NBA API client for fetching player and team statistics (currently contains placeholder implementations)

### Main Application

- **`app.py`**: Streamlit application with interactive UI for player-team fit analysis

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
