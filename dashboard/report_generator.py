import streamlit as st
import json
from datetime import datetime
import os

def load_data():
    try:
        with open("data/upcoming_fights.json", "r") as f:
            data = json.load(f)
            return data.get("events", [])
    except:
        return []

def load_saved_report(fight_id):
    """Load a saved report if it exists."""
    filename = f"data/reports/{fight_id}.md"
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return f.read()
    return None

def save_report(fight_id, content):
    """Save a report to file."""
    os.makedirs("data/reports", exist_ok=True)
    filename = f"data/reports/{fight_id}.md"
    with open(filename, "w") as f:
        f.write(content)
    return filename

def generate_report(event):
    """Generate a subscriber content draft from event data."""
    home = event.get('home_team', 'Unknown')
    away = event.get('away_team', 'Unknown')
    date = event.get('commence_time', '')
    fight_id = event.get('id', f"{home}_{away}".replace(" ", "_"))

    # Format the date
    if date:
        try:
            clean_date = date.split('T')[0]
            clean_time = date.split('T')[1].split('.')[0] if 'T' in date else ''
            date_str = f"{clean_date} at {clean_time} UTC"
        except:
            date_str = date
    else:
        date_str = "Date TBD"

    # Get odds
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
                    odds_data[fighter] = []
                odds_data[fighter].append(f"{book_name}: {price}")

    # Build the report
    report = f"""## {home} vs {away}

**Date:** {date_str}

### Market Snapshot

"""
    for fighter, books in odds_data.items():
        report += f"**{fighter}:**\n"
        for book in books:
            report += f"  - {book}\n"
        report += "\n"

    report += "### Key Context\n\n"
    report += "- [Add fighter records here]\n"
    report += "- [Add recent form here]\n"
    report += "- [Add rivalry or storyline context here]\n\n"

    report += "### Commercial Value Overlay\n\n"
    report += "- [Add commercial value stats here]\n"
    report += "- [Add social following or marketability context here]\n\n"

    report += "### What to Watch\n\n"
    report += "- [Add key tactical or strategic notes here]\n"
    report += "- [Add betting market context here]\n\n"

    report += "---\n"
    report += "*Disclaimer: Counter-Feint Intelligence provides commentary and analysis for informational and entertainment purposes only. It does not constitute financial, gambling, or betting advice. Past analysis does not guarantee future outcomes. Bet responsibly.*"

    return report, fight_id

def show_report_generator():
    st.markdown("## Export Report Generator")
    st.caption("Generate subscriber content drafts from fight data")

    events = load_data()
    if not events:
        st.warning("No data available")
        return

    # Select a fight
    fight_options = [
        f"{e.get('home_team', 'Unknown')} vs {e.get('away_team', 'Unknown')}"
        for e in events
    ]
    selected = st.selectbox("Select a fight", fight_options)

    # Find the selected event
    selected_event = None
    for e in events:
        if f"{e.get('home_team', 'Unknown')} vs {e.get('away_team', 'Unknown')}" == selected:
            selected_event = e
            break

    if not selected_event:
        st.error("Event not found")
        return

    # Show event preview
    st.markdown("### Event Preview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Home", selected_event.get('home_team', 'Unknown'))
    with col2:
        st.metric("Away", selected_event.get('away_team', 'Unknown'))
    with col3:
        st.metric("Books", len(selected_event.get('bookmakers', [])))

    # Generate or load report
    report, fight_id = generate_report(selected_event)
    
    # Check for saved version
    saved_report = load_saved_report(fight_id)
    if saved_report:
        st.info("📂 Saved report found. Edit below or generate a new one.")
        current_content = saved_report
    else:
        current_content = report

    # Editable text area
    edited_content = st.text_area(
        "Edit Report",
        current_content,
        height=400
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Report"):
            filename = save_report(fight_id, edited_content)
            st.success(f"Report saved to {filename}")
    
    with col2:
        if st.button("📋 Copy to Clipboard"):
            st.code(edited_content, language="markdown")
            st.caption("Copy this Markdown to post on Patreon or Discord")

    # Show preview
    with st.expander("Preview Report"):
        st.markdown(edited_content)

if __name__ == "__main__":
    show_report_generator()