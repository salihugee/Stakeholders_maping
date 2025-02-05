import folium
import pandas as pd
import geopandas as gpd
from folium.plugins import MousePosition

# Load Stakeholders Data
df = pd.read_csv("stakeholders.csv")

# Initialize the map centered in Nigeria
m = folium.Map(location=[10.5, 7.5], zoom_start=6, tiles="cartodb positron")

# Load GeoJSON for States and LGAs
try:
    states_gdf = gpd.read_file("kaduna.geojson")
    lgas_gdf = gpd.read_file("lga_boundaries.geojson")

    # Convert any Timestamp columns to string to avoid JSON errors
    for col in lgas_gdf.columns:
        if lgas_gdf[col].dtype == "datetime64[ns]":
            lgas_gdf[col] = lgas_gdf[col].astype(str)

    # Add State Boundaries
    folium.GeoJson(
        states_gdf,
        name="State Boundaries",
        style_function=lambda x: {
            "fillColor": "transparent",
            "color": "blue",
            "weight": 2,
        },
    ).add_to(m)

    # Add LGA Boundaries
    folium.GeoJson(
        lgas_gdf,
        name="LGA Boundaries",
        style_function=lambda x: {
            "fillColor": "transparent",
            "color": "green",
            "weight": 1,
        },
    ).add_to(m)

except Exception as e:
    print(f"Error loading boundaries: {e}")

# Feature Group for Stakeholder Locations
stakeholder_layer = folium.FeatureGroup(name="Stakeholders").add_to(m)

# Add Markers for Companies
company_locations = {}  # Store locations for JavaScript zoom function

for _, row in df.iterrows():
    if pd.notnull(row["Latitude"]) and pd.notnull(row["Longitude"]):
        popup_content = f"""
        <b>{row['Company Name']}</b><br>
        <b>Category:</b> {row['Category']}<br>
        <b>Commodity:</b> {row['Commodity']}<br>
        <b>Address:</b> {row['Office Address']}<br>
        <b>Contact:</b> {row['Contact Person']} ({row['Designation']})<br>
        <b>Phone:</b> {row['Phone number']}<br>
        <b>Email:</b> {row['Email/Website']}<br>
        """

        location = [row["Latitude"], row["Longitude"]]
        company_locations[row["Company Name"]] = location  # Store for search dropdown

        folium.Marker(
            location=location,
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=row["Company Name"],
            icon=folium.Icon(color="blue", icon="info-sign"),
        ).add_to(stakeholder_layer)

# JavaScript for Dropdown Search and Zoom
search_script = f"""
<script>
    function zoomToLocation() {{
        var companyLocations = {company_locations};  // Load Python dictionary into JS
        var selectedCompany = document.getElementById('companyDropdown').value;
        
        if (selectedCompany in companyLocations) {{
            var coords = companyLocations[selectedCompany];
            map.setView(coords, 12);  // Zoom to selected company
        }}
    }}
</script>
"""

# Create Dropdown for Company Search
search_dropdown_html = """
<div style="position: fixed; top: 10px; left: 10px; z-index: 1000; background: white; padding: 10px; border-radius: 5px; box-shadow: 2px 2px 5px grey;">
    <label for="companyDropdown"><b>Search Company:</b></label>
    <select id="companyDropdown" onchange="zoomToLocation()">
        <option value="">-- Select Company --</option>
"""

for company in company_locations.keys():
    search_dropdown_html += f'<option value="{company}">{company}</option>'

search_dropdown_html += """
    </select>
</div>
"""

# Add JavaScript and Search Dropdown to the Map
m.get_root().html.add_child(folium.Element(search_script))
m.get_root().html.add_child(folium.Element(search_dropdown_html))

# Add Mouse Position Coordinates
MousePosition(position="topright", separator=" | ", empty_string="No coordinates").add_to(m)

# Add Layer Control
folium.LayerControl().add_to(m)

# Save the Map
m.save("stakeholders_map.html")
print("✅ Map has been generated successfully! Open 'stakeholders_map.html' to view it.")
