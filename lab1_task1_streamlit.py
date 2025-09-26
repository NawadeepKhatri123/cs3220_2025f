import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from pyvis.network import Network
import os

# --- Page Configuration ---
st.set_page_config(page_title="War of the Five Kings", layout="wide")
st.title("Game of Thrones: War of the Five Kings")

# --- Data Loading and Caching ---
@st.cache_data
def load_data(file_path):
    """Loads and cleans the battle data from a CSV file."""
    data = pd.read_csv(file_path)
    # Keep only the columns we need and remove rows with missing values
    battles_df = data.loc[:, ['name', 'attacker_king', 'defender_king', 'attacker_size', 'defender_size']]
    return battles_df.dropna()

# --- Graph Generation Function ---
@st.cache_resource
def generate_graph(_battles_df, filename="GoT_Battles.html"):
    """Generates and saves the pyvis graph to an HTML file."""
    net5kings = Network(
        heading="War of the Five Kings",
        bgcolor="#242020",
        font_color="white",
        height="750px",
        width="100%",
        directed=True
    )

    kingColors = {
        "Joffrey/Tommen Baratheon": "red",
        "Robb Stark": "blue",
        "Stannis Baratheon": "purple",
        "Balon/Euron Greyjoy": "green",
        "Renly Baratheon": "orange",
        "Mance Rayder": "gold"
    }

    kings = set(_battles_df['attacker_king']).union(set(_battles_df['defender_king']))
    for king in kings:
        net5kings.add_node(
            king,
            label=king,
            shape="dot",
            font={"color": "white"},
            color=kingColors.get(king, "gray")
        )

    edges = _battles_df.groupby(['attacker_king', 'defender_king']).agg(
        battle_count=('name', 'count'),
        battle_names=('name', lambda x: ", ".join(x))
    ).reset_index()

    for _, row in edges.iterrows():
        net5kings.add_edge(
            row['attacker_king'],
            row['defender_king'],
            value=row['battle_count'],
            title=f"{row['battle_count']} battle(s): {row['battle_names']}"
        )
    
    enemies_map = net5kings.get_adj_list()
    for node in net5kings.nodes:
        king = node["id"]
        enemies = enemies_map.get(king, set())
        node["value"] = len(enemies) + 1

    net5kings.save_graph(filename)
    return filename

# --- Main Application ---
try:
    # Load the data
    battles_df_cleaned = load_data("data/game-of-thrones-battles.csv")
    
    # Create tabs
    tab1, tab2 = st.tabs(["Interactive Battle Graph", "Battle Data"])
    
    with tab1:
        st.header("Interactive Network of Alliances and Attacks")
        graph_html_file = generate_graph(battles_df_cleaned)
        with open(graph_html_file, 'r', encoding='utf-8') as f:
            html_source = f.read()
        components.html(html_source, height=800, scrolling=True)
        
    with tab2:
        st.header("Cleaned Battle Data")
        st.dataframe(battles_df_cleaned)

except FileNotFoundError:
    st.error("Error: `data/game-of-thrones-battles.csv` not found. Please ensure the file is in the correct directory.")