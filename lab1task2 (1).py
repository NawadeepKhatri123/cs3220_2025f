import streamlit as st
import streamlit.components.v1 as components
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import networkx as nx
from pyvis.network import Network
import os

# --- OOP Classes (Include them directly in the Streamlit script) ---
class Dynasty:
    def __init__(self, name):
        self._name = name
        self.characters = []
    @property
    def name(self): return self._name
    @name.setter
    def name(self, value):
        if not isinstance(value, str) or not value.strip(): raise ValueError("Name cannot be an empty string.")
        self._name = value
    def append(self, ch):
        if not isinstance(ch, str): raise TypeError("Character must be a string.")
        self.characters.append(ch)
    def __iter__(self):
        for person in self.characters: yield person
    def __contains__(self, ch): return ch in self.characters
    def __str__(self): return f"This is a House of {self.name}!"
    def getStrength(self): return len(self.characters)

class GameOfThronesGraph:
    def __init__(self, corpus):
        self.houses = {}
        for data_item in corpus:
            house_name = data_item['name']
            house_obj = Dynasty(house_name)
            for character in data_item['characters']: house_obj.append(character)
            self.houses[house_name] = house_obj
    def __iter__(self):
        for house in self.houses.values(): yield house
    def __contains__(self, h): return h in self.houses

# --- Streamlit App Configuration ---
st.set_page_config(page_title="Game of Thrones Houses", layout="wide")
st.title("Game of Thrones: House Relationships")

# --- Data Loading and Processing ---
@st.cache_data
def load_data(file_path):
    with open(file_path) as f:
        return json.load(f)

# --- Graph Generation Function ---
@st.cache_resource
def generate_and_save_graph(_got_houses, filename="GoT_Graph.html"):
    """Generates and saves the pyvis graph to an HTML file."""
    g = nx.Graph()
    for house in _got_houses:
        if house.name != "Include":
            g.add_node(house.name, size=house.getStrength(), color='grey')
            for person in house: g.add_node(person, size=10)
    
    myEdges = [(p, h.name) for h in _got_houses if h.name != "Include" for p in h]
    g.add_edges_from(myEdges)
    
    GoTNet = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", notebook=False, cdn_resources="remote")
    GoTNet.from_nx(g)
    
    colorKeys = [h.name for h in _got_houses if h.name != "Include"]
    palette = sns.color_palette("husl", len(colorKeys))
    nodeColors = dict(zip(colorKeys, ['#%02x%02x%02x' % tuple(int(c * 255) for c in cs) for cs in palette]))
    
    for node in GoTNet.nodes:
        if node["id"] in _got_houses:
            node["color"] = nodeColors.get(node["id"], 'grey')
        else:
            for house in _got_houses:
                if node["id"] in house:
                    node["color"] = nodeColors.get(house.name, 'grey')
                    break
    
    GoTNet.save_graph(filename)
    return filename

# --- Main Application Logic ---
try:
    # Updated file path
    json_data = load_data("data/game-of-thrones-characters-groups.json")
    corpusData = json_data['groups']
    GoTHouses = GameOfThronesGraph(corpusData)

    # Create the tabs
    tab1, tab2, tab3 = st.tabs(["Interactive Graph", "House Strength", "Members of Houses"])

    # --- Tab 1: Interactive Graph ---
    with tab1:
        st.header("Interactive Network of Houses and Characters")
        graph_html_file = generate_and_save_graph(GoTHouses)
        with open(graph_html_file, 'r', encoding='utf-8') as f:
            html_source = f.read()
        components.html(html_source, height=800, scrolling=True)

    # --- Tab 2: House Strength Bar Chart ---
    with tab2:
        st.header("Strength of Each Great House")
        
        visualisationData = {h.name: h.getStrength() for h in GoTHouses if h.name != "Include"}
        
        df = pd.DataFrame(list(visualisationData.items()), columns=['House', 'Strength'])
        df = df.sort_values('Strength', ascending=False)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.barplot(x='Strength', y='House', data=df, ax=ax, palette="viridis")
        
        ax.set_title('Game of Thrones House Strength', fontsize=16)
        ax.set_xlabel('Strength (Number of Members)', fontsize=12)
        ax.set_ylabel('House', fontsize=12)
        
        st.pyplot(fig)

    # --- Tab 3: Members of Houses (UPDATED) ---
    with tab3:
        st.header("Members of Each House")
        
        # Iterate through the houses and display them as requested
        for house in GoTHouses:
            if house.name != "Include":
                st.subheader(f"This is a House of {house.name}! Our members:")
                for character in house:
                    st.markdown(f"- {character}")
                st.write(f"We have {house.getStrength()} family members!!!")
                st.markdown("---")


except FileNotFoundError:
    st.error("Error: 'data/game-of-thrones-characters-groups.json' not found. Please ensure the file is in the correct directory.")