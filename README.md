# World Cup Match Simulation 🌍⚽

A lightweight Python prototype for simulating World Cup 2026 soccer matches. Pulls live data from **worldcup26.ir API**, ranks teams based on player form and league statistics, and predicts match outcomes with visualizations.

## Features

✨ **Live API Integration**: Fetches real World Cup 2026 data from worldcup26.ir
📊 **Relational Data Model**: Separate teams and players with league statistics
🎯 **Intelligent Ranking**: Squad strength + recent league form (60/40 weighted)
⚽ **Match Prediction**: Calculate win probabilities for any matchup
📈 **Visualizations**: Bar charts and radar plots (matplotlib support)
🔄 **Modular Design**: Easy to extend with new metrics and data sources
🎲 **Synthetic Player Stats**: Generates player stats from team performance data

## Quick Start

### Setup

```bash
cd ~/world-cup-sim
pip install requests  # If not already installed
```

### Fetch Live Data & Run Simulation

```bash
cd src
python3 main.py --live  # Fetch fresh data from worldcup26.ir
```

Or use static cached data (faster):

```bash
python3 main.py
```

### Standalone Data Fetch

```bash
python3 fetch_live_data.py
```

### Output

The script generates:
- `output/prediction.json` - Prediction results with composite scores
- `output/win_probability.png` - Win probability chart (if matplotlib available)
- `output/team_scores.png` - Team strength comparison
- `output/player_contribution.png` - Top 5 players radar chart

## Project Structure

```
world-cup-sim/
├── data/
│   ├── teams.json           # All 48 teams + league stats
│   └── players.json         # Generated player data
├── src/
│   ├── api_client.py        # worldcup26.ir API client
│   ├── models.py            # Team & Player dataclasses
│   ├── predictor.py         # Match prediction logic
│   ├── visualizer.py        # Chart generation
│   ├── main.py              # Entry point
│   └── fetch_live_data.py   # Standalone data sync script
├── output/                  # Generated visualizations & predictions
└── README.md
```

## API Integration

### Data Source
- **API**: worldcup26.ir (https://github.com/rezarahiminia/worldcup2026)
- **Endpoints**:
  - `GET /get/teams` — All 48 qualified teams
  - `GET /get/games` — All match fixtures/results
  - `GET /get/groups` — Group standings (unused for now)
  - `GET /get/stadiums` — Host stadiums (unused for now)

### Data Flow
1. Fetch teams and games from worldcup26.ir
2. Calculate team statistics from completed matches
3. Generate synthetic player data based on team performance
4. Save to `teams.json` and `players.json`
5. Load and rank teams for prediction

## Prediction Algorithm

### Composite Score Formula
```
Composite Score = (Squad Score × 0.6) + (League Strength × 0.4)
```

**Squad Score**: Average of top 7 starters' contribution scores
- Goals (40%)
- Assists (30%)
- Shot efficiency (20%)
- Heading accuracy (10%)

**League Strength**: Recent performance metrics
- Win rate (50%)
- Points per match (30%)
- Goal difference (20%)

**Win Probability**: Relative strength ratio
```
Team A Win % = Team A Score / (Team A Score + Team B Score) × 100
```

## Sample Output

```
Brazil vs South Africa

Brazil
  Squad Score: 0.00 | League Strength: 12.12
  Composite: 4.85
  Win Prob: 74.0% [██████████████░░░░░░]

South Africa
  Squad Score: 0.00 | League Strength: 4.25
  Composite: 1.70
  Win Prob: 26.0% [█████░░░░░░░░░░░░░░░]

🏆 Favorite: Brazil
```

## Next Steps

- [x] Basic relational data model
- [x] Live API integration
- [x] Match prediction logic
- [ ] Real player statistics (via additional APIs)
- [ ] Historical match validation
- [ ] ML-enhanced predictions
- [ ] Web dashboard / interactive UI
- [ ] Tournament bracket simulation
- [ ] Betting odds comparison
- [ ] Player performance tracking

## CLI Options

```bash
python3 main.py              # Use cached static data
python3 main.py --live       # Fetch fresh data from API
python3 main.py -L           # Short form of --live
```

## Requirements

- Python 3.8+
- `requests` (for API calls)
- `matplotlib` (optional, for chart generation)
- `numpy` (optional, for matplotlib)

## Error Handling

- **API timeout**: If worldcup26.ir is unreachable, falls back to cached data
- **Missing players**: Synthetic player data is generated from team stats
- **Matplotlib unavailable**: Charts gracefully skip, ASCII output still displays
- **Invalid JSON**: Errors logged, simulation continues with safe defaults

## License

MIT

## Data Attribution

World Cup 2026 data provided by [rezarahiminia/worldcup2026](https://github.com/rezarahiminia/worldcup2026)
