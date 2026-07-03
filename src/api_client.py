"""
World Cup 2026 API Client
Fetches live data from https://worldcup26.ir
"""
import requests
from typing import Dict, List, Optional
import json


class WorldCup26APIClient:
    """Client for worldcup26.ir API."""
    
    BASE_URL = "https://worldcup26.ir"
    TIMEOUT = 10
    
    def __init__(self, base_url: Optional[str] = None):
        """Initialize API client.
        
        Args:
            base_url: Override the default API base URL
        """
        self.base_url = base_url or self.BASE_URL
    
    def _request(self, endpoint: str) -> Dict:
        """Make HTTP request to API.
        
        Args:
            endpoint: API endpoint path (e.g., '/get/teams')
            
        Returns:
            JSON response as dict
            
        Raises:
            requests.RequestException: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, timeout=self.TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"API request failed for {endpoint}: {str(e)}")
    
    def get_teams(self) -> Dict:
        """Fetch all 48 qualified teams.
        
        Returns:
            Raw response from GET /get/teams
        """
        return self._request("/get/teams")
    
    def get_groups(self) -> Dict:
        """Fetch all 12 groups with standings.
        
        Returns:
            Raw response from GET /get/groups
        """
        return self._request("/get/groups")
    
    def get_games(self) -> Dict:
        """Fetch all match fixtures/results.
        
        Returns:
            Raw response from GET /get/games
        """
        return self._request("/get/games")
    
    def get_stadiums(self) -> Dict:
        """Fetch all 16 host stadiums.
        
        Returns:
            Raw response from GET /get/stadiums
        """
        return self._request("/get/stadiums")


class DataTransformer:
    """Transform WorldCup26 API data into simulator format."""
    
    @staticmethod
    def transform_teams(api_teams: Dict, api_games: Dict) -> tuple:
        """Transform API teams and games into simulator format.
        
        Args:
            api_teams: Raw teams response from API
            api_games: Raw games response from API
            
        Returns:
            Tuple of (teams_data, players_data)
        """
        teams_list = []
        players_list = []
        player_id_counter = 1
        
        # Build a map of team stats from games
        team_stats = {}
        if api_games and "games" in api_games:
            for game in api_games["games"]:
                # Check if game is finished
                if game.get("finished", "").upper() == "TRUE":
                    home_id = game.get("home_team_id")
                    away_id = game.get("away_team_id")
                    
                    if not home_id or not away_id:
                        continue
                    
                    if home_id not in team_stats:
                        team_stats[home_id] = {"wins": 0, "draws": 0, "losses": 0, "gf": 0, "ga": 0}
                    if away_id not in team_stats:
                        team_stats[away_id] = {"wins": 0, "draws": 0, "losses": 0, "gf": 0, "ga": 0}
                    
                    try:
                        home_goals = int(game.get("home_score", 0))
                        away_goals = int(game.get("away_score", 0))
                    except (ValueError, TypeError):
                        continue
                    
                    team_stats[home_id]["gf"] += home_goals
                    team_stats[home_id]["ga"] += away_goals
                    team_stats[away_id]["gf"] += away_goals
                    team_stats[away_id]["ga"] += home_goals
                    
                    if home_goals > away_goals:
                        team_stats[home_id]["wins"] += 1
                        team_stats[away_id]["losses"] += 1
                    elif away_goals > home_goals:
                        team_stats[away_id]["wins"] += 1
                        team_stats[home_id]["losses"] += 1
                    else:
                        team_stats[home_id]["draws"] += 1
                        team_stats[away_id]["draws"] += 1
        
        # Transform teams
        if api_teams and "teams" in api_teams:
            for team in api_teams["teams"]:
                team_id = f"team_{team['id']}"
                team_name = team.get("name_en", team.get("name", f"Team {team['id']}"))
                team_country = team.get("name_en", team_name)
                
                stats = team_stats.get(team["id"], {"wins": 0, "draws": 0, "losses": 0, "gf": 0, "ga": 0})
                matches_played = stats["wins"] + stats["draws"] + stats["losses"]
                points = stats["wins"] * 3 + stats["draws"]
                gd = stats["gf"] - stats["ga"]
                
                team_data = {
                    "id": team_id,
                    "name": team_name,
                    "country": team_country,
                    "starting_lineup": [],  # Will be populated with player IDs
                    "league_stats": {
                        "matches_played": matches_played,
                        "wins": stats["wins"],
                        "draws": stats["draws"],
                        "losses": stats["losses"],
                        "goals_for": stats["gf"],
                        "goals_against": stats["ga"],
                        "goal_difference": gd,
                        "points": points
                    }
                }
                
                # Generate synthetic players (11 starters)
                positions = ["GK", "DEF", "DEF", "DEF", "DEF", "MID", "MID", "MID", "FWD", "FWD", "FWD"]
                for i, position in enumerate(positions):
                    player_id = f"player_{player_id_counter}"
                    player_id_counter += 1
                    
                    # Synthetic stats based on team performance
                    avg_goals_per_player = stats["gf"] / 11 if matches_played > 0 else 0
                    position_multiplier = 1.2 if position == "FWD" else (0.5 if position == "MID" else 0.2)
                    
                    goals = int(avg_goals_per_player * position_multiplier)
                    assists = int(avg_goals_per_player * 0.4 * (1 if position in ["MID", "FWD"] else 0.3))
                    shots = goals * 3
                    shots_on_goal = goals * 2
                    headed = (goals // 2) if position in ["DEF", "FWD"] else 0
                    
                    player_data = {
                        "id": player_id,
                        "name": f"{team_country} Player {i+1}",
                        "team_id": team_id,
                        "position": position,
                        "goals": max(0, goals),
                        "assists": max(0, assists),
                        "shots_on_target": max(0, shots),
                        "shots_on_goal": max(0, shots_on_goal),
                        "headed_attempts_on_goal": max(0, headed)
                    }
                    
                    players_list.append(player_data)
                    team_data["starting_lineup"].append(player_id)
                
                teams_list.append(team_data)
        
        return {"teams": teams_list}, {"players": players_list}


def fetch_and_save_data(output_teams_path: str, output_players_path: str, base_url: Optional[str] = None) -> bool:
    """Fetch live World Cup data and save to JSON files.
    
    Args:
        output_teams_path: Path to save teams.json
        output_players_path: Path to save players.json
        base_url: Optional override for API base URL
        
    Returns:
        True if successful, False otherwise
    """
    try:
        print("🌐 Fetching World Cup 2026 data from worldcup26.ir...")
        
        client = WorldCup26APIClient(base_url=base_url)
        api_teams = client.get_teams()
        api_games = client.get_games()
        
        print("✅ Data fetched successfully")
        print(f"   Teams: {len(api_teams.get('teams', []))} teams")
        print(f"   Games: {len(api_games.get('games', []))} matches")
        
        # Transform data
        print("🔄 Transforming data...")
        teams_data, players_data = DataTransformer.transform_teams(api_teams, api_games)
        
        # Save to JSON
        print(f"💾 Saving to {output_teams_path}...")
        with open(output_teams_path, 'w') as f:
            json.dump(teams_data, f, indent=2)
        
        print(f"💾 Saving to {output_players_path}...")
        with open(output_players_path, 'w') as f:
            json.dump(players_data, f, indent=2)
        
        print("✨ Data sync complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error syncing data: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
