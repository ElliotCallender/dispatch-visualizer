import folium
from folium import plugins
import asyncio
import pandas as pd

# Define the center coordinates for the map
center_latitude = 39.2300
center_longitude = -98.2600

# Create a map object centered at the specified coordinates+
map = folium.Map(location=[center_latitude, center_longitude], zoom_start=4)

def main(df):
    for index, row in df.iterrows():
        tooltipHTML = """
        <h1 style="text-align: center">Site """+str(row['Site'])+"""</h1>
        <p style="text-align: center">"""+str(row['Date'].date())+"""</p>
        <p>Touchscreens: """+str(row['Touchscreens'])+"""</p>
        <p>Scanner scales: """+str(row['Scanner-Scales'])+"""</p>
        <p>ELOs: """+str(row['ELOs'])+"""</p>
        <p>SSDs: """+str(row['SSDs'])+"""</p>"""

        detailedHTML = tooltipHTML + """
        <br>
        <p>Printers: """+str(row['Epsons'])+"""</p>
        <p>Cash cables: """+str(row['Cash-Cables'])+"""</p>
        <p>Hand scanners: """+str(row['Hand-Scanners'])+"""</p>
        <p>Scale calibrations: """+str(row["Scale-Calibrations"])+"""</p>
        <p>Debit readers: """+str(row['Debits'])+"""</p>"""
        folium.Marker(
            location=[row['coords']['lat'], row['coords']['lng']],
            popup=folium.Popup(
                folium.IFrame(detailedHTML, height=500).render(),
                min_width=300,
                max_width=300),
            tooltip=folium.Tooltip(tooltipHTML),
            icon=plugins.BeautifyIcon(
                icon_shape="marker",
                text_color="black",
                scale=2,
                background_color="white",
                border_color=row["difficulty_color"],
                border_width=5,
                number=row['Team']
            )
        ).add_to(map)


    # Save the map as an HTML file
    map.save("my_map.html")