import os
import json
import random
from flask import Flask
from instagrapi import Client

# --- ENV CONFIG ---
SESSION_ID = os.getenv("SESSION_ID")
GROUP_IDS = os.getenv("GROUP_IDS", "")
GROUP_NAMES = os.getenv("GROUP_NAMES", "")
MESSAGE_TEXT = os.getenv("MESSAGE_TEXT", "Hello 👋")
PORT = int(os.getenv("PORT", 10000))

# --- RANDOM EMOJIS ---
EMOJIS = ["🔥","😎","🐍","🤭","🐶","🐷","🗿","💀","🎀","😠","🌪","💫","🥶","😔"]

def rand_emoji():
    return random.choice(EMOJIS)

# --- FLASK APP ---
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Bot ready — waiting for ping trigger"

# --- LOGIN ---
cl = Client()
try:
    cl.login_by_sessionid(SESSION_ID)
    print("✅ Logged in successfully")
except Exception as e:
    print("❌ Login failed:", e)

@app.route("/ping")
def ping_trigger():
    print("\n🔔 PING RECEIVED — Starting actions...\n")

    gids = [g.strip() for g in GROUP_IDS.split(",") if g.strip()]
    gnames = [n.strip() for n in GROUP_NAMES.split(",")] if GROUP_NAMES else []

    # --- SEND MESSAGES ---
    for i, gid in enumerate(gids):
        msg = MESSAGE_TEXT + rand_emoji()
        try:
            cl.direct_send(msg, thread_ids=[int(gid)])
            print(f"📩 Sent message to {gid}: {msg}")
        except Exception as e:
            print(f"⚠ Error sending to {gid}: {e}")

    # --- CHANGE NAMES ---
    for i, gid in enumerate(gids):
        base = gnames[i] if i < len(gnames) else None
        if not base:
            continue

        new_title = base + rand_emoji()

        try:
            variables = {"thread_fbid": gid, "new_title": new_title}
            payload = {"doc_id": "29088580780787855", "variables": json.dumps(variables)}
            resp = cl.private.post("https://www.instagram.com/api/graphql/", data=payload)

            if resp.status_code == 200:
                print(f"✨ Name changed ➜ {new_title}")
            else:
                print(f"⚠ Name change failed: {resp.text[:120]}")
        except Exception as e:
            print(f"⚠ Error name changing {gid}: {e}")

    print("\n✅ PING ROUND COMPLETE\n")
    return "Ping OK — Messages + Name Change Done"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
