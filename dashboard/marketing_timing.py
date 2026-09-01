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

def parse_fight_time(commence_time):
    """
    Parse the commence_time string from the API.
    Handles formats like: 2026-09-13T03:00:00.000Z
    """
    if not commence_time:
        return None
    
    try:
        # Remove the 'Z' and any milliseconds if present
        # Format: 2026-09-13T03:00:00.000Z
        if 'Z' in commence_time:
            # Split on 'Z' and take the first part
            clean_time = commence_time.split('Z')[0]
            # Handle milliseconds
            if '.' in clean_time:
                clean_time = clean_time.split('.')[0]
            return datetime.fromisoformat(clean_time)
        else:
            return datetime.fromisoformat(commence_time)
    except Exception as e:
        print(f"Error parsing date: {commence_time} - {e}")
        return None

def show_marketing_timing():
    st.markdown("## Marketing Calendar")
    st.caption("Plan your content around upcoming fights")
    
    events = load_data()
    if not events:
        st.warning("No data available")
        return
    
    today = datetime.now()
    
    for event in events:
        # Parse the fight time
        commence_time = event.get('commence_time', '')
        fight_time = parse_fight_time(commence_time)
        
        if fight_time:
            days_until = (fight_time - today).days
        else:
            days_until = None
        
        with st.expander(f"{event.get('home_team', 'Unknown')} vs {event.get('away_team', 'Unknown')}"):
            # Show the fight date and days until
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Fight Date", commence_time[:10] if commence_time else "Unknown")
            with col2:
                if days_until is not None:
                    st.metric("Days Until", days_until)
                else:
                    st.metric("Days Until", "Unknown")
            
            # Marketing timeline
            st.markdown("**Marketing Timeline**")
            if days_until is not None:
                if days_until > 21:
                    st.info("📝 Teaser phase — start building interest")
                elif days_until > 7:
                    st.info("📊 Build-up phase — share stats and context")
                elif days_until > 1:
                    st.warning("🔥 Peak phase — full content drop")
                elif days_until == 0:
                    st.success("✅ Fight day — post-fight recap coming")
                elif days_until < 0:
                    st.success(f"✅ Fight happened {abs(days_until)} days ago — recap ready")
                else:
                    st.caption("Fight is today!")
            else:
                st.caption("Date not available — check API response")
            
            # Show fighters
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Home", event.get('home_team', 'Unknown'))
            with col2:
                st.metric("Away", event.get('away_team', 'Unknown'))
            
            # Show bookmakers
            bookmakers = event.get('bookmakers', [])
            if bookmakers:
                st.caption(f"Odds available from {len(bookmakers)} books")