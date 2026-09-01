import streamlit as st
import json
import pandas as pd
from datetime import datetime
import csv
import io
from dashboard.comparison import show_comparison
from dashboard.movement import show_movement
from dashboard.commercial_value import show_commercial_value
from dashboard.marketing_timing import show_marketing_timing
from dashboard.report_generator import show_report_generator

# ---- AUTHENTICATION ----
def check_password():
    """Returns True if the user entered the correct password."""
    if st.session_state.get("authenticated", False):
        return True
    
    st.markdown("### 🔐 Enter Password")
    password = st.text_input("Password", type="password")
    
    # Replace with your own password
    CORRECT_PASSWORD = "Dw2402343!"
    
    if password == CORRECT_PASSWORD:
        st.session_state.authenticated = True
        st.rerun()
    elif password:
        st.error("Incorrect password")
    return False

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="Counter-Feint Signals",
    page_icon="🥊",
    layout="wide"
)

# Check password before showing anything else
if not check_password():
    st.stop()

# ---- EXPORT FUNCTION ----
def export_to_csv():
    """Export all fight data to CSV."""
    try:
        with open("data/upcoming_fights.json", "r") as f:
            data = json.load(f)
            events = data.get("events", [])
        
        if not events:
            st.warning("No data to export")
            return
        
        # Flatten the data for CSV
        rows = []
        for event in events:
            home = event.get('home_team', 'Unknown')
            away = event.get('away_team', 'Unknown')
            date = event.get('commence_time', 'Unknown')
            
            for book in event.get('bookmakers', []):
                book_name = book.get('title', 'Unknown')
                markets = book.get('markets', [])
                if markets:
                    outcomes = markets[0].get('outcomes', [])
                    for outcome in outcomes:
                        rows.append({
                            "Home": home,
                            "Away": away,
                            "Date": date,
                            "Bookmaker": book_name,
                            "Fighter": outcome.get('name', 'Unknown'),
                            "Price": outcome.get('price', 0)
                        })
        
        # Create CSV
        df = pd.DataFrame(rows)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        
        # Download button
        st.download_button(
            label="📥 Download CSV",
            data=csv_buffer.getvalue(),
            file_name=f"counterfeint_signals_export_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        st.caption(f"Exported {len(rows)} rows of data")
        
    except FileNotFoundError:
        st.error("No data file found to export")
    except Exception as e:
        st.error(f"Error exporting data: {e}")

# ---- DEFINE FUNCTIONS ----
def show_upcoming_fights():
    st.markdown("## Upcoming Fights")
    
    try:
        with open("data/upcoming_fights.json", "r") as f:
            data = json.load(f)
            events = data.get("events", [])
            timestamp = data.get("timestamp", "Unknown")
            
        st.caption(f"Last updated: {timestamp}")
        
        if events:
            st.success(f"Found {len(events)} upcoming fights")
            
            for event in events:
                with st.expander(f"{event.get('home_team', 'Unknown')} vs {event.get('away_team', 'Unknown')}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Home", event.get('home_team', 'Unknown'))
                        st.metric("Away", event.get('away_team', 'Unknown'))
                    with col2:
                        st.metric("Date/Time", event.get('commence_time', 'Unknown')[:16] if event.get('commence_time') else 'Unknown')
                    with col3:
                        bookmakers = event.get('bookmakers', [])
                        st.metric("Books", len(bookmakers))
                    
                    if bookmakers:
                        st.markdown("**Odds by Bookmaker**")
                        odds_data = []
                        for book in bookmakers:
                            book_name = book.get('title', 'Unknown')
                            markets = book.get('markets', [])
                            if markets:
                                outcomes = markets[0].get('outcomes', [])
                                for outcome in outcomes:
                                    odds_data.append({
                                        "Book": book_name,
                                        "Fighter": outcome.get('name', 'Unknown'),
                                        "Price": outcome.get('price', 0)
                                    })
                        if odds_data:
                            st.dataframe(pd.DataFrame(odds_data))
        else:
            st.warning("No upcoming fights found. Run `utils/odds_fetcher.py` to fetch data.")
            
    except FileNotFoundError:
        st.error("Data file not found. Run `utils/odds_fetcher.py` to fetch data.")
    except Exception as e:
        st.error(f"Error loading data: {e}")

# ---- UI STARTS HERE ----
st.title("🥊 Counter-Feint Signals")
st.subheader("Internal Analytics Dashboard")

# Sidebar Navigation
st.sidebar.header("Navigation")
st.sidebar.markdown("---")
st.sidebar.info(
    "**Private Dashboard**\n\n"
    "This dashboard is for internal use only. "
    "Subscribers never see this."
)

# Navigation
page = st.sidebar.selectbox(
    "Select View",
    ["Upcoming Fights", "Odds Comparison", "Odds Movement", "Commercial Value", "Marketing Calendar", "Report Generator"]
)

# Export button in sidebar
st.sidebar.markdown("---")
if st.sidebar.button("📥 Export All Data (CSV)"):
    export_to_csv()

st.sidebar.markdown("---")
st.sidebar.caption("Built with Streamlit | OpenOddsAPI")

# Page routing
if page == "Upcoming Fights":
    show_upcoming_fights()
elif page == "Odds Comparison":
    show_comparison()
elif page == "Odds Movement":
    show_movement()
elif page == "Commercial Value":
    show_commercial_value()
elif page == "Marketing Calendar":
    show_marketing_timing()
elif page == "Report Generator":
    show_report_generator()