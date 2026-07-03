"""
Match Simulator - Generate match results with scorers and assists.
"""
import random
from typing import List, Tuple, Optional
from dataclasses import dataclass
from models import Player, Team


@dataclass
class GoalEvent:
    """Represents a goal scored in a match."""
    scorer: str
    assister: Optional[str]
    minute: int
    team_name: str
    
    def __str__(self) -> str:
        assist_str = f" (assist: {self.assister})" if self.assister else ""
        return f"{self.scorer}{assist_str} {self.minute}'"


@dataclass
class MatchResult:
    """Represents a complete match simulation."""
    team_a_name: str
    team_b_name: str
    team_a_goals: int
    team_b_goals: int
    team_a_scorers: List[GoalEvent]
    team_b_scorers: List[GoalEvent]
    match_summary: str
    
    def get_winner(self) -> Optional[str]:
        """Get match winner or None for draw."""
        if self.team_a_goals > self.team_b_goals:
            return self.team_a_name
        elif self.team_b_goals > self.team_a_goals:
            return self.team_b_name
        return None
    
    def __str__(self) -> str:
        """Format match result as string."""
        result = f"\n{'='*70}\n"
        result += f"{self.team_a_name} {self.team_a_goals} - {self.team_b_goals} {self.team_b_name}\n"
        result += f"{'='*70}\n\n"
        
        if self.team_a_scorers:
            result += f"⚽ {self.team_a_name} Scorers:\n"
            for goal in self.team_a_scorers:
                result += f"   {goal}\n"
            result += "\n"
        
        if self.team_b_scorers:
            result += f"⚽ {self.team_b_name} Scorers:\n"
            for goal in self.team_b_scorers:
                result += f"   {goal}\n"
            result += "\n"
        
        if self.get_winner():
            result += f"🏆 Winner: {self.get_winner()}\n"
        else:
            result += f"🤝 Draw!\n"
        
        result += f"\n📝 Summary: {self.match_summary}\n"
        result += f"{'='*70}\n"
        
        return result


class MatchSimulator:
    """Simulates a match with goal predictions."""
    
    # Match minutes where goals can be scored
    POSSIBLE_MINUTES = [
        5, 8, 12, 15, 18, 22, 25, 28, 32, 35, 38, 40, 42, 45,  # First half
        47, 50, 53, 55, 58, 62, 65, 68, 70, 72, 75, 78, 80, 82, 85, 88, 90  # Second half
    ]
    
    def __init__(self, team_a: Team, team_b: Team, seed: Optional[int] = None):
        """Initialize match simulator.
        
        Args:
            team_a: First team
            team_b: Second team
            seed: Random seed for reproducibility
        """
        self.team_a = team_a
        self.team_b = team_b
        
        if seed is not None:
            random.seed(seed)
    
    def _calculate_goal_probability(self, team: Team) -> float:
        """Calculate probability of a goal being scored.
        
        Based on team's league statistics and squad strength.
        """
        league_stats = team.league_stats
        
        if league_stats.matches_played == 0:
            return 0.5  # Default for no history
        
        # Goals per match in recent games
        goals_per_match = league_stats.goals_for / league_stats.matches_played
        
        # Scale to 0-1 probability
        # Assume 2 goals/match = 50% chance in any 5-minute window
        return min(0.1, goals_per_match / 20)
    
    def _get_player_scores(self, team: Team) -> dict:
        """Get all players weighted by goal-scoring probability.
        
        Returns:
            Dict mapping player_id to (player, score)
        """
        starters = team.get_starting_players()
        scores = {}
        
        for player in starters:
            # FWD: 1.0x, MID: 0.5x, DEF: 0.1x, GK: 0.0x
            position_weight = {
                "FWD": 1.0,
                "MID": 0.5,
                "DEF": 0.1,
                "GK": 0.0
            }.get(player.position, 0.0)
            
            # Score based on goals + position
            goal_score = (player.goals + 1) * position_weight  # +1 to avoid zero
            scores[player.id] = (player, max(0.01, goal_score))  # Minimum score
        
        return scores
    
    def _get_assist_scores(self, team: Team) -> dict:
        """Get all players weighted by assist probability.
        
        Returns:
            Dict mapping player_id to (player, score)
        """
        starters = team.get_starting_players()
        scores = {}
        
        for player in starters:
            # MID: 1.0x, FWD: 0.7x, DEF: 0.5x, GK: 0.0x
            position_weight = {
                "MID": 1.0,
                "FWD": 0.7,
                "DEF": 0.5,
                "GK": 0.0
            }.get(player.position, 0.0)
            
            # Score based on assists + position
            assist_score = (player.assists + 1) * position_weight  # +1 to avoid zero
            scores[player.id] = (player, max(0.01, assist_score))  # Minimum score
        
        return scores
    
    def _select_player_weighted(self, scores: dict) -> Player:
        """Select a player based on weighted probabilities.
        
        Args:
            scores: Dict mapping player_id to (player, weight)
            
        Returns:
            Selected player
        """
        if not scores:
            return None
        
        # Extract players and scores
        players = [v[0] for v in scores.values()]
        weights = [v[1] for v in scores.values()]
        
        # Normalize scores to probabilities
        total = sum(weights)
        probabilities = [w / total for w in weights]
        
        # Weighted random selection
        return random.choices(players, weights=probabilities, k=1)[0]
    
    def _simulate_team_goals(self, team: Team, opponent_team: Team) -> List[GoalEvent]:
        """Simulate goals scored by a team.
        
        Args:
            team: Team that's scoring
            opponent_team: Defending team (for context)
            
        Returns:
            List of goal events
        """
        goals = []
        goal_probability = self._calculate_goal_probability(team)
        goal_scorer_weights = self._get_player_scores(team)
        assist_weights = self._get_assist_scores(team)
        
        # Simulate goal scoring at random minutes
        for minute in self.POSSIBLE_MINUTES:
            if random.random() < goal_probability:
                # Select scorer
                scorer = self._select_player_weighted(goal_scorer_weights)
                
                # Select assister (60% chance of assist)
                assister = None
                if random.random() < 0.6:
                    assister = self._select_player_weighted(assist_weights)
                    # Assister should be different from scorer
                    if assister == scorer:
                        # Pick a different player
                        other_players = [v[0] for v in assist_weights.values() if v[0].id != scorer.id]
                        if other_players:
                            assister = random.choice(other_players)
                
                goal = GoalEvent(
                    scorer=scorer.name,
                    assister=assister.name if assister else None,
                    minute=minute,
                    team_name=team.name
                )
                goals.append(goal)
        
        return goals
    
    def simulate(self) -> MatchResult:
        """Simulate a complete match.
        
        Returns:
            MatchResult with goals, scorers, and assists
        """
        # Simulate goals for both teams
        team_a_goals = self._simulate_team_goals(self.team_a, self.team_b)
        team_b_goals = self._simulate_team_goals(self.team_b, self.team_a)
        
        # Sort by minute
        team_a_goals.sort(key=lambda g: g.minute)
        team_b_goals.sort(key=lambda g: g.minute)
        
        # Generate summary
        score_a = len(team_a_goals)
        score_b = len(team_b_goals)
        
        if score_a > score_b:
            summary = f"{self.team_a.name} dominated with clinical finishing"
        elif score_b > score_a:
            summary = f"{self.team_b.name} controlled the match and found the net"
        else:
            summary = "Even contest with both sides getting chances"
        
        return MatchResult(
            team_a_name=self.team_a.name,
            team_b_name=self.team_b.name,
            team_a_goals=score_a,
            team_b_goals=score_b,
            team_a_scorers=team_a_goals,
            team_b_scorers=team_b_goals,
            match_summary=summary
        )
    
    def simulate_multiple(self, count: int = 100) -> dict:
        """Run multiple match simulations for statistics.
        
        Args:
            count: Number of simulations to run
            
        Returns:
            Dict with match statistics
        """
        results = {
            "team_a_wins": 0,
            "team_b_wins": 0,
            "draws": 0,
            "avg_goals_team_a": 0.0,
            "avg_goals_team_b": 0.0,
            "top_scorers_team_a": {},
            "top_scorers_team_b": {},
            "top_assisters_team_a": {},
            "top_assisters_team_b": {}
        }
        
        total_goals_a = 0
        total_goals_b = 0
        
        for _ in range(count):
            match = self.simulate()
            
            # Count winners
            if match.get_winner() == self.team_a.name:
                results["team_a_wins"] += 1
            elif match.get_winner() == self.team_b.name:
                results["team_b_wins"] += 1
            else:
                results["draws"] += 1
            
            # Accumulate goals
            total_goals_a += match.team_a_goals
            total_goals_b += match.team_b_goals
            
            # Track scorers
            for goal in match.team_a_scorers:
                results["top_scorers_team_a"][goal.scorer] = \
                    results["top_scorers_team_a"].get(goal.scorer, 0) + 1
                if goal.assister:
                    results["top_assisters_team_a"][goal.assister] = \
                        results["top_assisters_team_a"].get(goal.assister, 0) + 1
            
            for goal in match.team_b_scorers:
                results["top_scorers_team_b"][goal.scorer] = \
                    results["top_scorers_team_b"].get(goal.scorer, 0) + 1
                if goal.assister:
                    results["top_assisters_team_b"][goal.assister] = \
                        results["top_assisters_team_b"].get(goal.assister, 0) + 1
        
        # Calculate averages
        results["avg_goals_team_a"] = round(total_goals_a / count, 2)
        results["avg_goals_team_b"] = round(total_goals_b / count, 2)
        
        # Sort top scorers and assisters
        results["top_scorers_team_a"] = dict(sorted(
            results["top_scorers_team_a"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5])
        
        results["top_scorers_team_b"] = dict(sorted(
            results["top_scorers_team_b"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5])
        
        results["top_assisters_team_a"] = dict(sorted(
            results["top_assisters_team_a"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5])
        
        results["top_assisters_team_b"] = dict(sorted(
            results["top_assisters_team_b"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5])
        
        return results
