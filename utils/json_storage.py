import json
import os

# File paths
SAVED_MESSAGES_FILE = "saved_messages.json"
WARNINGS_FILE = "warnings.json"
WELCOME_FILE = "welcome_channels.json"
CLUB_DATA_FILE = "club_info.json"

# =============================
# SAVED MESSAGES STORAGE
# =============================
def load_saved_messages() -> dict:
    if not os.path.exists(SAVED_MESSAGES_FILE):
        return {}
    try:
        with open(SAVED_MESSAGES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_user_message(user_id: int, message: str):
    data = load_saved_messages()
    data[str(user_id)] = message
    with open(SAVED_MESSAGES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# =============================
# WARNINGS STORAGE
# =============================
def load_warnings() -> dict:
    if not os.path.exists(WARNINGS_FILE):
        return {}
    try:
        with open(WARNINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_warnings(data: dict):
    with open(WARNINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# =============================
# WELCOME CHANNELS STORAGE
# =============================
def load_welcome_channels() -> dict:
    if not os.path.exists(WELCOME_FILE):
        return {}
    try:
        with open(WELCOME_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_welcome_channel(guild_id: int, channel_id: int):
    data = load_welcome_channels()
    data[str(guild_id)] = channel_id
    with open(WELCOME_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# =============================
# CLUB INFO STORAGE
# =============================

def load_club_info() -> dict:
    if not os.path.exists(CLUB_DATA_FILE):
        return {}
    try:
        with open(CLUB_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_club_info(data: dict):
    with open(CLUB_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)