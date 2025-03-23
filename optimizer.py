from load_graph import create_les_arcs_graph
from collections import deque
import heapq

def find_max_distance_path(G, start, time_limit, distance_goal):
    if not G.nodes() or start not in G.nodes() or time_limit <= 0:
        return 0, []
    
    best_distance = 0
    best_path = []
    
    # Queue: (node, time_left, distance, path, last_lift, lift_repeat_count)
    queue = deque([(start, time_limit, 0, [], None, 0)])
    
    # Simple state tracking: (node, time_left // 5) -> distance
    visited = {}
    
    while queue:
        node, time_left, distance, path, last_lift, lift_count = queue.popleft()
        
        # Basic checks
        if time_left < 0:
            continue
            
        if distance > best_distance:
            best_distance = distance
            best_path = path.copy()
            
        # State-based pruning
        state = (node, time_left // 5)
        if state in visited and visited[state] >= distance:
            continue
        visited[state] = distance
        
        # Goal reached?
        if distance >= distance_goal:
            continue
        
        # Explore neighbors
        for next_node in G.neighbors(node):
            edge_data = G[node][next_node]
            
            # Skip if not enough time
            if edge_data["time"] > time_left:
                continue
            
            # Check lift repetition constraint
            is_lift = edge_data["distance"] == 0
            new_lift_count = 0
            
            if is_lift:
                if edge_data["name"] == last_lift:
                    if lift_count >= 3:  # Already used this lift 3 times
                        continue
                    new_lift_count = lift_count + 1
                else:
                    new_lift_count = 1  # First use of a different lift
            else:
                new_lift_count = lift_count  # Slopes don't reset the lift counter
            
            # Calculate new state
            new_time_left = time_left - edge_data["time"]
            new_distance = distance + edge_data["distance"]
            new_path = path + [edge_data["name"]]
            new_last_lift = edge_data["name"] if is_lift else last_lift
            
            # Add to queue
            queue.append((
                next_node,
                new_time_left,
                new_distance,
                new_path,
                new_last_lift,
                new_lift_count
            ))
    
    return best_distance, best_path

def print_path_breakdown(G, best_distance, best_path, start_node):
    """
    Print the path breakdown in segments of approximately 10km each.
    Only shows edge names, not nodes.
    
    Args:
        G: NetworkX graph containing the ski resort
        best_distance: Total distance of the path
        best_path: List of edge names representing the path
        start_node: Starting node of the path
    """
    print(f"Max distance: {best_distance} km")
    
    # Display path with breakdown by ~10km segments
    if best_path:
        print("\nPath breakdown:")
        
        cumulative_distance = 0
        current_segment = []
        segment_start = 0
        segment_distance = 0
        curr_node = start_node
        
        for i, edge_name in enumerate(best_path):
            # Find the edge and accumulate distance
            next_node = None
            for neighbor in G.neighbors(curr_node):
                edge_data = G[curr_node][neighbor]
                if edge_data['name'] == edge_name:
                    edge_distance = edge_data['distance']
                    segment_distance += edge_distance
                    cumulative_distance += edge_distance
                    
                    # Store the edge info
                    current_segment.append({
                        'name': edge_name,
                        'distance': edge_distance,
                        'time': edge_data['time']
                    })
                    
                    next_node = neighbor
                    break
            
            if next_node is None:
                print(f"ERROR: Invalid path segment from {curr_node} with edge {edge_name}")
                break
                
            curr_node = next_node
            
            # Print segment when we reach ~10km or at the end of the path
            if segment_distance >= 20 or i == len(best_path) - 1:
                segment_end = i
                print(f"\n--- ({segment_distance:.1f}km, cumulative: {cumulative_distance:.1f}km) ---")
                
                # Print just the edge names joined by arrows
                if current_segment:
                    path_str = " → ".join([edge['name'] for edge in current_segment])
                    print(path_str)
                
                # Reset for next segment
                segment_start = i + 1
                segment_distance = 0
                current_segment = []
    else:
        print("No path found.")

if __name__ == "__main__":
    G, node_rows = create_les_arcs_graph()
    start_node = "Vallandry"
    time_limit = 8*60  # 8 hours in minutes
    distance_goal = 100

    best_distance, best_path = find_max_distance_path(
        G, start_node, time_limit, distance_goal
    )
    
    # Print the result
    print_path_breakdown(G, best_distance, best_path, start_node)
