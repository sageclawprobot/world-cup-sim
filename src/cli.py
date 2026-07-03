"""
Command-line interface for World Cup Match Simulator.
Allows comparing specific teams with live data.
"""
import sys
import argparse
from pathlib import Path

from api_client import fetch_and_save_data
from models import Team
from predictor import MatchPredictor
from match_simulator import MatchSimulator
from visualizer import MatchVisualizer
from data_exporter import DataExportPipeline


def load_data(teams_path: str, players_path: str) -> tuple:
    """Load team and player data from JSON files."""
    import json
    
    # Load players
    with open(players_path, 'r') as f:
        players_data = json.load(f)
    
    players_by_id = {}
    for player_dict in players_data['players']:
        from models import Player
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
    
    teams = {}
    for team_dict in teams_data['teams']:
        from models import LeagueStats
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
        
        team_players = [players_by_id[pid] for pid in players_by_id 
                       if players_by_id[pid].team_id == team_dict['id']]
        
        team = Team(
            id=team_dict['id'],
            name=team_dict['name'],
            country=team_dict['country'],
            players=team_players,
            starting_lineup=team_dict['starting_lineup'],
            league_stats=league_stats
        )
        teams[team.name] = team
    
    return teams


def find_team_by_name(teams: dict, name: str) -> Team:
    """Find team by partial name match (case-insensitive)."""
    name_lower = name.lower()
    
    # Exact match first
    for team_name, team in teams.items():
        if team_name.lower() == name_lower:
            return team
    
    # Partial match
    for team_name, team in teams.items():
        if name_lower in team_name.lower() or team_name.lower() in name_lower:
            return team
    
    # Country match
    for team_name, team in teams.items():
        if name_lower in team.country.lower() or team.country.lower() in name_lower:
            return team
    
    return None


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='World Cup 2026 Match Simulator - Compare any two teams',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 cli.py Argentina "Cape Verde"
  python3 cli.py Brazil Mexico --live
  python3 cli.py "South Africa" "Saudi Arabia" --live --export all
        """
    )
    
    parser.add_argument('team_a', help='First team name')
    parser.add_argument('team_b', help='Second team name')
    parser.add_argument('--live', '-L', action='store_true',
                       help='Fetch fresh data from worldcup26.ir API')
    parser.add_argument('--export', '-E', choices=['all', 'csv', 'json', 'none'],
                       default='csv', help='Export results format')
    parser.add_argument('--output', '-O', default='output',
                       help='Output directory for results')
    parser.add_argument('--seed', '-S', type=int, default=42,
                       help='Random seed for reproducible simulations')
    parser.add_argument('--simulations', type=int, default=1,
                       help='Number of match simulations to run')
    
    args = parser.parse_args()
    
    # Setup paths
    project_root = Path(__file__).parent.parent
    data_dir = project_root / 'data'
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)
    
    teams_path = data_dir / 'teams.json'
    players_path = data_dir / 'players.json'
    
    # Fetch fresh data if requested
    if args.live:
        print(f"🌐 Fetching live World Cup 2026 data...")
        fetch_and_save_data(str(teams_path), str(players_path))
        print(f"✅ Data refreshed from worldcup26.ir\n")
    
    # Load teams
    print(f"📂 Loading team data...")
    teams = load_data(str(teams_path), str(players_path))
    print(f"✅ Loaded {len(teams)} teams\n")
    
    # Find specified teams
    team_a = find_team_by_name(teams, args.team_a)
    team_b = find_team_by_name(teams, args.team_b)
    
    if not team_a:
        print(f"❌ Team not found: {args.team_a}")
        print(f"Available teams: {', '.join(sorted(teams.keys()))}")
        return 1
    
    if not team_b:
        print(f"❌ Team not found: {args.team_b}")
        print(f"Available teams: {', '.join(sorted(teams.keys()))}")
        return 1
    
    print(f"⚽ Match: {team_a.name} vs {team_b.name}\n")
    
    # Display team stats
    print(f"📊 Team Statistics")
    print(f"{'='*70}")
    print(f"\n{team_a.name} ({team_a.country})")
    print(f"  Record: {team_a.league_stats.wins}W-{team_a.league_stats.draws}D-{team_a.league_stats.losses}L")
    print(f"  Goals: {team_a.league_stats.goals_for} for, {team_a.league_stats.goals_against} against (GD: {team_a.league_stats.goal_difference:+d})")
    print(f"  Points: {team_a.league_stats.points}")
    
    print(f"\n{team_b.name} ({team_b.country})")
    print(f"  Record: {team_b.league_stats.wins}W-{team_b.league_stats.draws}D-{team_b.league_stats.losses}L")
    print(f"  Goals: {team_b.league_stats.goals_for} for, {team_b.league_stats.goals_against} against (GD: {team_b.league_stats.goal_difference:+d})")
    print(f"  Points: {team_b.league_stats.points}")
    
    # Predict match
    print(f"\n{'='*70}")
    print(f"⚽ PREDICTION")
    print(f"{'='*70}\n")
    
    predictor = MatchPredictor(team_a, team_b)
    prediction = predictor.predict()
    
    print(f"{prediction['team_a']['name']}: {prediction['team_a']['win_probability']:.1f}%")
    print(f"  Squad Score: {prediction['team_a']['squad_score']:.2f}")
    print(f"  League Strength: {prediction['team_a']['league_strength']:.2f}")
    print(f"  Composite: {prediction['team_a']['composite_score']:.2f}")
    
    print(f"\n{prediction['team_b']['name']}: {prediction['team_b']['win_probability']:.1f}%")
    print(f"  Squad Score: {prediction['team_b']['squad_score']:.2f}")
    print(f"  League Strength: {prediction['team_b']['league_strength']:.2f}")
    print(f"  Composite: {prediction['team_b']['composite_score']:.2f}")
    
    print(f"\n🏆 Favorite: {prediction['favorite']}")
    
    # Simulate matches
    print(f"\n{'='*70}")
    print(f"🎮 MATCH SIMULATION ({args.simulations} match{'es' if args.simulations != 1 else ''})")
    print(f"{'='*70}\n")
    
    matches = []
    for i in range(args.simulations):
        simulator = MatchSimulator(team_a, team_b, seed=args.seed + i)
        match = simulator.simulate()
        matches.append(match)
        
        if args.simulations == 1:
            print(match)
        else:
            print(f"Match {i+1}: {match.team_a_name} {match.team_a_goals} - {match.team_b_goals} {match.team_b_name}")
    
    # Statistics for multiple simulations
    if args.simulations > 1:
        print(f"\n📈 Series Statistics ({args.simulations} matches)")
        print(f"{'='*70}")
        
        team_a_wins = sum(1 for m in matches if m.get_winner() == team_a.name)
        team_b_wins = sum(1 for m in matches if m.get_winner() == team_b.name)
        draws = len(matches) - team_a_wins - team_b_wins
        
        avg_goals_a = sum(m.team_a_goals for m in matches) / len(matches)
        avg_goals_b = sum(m.team_b_goals for m in matches) / len(matches)
        
        print(f"\n{team_a.name}: {team_a_wins}W - {draws}D - {team_b_wins}L")
        print(f"{team_b.name}: {team_b_wins}W - {draws}D - {team_a_wins}L")
        print(f"Draws: {draws}")
        print(f"\nAverage Goals:")
        print(f"  {team_a.name}: {avg_goals_a:.1f}")
        print(f"  {team_b.name}: {avg_goals_b:.1f}")
    
    # Export results
    if args.export != 'none':
        print(f"\n{'='*70}")
        print(f"📄 EXPORTING RESULTS")
        print(f"{'='*70}\n")
        
        if args.export in ['csv', 'all']:
            pipeline = DataExportPipeline(str(output_dir))
            export_results = pipeline.export_all([team_a, team_b], matches)
            
            for filename, info in export_results.items():
                print(f"✅ {filename}: {info['rows']} rows → {info['path']}")
        
        if args.export in ['json', 'all']:
            import json
            prediction_file = output_dir / 'prediction.json'
            with open(prediction_file, 'w') as f:
                json.dump(prediction, f, indent=2)
            print(f"✅ prediction.json → {prediction_file}")
    
    print(f"\n✨ Done!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
