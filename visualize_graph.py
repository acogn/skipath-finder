import networkx as nx
import matplotlib.pyplot as plt
from load_graph import create_les_arcs_graph
import numpy as np

def wrap_text(text, width=10):
    """Wrap text at specified width."""
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 <= width:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return '\n'.join(lines)


def draw_curved_edge(pos, node1, node2, color, label, rad, ax):
    """Draw a curved edge between two nodes."""
    # Calculate node radius (based on node_size)
    node_radius = np.sqrt(2000) / 2  # Updated to match new node_size

    # Add linestyle parameter for lifts (gray edges)
    if color == 'gray':
        linestyle = (0, (2, 2))  # Create a proper dash pattern (2 points on, 2 points off)
    else:
        linestyle = 'solid'
    
    curve = plt.matplotlib.patches.FancyArrowPatch(
        pos[node1],
        pos[node2],
        connectionstyle=f'arc3,rad={rad}',
        color=color,
        alpha=0.7,
        linewidth=1.0,  # Increased linewidth for better visibility
        mutation_scale=8,
        shrinkA=node_radius * 1.5,
        shrinkB=node_radius * 1.5,
        linestyle=linestyle
    )
    ax.add_patch(curve)
    
    # Calculate label position
    x1, y1 = pos[node1]
    x2, y2 = pos[node2]
    
    # Position label closer to the start (1/4 of the way instead of 1/3)
    if rad != 0:
        # Calculate position 1/4 along the curve
        mid_x = x1 + (x2 - x1) * 0.25
        mid_y = y1 + (y2 - y1) * 0.25
        dx = x2 - x1
        dy = y2 - y1
        # Adjust perpendicular to the curve direction
        mid_x += rad * dy * 0.5
        mid_y -= rad * dx * 0.5
    else:
        mid_x = x1 + (x2 - x1) * 0.25
        mid_y = y1 + (y2 - y1) * 0.25
    
    # Set background color based on edge type
    if color == 'gray':
        bg_color = 'lightgray'
        text_color = 'black'
    else:
        if color == 'blue':
            bg_color = 'lightblue'
        elif color == 'red':
            bg_color = 'lightpink'
        elif color == 'black':
            bg_color = 'lightgray'
        text_color = color
    
    # Add colored background to label
    bbox_props = dict(
        facecolor=bg_color,
        edgecolor=color,
        alpha=0.8,
        pad=1,
        boxstyle='round,pad=0.5'
    )
    ax.text(mid_x, mid_y, label,
            fontsize=9,
            color=text_color,
            horizontalalignment='center',
            verticalalignment='center',
            bbox=bbox_props)

def visualize_ski_resort():
    # Get graph and node rows
    G, node_rows = create_les_arcs_graph()
    fig, ax = plt.subplots(figsize=(18, 12))
    
    # Calculate positions based on rows
    pos = {}
    total_rows = len(node_rows)
    
    # Create a mapping of node to row number for easy lookup
    node_to_row = {}
    for row_idx, row in enumerate(node_rows):
        for node in row:
            node_to_row[node] = row_idx
    
    for row_idx, row in enumerate(node_rows):
        y = 1 - (row_idx / (total_rows - 1))  # Convert row to y coordinate (top = 1, bottom = 0)
        
        # Position nodes horizontally within their row
        for col_idx, node in enumerate(row):
            x = (col_idx - (len(row) - 1)/2) / max(4, len(row))
            x = x * 1.5  # Spread out horizontally
            pos[node] = (x, y)
    
    # Draw nodes with larger size
    nx.draw_networkx_nodes(G, pos,
                          node_color='lightblue',
                          node_size=2000,
                          alpha=0.7,
                          ax=ax)
    
    # Group edges by their endpoints
    edge_groups = {}
    for u, v, data in G.edges(data=True):
        key = frozenset([u, v])
        if key not in edge_groups:
            edge_groups[key] = {'up': [], 'down': []}
        
        # Determine direction based on row numbers
        u_row = [idx for idx, row in enumerate(node_rows) if u in row][0]
        v_row = [idx for idx, row in enumerate(node_rows) if v in row][0]
        
        if data['distance'] == 0:  # Lift
            edge_groups[key]['up'].append((u, v, data))
        else:  # Slope
            if v_row > u_row:  # Going down (remember: higher row number = lower altitude)
                edge_groups[key]['down'].append((u, v, data))
            else:
                edge_groups[key]['up'].append((u, v, data))
    
    # Draw edges with curves based on direction
    for key, directions in edge_groups.items():
        # Get the two nodes
        node1, node2 = list(key)
        # Get their row numbers (lower row number = higher altitude)
        row1 = node_to_row[node1]
        row2 = node_to_row[node2]
        # Determine which node is higher (lower row number = higher altitude)
        higher_node = node1 if row1 < row2 else node2
        lower_node = node2 if row1 < row2 else node1
        
        # Draw upward edges (going from lower to higher altitude)
        for i, (u, v, data) in enumerate(directions['up']):
            # Base curvature depends on whether edge starts from the left or right node
            x1, _ = pos[u]
            x2, _ = pos[v]
            is_going_right = x1 < x2
            
            # If going right, curve right (positive); if going left, curve left (negative)
            base_rad = 0.4 if is_going_right else -0.4
            # Add additional curve for parallel edges
            rad = base_rad + (0.2 * i if len(directions['up']) > 1 else 0)
            
            color = 'gray' if data['distance'] == 0 else {
                'blue': 'blue',
                'red': 'red',
                'black': 'black'
            }[data['grade']]
            
            label = (f"{wrap_text(data['name'])}\n{data['time']}m" if data['distance'] == 0 
                    else f"{wrap_text(data['name'])}\n{data['distance']}km\n{data['time']}m")
            
            draw_curved_edge(pos, u, v, color, label, rad, ax)
        
        # Draw downward edges (going from higher to lower altitude)
        for i, (u, v, data) in enumerate(directions['down']):
            # Base curvature depends on whether edge starts from the left or right node
            x1, _ = pos[u]
            x2, _ = pos[v]
            is_going_right = x1 < x2
            
            # Opposite curve direction from upward edges
            base_rad = -0.4 if is_going_right else 0.4
            # Add additional curve for parallel edges
            rad = base_rad - (0.2 * i if len(directions['down']) > 1 else 0)
            
            color = {
                'blue': 'blue',
                'red': 'red',
                'black': 'black'
            }[data['grade']]
            
            label = f"{wrap_text(data['name'])}\n{data['distance']}km\n{data['time']}m"
            draw_curved_edge(pos, u, v, color, label, rad, ax)
    
    # Draw node labels with larger font
    node_labels = {node: wrap_text(node, width=15) for node in G.nodes()}
    nx.draw_networkx_labels(G, pos,
                          labels=node_labels,
                          font_size=10,
                          font_weight='bold',
                          bbox=dict(facecolor='white',
                                  edgecolor='none',
                                  alpha=0.7,
                                  pad=3),
                          ax=ax)
    
    # Add altitude scale
    alt_ticks = list(range(1000, 3500, 500))
    ax2 = ax.twinx()
    ax2.set_ylim(ax.get_ylim())
    ax2.set_yticks([(alt - min(alt_ticks)) / (max(alt_ticks) - min(alt_ticks)) for alt in alt_ticks])
    ax2.set_yticklabels([f"{alt}m" for alt in alt_ticks])
    
    # Add legend with larger font
    legend_elements = [
        plt.Line2D([0], [0], color='gray', label='Lifts', linewidth=2.5, linestyle='--'),
        plt.Line2D([0], [0], color='blue', label='Blue Slopes', linewidth=2.5),
        plt.Line2D([0], [0], color='red', label='Red Slopes', linewidth=2.5),
        plt.Line2D([0], [0], color='black', label='Black Slopes', linewidth=2.5),
    ]
    ax.legend(handles=legend_elements,
             loc='lower right',
             bbox_to_anchor=(0.98, 0.02),
             fontsize=10,
             frameon=True,
             framealpha=0.8,
             facecolor='white',
             edgecolor='none')
    
    plt.title("Les Arcs Ski Resort Graph", pad=20, size=16)
    ax.margins(0.1)
    plt.axis('off')
    plt.tight_layout()
    
    plt.savefig('les_arcs_graph.png',
                bbox_inches='tight',
                dpi=300,
                facecolor='white',
                edgecolor='none',
                pad_inches=0.2)
    plt.show()

if __name__ == "__main__":
    visualize_ski_resort()