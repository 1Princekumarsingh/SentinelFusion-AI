import cv2
import numpy as np

class FrameRenderer:
    def __init__(self, display_settings=None, heatmap_settings=None):
        display_settings = display_settings or {}
        heatmap_settings = heatmap_settings or {}

        self.heatmap = None
        self.show_heatmap = bool(display_settings.get("show_heatmap", True))
        self.show_depth = bool(display_settings.get("show_depth", True))
        self.heatmap_radius = int(heatmap_settings.get("radius", 20))
        self.heatmap_opacity = float(heatmap_settings.get("opacity", 0.3))
        self.slow_decay = float(heatmap_settings.get("slow_decay", 0.98))
        self.fast_decay = float(heatmap_settings.get("fast_decay", 0.995))
    
    def update_heatmap(self, frame, tracks, fps=30):
        h, w, _ = frame.shape

        if self.heatmap is None:
            self.heatmap = np.zeros((h,w), dtype=np.float32)

        #decay
        decay = self.slow_decay if fps < 10 else self.fast_decay
        self.heatmap *= decay

        for obj in tracks:
            x1, y1, x2, y2 = obj["bbox"]
            cx = int((x1+x2)//2)
            cy = int((y1+y2)//2)

            cv2.circle(self.heatmap, (cx, cy), self.heatmap_radius, 1, -1)

    def draw_heatmap(self, frame):
        heat = cv2.normalize(self.heatmap, None, 0, 255, cv2.NORM_MINMAX)
        heat = heat.astype("uint8")

        heat_color = cv2.applyColorMap(heat, cv2.COLORMAP_JET)
        return cv2.addWeighted(frame, 1 - self.heatmap_opacity, heat_color, self.heatmap_opacity, 0)
    
    def draw_hud(self, frame, fps, tracks):
        th, tw, _ = frame.shape
        
        fps_text = f"FPS: {int(fps)}"
        (tw, th), _ = cv2.getTextSize(fps_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
        cv2.rectangle(frame, (15, 40-th-5), (20+tw+5, 45), (0,0,0), -1)
        cv2.putText(frame, fps_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        obj_text = f"Objects: {len(tracks)}"
        x = 20
        y = 80
        (tw, th), _ = cv2.getTextSize(obj_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        cv2.rectangle(frame, (x-5, y-th-5), (x+tw+5, y+5), (0,0,0), -1)
        cv2.putText(frame, obj_text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        return frame
