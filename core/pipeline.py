from vision.detection import YOLODetection, format_for_tracker
from vision.tracking import ObjectTracker
from vision.depth import DepthEstimator

class VisionPipeline:
    def __init__(self):
        self.detector = YOLODetection()
        self.tracker = ObjectTracker()
        self.depth = DepthEstimator()

        self.frame_count = 0
        self.depth_map = None

        self.det_frame_count = 0
        self.last_detections = []

    def process(self, frame):
        
        self.det_frame_count += 1
        if self.det_frame_count % 2 == 0 or not self.last_detections:
            detections = self.detector.detect(frame)
            self.last_detections = detections
        else:
            detections = self.last_detections

        formatted = format_for_tracker(detections)
        tracks = self.tracker.update(frame, formatted)

        self.frame_count += 1
        if self.frame_count%5 == 0 or self.depth_map is None:
            self.depth_map = self.depth.predict(frame)
        
        return {
            "tracks": tracks,
            "depth": self.depth_map
        }