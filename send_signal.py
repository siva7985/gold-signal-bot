import os, requests, datetime, yfinance as yf

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID")

def get_gold_price():
    ticker = yf.Ticker("GC=F")       # Gold Futures (more reliable)
    data = ticker.history(period="1d", interval="5m")
    if data.empty:
        return None
    last = data.iloc[-1]
    return float(last["Close"])

def generate_signal(price):
    ticker = yf.Ticker("GC=F")
    data = ticker.history(period="1d", interval="5m")
    if len(data) < 2:
        return "No Signal"

    last_close = data["Close"].iloc[-1]
    prev_close = data["Close"].iloc[-2]

    if last_close > prev_close:
        return f"📈 BUY (Last {last_close:.2f} > Prev {prev_close:.2f})"
    elif last_close < prev_close:
        return f"📉 SELL (Last {last_close:.2f} < Prev {prev_close:.2f})"
    else:
        return f"⚖️ HOLD (Last {last_close:.2f} ≈ Prev {prev_close:.2f})"

def build_message():
    now_utc = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    price = get_gold_price()
    if price is None:
        return f"🟡 GOLD SIGNAL\n⏰ {now_utc}\n⚠️ Could not fetch price."
    
    signal = generate_signal(price)

    # Example TP/SL levels (static, just for formatting demo)
    tp_level = round(price + 5, 2)   # take profit = +5
    sl_level = round(price - 5, 2)   # stop loss = -5

    return (
        "━━━━━━━━━━━━━━━━━━━\n"
        "📊 GOLD TRADING SIGNAL\n"
        f"⏰ Time: {now_utc}\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Price: {price:.2f}\n"
        f"📌 Signal: {signal}\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 TP: {tp_level}\n"
        f"🛑 SL: {sl_level}\n"
        "━━━━━━━━━━━━━━━━━━━"
    )
    
import time

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}

    for attempt in range(3):  # try up to 3 times
        try:
            r = requests.post(url, json=payload, timeout=30)
            r.raise_for_status()
            print("✅ Telegram message sent successfully")
            return True
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Telegram send failed (attempt {attempt+1}): {e}")
            time.sleep(5)  # wait 5s before retry
    
    raise Exception("❌ Failed to send Telegram message after 3 attempts")


if __name__ == "__main__":
    msg = build_message()
    send_telegram(msg)
