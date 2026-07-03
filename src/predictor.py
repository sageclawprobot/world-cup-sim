"""
Match prediction logic.
"""
from models import Team


class MatchPredictor:
    """Predicts match outcomes based on team stats and player form."""
    
    def __init__(self, team_a: Team, team_b: Team):
        self.team_a = team_a
        self.team_b = team_b
    
    def predict(self) -> dict:
        """
        Predict match outcome with win probabilities.
        
        Combines:
        - Player form score (current squad strength) - 60%
        - League stats (recent performance) - 40%
        
        Returns:
            dict with team scores and win probabilities
        """
        # Player form score (squad strength)
        player_score_a = self.team_a.calculate_team_score()
        player_score_b = self.team_b.calculate_team_score()
        
        # League strength (recent form)
        league_score_a = self.team_a.get_league_strength()
        league_score_b = self.team_b.get_league_strength()
        
        # Weighted composite score
        score_a = (player_score_a * 0.6) + (league_score_a * 0.4)
        score_b = (player_score_b * 0.6) + (league_score_b * 0.4)
        
        total_score = score_a + score_b
        
        if total_score == 0:
            prob_a = 0.5
            prob_b = 0.5
        else:
            prob_a = score_a / total_score
            prob_b = score_b / total_score
        
        return {
            "team_a": {
                "name": self.team_a.name,
                "country": self.team_a.country,
                "squad_score": round(player_score_a, 2),
                "league_strength": round(league_score_a, 2),
                "composite_score": round(score_a, 2),
                "win_probability": round(prob_a * 100, 1)
            },
            "team_b": {
                "name": self.team_b.name,
                "country": self.team_b.country,
                "squad_score": round(player_score_b, 2),
                "league_strength": round(league_score_b, 2),
                "composite_score": round(score_b, 2),
                "win_probability": round(prob_b * 100, 1)
            },
            "favorite": self.team_a.name if prob_a > prob_b else self.team_b.name
        }
