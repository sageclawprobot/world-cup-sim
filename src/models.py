"""
Data models for World Cup simulation.
"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Player:
    """Represents a soccer player."""
    id: str
    name: str
    team_id: str
    position: str  # GK, DEF, MID, FWD
    goals: int
    assists: int
    shots_on_target: int
    shots_on_goal: int
    headed_attempts_on_goal: int
    
    def get_score(self) -> float:
        """Calculate player's contribution score.
        
        Weighted calculation based on:
        - Goals (40%)
        - Assists (30%)
        - Shots on target (20%)
        - Headed attempts (10%)
        """
        base_score = (self.goals * 0.4) + (self.assists * 0.3)
        shot_efficiency = (self.shots_on_target / max(1, self.shots_on_goal)) * 0.2 if self.shots_on_goal > 0 else 0
        heading_score = (self.headed_attempts_on_goal * 0.05) * 0.1  # scaled
        return base_score + shot_efficiency + heading_score


@dataclass
class LeagueStats:
    """Team league statistics."""
    matches_played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int


@dataclass
class Team:
    """Represents a soccer team."""
    id: str
    name: str
    country: str
    players: List[Player]
    starting_lineup: List[str]  # List of player IDs
    league_stats: LeagueStats
    
    def get_starting_players(self) -> List[Player]:
        """Get the list of starting players."""
        player_map = {p.id: p for p in self.players}
        return [player_map[pid] for pid in self.starting_lineup if pid in player_map]
    
    def calculate_team_score(self) -> float:
        """Calculate overall team score from starting lineup."""
        starters = self.get_starting_players()
        if not starters:
            return 0.0
        
        # Sum of top 7 players' scores (typical starting 11 contribution)
        sorted_players = sorted(starters, key=lambda p: p.get_score(), reverse=True)
        top_players = sorted_players[:7]  # Top 7 contributors
        
        total_score = sum(p.get_score() for p in top_players)
        return total_score / len(top_players) if top_players else 0.0
    
    def get_league_strength(self) -> float:
        """Calculate league strength from recent performance.
        
        Factors: W/D/L record, goal difference, points.
        """
        if self.league_stats.matches_played == 0:
            return 0.0
        
        # Win rate (50%), points per match (30%), goal diff normalized (20%)
        win_rate = (self.league_stats.wins / self.league_stats.matches_played) * 50
        ppg = (self.league_stats.points / self.league_stats.matches_played) * 30
        goal_diff_score = min(20, max(0, (self.league_stats.goal_difference / self.league_stats.matches_played) * 5))
        
        return (win_rate + ppg + goal_diff_score) / 10
