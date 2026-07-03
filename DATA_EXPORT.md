# Data Export Guide 📊

## Overview

The **Data Exporter** converts World Cup simulator data into CSV files for analysis, reporting, and integration with other tools (Excel, Tableau, Power BI, etc.).

## Features

✅ **Full Match-up Data** - Teams + Players combined
✅ **Team Summary** - Aggregated league statistics
✅ **Player Summary** - Individual player performance
✅ **Match Results** - Goal-by-goal breakdown
✅ **Automatic Export** - Built into main pipeline
✅ **Multiple Formats** - Flexible CSV structures

## CSV Output Files

### 1. matchup.csv (Full Data)

**Purpose**: Complete denormalized view of teams and players

**Columns**:
```
TeamName
TeamMatchesPlayed
TeamWins
TeamDraws
TeamLosses
TeamGoalsScored
TeamGoalsAgainst
TeamGoalDifference
PlayerName
PlayerGoals
PlayerAssists
PlayerShotsOnTarget
PlayerShotsOnGoal
PlayerHeadedAttempts
```

**Example**:
```csv
TeamName,TeamMatchesPlayed,TeamWins,TeamDraws,TeamLosses,TeamGoalsScored,TeamGoalsAgainst,TeamGoalDifference,PlayerName,PlayerGoals,PlayerAssists,PlayerShotsOnTarget,PlayerShotsOnGoal,PlayerHeadedAttempts
Brazil,10,8,1,1,28,5,23,Brazil Player 1,0,0,0,0,0
Brazil,10,8,1,1,28,5,23,Neymar,8,4,24,20,2
Brazil,10,8,1,1,28,5,23,Mbappe,7,3,20,16,1
```

**Use Cases**:
- Pivot tables by team/player
- Filtering and sorting
- Excel VLOOKUP
- Database import

### 2. teams_summary.csv (Teams Only)

**Purpose**: Aggregated team statistics

**Columns**:
```
TeamName
Country
MatchesPlayed
Wins
Draws
Losses
GoalsFor
GoalsAgainst
GoalDifference
Points
WinRate (%)
AvgGoalsPerMatch
```

**Example**:
```csv
TeamName,Country,MatchesPlayed,Wins,Draws,Losses,GoalsFor,GoalsAgainst,GoalDifference,Points,WinRate,AvgGoalsPerMatch
Brazil,Brazil,10,8,1,1,28,5,23,25,80.0,2.8
Argentina,Argentina,10,7,2,1,25,10,15,23,70.0,2.5
```

**Use Cases**:
- Team rankings
- League tables
- Comparison analysis
- Dashboard widgets

### 3. players_summary.csv (Players Only)

**Purpose**: Individual player statistics

**Columns**:
```
PlayerName
TeamName
Position
Goals
Assists
ShotsOnTarget
ShotsOnGoal
HeadedAttempts
ContributionScore
```

**Example**:
```csv
PlayerName,TeamName,Position,Goals,Assists,ShotsOnTarget,ShotsOnGoal,HeadedAttempts,ContributionScore
Neymar,Brazil,FWD,8,4,24,20,2,8.5
Mbappe,Brazil,FWD,7,3,20,16,1,7.2
Messi,Argentina,FWD,9,5,28,22,1,9.1
```

**Use Cases**:
- Player rankings
- Golden Boot contenders
- Assist leaders
- Top performers

### 4. match_results.csv (Match Details)

**Purpose**: Goal-by-goal breakdown of matches

**Columns**:
```
MatchId
TeamA
TeamB
TeamAGoals
TeamBGoals
Winner
Scorer
ScorerTeam
ScorerMinute
Assister
Summary
```

**Example**:
```csv
MatchId,TeamA,TeamB,TeamAGoals,TeamBGoals,Winner,Scorer,ScorerTeam,ScorerMinute,Assister,Summary
1,Argentina,Brazil,3,2,Argentina,Messi,Argentina,15,De Paul,Argentina dominated with clinical finishing
1,Argentina,Brazil,3,2,Argentina,Alvarez,Argentina,42,,Argentina dominated with clinical finishing
1,Argentina,Brazil,3,2,Argentina,Martinez,Argentina,78,De Paul,Argentina dominated with clinical finishing
1,Argentina,Brazil,3,2,Argentina,Neymar,Brazil,25,Vinicius,Argentina dominated with clinical finishing
1,Argentina,Brazil,3,2,Argentina,Mbappe,Brazil,60,,Argentina dominated with clinical finishing
```

**Use Cases**:
- Match reports
- Goal statistics
- Timeline analysis
- Archive/history

## Usage

### Automatic Export

The main script automatically exports all data:

```bash
cd ~/world-cup-sim/src
python3 main.py
```

**Output**:
```
📄 Exporting Data to CSV...
   ✅ matchup.csv: 22 rows → /home/master/world-cup-sim/output/matchup.csv
   ✅ teams_summary.csv: 2 rows → /home/master/world-cup-sim/output/teams_summary.csv
   ✅ players_summary.csv: 22 rows → /home/master/world-cup-sim/output/players_summary.csv
   ✅ match_results.csv: 2 rows → /home/master/world-cup-sim/output/match_results.csv
```

### Programmatic Export

```python
from data_exporter import DataExporter, DataExportPipeline
from models import Team

# Single export
rows = DataExporter.export_to_csv(teams, "output.csv")

# Summary exports
DataExporter.export_teams_summary(teams, "teams.csv")
DataExporter.export_players_summary(teams, "players.csv")

# Full pipeline
pipeline = DataExportPipeline("output_dir")
results = pipeline.export_all(teams, match_results)

for filename, info in results.items():
    print(f"{filename}: {info['rows']} rows")
```

## Integration Examples

### Excel Analysis

1. **Open matchup.csv in Excel**
2. **Create Pivot Table**:
   - Rows: TeamName
   - Columns: Position
   - Values: Sum(PlayerGoals)

3. **Results**:
```
TeamName    GK   DEF   MID   FWD   Total
Argentina   0    1     9     18    28
Brazil      0    0     8     20    28
```

### Power BI Dashboard

```
1. Import teams_summary.csv
2. Create visuals:
   - Card: Top team by points
   - Column: Teams by goals scored
   - Table: Full league table
3. Publish to web
```

### Database Import

```sql
-- Create table
CREATE TABLE team_players (
  TeamName VARCHAR(50),
  TeamWins INT,
  PlayerName VARCHAR(50),
  PlayerGoals INT,
  PlayerAssists INT,
  ...
);

-- Import CSV
LOAD DATA INFILE 'matchup.csv'
INTO TABLE team_players
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;
```

## API Example

```python
from pathlib import Path
from data_exporter import DataExportPipeline
from main import load_data_from_json

# Load data
team_a, team_b = load_data_from_json("teams.json", "players.json")

# Export
pipeline = DataExportPipeline("export")
results = pipeline.export_all([team_a, team_b])

# Return paths
return {
    "matchup": results["matchup.csv"]["path"],
    "teams": results["teams_summary.csv"]["path"],
    "players": results["players_summary.csv"]["path"]
}
```

## Performance

| File | Rows | Size | Time |
|------|------|------|------|
| matchup.csv (48 teams) | 528 | ~50 KB | <500ms |
| teams_summary.csv | 48 | ~5 KB | <50ms |
| players_summary.csv | 528 | ~40 KB | <300ms |
| match_results.csv | 100+ | ~20 KB | <100ms |

## Customization

### Add Custom Fields

```python
def export_custom(teams, output_path):
    rows = []
    for team in teams:
        for player in team.players:
            row = {
                "TeamName": team.name,
                "PlayerName": player.name,
                "Goals": player.goals,
                "Assists": player.assists,
                # Add custom fields
                "GoalsPerMatch": player.goals / (len(team.league_stats) or 1),
                "IsFWD": 1 if player.position == "FWD" else 0,
            }
            rows.append(row)
    
    # Write to CSV
    with open(output_path, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
```

### Filter Before Export

```python
# Only export forwards
forwards = [p for t in teams for p in t.players if p.position == "FWD"]

# Export custom structure
rows = []
for player in forwards:
    rows.append({
        "Name": player.name,
        "Goals": player.goals,
        "Assists": player.assists,
        "Score": player.get_score()
    })
```

## Testing

```bash
cd ~/world-cup-sim/src
python3 test_data_exporter.py
```

**Tests**:
- ✅ CSV creation
- ✅ Header validation
- ✅ Data accuracy
- ✅ Multiple exports
- ✅ Empty data handling
- ✅ Pipeline workflow

## Data Dictionary

### Team Fields

| Field | Type | Description |
|-------|------|-------------|
| TeamName | String | Team name |
| TeamMatchesPlayed | Int | Matches played |
| TeamWins | Int | Number of wins |
| TeamDraws | Int | Number of draws |
| TeamLosses | Int | Number of losses |
| TeamGoalsScored | Int | Goals scored |
| TeamGoalsAgainst | Int | Goals conceded |
| TeamGoalDifference | Int | GF - GA |

### Player Fields

| Field | Type | Description |
|-------|------|-------------|
| PlayerName | String | Player name |
| PlayerGoals | Int | Goals scored |
| PlayerAssists | Int | Assists provided |
| PlayerShotsOnTarget | Int | Shots on target |
| PlayerShotsOnGoal | Int | Shots on goal |
| PlayerHeadedAttempts | Int | Headed attempts |
| Position | String | GK, DEF, MID, FWD |
| ContributionScore | Float | Weighted score |

## Troubleshooting

**CSV not created?**
- Check file permissions
- Ensure output directory exists
- Verify teams list is not empty

**Missing columns?**
- Verify DataExporter version
- Check CSV headers match expected

**Encoding issues?**
- Files are UTF-8 encoded
- Use encoding='utf-8' when reading

**Data looks wrong?**
- Verify source data in teams.json
- Check team statistics
- Validate player stats

## Next Steps

- [ ] Export to Excel with formatting
- [ ] Add charts to exported files
- [ ] Create PDF reports
- [ ] Database sync
- [ ] Real-time data updates
- [ ] API endpoint for exports

---

**Export your data with confidence!** 📊✅
