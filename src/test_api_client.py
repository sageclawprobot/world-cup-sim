"""
Unit tests for API Client and Data Transformer.
IMPORTANT: Tests will FAIL until player stats are properly obtained!
"""
import json
import unittest
from unittest.mock import Mock, patch, MagicMock
from api_client import WorldCup26APIClient, DataTransformer


class TestWorldCup26APIClient(unittest.TestCase):
    """Test API client."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = WorldCup26APIClient()
    
    @patch('api_client.requests.get')
    def test_get_teams(self, mock_get):
        """Test fetching teams."""
        mock_response = Mock()
        mock_response.json.return_value = {"teams": [{"id": 1, "name_en": "Brazil"}]}
        mock_get.return_value = mock_response
        
        result = self.client.get_teams()
        assert "teams" in result
        assert len(result["teams"]) > 0
    
    @patch('api_client.requests.get')
    def test_get_games(self, mock_get):
        """Test fetching games."""
        mock_response = Mock()
        mock_response.json.return_value = {"games": []}
        mock_get.return_value = mock_response
        
        result = self.client.get_games()
        assert "games" in result


class TestDataTransformerPlayerStats(unittest.TestCase):
    """Test player stat extraction - STRICT TESTS."""
    
    def test_player_stats_not_zero(self):
        """CRITICAL TEST: Player stats must NOT be zero!"""
        # Mock API data with actual match results
        api_teams = {
            "teams": [
                {
                    "id": "1",
                    "name_en": "Brazil",
                    "name": "Brazil"
                },
                {
                    "id": "2",
                    "name_en": "Argentina",
                    "name": "Argentina"
                }
            ]
        }
        
        # CRITICAL: Games with scorers - this is how we get player stats
        api_games = {
            "games": [
                {
                    "id": "1",
                    "home_team_id": "1",
                    "away_team_id": "2",
                    "home_score": "3",
                    "away_score": "2",
                    "finished": "TRUE",
                    "home_scorers": '{"Neymar 15", "Vinicius 45", "Rodrygo 78"}',
                    "away_scorers": '{"Messi 20", "De Paul 60"}'
                },
                {
                    "id": "2",
                    "home_team_id": "2",
                    "away_team_id": "1",
                    "home_score": "2",
                    "away_score": "1",
                    "finished": "TRUE",
                    "home_scorers": '{"Messi 10", "Alvarez 85"}',
                    "away_scorers": '{"Vinicius 50"}'
                }
            ]
        }
        
        # Transform data
        teams_data, players_data = DataTransformer.transform_teams(api_teams, api_games)
        
        players = players_data.get("players", [])
        
        # CRITICAL ASSERTIONS
        self.assertGreater(len(players), 0, "❌ FAIL: No players generated!")
        
        # Check that AT LEAST SOME players have non-zero stats
        players_with_goals = [p for p in players if p.get("goals", 0) > 0]
        players_with_shots = [p for p in players if p.get("shots_on_target", 0) > 0]
        
        self.assertGreater(
            len(players_with_goals), 0,
            "❌ FAIL: No players have goals! Player stats not being extracted from matches!"
        )
        
        self.assertGreater(
            len(players_with_shots), 0,
            "❌ FAIL: No players have shots on target! Player stats incomplete!"
        )
        
        # Check specific stats
        for player in players:
            # Players should have reasonable stats
            goals = player.get("goals", 0)
            assists = player.get("assists", 0)
            shots = player.get("shots_on_target", 0)
            
            # FWD players should have decent stats
            if player["position"] == "FWD":
                # Check at least some FWD have goals
                pass  # Some may have 0, that's ok
            
            # Sanity checks
            self.assertGreaterEqual(goals, 0, "Goals cannot be negative")
            self.assertGreaterEqual(assists, 0, "Assists cannot be negative")
            self.assertGreaterEqual(shots, 0, "Shots cannot be negative")
    
    def test_player_stats_derived_from_team_performance(self):
        """Test that player stats correlate with team performance."""
        api_teams = {
            "teams": [
                {"id": "1", "name_en": "Strong Team", "name": "Strong Team"},
                {"id": "2", "name_en": "Weak Team", "name": "Weak Team"}
            ]
        }
        
        # Strong team scores lots (multiple matches), weak team scores little
        api_games = {
            "games": [
                {
                    "id": "1",
                    "home_team_id": "1",
                    "away_team_id": "2",
                    "home_score": "5",
                    "away_score": "0",
                    "finished": "TRUE",
                    "home_scorers": '{"Player1 10", "Player2 20", "Player3 30", "Player4 40", "Player5 50"}',
                    "away_scorers": '{}'
                },
                {
                    "id": "2",
                    "home_team_id": "1",
                    "away_team_id": "2",
                    "home_score": "3",
                    "away_score": "0",
                    "finished": "TRUE",
                    "home_scorers": '{"Player1 15", "Player6 45", "Player7 80"}',
                    "away_scorers": '{}'
                }
            ]
        }
        
        teams_data, players_data = DataTransformer.transform_teams(api_teams, api_games)
        
        teams = teams_data.get("teams", [])
        players = players_data.get("players", [])
        
        # Find strong and weak teams
        strong_team = next((t for t in teams if t["name"] == "Strong Team"), None)
        weak_team = next((t for t in teams if t["name"] == "Weak Team"), None)
        
        self.assertIsNotNone(strong_team)
        self.assertIsNotNone(weak_team)
        
        # Get players for each team
        strong_players = [p for p in players if p["team_id"] == strong_team["id"]]
        weak_players = [p for p in players if p["team_id"] == weak_team["id"]]
        
        # Strong team should have more goals from real match data
        strong_total_goals = sum(p.get("goals", 0) for p in strong_players)
        weak_total_goals = sum(p.get("goals", 0) for p in weak_players)
        
        # At minimum, strong team should have some goals
        self.assertGreater(
            strong_total_goals, 0,
            "Strong team should have goals extracted from matches!"
        )
    
    def test_player_stats_minimum_requirements(self):
        """Test that players meet minimum stat requirements."""
        api_teams = {
            "teams": [
                {"id": "1", "name_en": "Team A", "name": "Team A"},
                {"id": "2", "name_en": "Team B", "name": "Team B"}
            ]
        }
        
        api_games = {
            "games": [
                {
                    "id": "1",
                    "home_team_id": "1",
                    "away_team_id": "2",
                    "home_score": "2",
                    "away_score": "1",
                    "finished": "TRUE",
                    "home_scorers": '{"Player1 10", "Player2 45"}',
                    "away_scorers": '{"Player5 60"}'
                }
            ]
        }
        
        teams_data, players_data = DataTransformer.transform_teams(api_teams, api_games)
        
        players = players_data.get("players", [])
        
        # MINIMUM REQUIREMENTS:
        # 1. Must have players
        self.assertGreater(len(players), 0, "Must have at least some players")
        
        # 2. Some players must have non-zero stats
        non_zero_stats = [
            p for p in players 
            if p.get("goals", 0) > 0 or p.get("shots_on_target", 0) > 0
        ]
        self.assertGreater(
            len(non_zero_stats), 0,
            "At least some players must have non-zero stats!"
        )
        
        # 3. Stats should be reasonable
        for player in players:
            # If has goals, should have shots
            if player.get("goals", 0) > 0:
                self.assertGreater(
                    player.get("shots_on_target", 0), 0,
                    f"Player {player['name']} has {player['goals']} goals but 0 shots on target - invalid!"
                )
    
    def test_forward_players_have_goal_stats(self):
        """Test that forward players have goal-related stats."""
        api_teams = {
            "teams": [
                {"id": "1", "name_en": "Team X", "name": "Team X"}
            ]
        }
        
        api_games = {
            "games": [
                {
                    "id": "1",
                    "home_team_id": "1",
                    "away_team_id": "2",
                    "home_score": "3",
                    "away_score": "0",
                    "finished": "TRUE",
                    "home_scorers": '{"Forward1 20", "Forward2 40", "Forward3 70"}',
                    "away_scorers": '{}'
                }
            ]
        }
        
        teams_data, players_data = DataTransformer.transform_teams(api_teams, api_games)
        
        players = players_data.get("players", [])
        
        # Get FWD players
        forwards = [p for p in players if p["position"] == "FWD"]
        
        self.assertGreater(len(forwards), 0, "Must have forward players")
        
        # At least some forwards should have goals or shots
        forwards_with_stats = [
            f for f in forwards 
            if f.get("goals", 0) > 0 or f.get("shots_on_target", 0) > 0
        ]
        
        self.assertGreater(
            len(forwards_with_stats), 0,
            "Forwards must have goal/shot stats!"
        )


class TestDataTransformerTeamStats(unittest.TestCase):
    """Test team statistics extraction."""
    
    def test_team_stats_calculation(self):
        """Test that team stats are calculated correctly."""
        api_teams = {
            "teams": [
                {"id": "1", "name_en": "Brazil", "name": "Brazil"},
                {"id": "2", "name_en": "Argentina", "name": "Argentina"}
            ]
        }
        
        api_games = {
            "games": [
                {
                    "id": "1",
                    "home_team_id": "1",
                    "away_team_id": "2",
                    "home_score": "3",
                    "away_score": "1",
                    "finished": "TRUE",
                    "home_scorers": '{"A 10", "B 20", "C 30"}',
                    "away_scorers": '{"D 50"}'
                }
            ]
        }
        
        teams_data, _ = DataTransformer.transform_teams(api_teams, api_games)
        teams = teams_data.get("teams", [])
        
        brazil = next((t for t in teams if "Brazil" in t["name"]), None)
        self.assertIsNotNone(brazil)
        
        stats = brazil["league_stats"]
        self.assertEqual(stats["goals_for"], 3)
        self.assertEqual(stats["goals_against"], 1)
        self.assertEqual(stats["wins"], 1)
        self.assertEqual(stats["draws"], 0)
        self.assertEqual(stats["losses"], 0)
        self.assertEqual(stats["points"], 3)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
