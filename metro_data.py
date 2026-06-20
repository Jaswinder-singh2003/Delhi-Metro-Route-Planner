# Delhi Metro Complete Lines (major lines)
import json
with open("lines.json", "r", encoding="utf-8") as file:
    metro_data = json.load(file)

lines = metro_data["lines"]
colors = metro_data["colors"]

station_lines = {}

for line_name, stations in lines.items():

    for station in stations:

        if station not in station_lines:
            station_lines[station] = []

        station_lines[station].append(line_name)
