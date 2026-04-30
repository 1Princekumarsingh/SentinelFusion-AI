import cv2
from typing import Optional
from pathlib import Path

import asyncio

from fastapi import FastAPI
from fastapi import WebSocket
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from core.cv_pipeline import CVPipeline
from core.settings import PROJECT_ROOT, settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = CVPipeline()
video_settings = settings["video"]


def get_video_source():
    source = video_settings["source"]
    if str(source).lower() in ("camera", "webcam"):
        return int(video_settings["camera_index"])

    path = Path(str(source))
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return str(path)

def generate_frames():
    cap = cv2.VideoCapture(get_video_source())

    if not cap.isOpened():
        print("Error: Cannot open camera")
        return
    
    while True:
        ret, frame= cap.read()

        if not ret:
            if video_settings["loop_video"]:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            break

        width = int(video_settings["frame_width"])
        height = int(video_settings["frame_height"])
        if width > 0 and height > 0:
            frame = cv2.resize(frame, (width, height))

        frame = pipeline.process_frame(frame)

        # encoding frame to jpeg
        jpeg_quality = int(video_settings["jpeg_quality"])
        encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]
        ret, buffer = cv2.imencode('.jpg', frame, encode_params)
        if not ret:
            continue

        frame_bytes = buffer.tobytes()

        # yielding frame in mjpeg format
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.get("/")
def home():
    return {"message": "AI Streaming Server Running"}

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(
        generate_frames(),
        media_type='multipart/x-mixed-replace; boundary=frame'
    )

@app.post("/config")
def update_config(heatmap: Optional[bool] = None, depth: Optional[bool] = None):
    if heatmap is not None:
        pipeline.renderer.show_heatmap = heatmap 
    if depth is not None:
        pipeline.renderer.show_depth = depth 

    return{
        "heatmap": pipeline.renderer.show_heatmap,
        "depth": pipeline.renderer.show_depth
    }

@app.websocket("/ws/stats")
async def websocket_endpoint(websocket: WebSocket):
    print("WS CONNECT ATTEMPT")
    await websocket.accept()
    print("WS CONNECTED")       

    while True:
        try:
            if pipeline.fps == 0:
                await asyncio.sleep(0.1)
                continue

            safe_alerts = []
            if pipeline.last_alerts:
                for a in pipeline.last_alerts:
                    if isinstance(a, dict):
                        safe_alerts.append({
                            "type": str(a.get("type", "")),
                            "pair": [int(a["pair"][0]), int(a["pair"][1])] if "pair" in a else [0, 0],
                            "distance": int(a.get("distance", 0))
                        })

            data = {
                "fps": int(pipeline.fps),
                "objects": len(pipeline.last_tracks),
                "alerts": safe_alerts
            }

            print("WS SEND:", data)  # debug

            await websocket.send_json(data)
            await asyncio.sleep(0.1)

        except Exception as e:
            print("WebSocket error:", e)
            await asyncio.sleep(0.5)
            continue
