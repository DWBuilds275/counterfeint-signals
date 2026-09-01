import streamlit as st
import json

def load_data():
    try:
        with open("data/upcoming_fights.json", "r") as f:
            data = json.load(f)
            return data.get("events", [])
    except:
        return []

def get_commercial_value(fighter_name):
    """
    Placeholder for commercial value scoring.
    Replace with real data (social media, BoxRec, etc.)
    """
    # Mock score based on name length (replace with real data)
    score = len(fighter_name) * 2
    return min(score, 100)

def show_commercial_value():
    st.markdown("## Commercial Value Overlay")
    st.caption("Marketability vs. Betting Odds — Your Signature Stat")
    
    events = load_data()
    if not events:
        st.warning("No data available")
        return
    
    for event in events:
        st.markdown(f"### {event.get('home_team', 'Unknown')} vs {event.get('away_team', 'Unknown')}")
        
        fighters = {}
        
        if event.get('bookmakers'):
            book = event['bookmakers'][0]
            markets = book.get('markets', [])
            if markets:
                outcomes = markets[0].get('outcomes', [])
                for outcome in outcomes:
                    fighter = outcome.get('name', 'Unknown')
                    price = outcome.get('price', 0)
                    
                    commercial_score = get_commercial_value(fighter)
                    
                    fighters[fighter] = {
                        "odds": price,
                        "commercial_score": commercial_score,
                        "gap": commercial_score - abs(price) if price != 0 else 0
                    }
        
        if fighters:
            for fighter, data in fighters.items():
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Fighter", fighter)
                with col2:
                    st.metric("Odds", data["odds"])
                with col3:
                    st.metric("Commercial Score", data["commercial_score"])
            
            # Show gap analysis
            st.caption("Gap: Difference between commercial value and betting odds")
            for fighter, data in fighters.items():
                # Normalize gap for progress bar (0-100)
                gap_norm = max(0, min(100, data["gap"] + 50))
                st.progress(gap_norm / 100, text=f"{fighter}: {data['gap']}% gap")
        else:
            st.caption("No odds data available")
        
        st.divider()

if __name__ == "__main__":
    show_commercial_value()
    