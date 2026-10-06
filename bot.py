import sys
import asyncio

# --- FIX FOR PYTHON 3.12 / 3.14 EVENT LOOP ISSUE ---
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

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
BOT_TOKEN = ""

OWNER_ID = 8640890230
OWNER_USERNAME = "Alex761kh"
BOT_USERNAME = "alexbanxunbanbot"

MANDATORY_CHANNEL = "alexbanxunban"
MANDATORY_GROUP_LINK = "https://t.me/banproofsgc"

# UPDATED DIRECT MP4 VIDEO URL
HEADER_VIDEO = "https://videotourl.com/videos/1791279853845-6cb60d69-8304-468c-a625-46219c88d2b3.mp4"

# --- 2. DUMMY FLASK SERVER FOR RENDER ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "⚡ ALEX BAN X UNBAN BOT IS ACTIVE AND RUNNING HIGH-SPEED! ⚡"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

# --- 3. PERSISTENT STORAGE SYSTEM ---
REQ_FILE = "approved_users.json"

def load_approved_users():
    if os.path.exists(REQ_FILE):
        try:
            with open(REQ_FILE, "r") as f:
                return set(json.load(f))
        except Exception:
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

app = Client("AlexBanUnbanBotSession", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- 4. JOIN REQUEST EVENT HANDLER ---
@app.on_chat_join_request()
async def track_join_requests(client, chat_join_request: ChatJoinRequest):
    user_id = chat_join_request.from_user.id
    save_approved_user(user_id)

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
    return text, buttons

def get_main_menu(user_id):
    user_data = users_db.get(user_id, {'referrals': 0, 'is_premium': False})
    
    if user_id == OWNER_ID:
        status_str = "👑 𝑶𝑾𝑵𝑬𝑹"
    elif user_data['is_premium']:
        status_str = "💎 𝑷𝑹𝑬𝑴𝑰𝑼𝑴"
    else:
        status_str = "🪙 𝑭𝑹𝑬𝑬 𝑼𝑺𝑬𝑹"

    caption = (
        "⚡ <b><u>𝑨𝑳𝑬𝑿 𝑩𝑨𝑵 𝑿 𝑼𝑵𝑩𝑨𝑵 𝑩𝑶𝑻 𝑽2.0</u></b> ⚡\n\n"
        "🔥 <i>The Most Powerful Multi-Tasking Telegram Shield Engine</i>\n\n"
        "<code>┌───────────────────────────────┐\n"
        f"│ 👤 User ID   : {user_id:<14} │\n"
        f"│ 🛡️️ Rank      : {status_str:<14} │\n"
        f"│ 🔮 Referrals : {str(user_data['referrals'])+'/10':<14} │\n"
        "└───────────────────────────────┘</code>\n\n"
        "🚀 <b>Choose your target module from below:</b>"
    )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("💀 Permanent Ban", callback_data="ban_perm"), InlineKeyboardButton("⏳ Temporary Ban", callback_data="ban_temp")],
        [InlineKeyboardButton("💥 Mass Report v2", callback_data="mass_report"), InlineKeyboardButton("🔓 Instant Unban", callback_data="unban")],
        [InlineKeyboardButton("🔍 Ban Inspector", callback_data="status"), InlineKeyboardButton("🤖 System Health", callback_data="bot_status")],
        [InlineKeyboardButton("💎 Invite & Unlock VIP", callback_data="invite"), InlineKeyboardButton("👑 Creator", url=f"https://t.me/{OWNER_USERNAME}")],
        [InlineKeyboardButton("📢 Official Channel", url=f"https://t.me/{MANDATORY_CHANNEL}"), InlineKeyboardButton("💬 Proof Group", url=MANDATORY_GROUP_LINK)]
    ])
    return caption, buttons

# --- 6. COMMAND HANDLERS ---
@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats_cmd(client, message):
    total_users = len(users_db)
    premium_users = sum(1 for u in users_db.values() if u.get('is_premium', False))
    free_users = total_users - premium_users
    
    stats_text = (
        "📊 <b><u>ALEX BOT SYSTEM CONTROL</u></b>\n\n"
        f"👥 <b>Total Active Users:</b> <code>{total_users}</code>\n"
        f"💎 <b>VIP Premium Members:</b> <code>{premium_users}</code>\n"
        f"🪙 <b>Free Tier Users:</b> <code>{free_users}</code>"
    )
    await message.reply(stats_text)

@app.on_message(filters.command("addpremium") & filters.user(OWNER_ID))
async def add_premium_cmd(client, message):
    if len(message.command) < 2:
        await message.reply("❌ <b>Usage:</b> <code>/addpremium <user_id></code>")
        return
    try:
        target_id = int(message.command[1])
        if target_id not in users_db:
            users_db[target_id] = {'referrals': 0, 'is_premium': True}
        else:
            users_db[target_id]['is_premium'] = True
        await message.reply(f"👑 User <code>{target_id}</code> successfully promoted to 💎 <b>VIP PREMIUM</b>!")
    except ValueError:
        await message.reply("❌ Invalid User ID provided.")

@app.on_message(filters.command("rempremium") & filters.user(OWNER_ID))
async def rem_premium_cmd(client, message):
    if len(message.command) < 2:
        await message.reply("❌ <b>Usage:</b> <code>/rempremium <user_id></code>")
        return
    try:
        target_id = int(message.command[1])
        if target_id in users_db:
            users_db[target_id]['is_premium'] = False
            await message.reply(f"🔻 User <code>{target_id}</code> demoted to Free status.")
        else:
            await message.reply("❌ User not found in database.")
    except ValueError:
        await message.reply("❌ Invalid User ID.")

@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_cmd(client, message):
    if not message.reply_to_message:
        await message.reply("❌ <b>Please reply to a message to broadcast.</b>")
        return
    
    msg = await message.reply("🚀 <b>Initiating High-Speed Broadcast...</b>")
    success, failed = 0, 0
    
    for uid in list(users_db.keys()):
        try:
            await message.reply_to_message.copy(uid)
            success += 1
            await asyncio.sleep(0.04)
        except Exception:
            failed += 1

    await msg.edit(
        "⚡ <b><u>BROADCAST FINISHED</u></b>\n\n"
        f"✅ <b>Delivered:</b> <code>{success}</code>\n"
        f"❌ <b>Failed:</b> <code>{failed}</code>"
    )

@app.on_message(filters.command("start"))
async def start_cmd(client, message):
    user_id = message.from_user.id
    user_states.pop(user_id, None)
    
    # Track Referral Logic
    is_new_user = user_id not in users_db
    if is_new_user:
        users_db[user_id] = {'referrals': 0, 'is_premium': False}
        if len(message.command) > 1:
            try:
                ref_by = int(message.command[1])
                if ref_by in users_db and ref_by != user_id:
                    users_db[ref_by]['referrals'] += 1
                    if users_db[ref_by]['referrals'] >= 10:
                        users_db[ref_by]['is_premium'] = True
                    try:
                        await client.send_message(
                            ref_by, 
                            f"🎉 <b>New Referral Joined!</b>\nTotal Referrals: <code>{users_db[ref_by]['referrals']}/10</code>"
                        )
                    except Exception:
                        pass
            except Exception:
                pass

    if not await check_force_join(client, user_id):
        text, buttons = get_force_join_menu()
        await message.reply_text(text, reply_markup=buttons)
        return

    caption, buttons = get_main_menu(user_id)
    try:
        await message.reply_video(video=HEADER_VIDEO, caption=caption, reply_markup=buttons)
    except Exception:
        await message.reply_text(text=caption, reply_markup=buttons)

@app.on_message(filters.text & ~filters.command(["start", "stats", "addpremium", "rempremium", "broadcast"]))
async def handle_input(client, message):
    user_id = message.from_user.id
    
    if user_id in user_states:
        action_type = user_states.pop(user_id)
        target = message.text.strip()
        
        msg = await message.reply("⏳ <b>Processing Task across Nodes...</b>")
        
        for pct in [25, 50, 75, 100]:
            await asyncio.sleep(0.6)
            bar = render_progress_bar(pct)
            
            table_text = (
                "⚡ <b>ALEX ENGINE LIVE MONITOR</b>\n\n"
                "<code>┌───────────────────────────────┐\n"
                f"│ Target  : {target[:12]:<17} │\n"
                f"│ Module  : {action_type:<17} │\n"
                f"│ Status  : {bar:<17} │\n"
                "└───────────────────────────────┘</code>"
            )
            await msg.edit_text(table_text)

        final_output = (
            "✅ <b><u>ACTION EXECUTED SUCCESSFULLY</u></b>\n\n"
            "📜 <i>Execution Log Overview:</i>\n\n"
            f"<blockquote>🎯 <b>Target:</b> {target}\n"
            f"⚙ <b>Module Loaded:</b> {action_type}\n"
            "🔥 <b>Result:</b> Routine finished with 0 fatal errors.</blockquote>"
        )
        back_btn = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Return to Main Dashboard", callback_data="back_to_menu")]])
        await msg.edit_text(final_output, reply_markup=back_btn)

# --- 7. CALLBACK QUERY HANDLER ---
@app.on_callback_query()
async def cb_handler(client, query):
    user_id = query.from_user.id
    data = query.data
    
    if data == "check_join_status":
        if await check_force_join(client, user_id):
            await query.answer("✅ Verification Completed! Access Granted.", show_alert=True)
            caption, buttons = get_main_menu(user_id)
            try:
                await query.message.reply_video(video=HEADER_VIDEO, caption=caption, reply_markup=buttons)
                await query.message.delete()
            except Exception:
                await query.message.edit_text(text=caption, reply_markup=buttons)
        else:
            await query.answer("❌ Channels join karke verify button dabayein!", show_alert=True)
        return

    if data == "back_to_menu":
        user_states.pop(user_id, None)
        caption, buttons = get_main_menu(user_id)
        try:
            await query.message.edit_caption(caption=caption, reply_markup=buttons)
        except Exception:
            await query.message.edit_text(text=caption, reply_markup=buttons)
        return

    if data == "invite":
        ref_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
        user_data = users_db.get(user_id, {'referrals': 0})
        invite_text = (
            "🚀 <b><u>REFERRAL SYSTEM & VIP ACCESS</u></b>\n\n"
            "💎 <i>Invite 10 Friends to instantly unlock VIP Premium Features for free!</i>\n\n"
            f"📊 <b>Your Invites:</b> <code>{user_data['referrals']}/10</code>\n"
            f"🔗 <b>Your Exclusive Link:</b>\n<code>{ref_link}</code>"
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📤 Share Referral Link", url=f"https://t.me/share/url?url={ref_link}&text=Try%20Alex%20Ban%20Unban%20Bot!")],
            [InlineKeyboardButton("👑 Owner Support", url=f"https://t.me/{OWNER_USERNAME}")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
        ])
        try:
            await query.message.edit_caption(caption=invite_text, reply_markup=buttons)
        except Exception:
            await query.message.edit_text(text=invite_text, reply_markup=buttons)
        return

    if data in ["ban_perm", "ban_temp", "mass_report", "unban", "status", "bot_status"]:
        user_data = users_db.get(user_id, {'referrals': 0, 'is_premium': False})
        
        if user_id != OWNER_ID and not user_data['is_premium']:
            ref_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
            restricted_text = (
                "🔒 <b><u>PREMIUM FEATURE LOCKED</u></b> 🔒\n\n"
                "⚠️ <i>Aap abhi Free Tier par hain! Is feature ke liye VIP Premium status zaroori hai.</i>\n\n"
                f"📊 <b>Your Referrals:</b> <code>{user_data['referrals']}/10</code>\n\n"
                "🎯 <b><u>HOW TO UNLOCK?</u></b>\n"
                f"1️⃣ Invite 10 Friends using: <code>{ref_link}</code>\n"
                f"2️⃣ Direct Buy by contacting Owner."
            )
            restricted_buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("📤 Share Referral Link", url=f"https://t.me/share/url?url={ref_link}&text=Join%20Alex%20Ban%20Bot")],
                [InlineKeyboardButton("👑 Buy Premium Access", url=f"https://t.me/{OWNER_USERNAME}")],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
            ])
            try:
                await query.message.edit_caption(caption=restricted_text, reply_markup=restricted_buttons)
            except Exception:
                await query.message.edit_text(text=restricted_text, reply_markup=restricted_buttons)
            return

        current_time = time.time()
        last_time = cooldowns.get(user_id, 0)
        if current_time - last_time < COOLDOWN_TIME:
            remaining = int(COOLDOWN_TIME - (current_time - last_time))
            mins, secs = divmod(remaining, 60)
            await query.answer(f"⏳ Cooldown Active! Please wait {mins}m {secs}s.", show_alert=True)
            return

        cooldowns[user_id] = current_time
        user_states[user_id] = data
        
        ask_text = (
            "🎯 <b><u>ENTER TARGET INFORMATION</u></b>\n\n"
            "✍️ <i>Target ka Username ya ID send karein:</i>"
        )
        buttons = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel Action", callback_data="back_to_menu")]])
        try:
            await query.message.edit_caption(caption=ask_text, reply_markup=buttons)
        except Exception:
            await query.message.edit_text(text=ask_text, reply_markup=buttons)

# --- 8. APPLICATION RUNNER ---
if __name__ == "__main__":
    print("🚀 Web Server Starting for Render...")
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()

    print("⚡ ALEX BAN X UNBAN BOT STARTING...")
    app.run()
