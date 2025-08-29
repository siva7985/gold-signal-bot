import os, requests, datetime, yfinance as yf, time

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID")

FH_KEY = os.getenv("FINNHUB_KEY")

def get_gold_price():
    if not FH_KEY:
        print("⚠️ No Finnhub API key found. Did you set FINNHUB_KEY in GitHub Secrets?")
        return None

    url = f"https://finnhub.io/api/v1/quote?symbol=OANDA:XAU_USD&token={FH_KEY}"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        print("DEBUG RESPONSE:", data)

        if "c" not in data or data["c"] == 0:
            print("⚠️ Invalid price received")
            return None

        return float(data["c"])  # current price
    except Exception as e:
        print("⚠️ Error fetching price:", e)
        return None

def generate_signal(price, symbol="XAUUSD=X"):
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1d", interval="5m")
    if len(data) < 5:
        return "No Signal"

    # Hybrid logic: SMA5 + last close
    sma5 = data["Close"].tail(5).mean()
    last_close = data["Close"].iloc[-1]

    if last_close > sma5:
        return f"📈 BUY (Price {last_close:.2f} > SMA5 {sma5:.2f})"
    elif last_close < sma5:
        return f"📉 SELL (Price {last_close:.2f} < SMA5 {sma5:.2f})"
    else:
        return f"⚖️ HOLD (Price {last_close:.2f} ≈ SMA5 {sma5:.2f})"

def build_message():
    now_utc = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    price = get_gold_price()
    if price is None:
        return f"🟡 GOLD SIGNAL\n⏰ {now_utc}\n⚠️ Could not fetch price."

    signal = generate_signal(price)

    # Dynamic TP/SL ±0.1% of current price
    tp_level = round(price * 1.001, 2)  # +0.1%
    sl_level = round(price * 0.999, 2)  # -0.1%

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

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}

    for attempt in range(3):
        try:
            r = requests.post(url, json=payload, timeout=30)
            r.raise_for_status()
            print("✅ Telegram message sent successfully")
            return True
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Telegram send failed (attempt {attempt+1}): {e}")
            time.sleep(5)

    raise Exception("❌ Failed to send Telegram message after 3 attempts")

if __name__ == "__main__":
    msg = build_message()
    send_telegram(msg)
