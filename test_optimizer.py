import unittest
import networkx as nx
from optimizer import find_max_distance_path

class TestSkiOptimizer(unittest.TestCase):
    def setUp(self):
        # Create a simple test graph
        self.G = nx.DiGraph()
        
        # Add test nodes and edges
        # Simple diamond-shaped graph with slopes and lifts
        self.G.add_edge("Start", "Mid1", distance=2, time=5, name="Blue1", grade="blue")
        self.G.add_edge("Start", "Mid2", distance=2, time=5, name="Red1", grade="red")
        self.G.add_edge("Mid1", "End", distance=2, time=5, name="Blue2", grade="blue")
        self.G.add_edge("Mid2", "End", distance=2, time=5, name="Red2", grade="red")
        self.G.add_edge("End", "Start", distance=0, time=10, name="Lift1")  # Lift back to start

    def test_early_termination(self):
        """Test if algorithm terminates early when finding good enough solution"""
        distance_goal = 4
        distance, path = find_max_distance_path(
            self.G, "Start", time_limit=100, distance_goal=distance_goal
        )
        
        self.assertGreaterEqual(distance, distance_goal)
        self.assertLess(len(path), 10)

    def test_time_limit_constraint(self):
        """Test if algorithm respects time limit"""
        # First edge is 5 minutes, so use 4 minutes as limit
        distance, path = find_max_distance_path(
            self.G, "Start", time_limit=4, distance_goal=10
        )
        self.assertEqual(distance, 0)
        self.assertEqual(len(path), 0)

    def test_consecutive_slope_limit(self):
        """Test if consecutive slope constraint is maintained"""
        G = nx.DiGraph()
        G.add_edge("A", "B", distance=1, time=5, name="Same1", grade="blue")
        G.add_edge("B", "C", distance=1, time=5, name="Same1", grade="blue")
        G.add_edge("C", "D", distance=1, time=5, name="Same1", grade="blue")
        G.add_edge("D", "E", distance=1, time=5, name="Same1", grade="blue")

        distance, path = find_max_distance_path(
            G, "A", time_limit=30, distance_goal=2
        )
        
        consecutive_count = 0
        last_slope = None
        for slope in path:
            if slope == last_slope:
                consecutive_count += 1
                self.assertLess(consecutive_count, 3)
            else:
                consecutive_count = 0
            last_slope = slope

    def test_empty_graph(self):
        """Test if empty graphs are handled correctly"""
        G = nx.DiGraph()
        distance, path = find_max_distance_path(
            G, "Start", time_limit=30, distance_goal=5
        )
        self.assertEqual(distance, 0)
        self.assertEqual(len(path), 0)

    def test_unreachable_goal(self):
        """Test behavior when distance goal is unreachable"""
        distance, path = find_max_distance_path(
            self.G, "Start", time_limit=30, distance_goal=1000
        )
        self.assertLess(distance, 1000)

    def test_lift_repetition_constraint(self):
        """Test that same lift cannot be used more than 3 times consecutively"""
        G = nx.DiGraph()
        
        # Create a circuit with multiple lifts and slopes
        G.add_edge("Base", "Top1", distance=0, time=5, name="Lift1")  # Lift
        G.add_edge("Top1", "Mid", distance=3, time=5, name="Slope1", grade="red")
        G.add_edge("Mid", "Base", distance=3, time=5, name="Slope2", grade="red")
        G.add_edge("Base", "Top2", distance=0, time=6, name="Lift2")  # Different lift
        
        # Run with enough time to potentially use lifts many times
        distance, path = find_max_distance_path(
            G, "Base", time_limit=100, distance_goal=50
        )
        
        # Check for lift repetitions
        consecutive_lift_count = 0
        last_lift = None
        
        for edge in path:
            if "Lift" in edge:  # It's a lift
                if edge == last_lift:
                    consecutive_lift_count += 1
                    self.assertLess(consecutive_lift_count, 3, 
                        f"Lift {edge} used more than 3 times consecutively")
                else:
                    consecutive_lift_count = 0
                last_lift = edge
            else:  # It's a slope - don't reset the counter
                if last_lift is not None:
                    last_lift = last_lift  # Keep tracking the same lift

    def test_slopes_dont_reset_lift_count(self):
        """Test that slopes between same lift uses count as consecutive lift usage"""
        G = nx.DiGraph()
        
        # Create a path where same lift must be used with slopes in between
        G.add_edge("Base", "Top", distance=0, time=5, name="Lift1")  # Lift
        G.add_edge("Top", "Mid", distance=2, time=3, name="Slope1", grade="red")
        G.add_edge("Mid", "Base", distance=2, time=3, name="Slope2", grade="red")
        
        # Run with enough time to use lift multiple times
        distance, path = find_max_distance_path(
            G, "Base", time_limit=50, distance_goal=20
        )
        
        # Count lift uses with slopes in between
        lift_uses = 0
        for edge in path:
            if edge == "Lift1":
                lift_uses += 1
        
        # Should not allow more than 3 uses of same lift, even with slopes between
        self.assertLessEqual(lift_uses, 3)

    def test_different_lifts_reset_counter(self):
        """Test that using a different lift resets the consecutive usage counter"""
        G = nx.DiGraph()
        
        # Create a circuit with alternating lifts
        G.add_edge("Base", "Top1", distance=0, time=5, name="Lift1")
        G.add_edge("Top1", "Mid", distance=2, time=3, name="Slope1", grade="red")
        G.add_edge("Mid", "Top2", distance=0, time=5, name="Lift2")
        G.add_edge("Top2", "Base", distance=2, time=3, name="Slope2", grade="red")
        
        distance, path = find_max_distance_path(
            G, "Base", time_limit=100, distance_goal=20
        )
        
        # Should be able to use alternating lifts more than 3 times each
        lift1_count = sum(1 for edge in path if edge == "Lift1")
        lift2_count = sum(1 for edge in path if edge == "Lift2")
        
        self.assertGreater(lift1_count + lift2_count, 6, 
            "Should be able to use different lifts more than 3 times each")

if __name__ == '__main__':
    unittest.main() 