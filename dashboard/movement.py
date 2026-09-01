import streamlit as st
import json
from datetime import datetime

def load_data():
    try:
        with open("data/upcoming_fights.json", "r") as f:
            data = json.load(f)
            return data.get("events", [])
    except:
        return []

def show_movement():
    st.markdown("## Odds Movement")
    st.caption("Track line changes over time (snapshots needed)")
    
    events = load_data()
    if not events:
        st.warning("No data available")
        return
    
    st.info("Movement tracking requires multiple snapshots. Current odds shown below.")
    
    for event in events[:5]:
        st.markdown(f"### {event.get('home_team', 'Unknown')} vs {event.get('away_team', 'Unknown')}")
        
        for book in event.get('bookmakers', []):
            book_name = book.get('title', 'Unknown')
            markets = book.get('markets', [])
            if markets:
                outcomes = markets[0].get('outcomes', [])
                if outcomes:
                    price = outcomes[0].get('price', 0)
                    st.caption(f"{book_name}: {price}")
        
        st.divider()

if __name__ == "__main__":
    show_movement()
    