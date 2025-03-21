from load_graph import create_les_arcs_graph
from collections import deque
import multiprocessing as mp
from itertools import product

def max_distance_with_time_constraint(G, start, time_limit, distance_goal, max_visits_per_node=10):
    # DP table: (node, time_left, last_slope_count) -> (max_distance, path)
    dp = {}
    # Queue now includes last_slope and consecutive_count
    # Format: (node, visited, time_left, distance, edge_names, path, last_slope, consecutive_count)
    queue = deque([(start, frozenset([start]), time_limit, 0, [], [start], None, 0)])
    
    best_distance = 0
    best_edge_names = []
    
    # Precompute neighbor data for faster access
    neighbor_data = {}
    for node in G.nodes():
        neighbor_data[node] = [(next_node, G[node][next_node]) 
                             for next_node in G.neighbors(node)]

    while queue:
        node, visited, time_left, distance, edge_names, path, last_slope, consecutive_count = queue.popleft()
        
        # State now includes the consecutive slope count
        state = (node, time_left, last_slope, consecutive_count)
        if state in dp and dp[state][0] >= distance:
            continue
        dp[state] = (distance, edge_names[:])
        
        if distance >= distance_goal and time_left >= 0:
            if distance > best_distance:
                best_distance = distance
                best_edge_names = edge_names
            continue
        
        if time_left < 0:
            continue
            
        # Explore neighbors using precomputed data
        for next_node, edge_data in neighbor_data[node]:
            visits = path.count(next_node)
            if visits >= max_visits_per_node:
                continue
                
            edge_time = edge_data["time"]
            edge_distance = edge_data["distance"]
            edge_name = edge_data["name"]
            current_slope = edge_data["name"]  # Using the slope name to track consecutive uses
            
            # Check consecutive slope usage
            new_consecutive_count = consecutive_count + 1 if current_slope == last_slope else 1
            if new_consecutive_count > 3:  # Skip if would exceed 3 consecutive uses
                continue
            
            new_time_left = time_left - edge_time
            if new_time_left < 0:
                continue
                
            new_distance = distance + edge_distance
            new_edge_names = edge_names + [edge_name]
            new_path = path + [next_node]
            new_visited = frozenset(new_path)
            
            # Add state to queue with slope tracking
            queue.append((
                next_node, 
                new_visited, 
                new_time_left, 
                new_distance, 
                new_edge_names, 
                new_path,
                current_slope,  # Track current slope for next iteration
                new_consecutive_count
            ))
    
    return best_distance, best_edge_names


if __name__ == "__main__":
    G, node_rows = create_les_arcs_graph()
    start_node = "Vallandry"
    end_node = "Vallandry"
    time_limit = 8*60  # 8 hours in minutes
    distance_goal = 100
    max_visits_per_node = 20

    best_distance, best_edge_names = max_distance_with_time_constraint(G, start_node, time_limit, distance_goal, max_visits_per_node)
    print(f"Max distance: {best_distance} km")
    print(f"Path: {' -> '.join(best_edge_names)}")
