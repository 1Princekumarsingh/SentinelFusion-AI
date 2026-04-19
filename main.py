import cv2
import time
from core.pipeline import VisionPipeline
from utils.visualizer import Visualizer
from utils.frame_renderer import FrameRenderer

def main():
    
    print("Opening video...")
    cap = cv2.VideoCapture(r"C:\Users\kprin\Desktop\SentinelFusion AI\video\test.mp4")
    # cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("failed to open video")
        exit()

    pipeline = VisionPipeline()
    visualizer = Visualizer()
    renderer = FrameRenderer()

    prev_time = time.time()
    fps = 0

    while True:
        ret, frame = cap.read()
        #frame = cv2.resize(frame, (640, 480))

        if not ret:
            break
            
        current_time = time.time()
        fps = 1 / (current_time - prev_time)
        prev_time = current_time
        
        # process through pipeline and update heatmap
        output = pipeline.process(frame)
        renderer.update_heatmap(frame, output["tracks"], fps)

        # first depth 
        if renderer.show_depth:
            frame = visualizer.overlay_depth(frame, output["depth"])

        # heatmap
        if renderer.show_heatmap:
            frame = renderer.draw_heatmap(frame)

        # tracking
        frame = visualizer.draw_tracks(frame, output["tracks"], output["depth"])

        # alerts
        frame = visualizer.draw_alerts(frame, output["alerts"])

        # hub
        frame = renderer.draw_hud(frame, fps, output["tracks"])

        cv2.imshow("Tracking System", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('h'):
            renderer.show_heatmap = not renderer.show_heatmap

        if key == ord('d'):
            renderer.show_depth = not renderer.show_depth

        if key == ord('q') or key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()