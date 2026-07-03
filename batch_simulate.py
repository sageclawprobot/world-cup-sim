#!/usr/bin/env python3
"""
Batch simulator for World Cup 2026 matches.
Runs simulations for all pending/interesting matchups.
"""
import json
import sys
from pathlib import Path
import subprocess
from datetime import datetime

def get_top_teams(teams_data, top_n=16):
    """Get top N teams by league strength."""
    teams_list = teams_data.get('teams', [])
    
    # Score teams by their league stats
    scored = []
    for team in teams_list:
        stats = team.get('league_stats', {})
        points = stats.get('points', 0)
        goals_diff = stats.get('goal_difference', 0)
        wins = stats.get('wins', 0)
        
        # Simple ranking: points + goal difference bonus
        score = points + (goals_diff * 0.5) + (wins * 2)
        scored.append((team['name'], team['country'], score))
    
    # Sort by score and return top N
    scored.sort(key=lambda x: x[2], reverse=True)
    return [name for name, country, score in scored[:top_n]]

def generate_matchups(teams, include_classic=True):
    """Generate interesting matchups."""
    matchups = []
    
    # All combinations of top teams
    for i, team_a in enumerate(teams):
        for team_b in teams[i+1:]:
            matchups.append((team_a, team_b))
    
    # Add classic rivalries if requested
    if include_classic:
        classics = [
            ('Argentina', 'Brazil'),
            ('France', 'Germany'),
            ('England', 'Spain'),
            ('Italy', 'Germany'),
            ('Netherlands', 'France'),
            ('Portugal', 'France'),
            ('Croatia', 'France'),
        ]
        for team_a, team_b in classics:
            if (team_a, team_b) not in matchups and (team_b, team_a) not in matchups:
                matchups.append((team_a, team_b))
    
    return matchups

def run_batch_simulations(matchups, output_dir='batch_results'):
    """Run simulations for all matchups."""
    Path(output_dir).mkdir(exist_ok=True)
    
    results = []
    total = len(matchups)
    
    print(f"\n🎮 BATCH SIMULATION - {total} Matchups")
    print("="*70)
    
    for i, (team_a, team_b) in enumerate(matchups, 1):
        # Run CLI for each matchup
        cmd = [
            'python3', 'src/cli.py',
            team_a, team_b,
            '--export', 'json',
            '--output', f'{output_dir}/match_{i}'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # Extract prediction from output
                if 'Favorite:' in result.stdout:
                    favorite = result.stdout.split('Favorite:')[1].split('\n')[0].strip()
                    prob_line = result.stdout.split('%')[0].split('\n')[-1]
                    
                    print(f"  {i:3d}/{total} ✅ {team_a:20s} vs {team_b:20s} → {favorite}")
                    
                    results.append({
                        'match_id': i,
                        'team_a': team_a,
                        'team_b': team_b,
                        'favorite': favorite,
                        'status': 'completed'
                    })
            else:
                print(f"  {i:3d}/{total} ❌ {team_a:20s} vs {team_b:20s}")
                results.append({
                    'match_id': i,
                    'team_a': team_a,
                    'team_b': team_b,
                    'status': 'failed'
                })
        
        except Exception as e:
            print(f"  {i:3d}/{total} ❌ {team_a:20s} vs {team_b:20s} - {str(e)[:30]}")
            results.append({
                'match_id': i,
                'team_a': team_a,
                'team_b': team_b,
                'status': 'error',
                'error': str(e)
            })
    
    return results

def generate_batch_report(results, output_dir='batch_results'):
    """Generate summary report."""
    Path(output_dir).mkdir(exist_ok=True)
    
    # Save results as JSON
    report_file = Path(output_dir) / 'batch_results.json'
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Generate CSV
    csv_file = Path(output_dir) / 'batch_results.csv'
    with open(csv_file, 'w') as f:
        f.write('match_id,team_a,team_b,favorite,status\n')
        for r in results:
            f.write(f"{r['match_id']},{r['team_a']},{r['team_b']},{r.get('favorite', 'N/A')},{r['status']}\n")
    
    # Print summary
    completed = sum(1 for r in results if r['status'] == 'completed')
    failed = len(results) - completed
    
    print("\n" + "="*70)
    print(f"📊 BATCH SIMULATION COMPLETE")
    print(f"  Completed: {completed}/{len(results)}")
    if failed > 0:
        print(f"  Failed: {failed}")
    print(f"\n  Results: {report_file}")
    print(f"  CSV: {csv_file}")
    
    return results

def main():
    """Main entry point."""
    print("🌍 World Cup 2026 - Batch Simulation")
    print("="*70)
    
    # Load team data
    with open('data/teams.json', 'r') as f:
        teams_data = json.load(f)
    
    # Get top teams
    print("\n📋 Selecting top 16 teams...")
    top_teams = get_top_teams(teams_data, top_n=16)
    
    print(f"✅ Top teams selected:")
    for i, team in enumerate(top_teams, 1):
        print(f"  {i:2d}. {team}")
    
    # Generate matchups
    print(f"\n🎯 Generating matchups...")
    matchups = generate_matchups(top_teams, include_classic=True)
    print(f"✅ {len(matchups)} matchups to simulate")
    
    # Run simulations
    results = run_batch_simulations(matchups, output_dir='batch_results')
    
    # Generate report
    generate_batch_report(results, output_dir='batch_results')
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
