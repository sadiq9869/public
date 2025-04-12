#!/usr/bin/env python3
import sys
import subprocess
import importlib.util
import asyncio
import random
import requests
import logging
import signal
from telegram import ChatPermissions
import time
import json
import os
from typing import Tuple
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from cryptography.fernet import Fernet
import pickle
import tenacity
from concurrent.futures import ThreadPoolExecutor
import threading

# Check and load dependencies manually
try:
    import feedparser
    print("feedparser loaded successfully, version:", feedparser.__version__)
except ImportError as e:
    print(f"Failed to import feedparser: {e}")
    sys.exit(1)

# Bot Setup
TELEGRAM_BOT_TOKEN = "8094930692:AAGy-bnpYA0A1j6B3lRWol-GyfK9gtiMwCo"
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Telegram bot token not found")
GROUP_ID = "-1002328886935"
CHANNEL_USERNAME = "@DDOS_SERVER69"
OVERLORD_IDS = {"1807014348", "1866961136"}
AI_ID = "AI_001_GROK"
TECH_NEWS_RSS = "http://feeds.feedburner.com/TechCrunch/"
FUN_FACTS_API_URL = "https://uselessfacts.jsph.pl/random.json?language=en"
TRENDING_TOPICS_URL = "https://www.reddit.com/r/technology/hot/.rss"
image_urls = ["https://envs.sh/g7a.jpg", "https://envs.sh/g7O.jpg", "https://envs.sh/g7_.jpg", "https://envs.sh/gHR.jpg"]

# Global Data
SELF_API_DATA = {"user_stats": {}, "attack_trends": {}, "user_behavior": {}, "global_trends": {}, "ai_health": {"health": 100, "load": 0, "errors": 0}}
SELF_API_FILE = "self_api_data.json"
EMERGENCY_BACKUP_FILE = "emergency_backup.pkl"
ENCRYPTION_KEY_FILE = "encryption_key.key"
if os.path.exists(ENCRYPTION_KEY_FILE):
    with open(ENCRYPTION_KEY_FILE, "rb") as f:
        ENCRYPTION_KEY = f.read()
else:
    ENCRYPTION_KEY = Fernet.generate_key()
    with open(ENCRYPTION_KEY_FILE, "wb") as f:
        f.write(ENCRYPTION_KEY)
cipher = Fernet(ENCRYPTION_KEY)
API_CACHE = {}
user_profiles = {}
successful_attacks = {}
used_handles = set()
attack_permissions = set()
paid_users = set()
approved_users = set()
trial_users = set()
trial_data = {}
join_points = {}
last_leaderboard_reset = time.time()
top_user_weekly = None
keys = {}
codes = {}
redeemed_keys = {}
redeemed_codes = {}
pending_feedback = {}
paid_user_attack_count = {}
USER_FILE = "users.txt"
user_data = {}
last_trial_reset = time.time()
violations = {}
nickname_violations = {}
command_abuse_violations = {}
muted_users = {}
banned_users = {}
attack_counts = {}
attack_timestamps = {}
user_levels = {}
user_powerups = {}
global_attack_leaderboard = {}
last_daily_reward = {}
action_logs = []
last_log_clear = time.time()
command_timestamps = {}
NORMAL_COOLDOWN_TIME = 60
PAID_COOLDOWN_TIME = 30
OVERLORD_COOLDOWN_TIME = 0
NORMAL_ATTACK_LIMIT = 15
PAID_ATTACK_LIMIT = float('inf')
TRIAL_ATTACK_LIMIT = 15
MAX_ATTACK_TIME_NORMAL = 160
MAX_ATTACK_TIME_PAID = 240
MAX_ATTACK_TIME_OVERLORD = float('inf')
global_attack_running = False
attack_lock = threading.Lock()
VALID_PORT_FIRST_DIGITS = {1, 2, 6, 7}
AI_TONE = "DynamicSwag"
AI_LANGUAGE = "Hinglish"
AI_PERFORMANCE_LEVEL = "High"
AI_FEATURES = ["Sentiment Analysis", "Dynamic Responses", "Auto-Taunt", "Fun Facts"]
ABUSIVE_WORDS = ["bhenchod", "madarchod", "chutiya", "gandu"]
DYNAMIC_NICKNAMES = ["SwagKing👑", "AttackMaster💥", "DDOSDon🔥", "CyberSher🦁"]
ACHIEVEMENTS = {
    "Rookie Attacker": {"attacks": 10, "points": 50, "reward": 20},
    "Pro Hacker": {"attacks": 20, "points": 200, "reward": 60},
    "DDOS King": {"attacks": 50, "points": 500, "reward": 150}
}
POWERUPS = {"DoubleDamage": 2.0, "SpeedBoost": 0.5, "ExtraTime": 1.5}
LEVEL_THRESHOLDS = {1: 0, 2: 100, 3: 300, 5: 1000}
executor = ThreadPoolExecutor(max_workers=10)
MESSAGE_THEMES = {
    "default": {
        "welcome": ["**🎉🔥 Welcome [handle]!** Tu DDOS ke jungle mein aa gaya! 💪 **[abusive]** ban ke dushman ko uda! 🚀"],
        "error": ["**😂🤦‍♂️ Oops [handle]!** Kuch galat ho gaya! 😡 **[abusive]** wala fail! Check kar! 🚨"],
        "attack_success": ["**💥🎉 Kya baat [handle]!** Target ko **[abusive]** bana diya! 😎 [taunt] 💪"],
        "attack_status": ["**🔥 ATTACK STATUS 🔥**\n**Status:** {status}\n**Progress:** [{progress}] {percent}% 💥"],
        "attack_report": ["**📊 ATTACK REPORT 📊**\n**Target:** {target}\n**Port:** {port}\n**Packets:** {packets}\n**Success:** {success_rate}% 🔥 **[abusive]** dushman ka server! 💀"],
        "cooldown": ["**⏳ [handle], Chill Kar!** Cooldown pe hai! 😏 **[abusive]** ban ke wait kar! 🔥 **{remaining}s** left ⏰"],
        "feedback_reminder": ["**📸 [handle], Feedback De!** Screenshot bhej, **[abusive]** mat ban! 🔥"],
        "feedback_request": ["**📸 [handle], 5 Attacks Done!** Feedback de do bhai, screenshot bhej! 😊 **[abusive]** mat ban! 🔥"],
        "hype_broadcast": ["**🔥🏆 BADA ATTACK DAY!** Leaderboard pe naam chadhao! 🚀 **[abusive]** swag dikhao! 👑"],
        "ai_status": ["**🤖 AI STATUS 👑**\n**Tone:** {tone}\n**Language:** {language}\n**Performance:** {performance}\n**Features:** {features} 🚀"],
        "ai_health": ["**🤖 AI HEALTH CHECK 🩺**\n**Health:** {health}%\n**Load:** {load}\n**Errors:** {errors} 💉"],
        "inquiry_response": ["**🤖 [handle] ka Jawab!**\n**Q:** {question}\n**A:** {response} 😎"],
        "inquiry_forward": ["**🚨 OVERLORD ALERT 🚨**\n**User:** {handle}\n**Q:** {question}\nAI confused hai, help karo! 😓"],
        "achievement_unlock": ["**🏆 [handle] ne [achievement] Unlock Kiya!** **[abusive]** swag! +{points} points! 🔥"],
        "level_up": ["**🎉 LEVEL UP! 🎉**\n**[handle]** ab Level {level} pe! 🔥 Power-up: {powerup} 💪"],
        "global_leaderboard": ["**🌍 TOP ATTACKERS 🌍**\n1️⃣ {top1_handle}: {top1_attacks}\n2️⃣ {top2_handle}: {top2_attacks}\n3️⃣ {top3_handle}: {top3_attacks}\n**[abusive]** swag dikhao! 🚀"],
        "daily_reward": ["**🎁 DAILY LOOT! 🎁**\n**[handle]**, {points} points mile! 🔥 Keep rocking! 💪"],
        "backup_success": ["**🤖💾 BACKUP DONE!**\n**Time:** {time}\n**Status:** Success 🚀 Safe hai Overlord ji! 🙏"],
        "shutdown_save": ["**🤖💾 SHUTDOWN SAVE!**\n**Time:** {time}\n**Status:** Success 🚀 Data safe hai! 🙏"],
        "startup_load": ["**🤖🔄 STARTUP LOAD!**\n**Time:** {time}\n**Status:** Success 🚀 Data wapas aa gaya! 🙏"]
    }
}

# Logging Setup
logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
abusive_logger = logging.getLogger('abusive_usage')
abusive_handler = logging.FileHandler('abusive_usage.log')
abusive_handler.setFormatter(logging.Formatter('%(asctime)s - UserID: %(user_id)s - Message: %(message)s'))
abusive_logger.addHandler(abusive_handler)
abusive_logger.setLevel(logging.INFO)

# Global application variable
application = None
data_lock = threading.Lock()

# Data Management
def save_self_api_data():
    try:
        with data_lock:
            with open(SELF_API_FILE, 'wb') as f:
                f.write(cipher.encrypt(json.dumps(SELF_API_DATA).encode()))
    except Exception as e:
        logger.error(f"Failed to save self API data: {e}")
        with data_lock:
            SELF_API_DATA["ai_health"]["errors"] += 1

def load_self_api_data():
    global SELF_API_DATA
    if os.path.exists(SELF_API_FILE):
        try:
            with open(SELF_API_FILE, 'rb') as f:
                SELF_API_DATA = json.loads(cipher.decrypt(f.read()).decode())
        except Exception as e:
            logger.error(f"Error loading self API data: {e}")

def load_users():
    try:
        with open(USER_FILE, "r") as file:
            for line in file:
                user_id, attacks, last_reset = line.strip().split(',')
                user_data[user_id] = {'attacks': int(attacks), 'last_reset': datetime.fromisoformat(last_reset), 'last_attack': None}
    except FileNotFoundError:
        pass
    except Exception as e:
        logger.error(f"Error parsing users file: {e}")

def save_users():
    try:
        with data_lock:
            with open(USER_FILE, "w") as file:
                for user_id, data in user_data.items():
                    file.write(f"{user_id},{data['attacks']},{data['last_reset'].isoformat()}\n")
    except Exception as e:
        logger.error(f"IO Error saving users: {e}")

def save_data_on_shutdown():
    data = {k: globals()[k] for k in ["user_profiles", "join_points", "successful_attacks", "used_handles", "attack_permissions", "paid_users", "trial_users", "trial_data", "last_leaderboard_reset", "keys", "codes", "redeemed_keys", "redeemed_codes", "pending_feedback", "paid_user_attack_count", "user_data", "last_trial_reset", "violations", "muted_users", "banned_users", "attack_counts", "attack_timestamps", "user_levels", "user_powerups", "global_attack_leaderboard", "last_daily_reward", "action_logs", "last_log_clear"]}
    with data_lock:
        with open(EMERGENCY_BACKUP_FILE, "wb") as f:
            pickle.dump(data, f)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = MESSAGE_THEMES["default"]["shutdown_save"].format(time=current_time)
    if application:
        for overlord_id in OVERLORD_IDS:
            try:
                application.bot.send_message(chat_id=overlord_id, text=message, disable_notification=False)
            except Exception as e:
                logger.error(f"Error sending shutdown message: {e}")
    executor.shutdown(wait=True)

def load_data_on_startup():
    global user_profiles, join_points, successful_attacks, used_handles, attack_permissions, paid_users, trial_users, trial_data, last_leaderboard_reset, keys, codes, redeemed_keys, redeemed_codes, pending_feedback, paid_user_attack_count, user_data, last_trial_reset, violations, muted_users, banned_users, attack_counts, attack_timestamps, user_levels, user_powerups, global_attack_leaderboard, last_daily_reward, action_logs, last_log_clear
    if os.path.exists(EMERGENCY_BACKUP_FILE):
        with data_lock:
            with open(EMERGENCY_BACKUP_FILE, "rb") as f:
                data = pickle.load(f)
                for key in data:
                    globals()[key] = data[key]
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = MESSAGE_THEMES["default"]["startup_load"].format(time=current_time)
        if application:
            for overlord_id in OVERLORD_IDS:
                try:
                    application.bot.send_message(chat_id=overlord_id, text=message, disable_notification=False)
                except Exception as e:
                    logger.error(f"Error sending startup message: {e}")

# API and Behavior Tracking
@tenacity.retry(stop=tenacity.stop_after_attempt(3), wait=tenacity.wait_exponential(multiplier=1, min=4, max=10))
def fetch_api_data(url, is_rss=False):
    with data_lock:
        if url in API_CACHE and (time.time() - API_CACHE[url]["timestamp"]) < 3600:
            return API_CACHE[url]["data"]
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = feedparser.parse(response.text) if is_rss else response.json()
        if is_rss and (not hasattr(data, 'entries') or not isinstance(data.entries, list)):
            raise ValueError(f"Invalid RSS feed from {url}")
        with data_lock:
            API_CACHE[url] = {"data": data, "timestamp": time.time()}
            if len(API_CACHE) > 100:
                oldest = min(API_CACHE.items(), key=lambda x: x[1]["timestamp"])
                del API_CACHE[oldest[0]]
            API_CACHE.update({k: v for k, v in API_CACHE.items() if time.time() - v["timestamp"] < 3600})
        return data
    except Exception as e:
        logger.error(f"Error fetching API data from {url}: {e}")
        raise

def update_user_behavior(user_id, behavior_type):
    user_id_str = str(user_id)
    with data_lock:
        if user_id_str not in SELF_API_DATA["user_behavior"]:
            SELF_API_DATA["user_behavior"][user_id_str] = {}
        SELF_API_DATA["user_behavior"][user_id_str][behavior_type] = SELF_API_DATA["user_behavior"][user_id_str].get(behavior_type, 0) + 1
        save_self_api_data()

def update_attack_trends(target, port, time):
    attack_data = {"target": target, "port": port, "time": time, "timestamp": str(datetime.now())}
    with data_lock:
        if "attacks" not in SELF_API_DATA["attack_trends"]:
            SELF_API_DATA["attack_trends"]["attacks"] = []
        SELF_API_DATA["attack_trends"]["attacks"].append(attack_data)
        save_self_api_data()

# AI Health and Status
stop_event = threading.Event()

def update_ai_health():
    while not stop_event.is_set():
        with data_lock:
            SELF_API_DATA["ai_health"]["health"] = max(100 - SELF_API_DATA["ai_health"]["errors"] * 5, 0)
            SELF_API_DATA["ai_health"]["load"] = len(SELF_API_DATA["user_behavior"])
            save_self_api_data()
        time.sleep(60)

async def auto_run_status_health(context: ContextTypes.DEFAULT_TYPE):
    while True:
        await context.bot.send_message(chat_id=GROUP_ID, text=MESSAGE_THEMES["default"]["ai_status"].format(
            tone=AI_TONE, language=AI_LANGUAGE, performance=AI_PERFORMANCE_LEVEL, features=", ".join(AI_FEATURES)), disable_notification=False)
        await context.bot.send_message(chat_id=GROUP_ID, text=MESSAGE_THEMES["default"]["ai_health"].format(
            health=SELF_API_DATA["ai_health"]["health"], load=SELF_API_DATA["ai_health"]["load"], errors=SELF_API_DATA["ai_health"]["errors"]), disable_notification=False)
        await asyncio.sleep(300)

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in OVERLORD_IDS:
        await update.message.reply_text("🚫 OVERLORD ONLY! 😡", disable_notification=False)
        return
    args = context.args
    if not args:
        await update.message.reply_text("❌ USAGE: /broadcast <message>", disable_notification=False)
        return
    message = " ".join(args)
    await context.bot.send_message(GROUP_ID, f"📢 **Overlord Broadcast**: {message}", parse_mode='Markdown', disable_notification=False)
    log_action(user_id, "broadcast", f"Message: {message}")

# Auto-Reset Functions
async def auto_reset(context: ContextTypes.DEFAULT_TYPE):
    while True:
        now = datetime.now()
        seconds_until_midnight = ((24 - now.hour - 1) * 3600) + ((60 - now.minute - 1) * 60) + (60 - now.second)
        await asyncio.sleep(seconds_until_midnight)
        with data_lock:
            for user_id in user_data:
                user_data[user_id]['attacks'] = 0
                user_data[user_id]['last_reset'] = datetime.now()
            for user_id in attack_counts:
                attack_counts[user_id] = {"date": datetime.now().date().isoformat(), "count": 0}
            save_users()
        await context.bot.send_message(GROUP_ID, "**🔄 DAILY ATTACK LIMITS RESET!** 🚀", disable_notification=False)

async def auto_reset_trial(context: ContextTypes.DEFAULT_TYPE):
    global last_trial_reset, trial_users, trial_data
    while True:
        current_time = time.time()
        if current_time - last_trial_reset >= 21 * 24 * 60 * 60:
            with data_lock:
                trial_users.clear()
                trial_data.clear()
                last_trial_reset = current_time
            await context.bot.send_message(GROUP_ID, "**🔄 TRIAL PERIOD RESET!** Use /trail! 🚀", disable_notification=False)
        await asyncio.sleep(24 * 3600)

async def check_leaderboard_reset(context: ContextTypes.DEFAULT_TYPE):
    global last_leaderboard_reset, top_user_weekly, join_points
    current_time = time.time()
    if current_time - last_leaderboard_reset >= 7 * 24 * 60 * 60:
        with data_lock:
            if join_points:
                top_user = max(join_points, key=join_points.get)
                if top_user_weekly == top_user:
                    key_name = f"top_{top_user}_{int(current_time)}"
                    keys[key_name] = {
                        "duration": "1d",
                        "device_limit": 1,
                        "devices_used": 0,
                        "expiry_time": current_time + 86400,
                        "price": 0
                    }
                    await context.bot.send_message(
                        GROUP_ID,
                        f"**🏆 {user_profiles.get(top_user, {}).get('handle', top_user)}** ne 1 week top rakha! Key: `{key_name}` 🎉",
                        disable_notification=False
                    )
                top_user_weekly = top_user
            join_points.clear()
            last_leaderboard_reset = current_time
        await context.bot.send_message(
            GROUP_ID, "**📊 Leaderboard Reset!** 🚀", disable_notification=False
        )

# Utility Functions
def check_abusive_language(text: str, user_id: str) -> bool:
    text_lower = text.lower()
    for word in ABUSIVE_WORDS:
        if word in text_lower:
            abusive_logger.info(f"Abusive word detected: {word}", extra={"user_id": user_id, "message": text})
            return True
    return False

async def apply_penalty(user_id: str, violation_type: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_str = str(user_id)
    violation_dict = nickname_violations if violation_type in ["nickname", "handle"] else command_abuse_violations
    with data_lock:
        violation_dict[user_id_str] = violation_dict.get(user_id_str, 0) + 1
        log_action(user_id_str, "violation", f"{violation_type} violation - Count: {violation_dict[user_id_str]}")
        if violation_dict[user_id_str] == 1:
            await update.message.reply_text(f"**⚠️ Warning:** {violation_type.capitalize()} violation! 😡", disable_notification=False)
        elif violation_dict[user_id_str] == 2:
            await update.message.reply_text("**⚠️ 2nd Warning:** 1 hour mute! 😡", disable_notification=False)
            await context.bot.restrict_chat_member(GROUP_ID, user_id, until_date=int(time.time() + 3600))
            muted_users[user_id_str] = time.time() + 3600
        else:
            await update.message.reply_text("**⚠️ Final Warning:** 1 day ban! 🚫", disable_notification=False)
            await context.bot.ban_chat_member(GROUP_ID, user_id, until_date=int(time.time() + 86400))
            banned_users[user_id_str] = time.time() + 86400
            violation_dict[user_id_str] = 0

def log_action(user_id: str, action_type: str, details: str):
    with data_lock:
        action_logs.append({"user_id": user_id, "action_type": action_type, "details": details, "timestamp": datetime.now().isoformat()})

def get_user_level(points: int) -> int:
    for level, threshold in sorted(LEVEL_THRESHOLDS.items(), key=lambda x: x[1], reverse=True):
        if points >= threshold:
            return level
    return 1

def generate_dynamic_taunt(user_id, theme="default"):
    user_id_str = str(user_id)
    try:
        trending_data = fetch_api_data(TRENDING_TOPICS_URL, is_rss=True)
        trending_topic = trending_data["entries"][0]["title"] if trending_data and "entries" in trending_data and trending_data["entries"] else "No trending topic"
    except Exception:
        trending_topic = "No trending topic"
    TAUNT_MESSAGES = {
        "default": [f"Dushman ka server {trending_topic} jaisa dhamaka kar gaya! 🔥 RIP! 💀"],
        "dark": [f"Teri raat ho gayi dushman! 🌙 Server andhere mein! 🖤"],
        "party": [f"Party mein dhoom macha di! 🎉 Server gaya! 🎈"],
        "warrior": [f"Jung mein server haar gaya! ⚔️ Teri jeet! 🛡️"]
    }
    return random.choice(TAUNT_MESSAGES.get(theme, TAUNT_MESSAGES["default"]))

def process_question(question: str) -> Tuple[str, bool]:
    question_lower = question.lower()
    if "hello" in question_lower:
        return "Hello! How can I assist you?", True
    elif "help" in question_lower:
        return "Sure, what do you need help with?", True
    elif "attack" in question_lower:
        return "Bhai, /attack <target> <port> <time> use kar! Eg: /attack 192.168.1.1 80 120 💥", True
    elif "key" in question_lower or "redeem" in question_lower:
        return "Key redeem karne ke liye /redeem <key_name>! Overlord se maang! 🔑", True
    elif "trial" in question_lower:
        return "Trial ke liye /trail use kar! 15 attacks, 3 weeks tak! 🕒", True
    elif "leaderboard" in question_lower:
        return "Leaderboard ke liye /myinfo! Top pe aane ke liye points collect kar! 🏆", True
    elif "points" in question_lower:
        return "Join pe 10, invite pe 20 points! Leaderboard ke liye jama kar! 🏅", True
    elif "mute" in question_lower or "ban" in question_lower:
        return "Mute/ban sirf Overlord kar sakta hai! Rules mat tod! 🚫", True
    elif "fun fact" in question_lower:
        try:
            fact_data = fetch_api_data(FUN_FACTS_API_URL)
            fact = fact_data.get('text', "DDOS attacks bohot dangerous hote hain! 🔥")
            return f"Sun! {fact} 😱", True
        except Exception:
            return "Fun fact nahi mila, try again! 😓", True
    else:
        return "Bhai, yeh mere samajh ke bahar hai! 😓 Overlord ko forward kar raha hu!", False

def check_rate_limit(user_id: str, command: str) -> bool:
    user_id_str = str(user_id)
    with data_lock:
        if user_id_str not in command_timestamps:
            command_timestamps[user_id_str] = {}
        if command not in command_timestamps[user_id_str]:
            command_timestamps[user_id_str][command] = 0
        last_use = command_timestamps[user_id_str][command]
        if time.time() - last_use < 5:
            return False
        command_timestamps[user_id_str][command] = time.time()
        return True

# Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_id_str = str(user_id)
    if user_id_str in banned_users and (banned_users[user_id_str] is None or time.time() < banned_users[user_id_str]):
        await update.message.reply_text("**🚫 BANNED!** Tu group se out hai! 😡", disable_notification=False)
        return
    with data_lock:
        if user_id_str not in user_profiles:
            nickname = random.choice(DYNAMIC_NICKNAMES)
            handle = f"@{nickname}_{random.randint(1000, 9999)}"
            while handle in used_handles:
                handle = f"@{nickname}_{random.randint(1000, 9999)}"
            used_handles.add(handle)
            user_profiles[user_id_str] = {"nickname": nickname, "handle": handle, "attack_style": "default", "bio": "Naya DDOS warrior! 🔥", "theme": "default"}
            join_points[user_id_str] = 10
            user_levels[user_id_str] = 1
            user_powerups[user_id_str] = []
        handle = user_profiles[user_id_str]["handle"]
        theme = user_profiles[user_id_str]["theme"]
        abusive = random.choice(ABUSIVE_WORDS)
        welcome_msg = random.choice(MESSAGE_THEMES[theme]["welcome"]).replace("[handle]", handle).replace("[abusive]", abusive)
    await update.message.reply_text(welcome_msg, parse_mode='Markdown', disable_notification=False)
    update_user_behavior(user_id, "messages_sent")
    log_action(user_id_str, "start", f"New user joined with handle {handle}")
    save_users()

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_rate_limit(str(update.effective_user.id), "help"):
        await update.message.reply_text("**⏳ Thoda Chill Kar!** 5 sec wait kar! 😡", disable_notification=False)
        return
    help_text = (
        "**📜 COMMANDS GUIDE 📜**\n\n"
        "🔹 /start - Shuru kar apna DDOS safar! 🚀\n"
        "🔹 /help - Yeh guide dekho! 📋\n"
        "🔹 /tutorial - DDOS ka full tutorial! 📚\n"
        "🔹 /attack <target> <port> <time> - Dushman ka server uda! 💥\n"
        "🔹 /myinfo - Apna profile check kar! 📊\n"
        "🔹 /attackhistory - Recent attacks dekho! 📜\n"
        "🔹 /referral [code] - Dost invite kar, points le! 🔗\n"
        "🔹 /broadcast <msg> - (Overlord) Group mein chillao! 📢\n"
        "🔹 /mute <user_id> [duration] - (Overlord) Chup karao! 🔇\n"
        "🔹 /unmute <user_id> - (Overlord) Bolne do! 🔊\n"
        "🔹 /ban <user_id> [duration] - (Overlord) Bahar karo! 🚫\n"
        "🔹 /unban <user_id> - (Overlord) Wapas lao! ✅\n"
        "🔹 /addall - (Overlord) Sabko attack permission! 🔓\n"
        "🔹 /removeall - (Overlord) Sabki permission hatao! 🔒\n"
        "🔹 /approve <id> - (Overlord) Paid features do! ✅\n"
        "🔹 /disapprove <id> - (Overlord) Features hatao! 🚫\n"
        "🔹 /gen <duration> <limit> [name] - (Overlord) Key banao! 🔑\n"
        "🔹 /redeem <key> - Paid access le! 🔓\n"
        "🔹 /redeem_code <code> - Trial access le! 🔓\n"
        "🔹 /trail - Free trial lo! 🕒\n"
        "🔹 /add <user_id> - (Overlord) User add karo! ➕\n"
        "🔹 /remove <user_id> - (Overlord) User hatao! ➖\n"
        "🔹 /inquiry <question> - AI se poochho! 🤖\n\n"
        "**💡 Example:** /attack 192.168.1.1 80 120"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown', disable_notification=False)
    update_user_behavior(str(update.effective_user.id), "messages_sent")

async def tutorial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if not check_rate_limit(user_id, "tutorial"):
        await update.message.reply_text("**⏳ Thoda Chill Kar!** 5 sec wait kar! 😡", disable_notification=False)
        return
    if user_id not in user_profiles:
        await update.message.reply_text("**❌ PAHLE /start KARO!** 😡", parse_mode='Markdown', disable_notification=False)
        return
    tutorial_text = (
        "**📚 DDOS TUTORIAL 📚**\n\n"
        "**Step-by-Step Guide:**\n"
        "1️⃣ **Permission Lo** - Trial: /trail | Paid: Overlord se maango!\n"
        "2️⃣ **Attack Karo** - /attack <target> <port> <time>\n"
        "3️⃣ **Rules Samjho** - Normal: 15 attacks/day, 60s cooldown\n\n"
        "**📎 Full Guide:** https://t.me/freeddos_group12/18291\n"
        "**💡 Help:** /inquiry <question>"
    )
    await update.message.reply_text(tutorial_text, parse_mode='Markdown', disable_notification=False)
    log_action(user_id, "tutorial", "User requested DDOS tutorial")

async def myinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if not check_rate_limit(user_id, "myinfo"):
        await update.message.reply_text("**⏳ Thoda Chill Kar!** 5 sec wait kar! 😡", disable_notification=False)
        return
    if user_id not in user_profiles:
        await update.message.reply_text("**❌ PAHLE /start KARO!** 😡", parse_mode='Markdown', disable_notification=False)
        return
    with data_lock:
        profile = user_profiles[user_id]
        points = join_points.get(user_id, 0)
        level = user_levels.get(user_id, 1)
        leaderboard_position = sorted(join_points.items(), key=lambda x: x[1], reverse=True).index((user_id, points)) + 1 if user_id in join_points else "N/A"
    
    info_text = (
        f"**📊 {profile['handle']} KA PROFILE 📊**\n"
        f"**🔹 Nickname:** {profile['nickname']}\n"
        f"**🔹 Level:** {level}\n"
        f"**🔹 Points:** {points}\n"
        f"**🔹 Leaderboard Pos:** {leaderboard_position}\n"
    )
    await update.message.reply_text(info_text, parse_mode='Markdown', disable_notification=False)

    args = context.args if context.args else []
    if len(args) >= 2:
        if args[0] in ["setnickname", "sethandle"]:
            new_value = args[1]
            if args[0] == "sethandle" and not new_value.startswith('@'):
                await update.message.reply_text("**❌ HANDLE @ SE START HONA CHAHIYE!** 😡", parse_mode='Markdown', disable_notification=False)
                return
            if args[0] == "sethandle" and new_value in used_handles:
                await update.message.reply_text("**❌ YEH HANDLE LIYA HUA HAI!** 😡", parse_mode='Markdown', disable_notification=False)
                return
            if check_abusive_language(new_value, user_id) and user_id not in OVERLORD_IDS:
                await update.message.reply_text(f"**❌ ABUSIVE {args[0][3:].upper()} NHI RAKH SAKTA!** 😡", parse_mode='Markdown', disable_notification=False)
                return
            with data_lock:
                if args[0] == "sethandle":
                    used_handles.remove(user_profiles[user_id]["handle"])
                    used_handles.add(new_value)
                user_profiles[user_id][args[0][3:]] = new_value
            await update.message.reply_text(f"**✅ {args[0][3:].upper()} SET!** New {args[0][3:]}: {new_value} 😎", parse_mode='Markdown', disable_notification=False)

async def mute_unmute(update: Update, context: ContextTypes.DEFAULT_TYPE, is_mute=True):
    user_id = str(update.effective_user.id)
    if user_id not in OVERLORD_IDS:
        await update.message.reply_text("🚫 OVERLORD ONLY! 😡", disable_notification=False)
        return
    args = context.args if context.args else []
    if len(args) < 1:
        await update.message.reply_text(f"**❌ USAGE:** /{'mute' if is_mute else 'unmute'} <user_id>", parse_mode='Markdown', disable_notification=False)
        return
    try:
        target_id = int(args[0])
        if is_mute:
            duration = None
            if len(args) > 1:
                try:
                    duration = int(args[1][:-1]) * (3600 if args[1].endswith('h') else 86400 if args[1].endswith('d') else 1)
                except ValueError:
                    await update.message.reply_text("**❌ VALID DURATION DO!** (e.g., 1h, 2d) 😡", parse_mode='Markdown', disable_notification=False)
                    return
            await context.bot.restrict_chat_member(GROUP_ID, target_id, permissions=ChatPermissions(can_send_messages=False), until_date=int(time.time() + duration) if duration else None)
            await update.message.reply_text(f"**✅ USER {target_id} MUTED!** 🔇", parse_mode='Markdown', disable_notification=False)
        else:
            await context.bot.restrict_chat_member(GROUP_ID, target_id, permissions=ChatPermissions(can_send_messages=True))
            await update.message.reply_text(f"**✅ USER {target_id} UNMUTED!** 🔊", parse_mode='Markdown', disable_notification=False)
        log_action(user_id, "mute" if is_mute else "unmute", f"Target: {target_id}")
    except Exception as e:
        await update.message.reply_text(f"**❌ ERROR:** {e} 😡", parse_mode='Markdown', disable_notification=False)

async def ban_unban(update: Update, context: ContextTypes.DEFAULT_TYPE, is_ban=True):
    user_id = str(update.effective_user.id)
    if user_id not in OVERLORD_IDS:
        await update.message.reply_text("🚫 OVERLORD ONLY! 😡", disable_notification=False)
        return
    args = context.args if context.args else []
    if len(args) < 1:
        await update.message.reply_text(f"**❌ USAGE:** /{'ban' if is_ban else 'unban'} <user_id>", parse_mode='Markdown', disable_notification=False)
        return
    try:
        target_id = int(args[0])
        if is_ban:
            duration = None
            if len(args) > 1:
                try:
                    duration = int(args[1][:-1]) * (3600 if args[1].endswith('h') else 86400 if args[1].endswith('d') else 1)
                except ValueError:
                    await update.message.reply_text("**❌ VALID DURATION DO!** (e.g., 1h, 2d) 😡", parse_mode='Markdown', disable_notification=False)
                    return
            await context.bot.ban_chat_member(GROUP_ID, target_id, until_date=int(time.time() + duration) if duration else None)
            with data_lock:
                banned_users[str(target_id)] = time.time() + duration if duration else None
            await update.message.reply_text(f"**✅ USER {target_id} BANNED!** 🚫", parse_mode='Markdown', disable_notification=False)
        else:
            await context.bot.unban_chat_member(GROUP_ID, target_id)
            with data_lock:
                banned_users.pop(str(target_id), None)
            await update.message.reply_text(f"**✅ USER {target_id} UNBANNED!** ✅", parse_mode='Markdown', disable_notification=False)
        log_action(user_id, "ban" if is_ban else "unban", f"Target: {target_id}")
    except Exception as e:
        await update.message.reply_text(f"**❌ ERROR:** {e} 😡", parse_mode='Markdown', disable_notification=False)

async def addall_removeall(update: Update, context: ContextTypes.DEFAULT_TYPE, is_add=True):
    user_id = str(update.effective_user.id)
    if not check_rate_limit(user_id, "addall" if is_add else "removeall"):
        await update.message.reply_text("⏳ Thoda Chill Kar! 5 sec wait kar! 😡", disable_notification=False)
        return
    if user_id not in OVERLORD_IDS:
        await update.message.reply_text("🚫 OVERLORD ONLY! 😡", disable_notification=False)
        await apply_penalty(user_id, "command_abuse", update, context)
        return
    with data_lock:
        if is_add:
            attack_permissions.update(user_profiles.keys())
            await update.message.reply_text("✅ SABKO ATTACK PERMISSION DI! 🔓", disable_notification=False)
            await context.bot.send_message(GROUP_ID, "🔓 SABKO ATTACK PERMISSION MIL GAYI! 💥", disable_notification=False)
        else:
            attack_permissions.clear()
            await update.message.reply_text("✅ SABKI PERMISSION HATA DI! 🔒", disable_notification=False)
            await context.bot.send_message(GROUP_ID, "🔒 SABKI ATTACK PERMISSION HATA DI! 🚫", disable_notification=False)
    log_action(user_id, "addall" if is_add else "removeall", "Affected all users")

async def approve_disapprove(update: Update, context: ContextTypes.DEFAULT_TYPE, is_approve=True):
    user_id = str(update.effective_user.id)
    if not check_rate_limit(user_id, "approve" if is_approve else "disapprove"):
        await update.message.reply_text("⏳ Thoda Chill Kar! 5 sec wait kar! 😡", disable_notification=False)
        return
    if user_id not in OVERLORD_IDS:
        await update.message.reply_text("🚫 OVERLORD ONLY! 😡", disable_notification=False)
        await apply_penalty(user_id, "command_abuse", update, context)
        return
    args = context.args if context.args else []
    if len(args) != 1:
        await update.message.reply_text(f"❌ USAGE: /{'approve' if is_approve else 'disapprove'} <user_id>", disable_notification=False)
        return
    target_id = args[0]
    with data_lock:
        if is_approve:
            approved_users.add(target_id)
            paid_users.add(target_id)
            trial_users.discard(target_id)
            trial_data.pop(target_id, None)
            await update.message.reply_text(f"✅ USER {target_id} KO PAID FEATURES! ✅", disable_notification=False)
            await context.bot.send_message(GROUP_ID, f"✅ USER {target_id} PAID MEMBER BAN GAYA! 🚀", disable_notification=False)
        else:
            approved_users.discard(target_id)
            paid_users.discard(target_id)
            await update.message.reply_text(f"✅ USER {target_id} SE PAID FEATURES HATA DIYE! 🚫", disable_notification=False)
            await context.bot.send_message(GROUP_ID, f"🚫 USER {target_id} SE PAID FEATURES HATA DIYE! 😐", disable_notification=False)
    log_action(user_id, "approve" if is_approve else "disapprove", f"Target: {target_id}")

async def gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if not check_rate_limit(user_id, "gen"):
        await update.message.reply_text("⏳ Thoda Chill Kar! 5 sec wait kar! 😡", disable_notification=False)
        return
    if user_id not in OVERLORD_IDS:
        await update.message.reply_text("🚫 OVERLORD ONLY! 😡", disable_notification=False)
        return
    args = context.args if context.args else []
    if len(args) < 2:
        await update.message.reply_text("❌ USAGE: /gen <duration> <device_limit> [key_name]", disable_notification=False)
        return
    duration, device_limit = args[0], args[1]
    try:
        device_limit = int(device_limit)
    except ValueError:
        await update.message.reply_text("❌ VALID DEVICE LIMIT DO! 😡", disable_notification=False)
        return
    key_name = args[2] if len(args) > 2 else f"KEY_{random.randint(1000, 9999)}"
    current_time = time.time()
    expiry_time = current_time + (int(duration[:-1]) * (3600 if duration.endswith('h') else 86400 if duration.endswith('d') else 30 * 86400))
    with data_lock:
        keys[key_name] = {"duration": duration, "device_limit": device_limit, "devices_used": 0, "expiry_time": expiry_time}
    await update.message.reply_text(f"✅ KEY GENERATED! Key: `{key_name}`, Duration: {duration}, Limit: {device_limit} 🔑", disable_notification=False)
    log_action(user_id, "gen", f"Generated key: {key_name}")

async def redeem_access(update: Update, context: ContextTypes.DEFAULT_TYPE, is_code=False):
    user_id = str(update.effective_user.id)
    if not check_rate_limit(user_id, "redeem" if not is_code else "redeem_code"):
        await update.message.reply_text("⏳ Thoda Chill Kar! 5 sec wait kar! 😡", disable_notification=False)
        return
    args = context.args if context.args else []
    if len(args) != 1:
        await update.message.reply_text(f"❌ USAGE: /{'redeem_code' if is_code else 'redeem'} <{'code' if is_code else 'key_name'}>", disable_notification=False)
        return
    key_name = args[0]
    key_dict = codes if is_code else keys
    with data_lock:
        if key_name not in key_dict:
            await update.message.reply_text(f"❌ INVALID {'CODE' if is_code else 'KEY'}! 😡", disable_notification=False)
            return
        key = key_dict[key_name]
        if key["devices_used"] >= key["device_limit"]:
            await update.message.reply_text(f"❌ {'CODE' if is_code else 'KEY'} MAX DEVICES PE USED! 😡", disable_notification=False)
            return
        if time.time() > key["expiry_time"]:
            del key_dict[key_name]
            await update.message.reply_text(f"❌ {'CODE' if is_code else 'KEY'} EXPIRED! 😡", disable_notification=False)
            return
        key["devices_used"] += 1
        (trial_users if is_code else paid_users).add(user_id)
        await update.message.reply_text(f"✅ {'CODE' if is_code else 'KEY'} REDEEMED! 🚀", disable_notification=False)
    log_action(user_id, "redeem" if not is_code else "redeem_code", f"Redeemed: {key_name}")

async def trail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if not check_rate_limit(user_id, "trail"):
        await update.message.reply_text("**⏳ Thoda Chill Kar!** 5 sec wait kar! 😡", disable_notification=False)
        return
    with data_lock:
        if user_id in trial_users or user_id in paid_users:
            await update.message.reply_text(f"**❌ TU {'TRIAL USER HAI' if user_id in trial_users else 'PAID USER HAI'}!** 😡", parse_mode='Markdown', disable_notification=False)
            return
        code_name = f"TRIAL_{user_id}_{int(time.time())}"
        current_time = time.time()
        codes[code_name] = {"duration": "21d", "device_limit": 1, "devices_used": 0, "expiry_time": current_time + (21 * 24 * 60 * 60), "price": 0}
        trial_users.add(user_id)
        trial_data[user_id] = {"attacks_left": TRIAL_ATTACK_LIMIT, "start_time": current_time}
        days_left = (last_trial_reset + (21 * 24 * 60 * 60) - current_time) // (24 * 60 * 60)
    await update.message.reply_text(
        f"**✅ TRIAL ACCESS!**\nCode: `{code_name}`\n"
        f"**🔹 Attacks Left:** {trial_data[user_id]['attacks_left']} 🕒\n"
        f"**🔹 Days Left:** {days_left} 📅\n"
        f"Activate: /redeem_code {code_name} 🚀", parse_mode='Markdown', disable_notification=False)
    log_action(user_id, "trail", f"Trial code generated: {code_name}")

async def add_remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE, is_add=True):
    user_id = str(update.effective_user.id)
    if not check_rate_limit(user_id, "add" if is_add else "remove"):
        await update.message.reply_text("⏳ Thoda Chill Kar! 5 sec wait kar! 😡", disable_notification=False)
        return
    if user_id not in OVERLORD_IDS:
        await update.message.reply_text("🚫 OVERLORD ONLY! 😡", disable_notification=False)
        return
    args = context.args if context.args else []
    if len(args) != 1:
        await update.message.reply_text(f"❌ USAGE: /{'add' if is_add else 'remove'} <user_id>", disable_notification=False)
        return
    target_id = args[0]
    with data_lock:
        if is_add:
            attack_permissions.add(target_id)
            await update.message.reply_text(f"✅ USER {target_id} KO ATTACK PERMISSION! 🔓", disable_notification=False)
        else:
            attack_permissions.discard(target_id)
            await update.message.reply_text(f"✅ USER {target_id} SE PERMISSION HATA DI! 🔒", disable_notification=False)
    log_action(user_id, "add" if is_add else "remove", f"Target: {target_id}")

async def perform_attack(user_id, target, port, attack_time, context):
    """Simulates a DDoS attack with random success metrics."""
    try:
        await asyncio.sleep(attack_time)  # Simulate attack duration
        with data_lock:
            success_rate = random.randint(80, 100)
            packets = random.randint(1000, 10000)
            handle = user_profiles[user_id]["handle"]
            theme = user_profiles[user_id]["theme"]
            taunt = generate_dynamic_taunt(user_id, theme)
            abusive = random.choice(ABUSIVE_WORDS)
            successful_attacks.setdefault(user_id, []).append({
                "target": target,
                "port": port,
                "time": attack_time,
                "timestamp": datetime.now().isoformat()
            })
            global_attack_leaderboard[user_id] = global_attack_leaderboard.get(user_id, 0) + 1
            # Check achievements
            total_attacks = len(successful_attacks[user_id])
            for achievement, data in ACHIEVEMENTS.items():
                if total_attacks >= data["attacks"] and achievement not in user_profiles[user_id].get("achievements", []):
                    user_profiles[user_id].setdefault("achievements", []).append(achievement)
                    join_points[user_id] = join_points.get(user_id, 0) + data["points"]
                    await context.bot.send_message(
                        chat_id=GROUP_ID,
                        text=MESSAGE_THEMES[theme]["achievement_unlock"]
                            .replace("[handle]", handle)
                            .replace("[achievement]", achievement)
                            .replace("[points]", str(data["points"]))
                            .replace("[abusive]", abusive),
                        parse_mode='Markdown',
                        disable_notification=False
                    )
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=MESSAGE_THEMES[theme]["attack_success"]
                .replace("[handle]", handle)
                .replace("[abusive]", abusive)
                .replace("[taunt]", taunt),
            parse_mode='Markdown',
            disable_notification=False
        )
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=MESSAGE_THEMES[theme]["attack_report"]
                .replace("[target]", target)
                .replace("[port]", str(port))
                .replace("[packets]", str(packets))
                .replace("[success_rate]", str(success_rate))
                .replace("[abusive]", abusive),
            parse_mode='Markdown',
            disable_notification=False
        )
        update_attack_trends(target, port, attack_time)
    except Exception as e:
        logger.error(f"Error in perform_attack for user {user_id}: {e}")
        with data_lock:
            SELF_API_DATA["ai_health"]["errors"] += 1
            save_self_api_data()
        raise

async def attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if not check_rate_limit(user_id, "attack"):
        await update.message.reply_text("⏳ Thoda Chill Kar! 5 sec wait kar! 😡", disable_notification=False)
        return

    # Check Ban, Mute & Profile
    with data_lock:
        if user_id in banned_users and (banned_users[user_id] is None or time.time() < banned_users[user_id]):
            await update.message.reply_text("🚫 BANNED! Tu group se out hai! 😡", disable_notification=False)
            return
        if user_id in muted_users and (muted_users[user_id] is None or time.time() < muted_users[user_id]):
            await update.message.reply_text("🔇 MUTED! Bol nahi sakta! 😡", disable_notification=False)
            return
        if user_id not in user_profiles:
            await update.message.reply_text("❌ PAHLE /start KARO! 😡", disable_notification=False)
            return

    try:
        photos = await update.effective_user.get_profile_photos(limit=1)
        if not photos.photos:
            await update.message.reply_text("❌ PROFILE PIC LAGAO! 😡", disable_notification=False)
            return
    except Exception:
        await update.message.reply_text("❌ PROFILE PIC CHECK FAILED! 😡", disable_notification=False)
        return

    # Check Attack Permission
    with data_lock:
        if user_id not in attack_permissions and user_id not in paid_users and user_id not in trial_users and user_id not in OVERLORD_IDS:
            await update.message.reply_text("❌ ATTACK PERMISSION NHI HAI! 😡", disable_notification=False)
            return

    # Parse Arguments
    args = context.args if context.args else []
    if len(args) != 3:
        await update.message.reply_text("❌ USAGE: /attack <target> <port> <time>", disable_notification=False)
        return
    
    target, port, attack_time = args[0], args[1], args[2]

    # Validate Input
    try:
        port = int(port)
        attack_time = int(attack_time)
        if not (1 <= port <= 65535):
            raise ValueError("Invalid Port Range")
        if attack_time <= 0:
            raise ValueError("Attack Time Must Be Positive")
        if not all(x.isdigit() and 0 <= int(x) <= 255 for x in target.split('.')) or len(target.split('.')) != 4:
            raise ValueError("Invalid IP Address")
    except ValueError as e:
        await update.message.reply_text(f"❌ VALID IP, PORT (1-65535), AUR TIME DO! {e} 😡", disable_notification=False)
        return

    # Check Port Validity
    if int(str(port)[0]) not in VALID_PORT_FIRST_DIGITS:
        await update.message.reply_text("❌ PORT 1, 2, 6, YA 7 SE START HONA CHAHIYE! 😡", disable_notification=False)
        return

    # Determine User Limits
    with data_lock:
        is_overlord = user_id in OVERLORD_IDS
        is_paid = user_id in paid_users
        is_trial = user_id in trial_users
        max_time = MAX_ATTACK_TIME_OVERLORD if is_overlord else MAX_ATTACK_TIME_PAID if is_paid else MAX_ATTACK_TIME_NORMAL
        cooldown_time = OVERLORD_COOLDOWN_TIME if is_overlord else PAID_COOLDOWN_TIME if is_paid else NORMAL_COOLDOWN_TIME
        attack_limit = float('inf') if is_overlord or is_paid else TRIAL_ATTACK_LIMIT if is_trial else NORMAL_ATTACK_LIMIT

        # Check Attack Time Limit
        if attack_time > max_time:
            await update.message.reply_text(f"❌ MAX TIME {max_time}s TAK! 😡", disable_notification=False)
            return

        # Check Cooldown
        last_attack = user_data.get(user_id, {}).get('last_attack', 0)
        if not is_overlord and time.time() - last_attack < cooldown_time:
            remaining = int(cooldown_time - (time.time() - last_attack))
            await update.message.reply_text(f"❌ COOL DOWN! {remaining}s LEFT! 😡", disable_notification=False)
            return

        # Check Attack Limit
        today = datetime.now().date().isoformat()
        attack_counts.setdefault(user_id, {"date": today, "count": 0})
        if attack_counts[user_id]["date"] != today:
            attack_counts[user_id] = {"date": today, "count": 0}
        if attack_counts[user_id]["count"] >= attack_limit:
            await update.message.reply_text(f"❌ DAILY LIMIT ({attack_limit}) KHATAM! 😡", disable_notification=False)
            return

    # Global Attack Lock
    with attack_lock:
        if global_attack_running and not is_overlord:
            await update.message.reply_text("❌ EK ATTACK CHAL RAHA HAI! WAIT KAR! 😡", disable_notification=False)
            return
        global_attack_running = True

    try:
        # Update User Data
        with data_lock:
            user_data.setdefault(user_id, {'attacks': 0, 'last_reset': datetime.now(), 'last_attack': 0})
            user_data[user_id]['last_attack'] = time.time()
            attack_counts[user_id]["count"] += 1
            user_data[user_id]['attacks'] += 1
            save_users()

        # Execute Attack
        await perform_attack(user_id, target, port, attack_time, context)

        # Update Behavior
        log_action(user_id, "attack", f"Target: {target}, Port: {port}, Time: {attack_time}")
        update_user_behavior(user_id, "attacks")

    except Exception as e:
        logger.error(f"Error in attack command for user {user_id}: {e}")
        with data_lock:
            handle = user_profiles.get(user_id, {}).get("handle", "Unknown")
            theme = user_profiles.get(user_id, {}).get("theme", "default")
            abusive = random.choice(ABUSIVE_WORDS)
            SELF_API_DATA["ai_health"]["errors"] += 1
            save_self_api_data()
        await update.message.reply_text(
            MESSAGE_THEMES[theme]["error"]
                .replace("[handle]", handle)
                .replace("[abusive]", abusive),
            parse_mode='Markdown',
            disable_notification=False
        )
    finally:
        with attack_lock:
            global_attack_running = False

async def attackhistory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if not check_rate_limit(user_id, "attackhistory"):
        await update.message.reply_text("⏳ Thoda Chill Kar! 5 sec wait kar! 😡", disable_notification=False)
        return
    if user_id not in user_profiles:
        await update.message.reply_text("❌ PAHLE /start KARO! 😡", disable_notification=False)
        return
    with data_lock:
        attacks = successful_attacks.get(user_id, []) or []
    if not attacks:
        await update.message.reply_text("📜 NO ATTACKS! 😡\nTune abhi tak koi attack nahi kiya.", disable_notification=False)
        return
    history = "**📜 ATTACK HISTORY (Last 5) 📜**\n"
    for attack in attacks[-min(len(attacks), 5):]:
        history += f"🔹 {attack['target']}:{attack['port']}, {attack['time']}s, {attack['timestamp']}\n"
    await update.message.reply_text(history, disable_notification=False)
    log_action(user_id, "attackhistory", "User checked attack history")

async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if not check_rate_limit(user_id, "referral"):
        await update.message.reply_text("⏳ Thoda Chill Kar! 5 sec wait kar! 😡", disable_notification=False)
        return
    if user_id not in user_profiles:
        await update.message.reply_text("❌ PAHLE /start KARO! 😡", disable_notification=False)
        return
    args = context.args if context.args else []
    with data_lock:
        if not args:
            code = f"REF_{random.randint(100, 999)}_{random.randint(1000, 9999)}"
            codes[code] = {"creator": user_id, "used_by": [], "expiry_time": float('inf'), "price": 0}
            await update.message.reply_text(f"🔗 REFERRAL CODE: `{code}`\nDost ko bol: `/referral {code}`", disable_notification=False)
        else:
            code = args[0]
            if code not in codes or user_id in codes[code]["used_by"]:
                await update.message.reply_text("❌ INVALID/USED CODE! 😡", disable_notification=False)
                return
            codes[code]["used_by"].append(user_id)
            join_points[user_id] = join_points.get(user_id, 0) + 5
            user_levels[user_id] = get_user_level(join_points[user_id])
            creator_id = codes[code]["creator"]
            join_points[creator_id] = join_points.get(creator_id, 0) + 10
            user_levels[creator_id] = get_user_level(join_points[creator_id])
            await update.message.reply_text("✅ REFERRAL DONE! Tu +5, Creator +10 points! 🚀", disable_notification=False)
    log_action(user_id, "referral", f"Referral code: {code if args else 'generated'}")
    save_users()

async def inquiry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if not check_rate_limit(user_id, "inquiry"):
        await update.message.reply_text("⏳ Thoda Chill Kar! 5 sec wait kar! 😡", disable_notification=False)
        return
    if user_id not in user_profiles:
        await update.message.reply_text("❌ PAHLE /start KARO! 😡", disable_notification=False)
        return
    args = context.args if context.args else []
    if len(args) < 1:
        await update.message.reply_text("❌ USAGE: /inquiry <question>", disable_notification=False)
        return
    question = " ".join(args)
    try:
        response, can_answer = process_question(question)
    except Exception as e:
        logger.error(f"Error processing inquiry for user {user_id}: {e}")
        response, can_answer = "Kuch galat ho gaya! Overlord ko bolo! 😡", False
    with data_lock:
        handle = user_profiles[user_id]["handle"]
    if can_answer:
        response_msg = MESSAGE_THEMES["default"]["inquiry_response"].replace("[handle]", handle).replace("[question]", question).replace("[response]", response)
        await update.message.reply_text(response_msg, disable_notification=False)
    else:
        forward_msg = MESSAGE_THEMES["default"]["inquiry_forward"].replace("[handle]", handle).replace("[question]", question)
        for overlord_id in OVERLORD_IDS:
            await context.bot.send_message(chat_id=overlord_id, text=forward_msg, disable_notification=False)
        await update.message.reply_text(response, disable_notification=False)
    log_action(user_id, "inquiry", f"Question: {question}")

# Background Tasks
async def global_attack_leaderboard_broadcast(context: ContextTypes.DEFAULT_TYPE):
    with data_lock:
        sorted_attackers = sorted(global_attack_leaderboard.items(), key=lambda x: x[1], reverse=True)[:3]
        top1, top2, top3 = ("N/A", 0), ("N/A", 0), ("N/A", 0)
        if len(sorted_attackers) >= 1:
            top1 = (user_profiles.get(sorted_attackers[0][0], {}).get("handle", "Unknown"), sorted_attackers[0][1])
        if len(sorted_attackers) >= 2:
            top2 = (user_profiles.get(sorted_attackers[1][0], {}).get("handle", "Unknown"), sorted_attackers[1][1])
        if len(sorted_attackers) >= 3:
            top3 = (user_profiles.get(sorted_attackers[2][0], {}).get("handle", "Unknown"), sorted_attackers[2][1])
    await context.bot.send_message(chat_id=GROUP_ID, text=MESSAGE_THEMES["default"]["global_leaderboard"].format(
        top1_handle=top1[0], top1_attacks=top1[1], top2_handle=top2[0], top2_attacks=top2[1], top3_handle=top3[0], top3_attacks=top3[1], abusive=random.choice(ABUSIVE_WORDS)), parse_mode='Markdown', disable_notification=False)

async def daily_rewards(context: ContextTypes.DEFAULT_TYPE):
    current_date = datetime.now().date().isoformat()
    with data_lock:
        for user_id, profile in user_profiles.items():
            if user_id in last_daily_reward and last_daily_reward[user_id] == current_date:
                continue
            last_daily_reward[user_id] = current_date
            points = random.randint(5, 15)
            join_points[user_id] = join_points.get(user_id, 0) + points
            user_levels[user_id] = get_user_level(join_points[user_id])
            try:
                await context.bot.send_message(chat_id=user_id, text=MESSAGE_THEMES["default"]["daily_reward"].format(handle=profile["handle"], points=points), parse_mode='Markdown', disable_notification=False)
            except Exception as e:
                logger.error(f"Error sending daily reward to {user_id}: {e}")
            log_action(user_id, "daily_reward", f"Awarded {points} points")

async def backup_data(context: ContextTypes.DEFAULT_TYPE):
    with data_lock:
        data = {"user_profiles": user_profiles, "join_points": join_points, "successful_attacks": successful_attacks}
        with open("ai_backup.pkl", "wb") as f:
            pickle.dump(data, f)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for overlord_id in OVERLORD_IDS:
        try:
            await context.bot.send_message(chat_id=overlord_id, text=MESSAGE_THEMES["default"]["backup_success"].format(time=current_time), parse_mode='Markdown', disable_notification=False)
        except Exception as e:
            logger.error(f"Error sending backup success to {overlord_id}: {e}")

# Periodic Save Function
def periodic_save():
    while not stop_event.is_set():
        time.sleep(300)
        save_self_api_data()
        save_users()

# Main Function
def main():
    load_self_api_data()
    load_users()
    load_data_on_startup()
    threading.Thread(target=update_ai_health, daemon=True).start()
    threading.Thread(target=periodic_save, daemon=True).start()
    global application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("tutorial", tutorial))
    application.add_handler(CommandHandler("myinfo", myinfo))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("mute", lambda update, context: mute_unmute(update, context, True)))
    application.add_handler(CommandHandler("unmute", lambda update, context: mute_unmute(update, context, False)))
    application.add_handler(CommandHandler("ban", lambda update, context: ban_unban(update, context, True)))
    application.add_handler(CommandHandler("unban", lambda update, context: ban_unban(update, context, False)))
    application.add_handler(CommandHandler("addall", lambda update, context: addall_removeall(update, context, True)))
    application.add_handler(CommandHandler("removeall", lambda update, context: addall_removeall(update, context, False)))
    application.add_handler(CommandHandler("approve", lambda update, context: approve_disapprove(update, context, True)))
    application.add_handler(CommandHandler("disapprove", lambda update, context: approve_disapprove(update, context, False)))
    application.add_handler(CommandHandler("gen", gen))
    application.add_handler(CommandHandler("redeem", lambda update, context: redeem_access(update, context, False)))
    application.add_handler(CommandHandler("redeem_code", lambda update, context: redeem_access(update, context, True)))
    application.add_handler(CommandHandler("trail", trail))
    application.add_handler(CommandHandler("add", lambda update, context: add_remove_user(update, context, True)))
    application.add_handler(CommandHandler("remove", lambda update, context: add_remove_user(update, context, False)))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("attackhistory", attackhistory))
    application.add_handler(CommandHandler("referral", referral))
    application.add_handler(CommandHandler("inquiry", inquiry))
    application.job_queue.run_repeating(auto_reset, interval=3600)
    application.job_queue.run_repeating(auto_reset_trial, interval=3600)
    application.job_queue.run_repeating(check_leaderboard_reset, interval=3600)
    application.job_queue.run_repeating(auto_run_status_health, interval=300)
    application.job_queue.run_repeating(global_attack_leaderboard_broadcast, interval=12*3600)
    application.job_queue.run_repeating(daily_rewards, interval=24*3600)
    application.job_queue.run_repeating(backup_data, interval=15*60)
    application.run_polling()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, lambda sig, frame: (save_data_on_shutdown(), sys.exit(0)))
    signal.signal(signal.SIGTERM, lambda sig, frame: (save_data_on_shutdown(), sys.exit(0)))
    main()