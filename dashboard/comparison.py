import streamlit as st
import json
import pandas as pd

def load_data():
    try:
        with open("data/upcoming_fights.json", "r") as f:
            data = json.load(f)
            return data.get("events", [])
    except:
        return []

def show_comparison():
    st.markdown("## Odds Comparison")
    st.caption("Compare odds across multiple bookmakers")
    
    events = load_data()
    if not events:
        st.warning("No data available. Run the fetcher first.")
        return
    
    for event in events:
        st.markdown(f"### {event.get('home_team', 'Unknown')} vs {event.get('away_team', 'Unknown')}")
        
        # Collect odds from all books
        odds_data = {}
        for book in event.get('bookmakers', []):
            book_name = book.get('title', 'Unknown')
            markets = book.get('markets', [])
            if markets:
                outcomes = markets[0].get('outcomes', [])
                for outcome in outcomes:
                    fighter = outcome.get('name', 'Unknown')
                    price = outcome.get('price', 0)
                    if fighter not in odds_data:
                        odds_data[fighter] = {}
                    odds_data[fighter][book_name] = price
        
        # Display as table
        if odds_data:
            df_data = []
            for fighter, books in odds_data.items():
                row = {"Fighter": fighter}
                for book, price in books.items():
                    row[book] = price
                df_data.append(row)
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.caption("No odds data available")
        
        st.divider()

if __name__ == "__main__":
    show_comparison()
    