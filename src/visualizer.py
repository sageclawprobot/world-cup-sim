"""
Visualization for match predictions.
"""
import json
from models import Team

try:
    import matplotlib.pyplot as plt
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class MatchVisualizer:
    """Creates visualizations for match analysis.
    
    Note: Charts will only be generated if matplotlib is installed.
    JSON output is always available.
    """
    
    def __init__(self, team_a: Team, team_b: Team, prediction: dict):
        self.team_a = team_a
        self.team_b = team_b
        self.prediction = prediction
    
    def save_win_probability_chart(self, output_path: str):
        """Create and save a bar chart of win probabilities."""
        if not HAS_MATPLOTLIB:
            return False
        
        teams = [
            self.prediction["team_a"]["name"],
            self.prediction["team_b"]["name"]
        ]
        probs = [
            self.prediction["team_a"]["win_probability"],
            self.prediction["team_b"]["win_probability"]
        ]
        
        plt.figure(figsize=(10, 6))
        colors = ['#4CAF50', '#FF6B6B']
        bars = plt.bar(teams, probs, color=colors, alpha=0.8, edgecolor='black', linewidth=2)
        
        # Add value labels on bars
        for bar, prob in zip(bars, probs):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{prob:.1f}%',
                    ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        plt.ylabel('Win Probability (%)', fontsize=12, fontweight='bold')
        plt.title('World Cup Match Prediction', fontsize=14, fontweight='bold')
        plt.ylim(0, 100)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        return True
    
    def save_team_scores_chart(self, output_path: str):
        """Create and save a chart comparing team composite scores."""
        if not HAS_MATPLOTLIB:
            return False
        
        teams = [
            self.prediction["team_a"]["name"],
            self.prediction["team_b"]["name"]
        ]
        scores = [
            self.prediction["team_a"]["composite_score"],
            self.prediction["team_b"]["composite_score"]
        ]
        
        plt.figure(figsize=(10, 6))
        colors = ['#2196F3', '#FF9800']
        bars = plt.bar(teams, scores, color=colors, alpha=0.8, edgecolor='black', linewidth=2)
        
        # Add value labels on bars
        for bar, score in zip(bars, scores):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{score:.2f}',
                    ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        plt.ylabel('Team Score', fontsize=12, fontweight='bold')
        plt.title('Team Strength Comparison', fontsize=14, fontweight='bold')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        return True
    
    def save_player_contribution_chart(self, output_path: str):
        """Create a radar chart comparing top players from each team."""
        if not HAS_MATPLOTLIB:
            return False
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6), subplot_kw=dict(projection='polar'))
        
        for idx, team in enumerate([self.team_a, self.team_b]):
            starters = team.get_starting_players()
            top_players = sorted(starters, key=lambda p: p.get_score(), reverse=True)[:5]
            
            names = [p.name for p in top_players]
            scores = [p.get_score() for p in top_players]
            
            angles = np.linspace(0, 2 * np.pi, len(names), endpoint=False).tolist()
            scores_plot = scores + [scores[0]]
            angles_plot = angles + [angles[0]]
            
            axes[idx].plot(angles_plot, scores_plot, 'o-', linewidth=2, markersize=8)
            axes[idx].fill(angles_plot, scores_plot, alpha=0.25)
            axes[idx].set_xticks(angles)
            axes[idx].set_xticklabels(names, size=10)
            axes[idx].set_ylim(0, max(scores) * 1.2)
            axes[idx].set_title(f"{team.name} - Top 5 Players", fontsize=12, fontweight='bold', pad=20)
            axes[idx].grid(True)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        return True
    
    def get_ascii_prediction(self) -> str:
        """Return a text-based prediction summary."""
        team_a = self.prediction["team_a"]
        team_b = self.prediction["team_b"]
        
        # Create a simple ASCII representation
        bars_a = int(team_a["win_probability"] / 5)
        bars_b = int(team_b["win_probability"] / 5)
        max_bars = 20
        
        output = []
        output.append(f"\n{team_a['name']:20} vs {team_b['name']:20}")
        output.append(f"({team_a['country']:15}) ({team_b['country']:15})")
        output.append("\n" + "="*70)
        
        output.append(f"\n{team_a['name']}")
        output.append(f"  Squad Score: {team_a['squad_score']:.2f} | League Strength: {team_a['league_strength']:.2f}")
        output.append(f"  Composite: {team_a['composite_score']:.2f}")
        output.append(f"  Win Prob: {team_a['win_probability']:.1f}% [{'█' * bars_a}{'░' * (max_bars - bars_a)}]")
        
        output.append(f"\n{team_b['name']}")
        output.append(f"  Squad Score: {team_b['squad_score']:.2f} | League Strength: {team_b['league_strength']:.2f}")
        output.append(f"  Composite: {team_b['composite_score']:.2f}")
        output.append(f"  Win Prob: {team_b['win_probability']:.1f}% [{'█' * bars_b}{'░' * (max_bars - bars_b)}]")
        
        output.append("\n" + "="*70)
        output.append(f"🏆 Favorite: {self.prediction['favorite']}")
        
        return "\n".join(output)
