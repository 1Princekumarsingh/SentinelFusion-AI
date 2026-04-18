import math

class DecisionEngine:
    def __init__(self):
        self.proximity_threshold = 50

    def compute_distance(self, p1, p2):
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    
    def get_center(self, bbox):
        x1, y1, x2, y2 = bbox
        return ((x1 + x2)//2, (y1 + y2)//2)
    
    def analyze(self, tracks, depth_map):
        centers = []

        for obj in tracks:
            bbox = obj["bbox"]
            track_id = obj["id"]
            
            cx, cy = self.get_center(bbox)

            h, w = depth_map.shape
            cx = min(max(cx, 0), w-1)
            cy = min(max(cy, 0), h-1)

            depth_val = depth_map[cy, cx]

            centers.append({
                "id": track_id,
                "center": (cx, cy),
                "depth": depth_val
            })
        return self.proximity_grid(centers)
    
    def proximity_grid(self, centers):
        alerts = []
        t = self.proximity_threshold
        cell_size = t

        grid = {}

        for obj in centers:
            x, y = obj["center"]

            cell_x = x // cell_size
            cell_y = y // cell_size

            key = (cell_x, cell_y)

            if key not in grid:
                grid[key] = []

            grid[key].append(obj)

        directions = [
            (0, 0), (1, 0), (-1, 0),
            (0, 1), (0, -1),
            (1, 1), (1, -1),
            (-1, 1), (-1, -1)
        ]

        # Check neighbors
        for (cell_x, cell_y), objs in grid.items():
            for dx, dy in directions:
                neighbor_cell = (cell_x + dx, cell_y + dy)

                if neighbor_cell not in grid:
                    continue

                for obj1 in objs:
                    for obj2 in grid[neighbor_cell]:

                        if obj1["id"] >= obj2["id"]:
                            continue

                        d = self.compute_distance(obj1["center"], obj2["center"])

                        if d < t:
                            alerts.append({
                                "type": "proximity",
                                "pair": (obj1["id"], obj2["id"]),
                                "distance": int(d)
                            })

        return alerts