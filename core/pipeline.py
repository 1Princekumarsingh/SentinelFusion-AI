from vision.detection import YOLODetection, format_for_tracker
from vision.tracking import ObjectTracker
from vision.depth import DepthEstimator
from core.decision import DecisionEngine
from core.settings import settings

class VisionPipeline:
    def __init__(self):
        detection_settings = settings["detection"]
        tracking_settings = settings["tracking"]
        alert_settings = settings["alerts"]
        depth_settings = settings["depth"]

        self.detector = YOLODetection(
            model_path=detection_settings["model_path"],
            base_conf=detection_settings["base_confidence"],
            iou_threshold=detection_settings["iou_threshold"],
            image_size=detection_settings["image_size"],
            target_classes=detection_settings["target_classes"],
            min_box_size=detection_settings["min_box_size"],
        )
        self.tracker = ObjectTracker(
            max_age=tracking_settings["max_age"],
            n_init=tracking_settings["n_init"],
            max_cosine_distance=tracking_settings["max_cosine_distance"],
            min_hits=tracking_settings["min_hits"],
            max_time_since_update=tracking_settings["max_time_since_update"],
        )
        self.depth = DepthEstimator()
        self.decision = DecisionEngine(
            proximity_threshold=alert_settings["proximity_threshold"],
        )

        self.frame_count = 0
        self.depth_map = None
        self.depth_was_enabled = False

        self.det_frame_count = 0
        self.last_detections = []
        self.detection_interval = int(detection_settings["interval"])
        self.depth_interval = int(depth_settings["interval"])

    def process(self, frame, compute_depth=True):

        #detect objects every few frames and let tracker fill the gaps
        self.det_frame_count += 1
        if self.det_frame_count % self.detection_interval == 0 or not self.last_detections:
            detections = self.detector.detect(frame)
            self.last_detections = detections
        else:
            detections = self.last_detections

        formatted = format_for_tracker(detections)
        tracks = self.tracker.update(frame, formatted)

        #depth every 15 frames, only when depth display is enabled
        self.frame_count += 1
        if compute_depth and (
            not self.depth_was_enabled
            or self.frame_count % self.depth_interval == 0
            or self.depth_map is None
        ):
            self.depth_map = self.depth.predict(frame)
        self.depth_was_enabled = compute_depth

        #decision layer
        alerts = self.decision.analyze(tracks, self.depth_map)
        
        return {
            "tracks": tracks,
            "depth": self.depth_map if compute_depth else None,
            "alerts": alerts
        }
