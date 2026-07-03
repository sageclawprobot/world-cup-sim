#!/usr/bin/env python3
"""
Standalone script to fetch live World Cup data and update JSON files.
Usage: python3 fetch_live_data.py
"""
import sys
from pathlib import Path
from api_client import fetch_and_save_data


def main():
    """Fetch and save live data."""
    project_root = Path(__file__).parent.parent
    teams_path = project_root / 'data' / 'teams.json'
    players_path = project_root / 'data' / 'players.json'
    
    success = fetch_and_save_data(
        str(teams_path),
        str(players_path)
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
