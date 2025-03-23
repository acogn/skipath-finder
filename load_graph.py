import networkx as nx

# Define average speeds (km/h) for each grade
SLOPE_SPEEDS = {
    'blue': 25,    # Easier slopes, faster average speed
    'red': 35,     # Medium difficulty
    'black': 15    # Difficult slopes, slower average speed
}

def calculate_slope_time(distance, grade):
    """
    Calculate time in minutes for a slope based on distance and grade
    Args:
        distance: float (in km)
        grade: string ('blue', 'red', or 'black')
    Returns:
        time: float (in minutes)
    """
    speed = SLOPE_SPEEDS[grade]
    # Convert speed from km/h to km/min and calculate time
    return round((distance / (speed / 60)), 1)

def create_les_arcs_graph():
    # Create a directed graph
    G = nx.DiGraph()

    # Real nodes (Les Arcs/Peisey-Vallandry locations)
    node_rows = [
        ["Comborciere Top", "Mont Blanc Top", "Bois de l'Ours Top", "Transarc Top"],
        ["Arc 1950",  "La Bulle Restaurant", "Le Derby Top", "Grizzly top" ],
        ["Comborciere Bottom","Arpette Bottom", "Transarc Middle", "Le Derby Bottom"],
        ["Arc 1600", "Arc 1800", "Vallandry"] 
    ]
    
    for row_idx, row in enumerate(node_rows):
        for node in row:
            G.add_node(node, row=row_idx)

    # Add slopes with names
    slopes = [
        
        ("Grizzly top", "Le Derby Bottom", 1.4, 'red', "Myrtilles upper part"),
        ("La Bulle Restaurant", "Arc 1950", 1.25, 'blue', "Vallee De L'Arc 1 upper part"),
        ("Arc 1950", "Comborciere Bottom", 1.25, 'blue', "Vallee De L'Arc 1 lower part"),
        ("Comborciere Top", "Mont Blanc Top", 0.3, 'blue', "Belvedere 4"),
        ("Le Derby Top", "Le Derby Bottom", 1.2, 'red', "Belette"), #rounded up because Belette is not complete
        ("Transarc Top", "La Bulle Restaurant", 2.74, 'blue', "Plan des eaux"),
        ("Le Derby Top", "Transarc Middle", 1.0, 'blue', "Traversee 3"), # Schatting
        ("Grizzly top", "Vallandry", 2.27, 'red', 'Aigle'),
        ("Le Derby Top", "Le Derby Bottom", 1.0, 'red', "Belette"),
        ("Bois de l'Ours Top", "Arc 1950", 1.5, 'black', "Bois de l'Ours"),
        ("Mont Blanc Top", "Arpette Bottom", 0.73, 'blue', "Belvedere 3"),
        ("Le Derby Bottom", "Vallandry", 1.1+1.2, 'blue', "Myrtille lower + barmont"),
        ("Mont Blanc Top", "Arc 1600", 3.7, 'blue', "Mont Blanc slope"),
        ("Mont Blanc Top", "Arc 1600", 3.6, 'red', "Arolles slope"),
        ("Bois de l'Ours Top", "Le Derby Bottom", 5, 'blue', "Arpette to Le Derby")
    ]

    # Add slopes to graph
    for start, end, distance, grade, name in slopes:
        G.add_edge(start, end, 
                  distance=distance,
                  grade=grade,
                  time=calculate_slope_time(distance, grade),
                  name=name)

    # Add lifts with names
    lifts = [
        ("Vallandry", "Grizzly top", 7, "Grizzly Lift"),
        ("Le Derby Bottom", "Le Derby Top", 6, "Derby Chairlift"),
        ("Arc 1600", "Mont Blanc Top", 5, "Mont Blanc Lift"),
        ("Arc 1800", "Transarc Middle", 6, "Transarc 1"),
        ("Transarc Middle", "Transarc Top", 9, "Transarc 2"),
        ("La Bulle Restaurant", "Transarc Top", 6, "Arcabulle Chairlift"),
        ("Comborciere Bottom", "Comborciere Top", 6,"Comborciere Chairlift"),
        ("Comborciere Bottom", "La Bulle Restaurant", 9,"Pre-Saint-Esprit lift"),
        ("Arc 1950", "Bois de l'Ours Top", 12, "Bois de l'Ours Lift"),
        ("Arpette Bottom", "Bois de l'Ours Top", 6, "Arpette Chairlift"),


    ]

    # Add lifts to graph
    for start, end, time, name in lifts:
        G.add_edge(start, end, distance=0, time=time, name=name)

    return G, node_rows 