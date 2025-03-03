import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load the pre-saved df_nga.csv file
@st.cache_data
def load_data():
    return pd.read_csv("merged_df_nga.csv")

merged_df_nga = load_data()

# Display the combined DataFrame in Streamlit
st.markdown("<h1 style='text-align: center;'>Super Eagles Tracker</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>Top 10 European Leagues</h2>", unsafe_allow_html=True)
st.dataframe(merged_df_nga)

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
    # Filter players with Assists > 0
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
st.pyplot(plot_goals(merged_df_nga))

st.markdown("<h2 style='text-align: center;'>Assists</h2>", unsafe_allow_html=True)
st.pyplot(plot_assists(merged_df_nga))

st.markdown("<h2 style='text-align: center;'>Goals + Assists by Matches</h2>", unsafe_allow_html=True)
st.pyplot(plot_goals_assists_matches(merged_df_nga))
