import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap
import json

# Load dataset
df = pd.read_csv("stakeholders.csv").fillna("")

# Convert Latitude & Longitude to numeric
df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

# Drop rows with missing coordinates
df = df.dropna(subset=["Latitude", "Longitude"])

# Center map on dataset average location
map_center = [df["Latitude"].mean(), df["Longitude"].mean()]
m = folium.Map(location=map_center, zoom_start=6)

# Category Icons
icon_mapping = {
    "Contract Farming": "img/contract.png",
    "Seeds Company": "img/seeds.png",
    "Aggregator": "img/aggreg.png",
    "Processors": "img/proces.png",
    "Fertilizer Company": "img/fert.png",
}

# Marker Cluster
marker_cluster = MarkerCluster().add_to(m)

# Store marker details for JavaScript
marker_data = []

# Add markers
for _, row in df.iterrows():
    icon_url = icon_mapping.get(row["Category"], "https://cdn-icons-png.flaticon.com/512/684/684908.png")

    popup_content = f"""
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
        location=[row["Latitude"], row["Longitude"]],
        icon=folium.CustomIcon(icon_url, icon_size=(30, 30)),
        popup=folium.Popup(popup_content, max_width=300),
        tooltip=row["Company Name"]
    )
    marker_cluster.add_child(marker)

    # Store marker details
    marker_data.append({
        "name": row["Company Name"],
        "lat": row["Latitude"],
        "lng": row["Longitude"],
        "popup": popup_content
    })

# Add Heatmap
heat_data = df[["Latitude", "Longitude"]].values.tolist()
HeatMap(heat_data, radius=10).add_to(m)

# Load and add Kaduna State boundary
with open("kaduna.geojson") as f:
    folium.GeoJson(json.load(f), name="Kaduna State Boundary").add_to(m)

# Load and add LGA boundaries
with open("lga_boundaries.geojson") as f:
    folium.GeoJson(json.load(f), name="LGA Boundaries").add_to(m)

# Layer Control
folium.LayerControl().add_to(m)

# Convert marker data to JSON for JavaScript
marker_json = json.dumps(marker_data)

# JavaScript for Search & Zoom
search_html = f"""
<input type="text" id="search-box" placeholder="Search for a company..." 
       style="position: fixed; top: 10px; left: 10px; z-index: 1000; width: 300px; padding: 5px;">

<ul id="suggestions" 
    style="position: fixed; top: 40px; left: 10px; z-index: 1000; width: 300px; background: white; 
           list-style-type: none; padding: 0; margin: 0; border: 1px solid #ccc;"></ul>

<script>
    var markerData = {marker_json};  
    var searchBox = document.getElementById('search-box');
    var suggestions = document.getElementById('suggestions');
    
    // Ensure we have access to the Leaflet map
    var mapInstance = null;
    function initializeMap() {{
        mapInstance = window.L.map(document.getElementsByClassName('folium-map')[0]);
    }}
    
    document.addEventListener("DOMContentLoaded", initializeMap);

    searchBox.addEventListener('input', function() {{
        var input = searchBox.value.toLowerCase();
        suggestions.innerHTML = '';

        if (input.length > 0) {{
            var filtered = markerData.filter(m => m.name.toLowerCase().includes(input));
            filtered.forEach(company => {{
                var li = document.createElement('li');
                li.textContent = company.name;
                li.style.padding = '5px';
                li.style.cursor = 'pointer';
                
                li.addEventListener('click', function() {{
                    searchBox.value = company.name;
                    suggestions.innerHTML = '';

                    if (mapInstance) {{
                        mapInstance.flyTo([company.lat, company.lng], 13);  

                        L.popup()
                            .setLatLng([company.lat, company.lng])
                            .setContent(company.popup)
                            .openOn(mapInstance);
                    }} else {{
                        console.error("Map instance not initialized!");
                    }}
                }});

                suggestions.appendChild(li);
            }});
        }}
    }});
</script>
"""

m.get_root().html.add_child(folium.Element(search_html))

# Save map
m.save("stakeholders_map.html")
print("Map saved successfully! Open 'stakeholders_map.html' in your browser.")

# Create a dictionary mapping company names to their coordinates
company_coordinates = df.set_index('Company Name')[['Latitude', 'Longitude']].T.to_dict('list')

# Convert the dictionary to a JavaScript object
company_coordinates_js = str(company_coordinates).replace("'", '"')

# Add the search functionality
search_html = f"""
<script>
    document.addEventListener('DOMContentLoaded', function() {{
        var searchInput = document.getElementById('search-input');
        var searchButton = document.getElementById('search-button');
        var map = L.map('map').setView([51.505, -0.09], 13);

        // Add a tile layer
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            maxZoom: 18
        }}).addTo(map);

        // Add a marker
        var marker = L.marker([51.5, -0.09]).addTo(map)
            .bindPopup('<b>Hello world!</b><br />I am a popup.').openPopup();

        // Add a circle
        var circle = L.circle([51.508, -0.11], {{
            color: 'red',
            fillColor: '#f03',
            fillOpacity: 0.5,
            radius: 500
        }}).addTo(map).bindPopup('I am a circle.');

        // Add a polygon
        var polygon = L.polygon([
            [51.509, -0.08],
            [51.503, -0.06],
            [51.51, -0.047]
        ]).addTo(map).bindPopup('I am a polygon.');

        // Company coordinates
        var companyCoordinates = {company_coordinates_js};

        searchButton.addEventListener('click', function() {{
            var companyName = searchInput.value;
            console.log('Searching for company:', companyName); // Debugging log

            var coordinates = companyCoordinates[companyName];
            if (coordinates) {{
                console.log('Company coordinates:', coordinates); // Debugging log
                map.setView(coordinates, 15); // Zoom to the company's location
            }} else {{
                console.log('Company not found'); // Debugging log
            }}
        }});
    }});
</script>
"""

m.get_root().html.add_child(folium.Element(search_html))

# Save the map to an HTML file
m.save("stakeholders_map.html")
print("Map saved successfully! Open 'stakeholders_map.html' in your browser.")
