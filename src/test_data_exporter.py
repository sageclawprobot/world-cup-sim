"""
Unit tests for data exporter.
"""
import pytest
import csv
import os
from pathlib import Path
from models import Player, Team, LeagueStats
from data_exporter import DataExporter, DataExportPipeline


class TestDataExporter:
    """Test DataExporter class."""
    
    def create_test_team(self, team_id: str, name: str) -> Team:
        """Helper to create test team."""
        stats = LeagueStats(10, 7, 2, 1, 25, 10, 15, 23)
        
        players = []
        for i in range(11):
            p = Player(
                f"{team_id}_p{i}",
                f"{name} P{i}",
                team_id,
                "GK" if i == 0 else ("DEF" if i < 5 else ("MID" if i < 8 else "FWD")),
                goals=max(0, 5 - i),
                assists=max(0, 3 - i),
                shots_on_target=max(0, 15 - i),
                shots_on_goal=max(0, 10 - i),
                headed_attempts_on_goal=max(0, 3 - i) if i < 5 else 0
            )
            players.append(p)
        
        return Team(team_id, name, name, players, [p.id for p in players], stats)
    
    def test_export_to_csv(self, tmp_path):
        """Test exporting to CSV."""
        team_a = self.create_test_team("team_a", "Team A")
        team_b = self.create_test_team("team_b", "Team B")
        teams = [team_a, team_b]
        
        output_file = tmp_path / "test.csv"
        rows = DataExporter.export_to_csv(teams, str(output_file))
        
        # Should have 22 rows (11 players × 2 teams)
        assert rows == 22
        assert output_file.exists()
        
        # Verify CSV content
        with open(output_file, 'r') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        
        assert len(data) == 22
        assert data[0]["TeamName"] == "Team A"
        assert data[0]["PlayerName"] == "Team A P0"
    
    def test_csv_headers_present(self, tmp_path):
        """Test that all required headers are in CSV."""
        team = self.create_test_team("team_a", "Team A")
        output_file = tmp_path / "test.csv"
        
        DataExporter.export_to_csv([team], str(output_file))
        
        with open(output_file, 'r') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
        
        required_headers = [
            "TeamName", "TeamMatchesPlayed", "TeamWins", "TeamDraws",
            "TeamLosses", "TeamGoalsScored", "TeamGoalsAgainst",
            "TeamGoalDifference", "PlayerName", "PlayerGoals", "PlayerAssists",
            "PlayerShotsOnTarget", "PlayerShotsOnGoal", "PlayerHeadedAttempts"
        ]
        
        for header in required_headers:
            assert header in headers
    
    def test_team_data_accuracy(self, tmp_path):
        """Test that team data is accurately exported."""
        team = self.create_test_team("team_a", "Team A")
        output_file = tmp_path / "test.csv"
        
        DataExporter.export_to_csv([team], str(output_file))
        
        with open(output_file, 'r') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        
        # All rows should have same team stats
        for row in data:
            assert row["TeamName"] == "Team A"
            assert row["TeamMatchesPlayed"] == "10"
            assert row["TeamWins"] == "7"
            assert row["TeamGoalsScored"] == "25"
    
    def test_player_data_accuracy(self, tmp_path):
        """Test that player data is accurately exported."""
        team = self.create_test_team("team_a", "Team A")
        output_file = tmp_path / "test.csv"
        
        DataExporter.export_to_csv([team], str(output_file))
        
        with open(output_file, 'r') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        
        # Check first player
        first_player = data[0]
        assert first_player["PlayerName"] == "Team A P0"
        assert first_player["PlayerGoals"] == "5"
        assert first_player["PlayerAssists"] == "3"
    
    def test_export_teams_summary(self, tmp_path):
        """Test exporting team summary."""
        team_a = self.create_test_team("team_a", "Team A")
        team_b = self.create_test_team("team_b", "Team B")
        output_file = tmp_path / "teams.csv"
        
        rows = DataExporter.export_teams_summary([team_a, team_b], str(output_file))
        
        assert rows == 2
        assert output_file.exists()
    
    def test_export_players_summary(self, tmp_path):
        """Test exporting player summary."""
        team = self.create_test_team("team_a", "Team A")
        output_file = tmp_path / "players.csv"
        
        rows = DataExporter.export_players_summary([team], str(output_file))
        
        assert rows == 11  # 11 players
        assert output_file.exists()
    
    def test_empty_teams_list(self, tmp_path):
        """Test exporting empty teams list."""
        output_file = tmp_path / "test.csv"
        rows = DataExporter.export_to_csv([], str(output_file))
        
        assert rows == 0
        assert output_file.exists()
        
        with open(output_file, 'r') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        
        assert len(data) == 0


class TestDataExportPipeline:
    """Test DataExportPipeline class."""
    
    def create_test_team(self, team_id: str, name: str) -> Team:
        """Helper to create test team."""
        stats = LeagueStats(10, 7, 2, 1, 25, 10, 15, 23)
        
        players = []
        for i in range(11):
            p = Player(
                f"{team_id}_p{i}",
                f"{name} P{i}",
                team_id,
                "GK" if i == 0 else ("DEF" if i < 5 else ("MID" if i < 8 else "FWD")),
                goals=max(0, 5 - i),
                assists=max(0, 3 - i),
                shots_on_target=max(0, 15 - i),
                shots_on_goal=max(0, 10 - i),
                headed_attempts_on_goal=max(0, 3 - i) if i < 5 else 0
            )
            players.append(p)
        
        return Team(team_id, name, name, players, [p.id for p in players], stats)
    
    def test_pipeline_initialization(self, tmp_path):
        """Test pipeline initialization."""
        pipeline = DataExportPipeline(str(tmp_path))
        
        assert pipeline.output_dir == tmp_path
        assert tmp_path.exists()
    
    def test_pipeline_export_all(self, tmp_path):
        """Test exporting all data."""
        pipeline = DataExportPipeline(str(tmp_path))
        
        team_a = self.create_test_team("team_a", "Team A")
        team_b = self.create_test_team("team_b", "Team B")
        teams = [team_a, team_b]
        
        results = pipeline.export_all(teams)
        
        assert "matchup.csv" in results
        assert "teams_summary.csv" in results
        assert "players_summary.csv" in results
        assert results["matchup.csv"]["rows"] == 22
        assert results["teams_summary.csv"]["rows"] == 2
        assert results["players_summary.csv"]["rows"] == 22
    
    def test_pipeline_export_with_match_results(self, tmp_path):
        """Test exporting with match results."""
        from match_simulator import MatchResult, GoalEvent
        
        pipeline = DataExportPipeline(str(tmp_path))
        
        team_a = self.create_test_team("team_a", "Team A")
        team_b = self.create_test_team("team_b", "Team B")
        
        goal1 = GoalEvent("Player A", "Player B", 15, "Team A")
        goal2 = GoalEvent("Player C", None, 45, "Team B")
        
        match = MatchResult(
            team_a_name="Team A",
            team_b_name="Team B",
            team_a_goals=1,
            team_b_goals=1,
            team_a_scorers=[goal1],
            team_b_scorers=[goal2],
            match_summary="Test match"
        )
        
        results = pipeline.export_all([team_a, team_b], [match])
        
        assert "match_results.csv" in results
        assert results["match_results.csv"]["rows"] > 0
    
    def test_all_csv_files_created(self, tmp_path):
        """Test that all expected CSV files are created."""
        pipeline = DataExportPipeline(str(tmp_path))
        
        team = self.create_test_team("team_a", "Team A")
        results = pipeline.export_all([team])
        
        # Check files exist
        for filename in ["matchup.csv", "teams_summary.csv", "players_summary.csv"]:
            filepath = tmp_path / filename
            assert filepath.exists(), f"{filename} not created"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
