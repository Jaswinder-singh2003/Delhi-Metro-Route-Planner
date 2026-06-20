from importlib.resources import path

from flask import Flask, render_template, request
from collections import deque
from metro_data import lines,station_lines,colors
import webbrowser

app = Flask(__name__)

# -------- Graph Build --------
def build_graph(lines):
    graph = {}
    for line in lines.values():
        for i in range(len(line)):
            if line[i] not in graph:
                graph[line[i]] = []

            if i > 0:
                graph[line[i]].append(line[i-1])
            if i < len(line)-1:
                graph[line[i]].append(line[i+1])
    return graph

graph = build_graph(lines)

def find_interchanges(lines):
    station_count = {}

    for line in lines.values():
        for station in line:
            station_count[station] = station_count.get(station, 0) + 1

    # jo station 2 ya zyada baar aaye = interchange
    interchanges = [s for s, count in station_count.items() if count > 1]

    return interchanges

interchange_stations = find_interchanges(lines)

# -------- BFS --------
def find_route(start, end):
    queue = deque([[start]])
    visited = set()

    while queue:
        path = queue.popleft()
        node = path[-1]

        if node == end:
            return path

        if node not in visited:
            visited.add(node)
            for neighbor in graph.get(node, []):
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)

    return None

def count_interchanges(path):

    current_line = None
    interchange_count = 0

    for station in path:

        station_line_list = station_lines[station]
        
        if current_line is None:
            current_line = station_line_list[0]

        elif current_line not in station_line_list:
            interchange_count += 1
            current_line = station_line_list[0]
    return interchange_count

# -------- Home --------
@app.route('/', methods=['GET', 'POST'])
def home():
    source_station = None
    destination_station = None
    route = None
    stops = 0
    error = None
    travel_time = 0
    interchange_count = 0
    fare = 0

    if request.method == 'POST':
        source = request.form['source']
        dest = request.form['destination']
        source_station = source
        destination_station = dest
        if source not in graph or dest not in graph:
            error = "Invalid station name"
        elif source == dest:
            error = "Source and destination cannot be same"
        else:
            path = find_route(source, dest)
            if path:
                for station in path:
                    formatted_path = []
                    current_line = station_lines[path[0]][0]
                
                for station in path:
                    station_available_lines = station_lines[station]

                    if current_line not in station_available_lines:
                        current_line = station_available_lines[0]

                        formatted_path.append({
                            "name": f"🔄 Change Here To {current_line}",
                            "color": "#facc15",
                            "is_change": True
                        })

                    formatted_path.append({
                        "name": station,
                        "color": colors.get(current_line, "#3b82f6"),
                        "is_change": False
                    })
                interchange_count = count_interchanges(path)

                route = formatted_path
                stops = len(path) - 1
                travel_time = (stops * 2) + (interchange_count * 5)  # Assuming 2 minutes per stop
                if stops <= 5:
                    fare = 11
                elif stops <= 10:
                    fare = 22
                elif stops <= 16:
                    fare = 33
                elif stops <= 22:
                    fare = 44
                else:
                    fare = 54
            else:
                error = "No route found"

    stations = sorted(graph.keys())
    return render_template('index.html', route=route, stops=stops, travel_time=travel_time,interchange_count=interchange_count,fare=fare, error=error, stations=stations,source_station=source_station,destination_station=destination_station)

# -------- Run --------
import webbrowser

if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:5000/")
    app.run(debug=False)