import os
import json
import time
from datetime import datetime
from config import config

LOGGING_ENABLED = config.get("logging", {}).get("enabled", False)

def _generate_log_path():
    app_mode = config["app_mode"]
    feedback_mode = config["feedback"]["mode"]
    feedback_focus = config["feedback"].get("focus", "unknown")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = "cpr_feedback_system/testing/test_logs"
    os.makedirs(folder, exist_ok=True)
    if app_mode == "plot_position":
        return f"{folder}/log_no_fb_position_{timestamp}.ndjson"
    elif app_mode == "plot_depth":
        return f"{folder}/log_no_fb_depth_{timestamp}.ndjson"
    elif app_mode == "feedback":
        return f"{folder}/log_{feedback_mode}_{feedback_focus}_{timestamp}.ndjson"
    else:
        print("Invalid app_mode")
        return None

LOG_PATH = _generate_log_path() if LOGGING_ENABLED else None

def get_selected_fixed_point():
    target_key = config["feedback"].get("target", "t1")
    return config["target"].get(f"fixed_point_{target_key}", None)

def get_selected_target_label():
    return config["feedback"].get("target", "t1")

def get_selected_depth_range():
    label = get_selected_target_label()
    mapping = config["depth_sensor"].get("target_to_range_map", {})
    range_key = mapping.get(label, None)
    return config["depth_sensor"].get(range_key, [0, 999])

def get_metadata():
    app_mode = config["app_mode"]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if app_mode == "feedback":
        meta = {
            "log_version": 1,
            "created": timestamp,
            "feedback_mode": config["feedback"]["mode"],
            "feedback_focus": config["feedback"].get("focus"),
            "target_position": get_selected_fixed_point(),
            "target_label": get_selected_target_label(),
            "target_position": get_selected_fixed_point(),
            "target_depth_range": get_selected_depth_range()
        }
    else:
        meta = {
            "log_version": 1,
            "created": time.time(),
            "feedback_mode": "N/A",
            "feedback_focus": "N/A",
            "mode": app_mode,
            "target_position": get_selected_fixed_point(),
            "target_label": get_selected_target_label(),
            "target_position": get_selected_fixed_point(),
            "target_depth_range": get_selected_depth_range()
        }
    return meta

# write metadata as first line
if LOG_PATH:
    print(f"🧪 logging to {LOG_PATH}")

    meta = get_metadata()

    with open(LOG_PATH, "w") as f:
        f.write(json.dumps(meta) + "\n")

def _round_floats(value):
    if isinstance(value, float):
        return round(value, 3)
    if isinstance(value, (list, tuple)):
        return [_round_floats(v) for v in value]
    return value

def log_event(matrix=None, cop=None, error=None, depth=None, bpm=None):
    if not LOG_PATH:
        return
    entry = {
        "system_time": time.time(),
        "cop": _round_floats(cop),
        "error_cop": _round_floats(error),
        "depth": _round_floats(depth),
        "bpm": _round_floats(bpm),
        "matrix": matrix.tolist() if matrix is not None else None,
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
