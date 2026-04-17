import cv2
import time
from core.pipeline import VisionPipeline
from utils.visualizer import Visualizer

def main():
    
    print("Opening video...")
    cap = cv2.VideoCapture(r"C:\Users\kprin\Desktop\SentinelFusion AI\video\test2.mp4")
    # cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("failed to open video")
        exit()

    pipeline = VisionPipeline()
    visualizer = Visualizer()

    prev_time = 0
    fps = 0

    while True:
        ret, frame = cap.read()
        #frame = cv2.resize(frame, (640, 480))

        if not ret:
            break

        # process through pipeline
        output = pipeline.process(frame)

        # draw tracking + depth
        frame = visualizer.draw_tracks(frame, output["tracks"], output["depth"])

        #fps calculation
        curr_time = time.time()
        dt = curr_time - prev_time
        if prev_time != 0:
            fps = 0.9 * fps + 0.1 * (1 / dt)
        prev_time = curr_time
        
        cv2.putText(frame, f"FPS: {int(fps)}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow("Tracking System", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()