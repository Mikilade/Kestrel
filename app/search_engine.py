"""Makes requests to the IGDB API to search for Games. We then use the results to populate our Game objects."""

import os
import requests
from typing import List, Dict, Any

class IGDBApi:
    BASE_URL = "https://api.igdb.com/v4"
    
    def __init__(self):
        self.client_id = os.environ.get("IGDB_CLIENT_ID")
        self.access_token = os.environ.get("IGDB_ACCESS_TOKEN")
        
        if not self.client_id or not self.access_token:
            raise ValueError("IGDB_CLIENT_ID and IGDB_ACCESS_TOKEN must be set in .env file")
        
        # Grab the JWT token for the session by auth'ing through Twitch
        val_url = 'https://id.twitch.tv/oauth2/token'

        val_params = {
            'client_id': self.client_id,
            'client_secret': self.access_token,
            'grant_type': 'client_credentials'
        }

        response = requests.post(val_url, params=val_params)

        if response.status_code == 200:
            token = response.json()['access_token']
        else:
            raise Exception(f"Authentication failed: {response.text}")
        
        # Set headers with the retrieved JWT
        self.headers = {
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {token}',
        }
    
    def _make_request(self, endpoint: str, body: str) -> List[Dict[str, Any]]:
        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.post(url, headers=self.headers, data=body)
        response.raise_for_status()
        return response.json()
    
    def _process_cover_url(self, cover: Dict[str, Any]) -> str:
        if not cover:
            return None
        image_id = cover.get('image_id')
        if not image_id:
            return None
        return f"https://images.igdb.com/igdb/image/upload/t_cover_big/{image_id}.jpg"

    def _process_franchise_names(self, franchises: List[Dict[str, Any]]) -> List[str]:
        if not franchises:
            return []
        
        franchise_ids = [str(franchise) for franchise in franchises]
        
        if not franchise_ids:
            return []
        
        body = f"fields name; where id = ({','.join(franchise_ids)});"
        try:
            response = self._make_request('franchises', body)
            return [franchise['name'] for franchise in response if 'name' in franchise]
        except Exception as e:
            print(f"Error fetching franchise names: {e}")
            return []
    
    def _process_company_names(self, companies: List[Dict]) -> List[str]:
        if not companies:
            return []
        
        developers = []
        company_ids = [str(company['id']) for company in companies if 'id' in company]
        
        if not company_ids:
            return []

        body = f"fields developer; where id = ({','.join(company_ids)});"
        
        try:
            response = self._make_request('involved_companies', body)
            for company in response:
                print(company)
                if company.get('developer'):
                    developer_name = next(developer for developer in companies if developer['id'] == company.get('id'))
                    developer_name = developer_name['company']['name']
                    developers.append(developer_name)
            return developers
        except Exception as e:
            print(f"Error fetching company names: {e}")
            return []


    
    def search_games(self, query: str, limit: int = 30) -> List[Dict[str, Any]]:
        body = f'search "{query}"; fields id,name,summary,first_release_date,cover.image_id; limit {limit};'
        games = self._make_request('games', body)
        for game in games:
            game['cover_url'] = self._process_cover_url(game.get('cover'))
        return games

    
    def get_game_details(self, game_id: int) -> Dict[str, Any]:
        body = f'''
            fields name, summary, first_release_date, cover.image_id, 
            franchises, involved_companies.company.name;
            where id = {game_id};
        '''
        results = self._make_request('games', body)
        print(results)
        if results:
            game = results[0]
            game['cover_url'] = self._process_cover_url(game.get('cover'))
            game['franchise'] = self._process_franchise_names(game.get('franchises'))
            game['studio'] = self._process_company_names(game.get('involved_companies'))
            print(game)
        return game if results else None

# Usage example
if __name__ == "__main__":
    igdb = IGDBApi()

    # Search for games
    print("Searching for 'The Legend of Zelda':")
    games = igdb.search_games("Persona 5 Royal")
    for game in games:
        print(f"Name: {game['name']}")
        print(f"id: {game['id']}")
        print(f"Summary: {game.get('summary', 'N/A')}")
        print(f"Release Date: {game.get('first_release_date', 'N/A')}")
        print(f"Cover URL: {game.get('cover_url', 'N/A')}")
        print("---")
    
    # Get details for a specific game
    print("\nGetting details for game with ID 1942 (The Legend of Zelda: Breath of the Wild):")
    game_details = igdb.get_game_details(114283)
    if game_details:
        print(f"Name: {game_details['name']}")
        print(f"Summary: {game_details.get('summary', 'N/A')}")
        print(f"Release Date: {game_details.get('first_release_date', 'N/A')}")
        print(f"Franchise: {game_details.get('franchise', 'N/A')}")
        print(f"Studio: {game_details.get('studio', 'N/A')}")
        print(f"Cover URL: {game_details.get('cover_url', 'N/A')}")
    else:
        print("Game details not found.")

    # Demonstrate error handling
    print("\nTrying to initialize IGDBApi without environment variables:")
    try:
        # Temporarily unset environment variables
        client_id = os.environ.pop("IGDB_CLIENT_ID", None)
        access_token = os.environ.pop("IGDB_ACCESS_TOKEN", None)
        
        IGDBApi()
    except ValueError as e:
        print(f"Caught expected error: {e}")
    finally:
        # Restore environment variables
        if client_id:
            os.environ["IGDB_CLIENT_ID"] = client_id
        if access_token:
            os.environ["IGDB_ACCESS_TOKEN"] = access_token
