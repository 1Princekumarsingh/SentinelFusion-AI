import cv2

def get_color(track_id):
    track_id = int(track_id)
    return (
        int((track_id * 37) % 200 + 55),
        int((track_id * 17) % 200 + 55),
        int((track_id * 29) % 200 + 55)
    )

def get_depth(depth_map, bbox):
    x1, y1, x2, y2 = bbox
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2

    h, w = depth_map.shape
    cx = min(max(cx, 0), w - 1)
    cy = min(max(cy, 0), h - 1)

    return depth_map[cy, cx]

class Visualizer:
    def __init__(self):
        self.prev_boxes = {}
        self.prev_centers = {}
        self.track_history = {}

    def draw_tracks(self, frame, tracks, depth_map):
        alpha = 0.6
        active_ids = []

        for obj in tracks:
            x1, y1, x2, y2 = obj["bbox"]
            track_id = obj["id"]

            active_ids.append(track_id)
            color = get_color(track_id)

            # smooth bounding box
            if track_id in self.prev_boxes:
                px1, py1, px2, py2 = self.prev_boxes[track_id]

                x1 = int(alpha * px1 + (1 - alpha) * x1)
                y1 = int(alpha * py1 + (1 - alpha) * y1)
                x2 = int(alpha * px2 + (1 - alpha) * x2)
                y2 = int(alpha * py2 + (1 - alpha) * y2)

            self.prev_boxes[track_id] = (x1, y1, x2, y2)

            # compute center
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            # smooth center
            if track_id in self.prev_centers:
                pcx, pcy = self.prev_centers[track_id]
                cx = int(alpha * pcx + (1 - alpha) * cx)
                cy = int(alpha * pcy + (1 - alpha) * cy)

                # draw direction arrow
                dx = abs(cx - pcx)
                dy = abs(cy - pcy)

                if dx > 2 or dy > 2:
                    cv2.arrowedLine(frame, (pcx, pcy), (cx, cy), color, 2, tipLength=0.3)

            self.prev_centers[track_id] = (cx, cy)

            # track history
            if track_id not in self.track_history:
                self.track_history[track_id] = []

            self.track_history[track_id].append((cx, cy))

            # limit trail length
            if len(self.track_history[track_id]) > 15:
                self.track_history[track_id].pop(0)

            # draw trail 
            points = self.track_history[track_id]

            for i in range(1, len(points)):
                thickness = max(1, int(6 * (i / len(points))))
                cv2.line(frame, points[i - 1], points[i], color, thickness)

            # depth
            if depth_map is not None:
                depth_value = get_depth(depth_map, (x1, y1, x2, y2))
            else:
                depth_value = 0

            # draw bounding box + info
            label = f"ID {track_id} D:{int(depth_value)}" #normalize depth
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # cleanup
        self.prev_boxes = {k: v for k, v in self.prev_boxes.items() if k in active_ids}
        self.prev_centers = {k: v for k, v in self.prev_centers.items() if k in active_ids}
        self.track_history = {k: v for k, v in self.track_history.items() if k in active_ids}

        return frame

    def draw_alerts(self, frame, alerts):
        y_offset = 80

        for alert in alerts:
            if alert["type"] == "proximity":
                text = f"ALERT: IDs {alert['pair'][0]} & {alert['pair'][1]} TOO CLOSE!"

                cv2.putText(frame, text,
                            (20, y_offset),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0, 0, 255),
                            2)

                y_offset += 30
        return frame