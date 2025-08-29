import os, requests, datetime, time

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID")
API_KEY   = os.getenv("METALPRICE_KEY")   # Metalprice API key

# ================== FETCH GOLD PRICE ==================
def get_gold_price():
    try:
        url = f"https://api.metalpriceapi.com/v1/latest?api_key={API_KEY}&base=XAU&currencies=USD"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        print("DEBUG:", data)  # log raw response

        if not data.get("success"):
            print("⚠️ Metalprice API failed")
            return None

        price = data["rates"].get("USD")
        if not price or price <= 0:
            print("⚠️ Invalid price from Metalprice API")
            return None

        return float(price)

    except Exception as e:
        print("⚠️ Error fetching price:", e)
        return None

# ================== TRADING SIGNAL ==================
def generate_signal(price):
    # Simple logic: Compare current price to 5-period SMA (mocked with ±1%)
    sma5 = price * 1.001  # pretend SMA5 is 0.1% higher for demo
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

    # Dynamic TP/SL ±0.1% of current price
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

# ================== MAIN ==================
if __name__ == "__main__":
    msg = build_message()
    send_telegram(msg)
