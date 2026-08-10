import json
import os

DATA_FILES = ["saved_message.json", "warnings.json"]

def load_saved_messages() -> dict:
    if not os.path.exists(DATA_FILES[0]):
        return {}
    try:
        with open(DATA_FILES[0], "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_user_message(user_id: int, message: str):
    data = load_saved_messages()
    data[str(user_id)] = message
    with open(DATA_FILES[0], "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def load_warnings() -> dict:
    if not os.path.exists(DATA_FILES[1]):
        return {}
    try:
        with open(DATA_FILES[1], "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_warnings(data: dict):
    with open(DATA_FILES[1], "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
