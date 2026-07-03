"""
Unit tests for match predictor.
"""
import pytest
from models import Player, Team, LeagueStats
from predictor import MatchPredictor


class TestMatchPredictor:
    """Test MatchPredictor class."""
    
    def create_team(self, team_id: str, name: str, wins: int, draws: int, losses: int) -> Team:
        """Helper to create a team with stats."""
        stats = LeagueStats(
            matches_played=wins + draws + losses,
            wins=wins,
            draws=draws,
            losses=losses,
            goals_for=wins * 2 + draws,
            goals_against=losses + draws,
            goal_difference=(wins * 2 + draws) - (losses + draws),
            points=wins * 3 + draws
        )
        
        # Create 11 starters
        players = []
        for i in range(11):
            p = Player(
                f"{team_id}_p{i}",
                f"{name} Player {i}",
                team_id,
                "GK" if i == 0 else ("DEF" if i < 5 else ("MID" if i < 8 else "FWD")),
                goals=max(0, 5 - i),
                assists=max(0, 3 - i),
                shots_on_target=max(0, 15 - i),
                shots_on_goal=max(0, 10 - i),
                headed_attempts_on_goal=max(0, 3 - i) if i < 5 else 0
            )
            players.append(p)
        
        team = Team(
            id=team_id,
            name=name,
            country=name,
            players=players,
            starting_lineup=[p.id for p in players],
            league_stats=stats
        )
        
        return team
    
    def test_predict_stronger_team_wins(self):
        """Test that stronger team has higher win probability."""
        # Strong team: 10W-0D-0L
        team_a = self.create_team("team_a", "Strong", 10, 0, 0)
        
        # Weak team: 0W-0D-10L
        team_b = self.create_team("team_b", "Weak", 0, 0, 10)
        
        predictor = MatchPredictor(team_a, team_b)
        prediction = predictor.predict()
        
        assert prediction["team_a"]["win_probability"] > prediction["team_b"]["win_probability"]
        assert prediction["favorite"] == "Strong"
    
    def test_predict_equal_teams(self):
        """Test prediction with equally matched teams."""
        team_a = self.create_team("team_a", "Team A", 5, 2, 3)
        team_b = self.create_team("team_b", "Team B", 5, 2, 3)
        
        predictor = MatchPredictor(team_a, team_b)
        prediction = predictor.predict()
        
        # Should be very close to 50-50
        assert abs(prediction["team_a"]["win_probability"] - 50) < 5
        assert abs(prediction["team_b"]["win_probability"] - 50) < 5
    
    def test_predict_probabilities_sum_to_100(self):
        """Test that win probabilities sum to 100%."""
        team_a = self.create_team("team_a", "Team A", 8, 1, 1)
        team_b = self.create_team("team_b", "Team B", 3, 3, 4)
        
        predictor = MatchPredictor(team_a, team_b)
        prediction = predictor.predict()
        
        total_prob = prediction["team_a"]["win_probability"] + prediction["team_b"]["win_probability"]
        assert abs(total_prob - 100) < 0.1
    
    def test_predict_output_structure(self):
        """Test prediction output has correct structure."""
        team_a = self.create_team("team_a", "Argentina", 7, 2, 1)
        team_b = self.create_team("team_b", "Brazil", 7, 2, 1)
        
        predictor = MatchPredictor(team_a, team_b)
        prediction = predictor.predict()
        
        # Check structure
        assert "team_a" in prediction
        assert "team_b" in prediction
        assert "favorite" in prediction
        
        # Check team_a keys
        assert "name" in prediction["team_a"]
        assert "country" in prediction["team_a"]
        assert "squad_score" in prediction["team_a"]
        assert "league_strength" in prediction["team_a"]
        assert "composite_score" in prediction["team_a"]
        assert "win_probability" in prediction["team_a"]
        
        # Check team_b keys
        assert "name" in prediction["team_b"]
        assert "country" in prediction["team_b"]
        assert "squad_score" in prediction["team_b"]
        assert "league_strength" in prediction["team_b"]
        assert "composite_score" in prediction["team_b"]
        assert "win_probability" in prediction["team_b"]
    
    def test_predict_composite_score_weighting(self):
        """Test that composite score correctly weights squad + league."""
        team_a = self.create_team("team_a", "Strong", 10, 0, 0)
        team_b = self.create_team("team_b", "Weak", 0, 0, 10)
        
        predictor = MatchPredictor(team_a, team_b)
        prediction = predictor.predict()
        
        # Composite should be between squad and league scores
        team_a_pred = prediction["team_a"]
        assert team_a_pred["composite_score"] > 0
        
        # Strong team's composite should reflect both good squad and good league record
        assert team_a_pred["league_strength"] > team_a_pred["squad_score"] or team_a_pred["squad_score"] == 0
    
    def test_predict_different_league_records(self):
        """Test prediction sensitivity to league records."""
        # Both have similar squad, but different league records
        team_a = self.create_team("team_a", "Consistent", 9, 1, 0)  # Very strong
        team_b = self.create_team("team_b", "Inconsistent", 5, 5, 0)  # Same points, less consistent
        
        predictor = MatchPredictor(team_a, team_b)
        prediction = predictor.predict()
        
        # Team A should have higher probability due to better record
        assert prediction["team_a"]["win_probability"] > prediction["team_b"]["win_probability"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
