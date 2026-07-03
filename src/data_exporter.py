"""
Data Exporter - Export team and player data to CSV format.
"""
import csv
from typing import List, Optional
from pathlib import Path
from models import Team, Player


class DataExporter:
    """Export team and player data to various formats."""
    
    CSV_HEADERS = [
        "TeamName",
        "TeamMatchesPlayed",
        "TeamWins",
        "TeamDraws",
        "TeamLosses",
        "TeamGoalsScored",
        "TeamGoalsAgainst",
        "TeamGoalDifference",
        "PlayerName",
        "PlayerGoals",
        "PlayerAssists",
        "PlayerShotsOnTarget",
        "PlayerShotsOnGoal",
        "PlayerHeadedAttempts"
    ]
    
    @staticmethod
    def export_to_csv(teams: List[Team], output_path: str) -> int:
        """Export team and player data to CSV file.
        
        Args:
            teams: List of Team objects to export
            output_path: Path to output CSV file
            
        Returns:
            Number of rows written
        """
        rows = []
        total_rows = 0
        
        # Process each team
        for team in teams:
            stats = team.league_stats
            
            # Create row for each player on the team
            for player in team.players:
                row = {
                    "TeamName": team.name,
                    "TeamMatchesPlayed": stats.matches_played,
                    "TeamWins": stats.wins,
                    "TeamDraws": stats.draws,
                    "TeamLosses": stats.losses,
                    "TeamGoalsScored": stats.goals_for,
                    "TeamGoalsAgainst": stats.goals_against,
                    "TeamGoalDifference": stats.goal_difference,
                    "PlayerName": player.name,
                    "PlayerGoals": player.goals,
                    "PlayerAssists": player.assists,
                    "PlayerShotsOnTarget": player.shots_on_target,
                    "PlayerShotsOnGoal": player.shots_on_goal,
                    "PlayerHeadedAttempts": player.headed_attempts_on_goal
                }
                rows.append(row)
                total_rows += 1
        
        # Write to CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=DataExporter.CSV_HEADERS)
            writer.writeheader()
            writer.writerows(rows)
        
        return total_rows
    
    @staticmethod
    def export_teams_summary(teams: List[Team], output_path: str) -> int:
        """Export summary statistics for teams only.
        
        Args:
            teams: List of Team objects to export
            output_path: Path to output CSV file
            
        Returns:
            Number of rows written
        """
        rows = []
        
        headers = [
            "TeamName",
            "Country",
            "MatchesPlayed",
            "Wins",
            "Draws",
            "Losses",
            "GoalsFor",
            "GoalsAgainst",
            "GoalDifference",
            "Points",
            "WinRate",
            "AvgGoalsPerMatch"
        ]
        
        for team in teams:
            stats = team.league_stats
            win_rate = (stats.wins / stats.matches_played * 100) if stats.matches_played > 0 else 0
            avg_goals = (stats.goals_for / stats.matches_played) if stats.matches_played > 0 else 0
            
            row = {
                "TeamName": team.name,
                "Country": team.country,
                "MatchesPlayed": stats.matches_played,
                "Wins": stats.wins,
                "Draws": stats.draws,
                "Losses": stats.losses,
                "GoalsFor": stats.goals_for,
                "GoalsAgainst": stats.goals_against,
                "GoalDifference": stats.goal_difference,
                "Points": stats.points,
                "WinRate": round(win_rate, 2),
                "AvgGoalsPerMatch": round(avg_goals, 2)
            }
            rows.append(row)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
        
        return len(rows)
    
    @staticmethod
    def export_players_summary(teams: List[Team], output_path: str) -> int:
        """Export summary statistics for players only.
        
        Args:
            teams: List of Team objects to export
            output_path: Path to output CSV file
            
        Returns:
            Number of rows written
        """
        rows = []
        
        headers = [
            "PlayerName",
            "TeamName",
            "Position",
            "Goals",
            "Assists",
            "ShotsOnTarget",
            "ShotsOnGoal",
            "HeadedAttempts",
            "ContributionScore"
        ]
        
        for team in teams:
            for player in team.players:
                score = player.get_score()
                
                row = {
                    "PlayerName": player.name,
                    "TeamName": team.name,
                    "Position": player.position,
                    "Goals": player.goals,
                    "Assists": player.assists,
                    "ShotsOnTarget": player.shots_on_target,
                    "ShotsOnGoal": player.shots_on_goal,
                    "HeadedAttempts": player.headed_attempts_on_goal,
                    "ContributionScore": round(score, 2)
                }
                rows.append(row)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
        
        return len(rows)
    
    @staticmethod
    def export_match_results(match_results: list, output_path: str) -> int:
        """Export match simulation results to CSV.
        
        Args:
            match_results: List of MatchResult objects
            output_path: Path to output CSV file
            
        Returns:
            Number of rows written
        """
        rows = []
        
        headers = [
            "MatchId",
            "TeamA",
            "TeamB",
            "TeamAGoals",
            "TeamBGoals",
            "Winner",
            "Scorer",
            "ScorerTeam",
            "ScorerMinute",
            "Assister",
            "Summary"
        ]
        
        for match_id, match in enumerate(match_results, 1):
            all_goals = match.team_a_scorers + match.team_b_scorers
            
            if not all_goals:
                # Match with no goals
                row = {
                    "MatchId": match_id,
                    "TeamA": match.team_a_name,
                    "TeamB": match.team_b_name,
                    "TeamAGoals": match.team_a_goals,
                    "TeamBGoals": match.team_b_goals,
                    "Winner": match.get_winner() or "Draw",
                    "Scorer": "",
                    "ScorerTeam": "",
                    "ScorerMinute": "",
                    "Assister": "",
                    "Summary": match.match_summary
                }
                rows.append(row)
            else:
                # One row per goal
                for goal in all_goals:
                    row = {
                        "MatchId": match_id,
                        "TeamA": match.team_a_name,
                        "TeamB": match.team_b_name,
                        "TeamAGoals": match.team_a_goals,
                        "TeamBGoals": match.team_b_goals,
                        "Winner": match.get_winner() or "Draw",
                        "Scorer": goal.scorer,
                        "ScorerTeam": goal.team_name,
                        "ScorerMinute": goal.minute,
                        "Assister": goal.assister or "",
                        "Summary": match.match_summary
                    }
                    rows.append(row)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
        
        return len(rows)


class DataExportPipeline:
    """Complete data export pipeline."""
    
    def __init__(self, output_dir: str):
        """Initialize export pipeline.
        
        Args:
            output_dir: Directory to write all CSV files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def export_all(self, teams: List[Team], match_results: Optional[list] = None) -> dict:
        """Export all data to CSV files.
        
        Args:
            teams: List of teams to export
            match_results: Optional list of match results
            
        Returns:
            Dict with file paths and row counts
        """
        results = {}
        
        # Full data export (teams + players)
        full_path = self.output_dir / "matchup.csv"
        rows = DataExporter.export_to_csv(teams, str(full_path))
        results["matchup.csv"] = {
            "path": str(full_path),
            "rows": rows
        }
        
        # Teams summary
        teams_path = self.output_dir / "teams_summary.csv"
        rows = DataExporter.export_teams_summary(teams, str(teams_path))
        results["teams_summary.csv"] = {
            "path": str(teams_path),
            "rows": rows
        }
        
        # Players summary
        players_path = self.output_dir / "players_summary.csv"
        rows = DataExporter.export_players_summary(teams, str(players_path))
        results["players_summary.csv"] = {
            "path": str(players_path),
            "rows": rows
        }
        
        # Match results (if available)
        if match_results:
            match_path = self.output_dir / "match_results.csv"
            rows = DataExporter.export_match_results(match_results, str(match_path))
            results["match_results.csv"] = {
                "path": str(match_path),
                "rows": rows
            }
        
        return results
