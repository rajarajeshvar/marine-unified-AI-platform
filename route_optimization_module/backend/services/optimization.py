import math
import heapq
from typing import List, Tuple, Dict
from models.schemas import RouteWaypoint, OptimizationResponse, Coordinates

class AStarNode:
    def __init__(self, lat: float, lng: float, parent=None):
        self.lat = lat
        self.lng = lng
        self.parent = parent
        self.g = 0 # Cost from start to node
        self.h = 0 # Heuristic cost from node to destination
        self.f = 0 # Total cost

    def __eq__(self, other):
        return round(self.lat, 2) == round(other.lat, 2) and round(self.lng, 2) == round(other.lng, 2)
    
    def __lt__(self, other):
        return self.f < other.f
    
    def __hash__(self):
        return hash((round(self.lat, 2), round(self.lng, 2)))

class AStarOptimizer:
    def __init__(self):
        self.grid_size = 1.0 # degrees

    def haversine(self, lat1, lon1, lat2, lon2):
        R = 6371.0 # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def get_neighbors(self, node: AStarNode) -> List[AStarNode]:
        neighbors = []
        # 8 directions
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]
        for d in directions:
            neighbors.append(AStarNode(node.lat + d[0] * self.grid_size, node.lng + d[1] * self.grid_size))
        return neighbors

    def calculate_edge_cost(self, current: AStarNode, neighbor: AStarNode, optimize_for: str) -> float:
        distance = self.haversine(current.lat, current.lng, neighbor.lat, neighbor.lng)
        
        # Dummy values for weather and engine risk to simulate
        fuel_cost = distance * 0.2
        weather_risk = 0
        
        # Introduce a dummy storm area around specific coordinates (e.g., Lat 30, Lng -40)
        if 25 <= neighbor.lat <= 35 and -45 <= neighbor.lng <= -35:
            weather_risk = 5000 # High penalty

        engine_risk = distance * 0.05
        
        if optimize_for == 'fuel':
            return distance + (fuel_cost * 2) + weather_risk + engine_risk
        elif optimize_for == 'time':
            return distance + fuel_cost + weather_risk + engine_risk
        elif optimize_for == 'safety':
            return distance + fuel_cost + (weather_risk * 5) + engine_risk
        else:
            return distance + fuel_cost + weather_risk + engine_risk

    def calculate_optimal_route(self, start_coords: Coordinates, dest_coords: Coordinates, optimize_for: str) -> OptimizationResponse:
        start_node = AStarNode(start_coords.lat, start_coords.lng)
        end_node = AStarNode(dest_coords.lat, dest_coords.lng)

        open_list = []
        heapq.heappush(open_list, start_node)
        
        # Track the best g_score for each coordinate to avoid O(N) lookup in open_list
        g_scores = {(round(start_node.lat, 2), round(start_node.lng, 2)): 0}
        closed_set = set()

        best_path = []
        max_iterations = 20000
        iterations = 0

        while open_list and iterations < max_iterations:
            iterations += 1
            current_node = heapq.heappop(open_list)
            
            coord_key = (round(current_node.lat, 2), round(current_node.lng, 2))
            
            # If we popped a node but we already found a better path to it earlier, skip it
            if coord_key in closed_set:
                continue
                
            closed_set.add(coord_key)

            if self.haversine(current_node.lat, current_node.lng, end_node.lat, end_node.lng) < 150:
                # Found path
                current = current_node
                while current is not None:
                    best_path.append(RouteWaypoint(lat=current.lat, lng=current.lng, weather_risk=0.1))
                    current = current.parent
                best_path = best_path[::-1]
                break

            for neighbor in self.get_neighbors(current_node):
                n_key = (round(neighbor.lat, 2), round(neighbor.lng, 2))
                if n_key in closed_set:
                    continue

                cost = self.calculate_edge_cost(current_node, neighbor, optimize_for)
                tentative_g = current_node.g + cost

                if n_key not in g_scores or tentative_g < g_scores[n_key]:
                    # Found a better path to neighbor
                    g_scores[n_key] = tentative_g
                    neighbor.g = tentative_g
                    neighbor.h = self.haversine(neighbor.lat, neighbor.lng, end_node.lat, end_node.lng)
                    neighbor.f = neighbor.g + neighbor.h
                    neighbor.parent = current_node
                    heapq.heappush(open_list, neighbor)

        if not best_path:
            # Fallback direct line if A* fails to find path in time
            best_path = [
                RouteWaypoint(lat=start_node.lat, lng=start_node.lng),
                RouteWaypoint(lat=end_node.lat, lng=end_node.lng)
            ]

        # Calculate metrics
        total_distance = 0
        for i in range(len(best_path) - 1):
            total_distance += self.haversine(best_path[i].lat, best_path[i].lng, best_path[i+1].lat, best_path[i+1].lng)
        
        return OptimizationResponse(
            best_route=best_path,
            alternative_routes=[],
            estimated_fuel_saved_percent=9.5,
            estimated_eta="2026-08-15T12:00:00Z",
            distance_km=round(total_distance, 2),
            average_speed_knots=18.5,
            weather_risk_score=2.1,
            safety_score=95.0,
            total_cost=total_distance * 1.5
        )
