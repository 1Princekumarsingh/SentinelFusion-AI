import time
from core.pipeline import VisionPipeline
from core.settings import settings
from utils.visualizer import Visualizer
from utils.frame_renderer import FrameRenderer

class CVPipeline:
    def __init__(self):
        self.pipeline = VisionPipeline()
        self.visualizer = Visualizer()
        self.renderer = FrameRenderer(
            display_settings=settings["display"],
            heatmap_settings=settings["heatmap"],
        )

        self.last_tracks = []
        self.last_alerts = []

        self.prev_time = None
        self.fps = 0

    def process_frame(self, frame):
        #fps
        curr_time = time.time()
        if self.prev_time is not None:
            self.fps = 1 / (curr_time - self.prev_time)
        self.prev_time = curr_time 

        # process through pipeline and update heatmap
        output = self.pipeline.process(frame, compute_depth=self.renderer.show_depth)
        self.renderer.update_heatmap(frame, output["tracks"], self.fps)

        # store latest data
        self.last_tracks = output["tracks"]
        self.last_alerts = output["alerts"]

        # rendering order
        if self.renderer.show_depth and output["depth"] is not None:
            frame = self.visualizer.overlay_depth(frame, output["depth"])
        if self.renderer.show_heatmap:
            frame = self.renderer.draw_heatmap(frame)

        frame = self.visualizer.draw_tracks(frame, output["tracks"], output["depth"])

        return frame
