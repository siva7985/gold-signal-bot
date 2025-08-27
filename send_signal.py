import os, requests, datetime

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID")

def build_message():
    # Right now, just a simple placeholder message with timestamp.
    # Later, we can add real gold signal logic here.
    now_utc = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    return f"🟡 GOLD SIGNAL (auto)\nTime: {now_utc}\nSignal: BUY/SELL ?"

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    r = requests.post(url, json=payload, timeout=15)
    r.raise_for_status()

if __name__ == "__main__":
    msg = build_message()
    send_telegram(msg)
