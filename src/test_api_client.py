"""
Unit tests for API client with mocking.
"""
import pytest
from unittest.mock import patch, MagicMock
from api_client import WorldCup26APIClient, DataTransformer


class TestWorldCup26APIClient:
    """Test WorldCup26APIClient."""
    
    def test_client_initialization(self):
        """Test client initialization with default URL."""
        client = WorldCup26APIClient()
        assert client.base_url == "https://worldcup26.ir"
    
    def test_client_custom_url(self):
        """Test client initialization with custom URL."""
        custom_url = "https://custom.api.com"
        client = WorldCup26APIClient(base_url=custom_url)
        assert client.base_url == custom_url
    
    @patch('requests.get')
    def test_get_teams(self, mock_get):
        """Test fetching teams."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "teams": [
                {"id": "1", "name_en": "Brazil", "fifa_code": "BRA"},
                {"id": "2", "name_en": "France", "fifa_code": "FRA"}
            ]
        }
        mock_response.ok = True
        mock_get.return_value = mock_response
        
        client = WorldCup26APIClient()
        result = client.get_teams()
        
        assert "teams" in result
        assert len(result["teams"]) == 2
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_get_games(self, mock_get):
        """Test fetching games."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "games": [
                {"id": "1", "home_team_id": "1", "away_team_id": "2", "finished": "TRUE"}
            ]
        }
        mock_response.ok = True
        mock_get.return_value = mock_response
        
        client = WorldCup26APIClient()
        result = client.get_games()
        
        assert "games" in result
        assert len(result["games"]) == 1
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_api_error_handling(self, mock_get):
        """Test API error handling."""
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status = 500
        mock_get.return_value = mock_response
        
        client = WorldCup26APIClient()
        
        with pytest.raises(Exception):
            client.get_teams()


class TestDataTransformer:
    """Test DataTransformer."""
    
    def test_transform_empty_data(self):
        """Test transforming empty API data."""
        api_teams = {"teams": []}
        api_games = {"games": []}
        
        teams_data, players_data = DataTransformer.transform_teams(api_teams, api_games)
        
        assert teams_data["teams"] == []
        assert players_data["players"] == []
    
    def test_transform_single_team(self):
        """Test transforming a single team."""
        api_teams = {
            "teams": [
                {
                    "id": "1",
                    "name_en": "Brazil",
                    "name": "Brazil",
                    "fifa_code": "BRA"
                }
            ]
        }
        api_games = {
            "games": [
                {
                    "home_team_id": "1",
                    "away_team_id": "2",
                    "home_score": "2",
                    "away_score": "1",
                    "finished": "TRUE"
                }
            ]
        }
        
        teams_data, players_data = DataTransformer.transform_teams(api_teams, api_games)
        
        assert len(teams_data["teams"]) == 1
        assert teams_data["teams"][0]["name"] == "Brazil"
        assert teams_data["teams"][0]["league_stats"]["goals_for"] == 2
        assert teams_data["teams"][0]["league_stats"]["goals_against"] == 1
    
    def test_transform_calculates_stats(self):
        """Test that transformation calculates statistics correctly."""
        api_teams = {
            "teams": [
                {"id": "1", "name_en": "Team A"},
                {"id": "2", "name_en": "Team B"}
            ]
        }
        api_games = {
            "games": [
                {
                    "home_team_id": "1",
                    "away_team_id": "2",
                    "home_score": "3",
                    "away_score": "1",
                    "finished": "TRUE"
                },
                {
                    "home_team_id": "2",
                    "away_team_id": "1",
                    "home_score": "2",
                    "away_score": "0",
                    "finished": "TRUE"
                }
            ]
        }
        
        teams_data, players_data = DataTransformer.transform_teams(api_teams, api_games)
        
        # Find teams in result
        team_a = next(t for t in teams_data["teams"] if t["name"] == "Team A")
        team_b = next(t for t in teams_data["teams"] if t["name"] == "Team B")
        
        # Team A: 1W-0D-1L, GF=3, GA=3
        assert team_a["league_stats"]["wins"] == 1
        assert team_a["league_stats"]["losses"] == 1
        assert team_a["league_stats"]["goals_for"] == 3
        assert team_a["league_stats"]["goals_against"] == 3
        
        # Team B: 1W-0D-1L, GF=3, GA=3
        assert team_b["league_stats"]["wins"] == 1
        assert team_b["league_stats"]["losses"] == 1
        assert team_b["league_stats"]["goals_for"] == 3
        assert team_b["league_stats"]["goals_against"] == 3
    
    def test_transform_generates_players(self):
        """Test that transformation generates player data."""
        api_teams = {
            "teams": [
                {"id": "1", "name_en": "Brazil"}
            ]
        }
        api_games = {"games": []}
        
        teams_data, players_data = DataTransformer.transform_teams(api_teams, api_games)
        
        # Should generate 11 players per team
        assert len(players_data["players"]) == 11
        
        # Check player structure
        for player in players_data["players"]:
            assert "id" in player
            assert "name" in player
            assert "team_id" in player
            assert "position" in player
            assert "goals" in player
            assert "assists" in player
    
    def test_transform_skips_unfinished_games(self):
        """Test that transformation skips unfinished games."""
        api_teams = {
            "teams": [
                {"id": "1", "name_en": "Team A"},
                {"id": "2", "name_en": "Team B"}
            ]
        }
        api_games = {
            "games": [
                {
                    "home_team_id": "1",
                    "away_team_id": "2",
                    "home_score": "1",
                    "away_score": "0",
                    "finished": "FALSE"  # Not finished
                }
            ]
        }
        
        teams_data, players_data = DataTransformer.transform_teams(api_teams, api_games)
        
        team_a = next(t for t in teams_data["teams"] if t["name"] == "Team A")
        
        # Should have 0 wins (game not counted)
        assert team_a["league_stats"]["matches_played"] == 0
        assert team_a["league_stats"]["wins"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
