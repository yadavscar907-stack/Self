import os
import time
import threading
import json
import random
import requests
from flask import Flask
from instagrapi import Client

# --- ENV CONFIG ---
SESSION_ID = os.getenv("SESSION_ID")
GROUP_IDS = os.getenv("GROUP_IDS", "")
GROUP_NAMES = os.getenv("GROUP_NAMES", "")
MESSAGE_TEXT = os.getenv("MESSAGE_TEXT", "Hello 👋")
SELF_URL = os.getenv("SELF_URL", "")
PORT = int(os.getenv("PORT", 10000))

# --- RANDOM EMOJIS LIST ---
EMOJIS = ["🔥","😎","🐍","🤭","🐶","🐷","🗿","💀","🎀","😠","🌪","💫","🥶","😔"]

def rand_emoji():
    return random.choice(EMOJIS)

# --- HUMAN LIKE DELAY ---
def human_delay():
    # Small pause (human typing effect)
    time.sleep(random.uniform(1.5, 3.5))

    # Normal delay between 7–23 sec
    delay = random.randint(7, 23)

    # 1 out of 6 times → long pause (40–120 sec)
    if random.random() < 0.16:
        delay = random.randint(40, 120)

    print(f"⏳ Human-like delay: {delay}s")
    time.sleep(delay)

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Bot running — IG human-like mode active"

# --- MESSAGE SENDER ---
def send_message(cl, gid, msg):
    try:
        final_msg = f"{msg} {rand_emoji()}"
        cl.direct_send(final_msg, thread_ids=[int(gid)])
        print(f"✅ Sent message to {gid} ➜ {final_msg}")
        return True
    except Exception as e:
        print(f"⚠ IG Error sending to {gid}: {e}")
        return False

# --- MESSAGE LOOP ---
def message_loop(cl, gid, gname):
    while True:
        print(f"\n🚀 Sending messages to {gname or gid}")

        ok = send_message(cl, gid, MESSAGE_TEXT)

        if not ok:
            print("⚠ IG blocked — waiting 5 minutes...")
            time.sleep(300)
        else:
            # Use human-like delay
            human_delay()

# --- NAME CHANGER ---
def name_changer(cl, gids, gnames):
    while True:
        for i, gid in enumerate(gids):
            base = gnames[i] if i < len(gnames) else None
            if not base:
                continue

            new_title = f"{base}{rand_emoji()}"

            try:
                variables = {"thread_fbid": gid, "new_title": new_title}
                payload = {"doc_id": "29088580780787855", "variables": json.dumps(variables)}
                resp = cl.private.post("https://www.instagram.com/api/graphql/", data=payload)

                if resp.status_code == 200:
                    print(f"✨ Name changed → {new_title}")
                else:
                    print(f"⚠ Name change failed: {resp.text[:100]}")
            except Exception as e:
                print(f"⚠ Error renaming {gid}: {e}")

        print("⏳ Next name change in 4–7 minutes...\n")
        time.sleep(random.randint(240, 420))

# --- SELF PING ---
def self_ping():
    while True:
        if SELF_URL:
            try:
                requests.get(SELF_URL, timeout=10)
                print("🔁 Self ping OK")
            except Exception as e:
                print(f"⚠ Self ping error: {e}")
        time.sleep(60)

# --- ANTI SLEEP ---
def render_ping():
    while True:
        try:
            if SELF_URL:
                requests.get(SELF_URL)
                print("🔁 Render anti-sleep ping")
        except:
            print("⚠ Render ping failed")
        time.sleep(50)

# --- WATCHDOG ---
def keepalive_checker():
    while True:
        print("🧠 Keepalive check...")
        try:
            requests.get("https://google.com", timeout=5)
            print("🌍 Internet OK")
        except:
            print("⚠ Internet unstable")
        time.sleep(90)

def main():
    if not SESSION_ID or not GROUP_IDS:
        print("❌ Missing SESSION_ID or GROUP_IDS!")
        return

    gids = [g.strip() for g in GROUP_IDS.split(",") if g.strip()]
    gnames = [n.strip() for n in GROUP_NAMES.split(",")] if GROUP_NAMES else []

    cl = Client()
    try:
        cl.login_by_sessionid(SESSION_ID)
        print("✅ Logged in successfully")
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return

    for i, gid in enumerate(gids):
        gname = gnames[i] if i < len(gnames) else ""
        threading.Thread(target=message_loop, args=(cl, gid, gname), daemon=True).start()

    threading.Thread(target=name_changer, args=(cl, gids, gnames), daemon=True).start()
    threading.Thread(target=self_ping, daemon=True).start()
    threading.Thread(target=render_ping, daemon=True).start()
    threading.Thread(target=keepalive_checker, daemon=True).start()

    app.run(host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    main()
