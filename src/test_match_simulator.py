"""
Unit tests for match simulator.
"""
import pytest
from models import Player, Team, LeagueStats
from match_simulator import MatchSimulator, GoalEvent, MatchResult


class TestGoalEvent:
    """Test GoalEvent class."""
    
    def test_goal_event_creation(self):
        """Test creating a goal event."""
        goal = GoalEvent(
            scorer="Messi",
            assister="De Paul",
            minute=15,
            team_name="Argentina"
        )
        
        assert goal.scorer == "Messi"
        assert goal.assister == "De Paul"
        assert goal.minute == 15
        assert goal.team_name == "Argentina"
    
    def test_goal_event_without_assist(self):
        """Test goal event without assist."""
        goal = GoalEvent(
            scorer="Own Goal",
            assister=None,
            minute=40,
            team_name="Brazil"
        )
        
        assert goal.assister is None
        assert "Own Goal" in str(goal)
    
    def test_goal_event_string_format(self):
        """Test goal event string representation."""
        goal = GoalEvent("Ronaldo", "Neymar", 20, "Brazil")
        goal_str = str(goal)
        
        assert "Ronaldo" in goal_str
        assert "Neymar" in goal_str
        assert "20'" in goal_str


class TestMatchResult:
    """Test MatchResult class."""
    
    def test_match_result_creation(self):
        """Test creating a match result."""
        goal1 = GoalEvent("Messi", "De Paul", 15, "Argentina")
        goal2 = GoalEvent("Neymar", None, 45, "Brazil")
        
        result = MatchResult(
            team_a_name="Argentina",
            team_b_name="Brazil",
            team_a_goals=1,
            team_b_goals=1,
            team_a_scorers=[goal1],
            team_b_scorers=[goal2],
            match_summary="Evenly matched"
        )
        
        assert result.team_a_name == "Argentina"
        assert result.team_b_goals == 1
        assert len(result.team_a_scorers) == 1
    
    def test_match_result_winner(self):
        """Test determining match winner."""
        result = MatchResult(
            team_a_name="Argentina",
            team_b_name="Brazil",
            team_a_goals=2,
            team_b_goals=1,
            team_a_scorers=[],
            team_b_scorers=[],
            match_summary="Test"
        )
        
        assert result.get_winner() == "Argentina"
    
    def test_match_result_draw(self):
        """Test draw result."""
        result = MatchResult(
            team_a_name="Argentina",
            team_b_name="Brazil",
            team_a_goals=1,
            team_b_goals=1,
            team_a_scorers=[],
            team_b_scorers=[],
            match_summary="Test"
        )
        
        assert result.get_winner() is None


class TestMatchSimulator:
    """Test MatchSimulator class."""
    
    def create_test_team(self, team_id: str, name: str) -> Team:
        """Helper to create test team."""
        stats = LeagueStats(10, 7, 2, 1, 25, 10, 15, 23)
        
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
        
        return Team(
            id=team_id,
            name=name,
            country=name,
            players=players,
            starting_lineup=[p.id for p in players],
            league_stats=stats
        )
    
    def test_simulator_initialization(self):
        """Test simulator initialization."""
        team_a = self.create_test_team("team_a", "Team A")
        team_b = self.create_test_team("team_b", "Team B")
        
        simulator = MatchSimulator(team_a, team_b)
        
        assert simulator.team_a == team_a
        assert simulator.team_b == team_b
    
    def test_simulate_produces_match_result(self):
        """Test that simulation produces valid match result."""
        team_a = self.create_test_team("team_a", "Team A")
        team_b = self.create_test_team("team_b", "Team B")
        
        simulator = MatchSimulator(team_a, team_b, seed=42)
        result = simulator.simulate()
        
        assert isinstance(result, MatchResult)
        assert result.team_a_name == "Team A"
        assert result.team_b_name == "Team B"
        assert result.team_a_goals >= 0
        assert result.team_b_goals >= 0
    
    def test_simulate_scorers_count_matches_goals(self):
        """Test that number of scorers matches goal count."""
        team_a = self.create_test_team("team_a", "Team A")
        team_b = self.create_test_team("team_b", "Team B")
        
        simulator = MatchSimulator(team_a, team_b, seed=42)
        result = simulator.simulate()
        
        assert len(result.team_a_scorers) == result.team_a_goals
        assert len(result.team_b_scorers) == result.team_b_goals
    
    def test_simulate_goal_minutes_valid(self):
        """Test that goals occur at valid match minutes."""
        team_a = self.create_test_team("team_a", "Team A")
        team_b = self.create_test_team("team_b", "Team B")
        
        simulator = MatchSimulator(team_a, team_b, seed=42)
        result = simulator.simulate()
        
        valid_minutes = set(simulator.POSSIBLE_MINUTES)
        
        for goal in result.team_a_scorers + result.team_b_scorers:
            assert goal.minute in valid_minutes
    
    def test_simulate_reproducible_with_seed(self):
        """Test that simulation is reproducible with same seed."""
        team_a = self.create_test_team("team_a", "Team A")
        team_b = self.create_test_team("team_b", "Team B")
        
        sim1 = MatchSimulator(team_a, team_b, seed=123)
        result1 = sim1.simulate()
        
        sim2 = MatchSimulator(team_a, team_b, seed=123)
        result2 = sim2.simulate()
        
        assert result1.team_a_goals == result2.team_a_goals
        assert result1.team_b_goals == result2.team_b_goals
    
    def test_get_player_scores(self):
        """Test player scoring weights."""
        team = self.create_test_team("team_a", "Team A")
        simulator = MatchSimulator(team, team)
        
        scores = simulator._get_player_scores(team)
        
        assert len(scores) > 0
        assert all(score > 0 for score in scores.values())
    
    def test_get_assist_scores(self):
        """Test player assist weights."""
        team = self.create_test_team("team_a", "Team A")
        simulator = MatchSimulator(team, team)
        
        scores = simulator._get_assist_scores(team)
        
        assert len(scores) > 0
        assert all(score > 0 for score in scores.values())
    
    def test_simulate_multiple(self):
        """Test multiple simulations."""
        team_a = self.create_test_team("team_a", "Strong Team")
        team_b = self.create_test_team("team_b", "Weak Team")
        
        simulator = MatchSimulator(team_a, team_b, seed=42)
        stats = simulator.simulate_multiple(count=10)
        
        assert "team_a_wins" in stats
        assert "team_b_wins" in stats
        assert "draws" in stats
        assert stats["team_a_wins"] + stats["team_b_wins"] + stats["draws"] == 10
        assert "avg_goals_team_a" in stats
        assert "avg_goals_team_b" in stats
    
    def test_simulate_multiple_top_scorers(self):
        """Test that top scorers are tracked."""
        team_a = self.create_test_team("team_a", "Team A")
        team_b = self.create_test_team("team_b", "Team B")
        
        simulator = MatchSimulator(team_a, team_b, seed=42)
        stats = simulator.simulate_multiple(count=5)
        
        assert "top_scorers_team_a" in stats
        assert "top_scorers_team_b" in stats
        assert len(stats["top_scorers_team_a"]) <= 5
        assert len(stats["top_scorers_team_b"]) <= 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
