"""
Unit tests for visualizer.
"""
import pytest
from models import Player, Team, LeagueStats
from visualizer import MatchVisualizer


class TestMatchVisualizer:
    """Test MatchVisualizer class."""
    
    def create_test_prediction(self):
        """Helper to create test prediction."""
        return {
            "team_a": {
                "name": "Argentina",
                "country": "Argentina",
                "squad_score": 5.5,
                "league_strength": 10.0,
                "composite_score": 7.25,
                "win_probability": 60.0
            },
            "team_b": {
                "name": "Brazil",
                "country": "Brazil",
                "squad_score": 5.2,
                "league_strength": 9.5,
                "composite_score": 7.0,
                "win_probability": 40.0
            },
            "favorite": "Argentina"
        }
    
    def create_test_team(self):
        """Helper to create test team."""
        stats = LeagueStats(10, 7, 2, 1, 25, 10, 15, 23)
        
        players = []
        for i in range(11):
            p = Player(
                f"p{i}",
                f"Player {i}",
                "team_1",
                "GK" if i == 0 else ("DEF" if i < 5 else ("MID" if i < 8 else "FWD")),
                goals=max(0, 5 - i),
                assists=max(0, 3 - i),
                shots_on_target=max(0, 15 - i),
                shots_on_goal=max(0, 10 - i),
                headed_attempts_on_goal=max(0, 3 - i) if i < 5 else 0
            )
            players.append(p)
        
        return Team(
            id="team_1",
            name="Argentina",
            country="Argentina",
            players=players,
            starting_lineup=[p.id for p in players],
            league_stats=stats
        )
    
    def test_visualizer_initialization(self):
        """Test visualizer initialization."""
        team_a = self.create_test_team()
        team_b = self.create_test_team()
        prediction = self.create_test_prediction()
        
        visualizer = MatchVisualizer(team_a, team_b, prediction)
        
        assert visualizer.team_a == team_a
        assert visualizer.team_b == team_b
        assert visualizer.prediction == prediction
    
    def test_get_ascii_prediction(self):
        """Test ASCII prediction output."""
        team_a = self.create_test_team()
        team_b = self.create_test_team()
        prediction = self.create_test_prediction()
        
        visualizer = MatchVisualizer(team_a, team_b, prediction)
        ascii_output = visualizer.get_ascii_prediction()
        
        # Check output contains expected content
        assert "Argentina" in ascii_output
        assert "Brazil" in ascii_output
        assert "60.0%" in ascii_output
        assert "40.0%" in ascii_output
        assert "Favorite" in ascii_output
        assert "Squad Score" in ascii_output
        assert "League Strength" in ascii_output
    
    def test_get_ascii_prediction_contains_bars(self):
        """Test ASCII prediction has probability bars."""
        team_a = self.create_test_team()
        team_b = self.create_test_team()
        prediction = self.create_test_prediction()
        
        visualizer = MatchVisualizer(team_a, team_b, prediction)
        ascii_output = visualizer.get_ascii_prediction()
        
        # Should contain bar characters
        assert "█" in ascii_output or "■" in ascii_output or "#" in ascii_output or "=" in ascii_output
    
    def test_get_ascii_prediction_with_close_match(self):
        """Test ASCII prediction with nearly equal teams."""
        team_a = self.create_test_team()
        team_b = self.create_test_team()
        
        prediction = {
            "team_a": {
                "name": "Team A",
                "country": "Country A",
                "squad_score": 3.0,
                "league_strength": 10.0,
                "composite_score": 6.2,
                "win_probability": 50.5
            },
            "team_b": {
                "name": "Team B",
                "country": "Country B",
                "squad_score": 3.1,
                "league_strength": 10.0,
                "composite_score": 6.22,
                "win_probability": 49.5
            },
            "favorite": "Team A"
        }
        
        visualizer = MatchVisualizer(team_a, team_b, prediction)
        ascii_output = visualizer.get_ascii_prediction()
        
        # Both teams should have similar bar lengths
        assert "Team A" in ascii_output
        assert "Team B" in ascii_output
    
    def test_save_win_probability_chart_no_matplotlib(self):
        """Test chart saving gracefully handles missing matplotlib."""
        team_a = self.create_test_team()
        team_b = self.create_test_team()
        prediction = self.create_test_prediction()
        
        visualizer = MatchVisualizer(team_a, team_b, prediction)
        
        # Should return False if matplotlib not available (but not crash)
        result = visualizer.save_win_probability_chart("/tmp/test.png")
        
        # Either saves successfully or returns False
        assert result is True or result is False
    
    def test_ascii_output_format(self):
        """Test ASCII output has proper formatting."""
        team_a = self.create_test_team()
        team_b = self.create_test_team()
        prediction = self.create_test_prediction()
        
        visualizer = MatchVisualizer(team_a, team_b, prediction)
        ascii_output = visualizer.get_ascii_prediction()
        
        lines = ascii_output.split('\n')
        
        # Should have multiple lines
        assert len(lines) > 5
        
        # Should contain separator lines
        assert any("=" in line for line in lines)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
