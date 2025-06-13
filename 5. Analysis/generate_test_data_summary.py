"""
This script processes CPR test session data collected from multiple participants.
It parses `.ndjson` log files containing time series data (e.g., compression depth,
center of pressure error, BPM), extracts summary statistics for each session,
and stores both a summary CSV and a detailed Parquet file for further analysis.

The script is designed to support statistical evaluation of CPR performance metrics
(such as compression accuracy, rate, and depth) across multiple feedback modalities.
"""

import json
import pandas as pd
from tqdm import tqdm
from pathlib import Path
import numpy as np

def parse_ndjson(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()

    metadata = json.loads(lines[0])
    data = [json.loads(line) for line in lines[1:]]

    return metadata, data

def extract_session_summary(participant_id, session_index, metadata, data):
    feedback_mode = metadata.get('feedback_mode', 'none')
    feedback_focus = metadata.get('feedback_focus', 'none')
    target_position = metadata.get('target_position', [None, None])
    target_label = metadata.get('target_label', 'none')
    target_depth_range = metadata.get('target_depth_range', [0, 100])

    errors = [d["error_cop"] for d in data if d["error_cop"] is not None]
    depths = [d["depth"] for d in data if d["depth"] is not None]
    bpms = [d["bpm"] for d in data if d["bpm"] is not None]

    return {
        "participant_id": participant_id,
        "session_index": session_index,
        "feedback_mode": feedback_mode,
        "feedback_focus": feedback_focus,
        "target_position_x": target_position[0],
        "target_position_y": target_position[1],
        "target_label": target_label,
        "target_depth_min": target_depth_range[0],
        "target_depth_max": target_depth_range[1],
        "avg_error": np.mean(errors) if errors else None,
        "std_error": np.std(errors) if errors else None,
        "avg_depth": np.mean(depths) if depths else None,
        "std_depth": np.std(depths) if depths else None,
        "avg_bpm": np.mean(bpms) if bpms else None,
        "std_bpm": np.std(bpms) if bpms else None,
        "n_valid_timesteps": len(data)
    }

def extract_detailed_data(participant_id, session_index, metadata, data):
    feedback_mode = metadata.get('feedback_mode', 'none')
    feedback_focus = metadata.get('feedback_focus', 'none')
    target_position = metadata.get('target_position', [None, None])
    target_label = metadata.get('target_label', 'none')
    target_depth_range = metadata.get('target_depth_range', [0, 100])

    detailed_rows = []
    for entry in data:
        cop = entry.get("cop")
        if isinstance(cop, list) and len(cop) == 2:
            cop_x, cop_y = cop
        else:
            cop_x, cop_y = None, None

        row = {
            "participant_id": participant_id,
            "session_index": session_index,
            "system_time": entry.get("system_time"),
            "cop_x": cop_x,
            "cop_y": cop_y,
            "error_cop": entry.get("error_cop"),
            "depth": entry.get("depth"),
            "bpm": entry.get("bpm"),
            "feedback_mode": feedback_mode,
            "feedback_focus": feedback_focus,
            "target_position_x": target_position[0],
            "target_position_y": target_position[1],
            "target_label": target_label,
            "target_depth_min": target_depth_range[0],
            "target_depth_max": target_depth_range[1]
        }

        detailed_rows.append(row)

    return detailed_rows

def generate_global_data(data_root='.', summary_output='final_tests_analysis/global_summary.csv', detailed_output='final_tests_analysis/global_detailed.parquet', participant_ids=None):
    summary_list = []
    detailed_rows = []

    candidate_dirs = sorted(Path(data_root).glob("Candidate *"))

    for candidate_folder in tqdm(candidate_dirs):
        participant_id = int(candidate_folder.name.split()[-1])

        # Skip participants not in list
        if participant_ids is not None and participant_id not in participant_ids:
            continue

        session_files = sorted(candidate_folder.glob("*.ndjson"))

        for session_index, session_file in enumerate(session_files):
            metadata, data = parse_ndjson(session_file)
            summary = extract_session_summary(participant_id, session_index, metadata, data)
            detailed = extract_detailed_data(participant_id, session_index, metadata, data)

            summary_list.append(summary)
            detailed_rows.extend(detailed)

    # Save summary
    df_summary = pd.DataFrame(summary_list)
    df_summary.to_csv(summary_output, index=False)

    # Save detailed frame-by-frame data
    df_detailed = pd.DataFrame(detailed_rows)
    df_detailed.to_parquet(detailed_output, index=False)

    print(f"Saved summary to {summary_output}")
    print(f"Saved detailed data to {detailed_output}")


generate_global_data(
    data_root="cpr_feedback_system/testing/ordered_test_logs",
    participant_ids=list(range(7, 19))  # IDs 7 to 18 inclusive
)
