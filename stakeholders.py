import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap, Search
import json

# Load dataset
df = pd.read_csv("stakeholders.csv")

# Fill NaN values with empty strings to avoid errors
df = df.fillna("")

# Ensure Latitude and Longitude are numeric
df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

# Drop rows with missing coordinates
df = df.dropna(subset=["Latitude", "Longitude"])

# Define map center
map_center = [df["Latitude"].mean(), df["Longitude"].mean()]
m = folium.Map(location=map_center, zoom_start=6)

# Define icon mapping for different categories
icon_mapping = {
    "Contract Farming": "img/contract.png",
    "Seeds Company": "img/seeds.png",
    "Aggregator": "img/aggreg.png",
    "Processors": "img/proces.png",
    "Fertilizer Company": "img/fert.png",
}

# Create marker cluster
marker_cluster = MarkerCluster().add_to(m)

# Dictionary to store markers for search functionality
marker_dict = {}

# Add markers for each stakeholder
for _, row in df.iterrows():
    icon_url = icon_mapping.get(row["Category"], "https://cdn-icons-png.flaticon.com/512/684/684908.png")

    # Create the popup content
    popup_text = f"""
    <b>Company:</b> {row['Company Name']}<br>
    <b>Category:</b> {row['Category']}<br>
    <b>Commodity:</b> {row['Commodity']}<br>
    <b>Office Address:</b> {row['Office Address']}<br>
    <b>Contact Person:</b> {row['Contact Person']}<br>
    <b>Phone:</b> {row['Phone number']}<br>
    <b>Designation:</b> {row['Designation']}<br>
    <b>Email/Website:</b> {row['Email/Website']}
    """

    # Add marker to map
    marker = folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        icon=folium.CustomIcon(icon_url, icon_size=(30, 30)),
        popup=folium.Popup(popup_text, max_width=300),
        tooltip=row["Company Name"]  # Tooltip for hover effect
    )
    marker_cluster.add_child(marker)

    # Store marker for search
    marker_dict[row["Company Name"]] = marker

# Add search functionality using company names
search = Search(
    layer=marker_cluster,
    search_label="Company Name",
    search_zoom=12,
    placeholder="Search for a company...",
    collapsed=False
).add_to(m)

# Add heatmap layer to show density
heat_data = df[["Latitude", "Longitude"]].values.tolist()
HeatMap(heat_data, radius=10).add_to(m)

# Add Kaduna State boundary
with open("kaduna.geojson") as f:
    geojson_data = json.load(f)
folium.GeoJson(geojson_data, name="Kaduna State Boundary").add_to(m)

# Add LGA boundaries
with open("kd_LGA.geojson") as f:
    lga_geojson_data = json.load(f)
folium.GeoJson(lga_geojson_data, name="LGA Boundaries").add_to(m)

# Add layer control
folium.LayerControl().add_to(m)

# Save the map to an HTML file
m.save("stakeholders_map.html")
print("Map saved successfully! Open 'stakeholders_map.html' in your browser.")
