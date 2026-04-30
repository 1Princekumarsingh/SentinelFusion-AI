from copy import deepcopy
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SETTINGS_PATH = PROJECT_ROOT / "settings.yaml"

DEFAULT_SETTINGS = {
    "video": {
        "source": "video/test.mp4",
        "camera_index": 0,
        "loop_video": True,
        "frame_width": 640,
        "frame_height": 360,
        "jpeg_quality": 85,
    },
    "display": {
        "show_heatmap": True,
        "show_depth": True,
    },
    "detection": {
        "model_path": "yolov8n.pt",
        "interval": 4,
        "image_size": 416,
        "base_confidence": 0.2,
        "iou_threshold": 0.3,
        "min_box_size": 20,
        "target_classes": [0, 2],
    },
    "depth": {
        "interval": 15,
    },
    "tracking": {
        "max_age": 30,
        "n_init": 3,
        "max_cosine_distance": 0.3,
        "min_hits": 3,
        "max_time_since_update": 2,
    },
    "alerts": {
        "proximity_threshold": 50,
    },
    "heatmap": {
        "radius": 20,
        "opacity": 0.3,
        "slow_decay": 0.98,
        "fast_decay": 0.995,
    },
    "demo": {
        "output_path": "demo_output.mp4",
        "max_seconds": 10,
        "output_fps": 0,
    },
}


def merge_settings(defaults, overrides):
    merged = deepcopy(defaults)
    for key, value in (overrides or {}).items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_settings(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_settings():
    if not SETTINGS_PATH.exists():
        return deepcopy(DEFAULT_SETTINGS)

    with SETTINGS_PATH.open("r", encoding="utf-8") as file:
        user_settings = yaml.safe_load(file) or {}

    return merge_settings(DEFAULT_SETTINGS, user_settings)


settings = load_settings()
