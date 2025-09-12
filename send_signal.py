import os, requests, datetime, yfinance as yf, time 

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") 
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ================== FETCH GOLD PRICE ==================
def get_gold_price():
    symbols = ["GC=F", "XAUUSD=X", "XAU=X"]  # GC=F is most reliable
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="5m")
            if not data.empty:
                last = data.iloc[-1]
                print(f"DEBUG: Using {symbol}, price={last['Close']}")
                return float(last["Close"])
        except Exception as e:
            print(f"⚠️ Failed {symbol}: {e}")
    return None

# ================== TRADING SIGNAL ==================
def generate_signal(price):
    ticker = yf.Ticker("GC=F")
    data = ticker.history(period="1d", interval="5m")
    if data.empty or len(data) < 5:
        return "No Signal"

    sma5 = data["Close"].tail(5).mean()
    last_close = data["Close"].iloc[-1]
    
    if price > sma5:
        return f"📈 BUY (Price {price:.2f} > SMA5 {sma5:.2f})"
    elif price < sma5:
        return f"📉 SELL (Price {price:.2f} < SMA5 {sma5:.2f})"
    else:
        return f"⚖️ HOLD (Price {price:.2f} ≈ SMA5 {sma5:.2f})"

# ================== MESSAGE BUILDER ==================
def build_message():
    now_utc = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    price = get_gold_price()
    if price is None:
        return f"🟡 GOLD SIGNAL\n⏰ {now_utc}\n⚠️ Could not fetch price."

    signal = generate_signal(price)

    tp_level = round(price * 1.001, 2)
    sl_level = round(price * 0.999, 2)

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

# ================== SEND TO TELEGRAM ==================
def send_telegram(text, retries=3):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}

    for attempt in range(1, retries + 1):
        try:
            r = requests.post(url, json=payload, timeout=10)  # shorter timeout
            r.raise_for_status()
            print("✅ Telegram message sent successfully")
            return True
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Telegram send failed (attempt {attempt}): {e}")
            time.sleep(attempt * 5)  # exponential backoff

    raise Exception("❌ Failed to send Telegram message after retries")

# ================== MAIN ==================
if __name__ == "__main__":
    msg = build_message()
    send_telegram(msg)
