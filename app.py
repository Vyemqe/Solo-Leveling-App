from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)
SAVE_FILE = "curr_data.json"

# --- SYSTEM DATABASES ---
def get_rank(level):
    if level >= 300: return "SSS-Rank Hunter"
    if level >= 150: return "SS-Rank Hunter"
    if level >= 100: return "S-Rank Hunter"
    if level >= 75: return "A-Rank Hunter"
    if level >= 50: return "B-Rank Hunter"
    if level >= 25: return "C-Rank Hunter"
    if level >= 10:  return "D-Rank Hunter"
    return "E-Rank Hunter"

ACHIEVEMENTS_DB = [
    {"id": "q5", "type": "quest_count", "target": 5, "title": "Warming Up", "desc": "Completed 5 quests!", "icon": "5"},
    {"id": "q10", "type": "quest_count", "target": 10, "title": "Consistency is Key", "desc": "Completed 10 quests!", "icon": "10"},
    {"id": "q25", "type": "quest_count", "target": 25, "title": "Daily Routine", "desc": "Completed 25 quests!", "icon": "25"},
    {"id": "q50", "type": "quest_count", "target": 50, "title": "Busy Bee", "desc": "Completed 50 quests!", "icon": "50"},
    {"id": "q100", "type": "quest_count", "target": 100, "title": "Superhuman", "desc": "Completed 100 quests!", "icon": "100"},
    {"id": "q200", "type": "quest_count", "target": 200, "title": "Godhuman", "desc": "Completed 200 quests!", "icon": "200"},
    {"id": "rank_d", "type": "rank", "target": "D-Rank Hunter", "title": "Awakening", "desc": "You've become a D-Rank Hunter!", "icon": "D"},
    {"id": "rank_c", "type": "rank", "target": "C-Rank Hunter", "title": "Elite", "desc": "You've become a C-Rank Hunter!", "icon": "C"},
    {"id": "rank_b", "type": "rank", "target": "B-Rank Hunter", "title": "Veteran", "desc": "You've become a B-Rank Hunter!", "icon": "B"},
    {"id": "rank_a", "type": "rank", "target": "A-Rank Hunter", "title": "High Orc Level", "desc": "You've become an A-Rank Hunter!", "icon": "A"},
    {"id": "rank_s", "type": "rank", "target": "S-Rank Hunter", "title": "National Level", "desc": "You've become an S-Rank Hunter!", "icon": "S"},
    {"id": "rank_ss", "type": "rank", "target": "SS-Rank Hunter", "title": "International Level", "desc": "You've become an SS-Rank Hunter!", "icon": "SS"},
    {"id": "rank_sss", "type": "rank", "target": "SSS-Rank Hunter", "title": "Liberator of the Sky", "desc": "You've become an SSS-Rank Hunter!", "icon": "SSS"},
]

DEFAULT_DATA = {
    "player": {"level": 1, "xp": 0, "max_xp": 100, "title": "E-Rank Hunter"},
    "stats": {"total_quests_completed": 0},
    "achievements": [],
    "tasks": [],
    "task_id_counter": 1
}

# --- SAVE/LOAD LOGIC ---
def load_data():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
            # Migrations for older save files
            if "stats" not in data:
                data["stats"] = {"total_quests_completed": sum(1 for t in data.get("tasks", []) if t.get("completed"))}
            if "achievements" not in data:
                data["achievements"] = []
            return data
    return DEFAULT_DATA.copy()

def save_data(data):
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- ROUTES ---
@app.route("/")
def index():
    data = load_data()
    active_tasks = [t for t in data["tasks"] if not t.get("archived", False)]
    return render_template("index.html", player=data["player"], tasks=active_tasks)

@app.route("/history")
def history():
    data = load_data()
    completed = [t for t in reversed(data["tasks"]) if t["completed"]]
    # return render_template("history.html", tasks=completed)
        # 1. Sort descending by actual datetime (newest first)
    def parse_time(task):
        time_str = task.get("completed_at")
        if time_str:
            try:
                return datetime.strptime(time_str, "%Y-%m-%d %I:%M %p")
            except ValueError:
                pass
        return datetime.min # Fallback if time is broken
    completed.sort(key=parse_time, reverse=True)
    # 2. Group by date
    grouped_tasks = {}
    for task in completed:
        time_str = task.get("completed_at")
        date_key = time_str.split(" ")[0] if time_str else "Unknown Date"
        if date_key not in grouped_tasks:
            grouped_tasks[date_key] = []
        grouped_tasks[date_key].append(task)
    return render_template("history.html", grouped_tasks=grouped_tasks)


@app.route("/achievements")
def achievements():
    data = load_data()
    unlocked_ids = [a["id"] for a in data["achievements"]]
    unlocked = []
    locked = []
    for ach in ACHIEVEMENTS_DB:
        ach_copy = ach.copy()
        if ach["id"] in unlocked_ids:
            # Find the timestamp
            for saved_ach in data["achievements"]:
                if saved_ach["id"] == ach["id"]:
                    ach_copy["unlocked_at"] = saved_ach["unlocked_at"]
            unlocked.append(ach_copy)
        else:   locked.append(ach_copy)
    return render_template("achievements.html", unlocked=unlocked, locked=locked, stats=data["stats"])

@app.route("/complete", methods=["POST"])
def complete_task():
    data = load_data()
    task_id = int(request.json.get("id"))   # request.json.get("id") -> str
    events = [] # Toasts queue
    leveled_up = False
    for task in data["tasks"]:
        if task["id"] == task_id and not task["completed"]:
            task["completed"] = True
            task["completed_at"] = datetime.now().strftime("%Y-%m-%d %I:%M %p")
            data["player"]["xp"] += task["xp"]
            data["stats"]["total_quests_completed"] += 1
            # Event 1: Quest complete
            events.append({"title": "Quest Cleared!", "desc": task["title"], "icon": "sword"})
            # Level Up Logic
            while data["player"]["xp"] >= data["player"]["max_xp"]:
                data["player"]["level"] += 1
                data["player"]["xp"] -= data["player"]["max_xp"]
                data["player"]["max_xp"] = int(data["player"]["max_xp"] * 1.25)
                leveled_up = True
            old_rank = data["player"]["title"]
            new_rank = get_rank(data["player"]["level"])
            data["player"]["title"] = new_rank
            # Check for new Achievements
            unlocked_ids = [a["id"] for a in data["achievements"]]
            for ach in ACHIEVEMENTS_DB:
                if ach["id"] in unlocked_ids: continue # Already have it
                just_unlocked = False
                if ach["type"] == "quest_count" and data["stats"]["total_quests_completed"] >= ach["target"]:
                    just_unlocked = True
                elif ach["type"] == "rank" and new_rank == ach["target"] and new_rank != old_rank:
                    just_unlocked = True
                if just_unlocked:
                    data["achievements"].append({
                        "id": ach["id"],
                        "unlocked_at": datetime.now().strftime("%Y-%m-%d %I:%M %p")
                    })
                    events.append({"title": ach["title"], "desc": ach["desc"], "icon": ach["icon"]})
            # Save state
            save_data(data)
            return jsonify({
                "success": True,
                "player": data["player"],
                "leveled_up": leveled_up,
                "events": events
            })
    return jsonify({"success": False}), 400

@app.route("/add", methods=["POST"])
def add_task():
    data = load_data()
    data["tasks"].append({
        "id": data["task_id_counter"],
        "title": request.json.get("title"),
        "xp": request.json.get("xp", 40),
        "completed": False, "archived": False, "completed_at": None
    })
    data["task_id_counter"] += 1
    save_data(data)
    return jsonify({"success": True})

@app.route("/clear", methods=["POST"])
def clear_tasks():
    data = load_data()
    for task in data["tasks"]:
        if task["completed"]: task["archived"] = True
    save_data(data)
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True, port=9090)