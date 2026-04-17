import time
from ultralytics import YOLO

class YOLODetection:
    def __init__(self, model_path="yolov8n.pt", base_conf=0.3, iou_threshold=0.3):
        self.model = YOLO(model_path)
        self.target_classes = [0, 2]

        self.base_conf = base_conf
        self.iou_threshold = iou_threshold

        self.prev_time = time.time()
        self.fps = 0

    def update_fps(self):
        curr_time = time.time()
        self.fps = 1 / (curr_time - self.prev_time)
        self.prev_time = curr_time
    
    def get_dynamic_conf(self):
        if self.fps < 15:
            return min(self.base_conf + 0.2, 0.7)
        elif self.fps > 25:
            return max(self.base_conf - 0.1, 0.2)
        else:
            return self.base_conf
    
    def detect(self, frame):
        self.update_fps()
        dynamic_conf = self.get_dynamic_conf()
 
        results = self.model(frame, stream=True, iou=self.iou_threshold, conf=dynamic_conf)
        detections = []

        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0]) 
                if cls in self.target_classes:
                    x1, y1,x2,y2 = map(int, box.xyxy[0])

                    if (x2 - x1) < 20 or (y2 - y1) < 20:
                        continue

                    detections.append({
                        "bbox": (x1, y1, x2, y2),
                        "class": cls,
                        "conf": conf
                    })
        return detections
        
def format_for_tracker(detections):
    formatted = []
    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        conf = det["conf"]
        cls = det["class"]

        w = x2 - x1
        h = y2 - y1

        if w <= 0 or h <= 0:
            continue
        
        formatted.append(([x1, y1, w, h], conf, cls))  

    return formatted