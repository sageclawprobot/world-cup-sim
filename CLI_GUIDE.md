# CLI Guide - Match Comparison Tool 🎯

## Overview

The **CLI tool** allows you to compare any two World Cup 2026 teams with real-time data, predictions, simulations, and CSV exports.

## Quick Start

```bash
cd ~/world-cup-sim/src

# Basic comparison
python3 cli.py Argentina "Cape Verde"

# With live data from API
python3 cli.py Argentina "Cape Verde" --live

# Export to CSV
python3 cli.py France Germany --live --export csv

# Multiple simulations
python3 cli.py Brazil Mexico --simulations 100

# Custom output directory
python3 cli.py "South Africa" "Saudi Arabia" --output my_results
```

## Usage

```
python3 cli.py TEAM_A TEAM_B [OPTIONS]
```

### Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| TEAM_A | First team name (supports partial match) | `Argentina`, `Cape Verde`, `Brazil` |
| TEAM_B | Second team name | `"Cape Verde"` (quoted for spaces) |

### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--live` | `-L` | flag | false | Fetch fresh data from worldcup26.ir API |
| `--export` | `-E` | choice | `csv` | Export format: `csv`, `json`, `all`, `none` |
| `--output` | `-O` | path | `output` | Output directory for results |
| `--seed` | `-S` | int | `42` | Random seed for reproducible simulations |
| `--simulations` | | int | `1` | Number of match simulations to run |

## Examples

### Example 1: Basic Comparison (Argentina vs Cape Verde)

```bash
python3 cli.py Argentina "Cape Verde"
```

**Output**:
```
⚽ Match: Argentina vs Cape Verde

📊 Team Statistics
Argentina (Argentina)
  Record: 3W-0D-0L
  Goals: 8 for, 1 against (GD: +7)
  Points: 9

Cape Verde (Cape Verde)
  Record: 0W-3D-0L
  Goals: 2 for, 2 against (GD: +0)
  Points: 3

⚽ PREDICTION
Argentina: 83.5%
Cape Verde: 16.5%

🏆 Favorite: Argentina

🎮 MATCH SIMULATION
Argentina 6 - 1 Cape Verde

⚽ Argentina Scorers:
   Argentina Player 7 (assist: Argentina Player 9) 8'
   Argentina Player 9 (assist: Argentina Player 5) 18'
   ...
```

### Example 2: With Live Data

```bash
python3 cli.py France Germany --live
```

**Benefits**:
- Fetches latest teams, players, and match results
- Updates league statistics
- Fresh predictions based on current form

### Example 3: Multiple Simulations

```bash
python3 cli.py Brazil Mexico --simulations 100
```

**Output**:
```
📈 Series Statistics (100 matches)
Brazil: 78W - 12D - 10L
Mexico: 10W - 12D - 78L
Draws: 12

Average Goals:
  Brazil: 2.3
  Mexico: 0.9
```

### Example 4: CSV Export

```bash
python3 cli.py Spain Italy --export csv --output spain_vs_italy
```

**Creates**:
- `spain_vs_italy/matchup.csv` - Full data
- `spain_vs_italy/teams_summary.csv` - Team stats
- `spain_vs_italy/players_summary.csv` - Player stats
- `spain_vs_italy/match_results.csv` - Goals breakdown

### Example 5: All Exports

```bash
python3 cli.py "South Africa" "Saudi Arabia" --export all --output sa_vs_sa
```

**Creates**:
- CSV files (as above)
- `prediction.json` - Prediction results

## Team Name Matching

The CLI supports flexible team name matching:

```bash
# All of these work:
python3 cli.py Argentina Brazil
python3 cli.py "South Africa" "Saudi Arabia"
python3 cli.py arge capv        # Partial matches
python3 cli.py arg "cape verde" # Case-insensitive
```

## Output Formats

### Console Output

**Prediction**:
```
Team A: 65.3%
  Squad Score: 5.50
  League Strength: 10.22
  Composite: 6.75
```

**Match Simulation**:
```
Team A 3 - 2 Team B

⚽ Team A Scorers:
   Player 1 (assist: Player 2) 15'
   Player 3 42'
   Player 2 (assist: Player 4) 78'

⚽ Team B Scorers:
   Player 5 (assist: Player 6) 25'
   Player 7 68'

🏆 Winner: Team A

📝 Summary: Team A's clinical finishing secured the victory
```

### CSV Output

**teams_summary.csv**:
```
TeamName,Country,MatchesPlayed,Wins,Draws,Losses,GoalsFor,GoalsAgainst,GoalDifference,Points,WinRate,AvgGoalsPerMatch
Argentina,Argentina,3,3,0,0,8,1,7,9,100.0,2.67
Cape Verde,Cape Verde,3,0,3,0,2,2,0,3,0.0,0.67
```

**match_results.csv**:
```
MatchId,TeamA,TeamB,TeamAGoals,TeamBGoals,Winner,Scorer,ScorerTeam,ScorerMinute,Assister,Summary
1,Argentina,Cape Verde,6,1,Argentina,Argentina Player 7,Argentina,8,Argentina Player 9,Argentina dominated with clinical finishing
1,Argentina,Cape Verde,6,1,Argentina,Argentina Player 9,Argentina,18,Argentina Player 5,Argentina dominated with clinical finishing
...
```

## Data Sources

### Cached Data (Default)

```bash
python3 cli.py Argentina "Cape Verde"
```

Uses existing `data/teams.json` and `data/players.json`

**Pros**: Fast, no network needed
**Cons**: May be stale

### Live API Data

```bash
python3 cli.py Argentina "Cape Verde" --live
```

Fetches from `https://worldcup26.ir/`

**Pros**: Latest statistics and results
**Cons**: Takes 3-5 seconds for API call

## Reproducibility

Use `--seed` for reproducible match simulations:

```bash
# Same seed = same results
python3 cli.py Argentina Brazil --seed 42
python3 cli.py Argentina Brazil --seed 42

# Same match output both times
```

Great for:
- Testing
- Documentation
- Demos
- Reports

## Advanced Usage

### Scripting

```bash
#!/bin/bash
# Tournament simulation

for team1 in Argentina Brazil France; do
  for team2 in Germany Spain Italy; do
    python3 cli.py "$team1" "$team2" \
      --export csv \
      --output "results/${team1}_vs_${team2}" \
      --simulations 10
  done
done
```

### Python Integration

```python
import subprocess
import json

# Run CLI
result = subprocess.run([
    'python3', 'cli.py',
    'Argentina', 'Brazil',
    '--export', 'all'
], capture_output=True, text=True)

print(result.stdout)
if result.returncode == 0:
    # Load results
    with open('output/prediction.json') as f:
        prediction = json.load(f)
    print(f"Favorite: {prediction['favorite']}")
```

## Troubleshooting

### Team Not Found

```bash
python3 cli.py "InvalidTeam" Brazil
# ❌ Team not found: InvalidTeam
# Available teams: Argentina, Brazil, ...
```

**Solution**: Check team name spelling or use partial match

### No Live Data

```bash
python3 cli.py Argentina Brazil --live
# ❌ Connection error
```

**Solution**: Use default cached data or check internet connection

### Missing Output Files

```bash
# Make sure output directory exists and is writable
python3 cli.py Argentina Brazil --output /tmp/results
```

## Performance

| Operation | Time |
|-----------|------|
| Single match simulation | 50-100ms |
| 100 match simulations | 5-10s |
| CSV export (2 teams) | <500ms |
| API fetch | 3-5s |

## Examples for Analysis

### Comparing Top Teams

```bash
python3 cli.py Argentina France --export all
python3 cli.py Brazil Germany --export all
python3 cli.py Spain Italy --export all
```

### Head-to-Head Records

```bash
python3 cli.py Argentina Brazil --simulations 100 --export csv
# See results in CSV files
```

### Team Strength Ranking

```bash
python3 cli.py "South Africa" "Saudi Arabia" --live
python3 cli.py Mexico Canada --live
python3 cli.py "New Zealand" Honduras --live
# Compare team statistics
```

## Next Features

- [ ] Parallel simulations
- [ ] Batch processing
- [ ] Historical comparisons
- [ ] Tournament generator
- [ ] Web interface

## Summary

The CLI tool makes it easy to:

✅ Compare any two teams
✅ Get live data from API
✅ Predict match outcomes
✅ Simulate matches
✅ Export to CSV for analysis
✅ Reproduce results with seeds

Perfect for analysis, reporting, and data extraction!

---

**Ready to analyze matches?** ⚽🚀
