import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
import matplotlib.pyplot as plt

# Dictionary to store league names and URLs
leagues = {
    "Belgian Pro League": "https://fbref.com/en/comps/37/stats/Belgian-Pro-League-Stats",
    "Bundesliga": "https://fbref.com/en/comps/20/stats/Bundesliga-Stats",
    "Premier League": "https://fbref.com/en/comps/9/stats/Premier-League-Stats",
    "La Liga": "https://fbref.com/en/comps/12/stats/La-Liga-Stats",
    "Serie A": "https://fbref.com/en/comps/11/stats/Serie-A-Stats",
    "Ligue 1": "https://fbref.com/en/comps/13/stats/Ligue-1-Stats",
    "Eredivisie": "https://fbref.com/en/comps/23/stats/Eredivisie-Stats",
    "Portuguese Primeira Liga": "https://fbref.com/en/comps/32/stats/Primeira-Liga-Stats",
    "Turkish Super Lig": "https://fbref.com/en/comps/26/stats/Super-Lig-Stats"
}

@st.cache_data
def load_data(url):
    driver_path = "/Users/november/.wdm/drivers/chromedriver/mac64/129.0.6668.100/chromedriver-mac-arm64/chromedriver"
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service)
    try:
        driver.get(url)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    finally:
        driver.quit()

    # Parse the table
    table = soup.find("table", {"id": "stats_standard"})
    df = pd.read_html(str(table))[0]
    return df

def clean_data(df, league):
    # Define expected column names for consistency
    expected_columns = [
        "Rank", "Player", "Nation", "Position", "Squad", "Age", "Born",
        "Matches_Played", "Starts", "Minutes", "Ninety_Minutes_Played",
        "Goals", "Assists", "Goals_Assists", "Non_Penalty_Goals", "Penalties_Made", 
        "Penalties_Attempted", "Yellow_Cards", "Red_Cards", "xG", "Non_Penalty_xG", 
        "xAG", "npxG_xAG", "Progressive_Carries", "Progressive_Passes", 
        "Progressive_Passes_Received", "Goals_Per_90", "Assists_Per_90", 
        "Goals_Assists_Per_90", "Non_Penalty_Goals_Per_90", "Goals_Assists_Penalty_Per_90", 
        "xG_Per_90", "xAG_Per_90", "xG_xAG_Per_90", "Non_Penalty_xG_Per_90", 
        "npxG_xAG_Per_90", "Matches"
    ]
    
    # Adjust columns to match the expected structure
    if len(df.columns) < len(expected_columns):
        # Add missing columns with NaN values
        for col in expected_columns[len(df.columns):]:
            df[col] = pd.NA
    elif len(df.columns) > len(expected_columns):
        # Trim extra columns if there are too many
        df = df.iloc[:, :len(expected_columns)]
    
    # Now rename columns
    df.columns = expected_columns
    
    # Filter out rows where Rank is 'Rk'
    df = df[df['Rank'] != 'Rk']
    df.reset_index(drop=True, inplace=True)

    # Convert numeric columns
    for col in ["Matches_Played", "Goals_Assists", "Goals", "Assists"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Add league column
    df["League"] = league

    return df



# Load and clean data for all leagues
combined_df = pd.DataFrame()
for league, url in leagues.items():
    
    # Load and clean each league's data with error handling
    try:
        df = load_data(url)
        df_cleaned = clean_data(df, league)
        combined_df = pd.concat([combined_df, df_cleaned], ignore_index=True)
    except Exception as e:
        st.write(f"Failed to load data for {league}: {e}")

# Filter for Nigerian players only for visualizations
df_nga = combined_df[combined_df['Nation'] == 'ng NGA'].drop(columns=['Rank'])

# Reset the index to start from 1
df_nga = df_nga.reset_index(drop=True)
df_nga.index = df_nga.index + 1

# Display the combined DataFrame in Streamlit
st.markdown("<h1 style='text-align: center;'>Super Eagles Tracker</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>Top 10 European Leagues</h2>", unsafe_allow_html=True)

st.dataframe(df_nga)



def plot_goals(df):

    # Filter players with Goals > 0
    df_filtered = df[df["Goals"] > 0]

    # Sort and extract data
    df_sorted = df_filtered.sort_values(by="Goals", ascending=False)
    players = df_sorted["Player"]
    goals = df_sorted["Goals"]

    # Create plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(players, goals, color='cornflowerblue')
    ax.set_xlabel("Goals")
    ax.set_ylabel("Player")
    ax.set_title("Goals by Player")
    plt.tight_layout()
    return fig

def plot_assists(df):
    
    # Filter players with Goals > 0
    df_filtered = df[df["Assists"] > 0]

    # Sort and extract data
    df_sorted = df_filtered.sort_values(by="Assists", ascending=False)
    players = df_sorted["Player"]
    assists = df_sorted["Assists"]

    # Create plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(players, assists, color='lightgreen')
    ax.set_xlabel("Assists")
    ax.set_ylabel("Player")
    ax.set_title("Assists by Player")
    plt.tight_layout()
    return fig

def plot_goals_assists_matches(df):
    # Filter players with Goals + Assists > 0
    df_filtered = df[df["Goals_Assists"] > 0]

    # Sort data
    df_sorted = df_filtered.sort_values(by="Matches_Played", ascending=False)
    players = df_sorted["Player"]
    goals_assists = df_sorted["Goals_Assists"]
    matches_played = df_sorted["Matches_Played"]

    # Create plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(players, matches_played, color='lightgrey', label="Matches Played")
    ax.barh(players, goals_assists, color='salmon', label="Goals + Assists")

    # Adjust x-axis limit
    max_value = max(matches_played.max(), goals_assists.max()) * 1.1
    ax.set_xlim(0, max_value)

    # Labels and legend
    ax.set_xlabel("Total")
    ax.set_ylabel("Player")
    ax.set_title("(Only Players with > 0 Goals + Assists)")
    ax.legend(loc="upper right")
    plt.tight_layout()
    return fig


# Main app - Display plots for Nigerian players in the combined data
st.markdown("<h2 style='text-align: center;'>Goals</h2>", unsafe_allow_html=True)
st.pyplot(plot_goals(df_nga))

st.markdown("<h2 style='text-align: center;'>Assists</h2>", unsafe_allow_html=True)
st.pyplot(plot_assists(df_nga))

st.markdown("<h2 style='text-align: center;'>Goals + Assists by Matches</h2>", unsafe_allow_html=True)
st.pyplot(plot_goals_assists_matches(df_nga))
