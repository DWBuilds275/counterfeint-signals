import requests
import json
import os
from datetime import datetime

def fetch_upcoming_boxing_events(api_key):
    """
    Fetch upcoming boxing events from OpenOddsAPI.
    """
    url = "https://api.openoddsapi.com/v1/sports/boxing/odds"
    headers = {
        "X-API-Key": api_key
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            return transform_openodds_response(data)
        else:
            print(f"Error response: {response.text}")
            return []
    except Exception as e:
        print(f"Error fetching odds: {e}")
        return []

def transform_openodds_response(data):
    """
    Transform OpenOddsAPI response to our internal format.
    """
    events = []
    
    for bout in data.get("bouts", []):
        event = {
            "id": f"{bout.get('home', '')}_vs_{bout.get('away', '')}".replace(" ", "_"),
            "sport_title": "Boxing",
            "home_team": bout.get("home", "Unknown"),
            "away_team": bout.get("away", "Unknown"),
            "commence_time": bout.get("commence_time", ""),
            "bookmakers": []
        }
        
        for book in bout.get("books", []):
            bookmaker = {
                "key": book.get("book", "unknown"),
                "title": book.get("book", "Unknown").capitalize(),
                "last_update": book.get("last_update", ""),
                "markets": [
                    {
                        "key": "h2h",
                        "outcomes": []
                    }
                ]
            }
            
            for outcome in book.get("outcomes", []):
                bookmaker["markets"][0]["outcomes"].append({
                    "name": outcome.get("name", "Unknown"),
                    "price": outcome.get("price", 0)
                })
            
            event["bookmakers"].append(bookmaker)
        
        events.append(event)
    
    return events

def save_events_to_file(events, filename="data/upcoming_fights.json"):
    """
    Save events to a JSON file with timestamp.
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    data = {
        "timestamp": datetime.now().isoformat(),
        "events": events
    }
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved {len(events)} events to {filename}")

def main():
    api_key = os.getenv("OPENODDS_API_KEY")
    if not api_key:
        print("Error: OPENODDS_API_KEY environment variable not set")
        return
    
    events = fetch_upcoming_boxing_events(api_key)
    if events:
        save_events_to_file(events)
        print(f"Fetched {len(events)} events")
        
        # Print a sample event to verify
        if events:
            print("\nSample event:")
            sample = events[0]
            print(f"  {sample['home_team']} vs {sample['away_team']}")
            print(f"  Time: {sample['commence_time']}")
            if sample['bookmakers']:
                print(f"  Books: {', '.join([b['title'] for b in sample['bookmakers']])}")
    else:
        print("No events found or API error")

if __name__ == "__main__":
    main()