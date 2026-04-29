# presets.py
import json
import os

def save_presets(patterns, filename="presets.json"):
    data = []
    for p in patterns:
        data.append({
            "steps": p.steps,
            "rows": p.to_text()
        })
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def load_presets(filename="presets.json"):
    if not os.path.exists(filename):
        return []

    with open(filename, "r") as f:
        data = json.load(f)

    from sequencer import Pattern
    patterns = []

    for p in data:
        pat = Pattern(p["steps"])
        pat.from_text(p["rows"])
        patterns.append(pat)

    return patterns
