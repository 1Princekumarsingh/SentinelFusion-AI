"""
SentinelFusion AI - Main Entry Point

Standalone desktop application for real-time object detection and tracking.
Displays video feed with tracking overlays in an OpenCV window.

Keyboard Controls:
    h - Toggle heatmap visualization
    d - Toggle depth visualization
    q/ESC - Quit application

Usage:
    python main.py
"""

import cv2
from core.cv_pipeline import CVPipeline

def main():
    cap = cv2.VideoCapture(r"C:\Users\kprin\Desktop\SentinelFusion AI\video\test.mp4")
    # cap = cv2.VideoCapture(0)

    pipeline = CVPipeline()

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.resize(frame, (640, 480))
        frame = pipeline.process_frame(frame)

        cv2.imshow("Tracking System", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('h'):
            pipeline.renderer.show_heatmap = not pipeline.renderer.show_heatmap
        if key == ord('d'):
            pipeline.renderer.show_depth = not pipeline.renderer.show_depth
        if key == ord('q') or key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()