import pandas as pd
import folium
from folium.plugins import MarkerCluster, Search, HeatMap
import openrouteservice

# Load dataset
df = pd.read_csv("stakeholders.csv")  # Ensure your file has correct headers

# Define map center (average coordinates)
map_center = [df['Latitude'].mean(), df['Longitude'].mean()]
m = folium.Map(location=map_center, zoom_start=6, control_scale=True)

# Define icon mapping for categories (Custom Icons)
icon_mapping = {
    "Contract Farming": "https://cdn-icons-png.flaticon.com/512/1995/1995617.png",
    "Seeds Company": "https://cdn-icons-png.flaticon.com/512/1673/1673122.png",
    "Aggregators": "https://cdn-icons-png.flaticon.com/512/3063/3063818.png",
    "Processors": "https://cdn-icons-png.flaticon.com/512/2912/2912106.png",
    "Fertilizer Company": "https://cdn-icons-png.flaticon.com/512/1903/1903162.png",
}

# Create Feature Groups for each category
categories = df["Category"].unique()
category_layers = {cat: folium.FeatureGroup(name=cat) for cat in categories}

# Initialize Marker Cluster
marker_cluster = MarkerCluster()

# Add markers to the map
for _, row in df.iterrows():
    icon_url = icon_mapping.get(row['Category'], 'https://cdn-icons-png.flaticon.com/512/684/684908.png')
    icon = folium.CustomIcon(icon_url, icon_size=(30, 30))

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

    marker = folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        icon=icon,
        popup=folium.Popup(popup_text, max_width=300)
    )
    
    marker_cluster.add_child(marker)
    category_layers[row['Category']].add_child(marker)

# Add Clustered Markers to the Map
m.add_child(marker_cluster)

# Add category layers to the map
for layer in category_layers.values():
    m.add_child(layer)

# Add Layer Control
folium.LayerControl(collapsed=False).add_to(m)

# Add Heatmap for density visualization
heat_data = df[['Latitude', 'Longitude']].dropna().values.tolist()
HeatMap(heat_data, radius=15, gradient={0.2: 'blue', 0.5: 'green', 0.8: 'yellow', 1: 'red'}).add_to(m)

# Add Search Functionality
search = Search(
    layer=marker_cluster,
    geom_type="Point",
    placeholder="Search for a company...",
    search_label="Company Name",
    collapsed=False
)
m.add_child(search)

# Export CSV Functionality (Manual Step: Can be integrated into Flask for UI download)
df.to_csv("filtered_stakeholders.csv", index=False)

# Save and display the map
m.save("stakeholders_map.html")
print("Map has been saved as stakeholders_map.html")

# OPTIONAL: Route Calculation (Example: Between First 2 Locations)
client = openrouteservice.Client(key='YOUR_API_KEY')  # Get API key from openrouteservice.org
if len(df) >= 2:
    coords = [(df.iloc[0]['Longitude'], df.iloc[0]['Latitude']), (df.iloc[1]['Longitude'], df.iloc[1]['Latitude'])]
    route = client.directions(coords, profile='driving-car', format='geojson')

    folium.PolyLine(
        locations=[(pt[1], pt[0]) for pt in route['routes'][0]['geometry']['coordinates']],
        color="blue",
        weight=5,
        opacity=0.7
    ).add_to(m)
