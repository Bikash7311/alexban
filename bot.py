import sys
import asyncio
import json
import os
import time
import threading
from flask import Flask

from hydrogram import Client, filters
from hydrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatJoinRequest
from hydrogram.errors import UserNotParticipant

# --- 1. CONFIGURATION ---
API_ID = 33772941  
API_HASH = "3b6ab6b1940c87915439bb41e4e80ea8"  
BOT_TOKEN = "8844875546:AAHJmca5Y5WvoisObgCldpF3Qz80tKpk0XY"

OWNER_ID = 8640890230
OWNER_USERNAME = "Alex761kh"
BOT_USERNAME = "alexbanxunbanbot"

MANDATORY_CHANNEL = "alexbanxunban"
MANDATORY_GROUP_LINK = "https://t.me/banproofsgc"
REQ_CHANNEL_LINK = "https://t.me/alexbanxunban"

HEADER_VIDEO = "https://videotourl.com/videos/1791279853845-6cb60d69-8304-468c-a625-46219c88d2b3.mp4"

# --- 2. DUMMY FLASK SERVER FOR RENDER ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "⚡ ALEX BAN X UNBAN BOT IS ACTIVE AND RUNNING HIGH-SPEED! ⚡"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

# --- 3. APPROVED REQUEST USERS FILE SYSTEM ---
REQ_FILE = "approved_users.json"

def load_approved_users():
    if os.path.exists(REQ_FILE):
        try:
            with open(REQ_FILE, "r") as f:
                return set(json.load(f))
        except Exception as e:
            print(f"Error loading approved users: {e}")
            return set()
    return set()

approved_req_users = load_approved_users()

def save_approved_user(user_id):
    approved_req_users.add(user_id)
    try:
        with open(REQ_FILE, "w") as f:
            json.dump(list(approved_req_users), f)
    except Exception as e:
        print(f"Error saving approved user: {e}")

users_db = {}
cooldowns = {}
user_states = {}
COOLDOWN_TIME = 300

# INITIALIZE CLIENT
app = Client("AlexBanUnbanBotSession", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- 4. JOIN REQUEST EVENT HANDLER ---
@app.on_chat_join_request()
async def track_join_requests(client, chat_join_request: ChatJoinRequest):
    user_id = chat_join_request.from_user.id
    save_approved_user(user_id)
    print(f"✅ [JOIN REQUEST APPROVED] User ID: {user_id}")

# --- 5. HELPER FUNCTIONS ---
def render_progress_bar(percent: int, length: int = 12) -> str:
    filled = int(length * percent // 100)
    bar = "▓" * filled + "░" * (length - filled)
    return f"[{bar}] {percent}%"

async def check_force_join(client, user_id):
    if user_id == OWNER_ID:
        return True
    
    try:
        await client.get_chat_member(MANDATORY_CHANNEL, user_id)
    except UserNotParticipant:
        return False
    except Exception:
        pass

    if user_id in approved_req_users:
        return True

    try:
        chat_member = await client.get_chat_member("banproofsgc", user_id)
        if chat_member:
            save_approved_user(user_id)
            return True
    except Exception:
        pass

    return False

def get_force_join_menu():
    text = (
        "🛑 <b><u>ACCESS RESTRICTED — VERIFICATION REQUIRED</u></b> 🛑\n\n"
        "✨ <i>Bot ki high-power features access karne ke liye niche diye gaye Official Channels join karein!</i>\n\n"
        "📢 1️⃣ <b>Official Main Channel</b>\n"
        "💬 2️⃣ <b>Proof & Discussion GC</b>\n\n"
        "⚡ <i>Sabhi channels join karke <b>'Verify Access 🔄'</b> par click karein.</i>"
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Main Channel", url=f"https://t.me/{MANDATORY_CHANNEL}")],
        [InlineKeyboardButton("💬 Join Proof Group", url=MANDATORY_GROUP_LINK)],
        [InlineKeyboardButton("🔄 Verify Access / Try Again", callback_data="check_join_status")]
    ])
