"""
Unit tests for data models.
"""
import pytest
from models import Player, Team, LeagueStats


class TestPlayer:
    """Test Player model."""
    
    def test_player_creation(self):
        """Test creating a player."""
        player = Player(
            id="p1",
            name="Messi",
            team_id="team_1",
            position="FWD",
            goals=15,
            assists=8,
            shots_on_target=42,
            shots_on_goal=38,
            headed_attempts_on_goal=3
        )
        
        assert player.id == "p1"
        assert player.name == "Messi"
        assert player.position == "FWD"
        assert player.goals == 15
    
    def test_player_score_calculation(self):
        """Test player score calculation."""
        player = Player(
            id="p1",
            name="Messi",
            team_id="team_1",
            position="FWD",
            goals=10,
            assists=5,
            shots_on_target=30,
            shots_on_goal=20,
            headed_attempts_on_goal=2
        )
        
        score = player.get_score()
        # Score = (goals * 0.4) + (assists * 0.3) + shot_efficiency + heading
        # = (10 * 0.4) + (5 * 0.3) + (30/20)*0.2 + (2*0.05)*0.1
        # = 4 + 1.5 + 0.3 + 0.01 = 5.81
        assert score > 0
        assert score > 5  # Should be substantial for a striker
    
    def test_player_score_zero_stats(self):
        """Test player score with no stats."""
        player = Player(
            id="p1",
            name="Rookie",
            team_id="team_1",
            position="GK",
            goals=0,
            assists=0,
            shots_on_target=0,
            shots_on_goal=0,
            headed_attempts_on_goal=0
        )
        
        score = player.get_score()
        assert score == 0.0


class TestLeagueStats:
    """Test LeagueStats model."""
    
    def test_league_stats_creation(self):
        """Test creating league stats."""
        stats = LeagueStats(
            matches_played=10,
            wins=7,
            draws=2,
            losses=1,
            goals_for=25,
            goals_against=10,
            goal_difference=15,
            points=23
        )
        
        assert stats.matches_played == 10
        assert stats.wins == 7
        assert stats.points == 23
        assert stats.goal_difference == 15


class TestTeam:
    """Test Team model."""
    
    def test_team_creation(self):
        """Test creating a team."""
        stats = LeagueStats(10, 7, 2, 1, 25, 10, 15, 23)
        team = Team(
            id="team_1",
            name="Argentina",
            country="Argentina",
            players=[],
            starting_lineup=[],
            league_stats=stats
        )
        
        assert team.id == "team_1"
        assert team.name == "Argentina"
        assert team.league_stats.wins == 7
    
    def test_team_get_starting_players(self):
        """Test retrieving starting players."""
        stats = LeagueStats(10, 7, 2, 1, 25, 10, 15, 23)
        
        p1 = Player("p1", "Messi", "team_1", "FWD", 10, 5, 30, 20, 2)
        p2 = Player("p2", "De Paul", "team_1", "MID", 3, 6, 18, 12, 1)
        
        team = Team(
            id="team_1",
            name="Argentina",
            country="Argentina",
            players=[p1, p2],
            starting_lineup=["p1", "p2"],
            league_stats=stats
        )
        
        starters = team.get_starting_players()
        assert len(starters) == 2
        assert starters[0].name == "Messi"
        assert starters[1].name == "De Paul"
    
    def test_team_get_starting_players_missing(self):
        """Test retrieving starting players with missing IDs."""
        stats = LeagueStats(10, 7, 2, 1, 25, 10, 15, 23)
        
        p1 = Player("p1", "Messi", "team_1", "FWD", 10, 5, 30, 20, 2)
        
        team = Team(
            id="team_1",
            name="Argentina",
            country="Argentina",
            players=[p1],
            starting_lineup=["p1", "p_missing"],  # p_missing doesn't exist
            league_stats=stats
        )
        
        starters = team.get_starting_players()
        assert len(starters) == 1  # Only p1
    
    def test_team_calculate_team_score(self):
        """Test team score calculation."""
        stats = LeagueStats(10, 7, 2, 1, 25, 10, 15, 23)
        
        # Create 7 starters with varying scores
        players = []
        for i in range(7):
            p = Player(
                f"p{i}",
                f"Player {i}",
                "team_1",
                "FWD" if i < 3 else "MID",
                10 - i,  # Decreasing goals
                5 - (i // 2),  # Decreasing assists
                30 - i * 2,
                20 - i * 2,
                2 - (i // 3)
            )
            players.append(p)
        
        team = Team(
            id="team_1",
            name="Argentina",
            country="Argentina",
            players=players,
            starting_lineup=[p.id for p in players],
            league_stats=stats
        )
        
        score = team.calculate_team_score()
        assert score > 0
    
    def test_team_calculate_team_score_empty(self):
        """Test team score with no players."""
        stats = LeagueStats(10, 7, 2, 1, 25, 10, 15, 23)
        
        team = Team(
            id="team_1",
            name="Argentina",
            country="Argentina",
            players=[],
            starting_lineup=[],
            league_stats=stats
        )
        
        score = team.calculate_team_score()
        assert score == 0.0
    
    def test_team_get_league_strength(self):
        """Test league strength calculation."""
        stats = LeagueStats(
            matches_played=10,
            wins=8,
            draws=1,
            losses=1,
            goals_for=30,
            goals_against=10,
            goal_difference=20,
            points=25
        )
        
        team = Team(
            id="team_1",
            name="Brazil",
            country="Brazil",
            players=[],
            starting_lineup=[],
            league_stats=stats
        )
        
        strength = team.get_league_strength()
        assert strength > 0
        assert strength > 8  # Strong team should score high
    
    def test_team_get_league_strength_no_matches(self):
        """Test league strength with no matches."""
        stats = LeagueStats(0, 0, 0, 0, 0, 0, 0, 0)
        
        team = Team(
            id="team_1",
            name="NewTeam",
            country="NewCountry",
            players=[],
            starting_lineup=[],
            league_stats=stats
        )
        
        strength = team.get_league_strength()
        assert strength == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
