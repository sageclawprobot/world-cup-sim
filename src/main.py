"""
World Cup Match Simulation - Main Entry Point
"""
import json
import sys
from pathlib import Path

from api_client import fetch_and_save_data
from models import Player, Team, LeagueStats
from predictor import MatchPredictor
from visualizer import MatchVisualizer
from match_simulator import MatchSimulator
from data_exporter import DataExportPipeline


def load_data_from_json(teams_path: str, players_path: str) -> tuple[Team, Team]:
    """Load team and player data from separate JSON files."""
    # Load players
    with open(players_path, 'r') as f:
        players_data = json.load(f)
    
    players_by_id = {}
    for player_dict in players_data['players']:
        player = Player(
            id=player_dict['id'],
            name=player_dict['name'],
            team_id=player_dict['team_id'],
            position=player_dict['position'],
            goals=player_dict['goals'],
            assists=player_dict['assists'],
            shots_on_target=player_dict['shots_on_target'],
            shots_on_goal=player_dict['shots_on_goal'],
            headed_attempts_on_goal=player_dict['headed_attempts_on_goal']
        )
        players_by_id[player.id] = player
    
    # Load teams
    with open(teams_path, 'r') as f:
        teams_data = json.load(f)
    
    teams = []
    for team_dict in teams_data['teams']:
        league_stats = LeagueStats(
            matches_played=team_dict['league_stats']['matches_played'],
            wins=team_dict['league_stats']['wins'],
            draws=team_dict['league_stats']['draws'],
            losses=team_dict['league_stats']['losses'],
            goals_for=team_dict['league_stats']['goals_for'],
            goals_against=team_dict['league_stats']['goals_against'],
            goal_difference=team_dict['league_stats']['goal_difference'],
            points=team_dict['league_stats']['points']
        )
        
        # Get team players
        team_players = [players_by_id[pid] for pid in players_by_id if players_by_id[pid].team_id == team_dict['id']]
        
        team = Team(
            id=team_dict['id'],
            name=team_dict['name'],
            country=team_dict['country'],
            players=team_players,
            starting_lineup=team_dict['starting_lineup'],
            league_stats=league_stats
        )
        teams.append(team)
    
    return teams[0], teams[1]


def main():
    """Main simulation flow."""
    # Load data
    project_root = Path(__file__).parent.parent
    teams_path = project_root / 'data' / 'teams.json'
    players_path = project_root / 'data' / 'players.json'
    output_dir = project_root / 'output'
    output_dir.mkdir(exist_ok=True)
    
    print("🌍 World Cup Match Simulation")
    print("=" * 50)
    
    # Check if we should fetch live data
    use_live_data = '--live' in sys.argv or '-L' in sys.argv
    if use_live_data:
        print("\n📡 Fetching live World Cup data...")
        fetch_and_save_data(str(teams_path), str(players_path))
    else:
        print("\n📂 Using static local data (use --live or -L to fetch fresh data)")
    
    # Load teams and players
    team_a, team_b = load_data_from_json(str(teams_path), str(players_path))
    print(f"\n📋 Teams Loaded:")
    print(f"   Team A: {team_a.name} ({team_a.country})")
    print(f"   Team B: {team_b.name} ({team_b.country})")
    
    # Display league stats
    print(f"\n📊 League Statistics:")
    print(f"   {team_a.name}: {team_a.league_stats.wins}W-{team_a.league_stats.draws}D-{team_a.league_stats.losses}L (GD: {team_a.league_stats.goal_difference:+d}, Pts: {team_a.league_stats.points})")
    print(f"   {team_b.name}: {team_b.league_stats.wins}W-{team_b.league_stats.draws}D-{team_b.league_stats.losses}L (GD: {team_b.league_stats.goal_difference:+d}, Pts: {team_b.league_stats.points})")
    
    # Run prediction
    predictor = MatchPredictor(team_a, team_b)
    prediction = predictor.predict()
    
    print(f"\n⚽ Prediction Results:")
    print(f"   {prediction['team_a']['name']}: {prediction['team_a']['win_probability']}% (Composite: {prediction['team_a']['composite_score']})")
    print(f"   {prediction['team_b']['name']}: {prediction['team_b']['win_probability']}% (Composite: {prediction['team_b']['composite_score']})")
    print(f"\n🏆 Favorite: {prediction['favorite']}")
    
    # Simulate a sample match
    print(f"\n🎮 Simulating Match...")
    simulator = MatchSimulator(team_a, team_b, seed=42)
    match_result = simulator.simulate()
    print(match_result)
    
    # Export data to CSV
    print(f"\n📄 Exporting Data to CSV...")
    pipeline = DataExportPipeline(str(output_dir))
    export_results = pipeline.export_all([team_a, team_b], [match_result])
    
    for filename, info in export_results.items():
        print(f"   ✅ {filename}: {info['rows']} rows → {info['path']}")
    
    # Generate visualizations
    print(f"\n📊 Generating visualizations...")
    visualizer = MatchVisualizer(team_a, team_b, prediction)
    
    prob_chart = output_dir / 'win_probability.png'
    score_chart = output_dir / 'team_scores.png'
    player_chart = output_dir / 'player_contribution.png'
    
    if visualizer.save_win_probability_chart(str(prob_chart)):
        print(f"   ✅ Win Probability Chart: {prob_chart}")
    else:
        print(f"   ℹ️  Win Probability Chart: matplotlib not available (install with: pip install matplotlib)")
    
    if visualizer.save_team_scores_chart(str(score_chart)):
        print(f"   ✅ Team Scores Chart: {score_chart}")
    else:
        print(f"   ℹ️  Team Scores Chart: matplotlib not available")
    
    if visualizer.save_player_contribution_chart(str(player_chart)):
        print(f"   ✅ Player Contribution Chart: {player_chart}")
    else:
        print(f"   ℹ️  Player Contribution Chart: matplotlib not available")
    
    # Print ASCII visualization
    print(visualizer.get_ascii_prediction())
    
    # Save prediction to JSON
    prediction_output = output_dir / 'prediction.json'
    with open(prediction_output, 'w') as f:
        json.dump(prediction, f, indent=2)
    print(f"   ✅ Prediction Output: {prediction_output}")
    
    print("\n✨ Simulation complete!")


if __name__ == '__main__':
    main()
