import random
import json
from pathlib import Path

participant_seed = 18  # change this per participant for reproducibility

"""
test_plan_generator.py

Generates randomized but reproducible CPR feedback prototype testing plans
for individual participants, pairing feedback prototypes with compression
target positions.

Functionality:
--------------
- For each participant, a list of trials is generated where each trial is a 
  unique combination of a feedback prototype and a target position.
- The order of the trials is randomized using a fixed seed to ensure reproducibility.
- Plans can be saved as JSON files for loading into the CPR feedback test system.

Parameters:
-----------
- `prototypes`: List of prototype system identifiers (e.g. ["audio", "box", ...]).
- `targets`: List of compression target labels (e.g. ["t1", "t2", ..., "t6"]).
- `seed`: Integer seed value used to initialize the random generator, usually tied to the participant ID.
- `allow_repeats`: If True, target positions may repeat across trials.

Outputs:
--------
- Console preview of the participant's assigned trials.
- JSON file saved to: `cpr_feedback_system/testing/ordered_test_logs/a_test_plans/candidate_<seed>_plan.json`
"""

def generate_participant_plan(prototypes, targets, seed=None, allow_repeats=True):
    random.seed(seed)

    # fixed prototypes per participant
    selected_prototypes = prototypes.copy()

    # draw random targets
    if allow_repeats:
        selected_targets = [random.choice(targets) for _ in range(len(prototypes))]
    else:
        selected_targets = random.sample(targets, len(prototypes))

    # pair them up in random order
    trial_plan = list(zip(selected_prototypes, selected_targets))
    random.shuffle(trial_plan)

    return trial_plan

def save_plan_as_json(plan, seed, folder="cpr_feedback_system/testing/ordered_test_logs/a_test_plans"):
    Path(folder).mkdir(exist_ok=True)
    filename = f"{folder}/candidate_{seed}_plan.json"
    data = {
        "participant_id": seed,
        "trials": [{"trial": idx, "prototype": proto, "target": target} for idx, (proto, target) in enumerate(plan, 1)]
    }
    with open(filename, "w") as jsonfile:
        json.dump(data, jsonfile, indent=2)
    print(f"✅ JSON saved to {filename}")

prototypes = ["audio", "box", "glove", "belt", "screen"]
targets = ["t1", "t2", "t3", "t4", "t5", "t6"]

plan = generate_participant_plan(prototypes, targets, seed=participant_seed, allow_repeats=True)
print("\n")
print(f"Participant Test Plan (Seed: {participant_seed}):")
for i, (proto, target) in enumerate(plan, 1):
    print(f"Trial {i}: {proto} → {target}")

save_plan_as_json(plan, participant_seed)
