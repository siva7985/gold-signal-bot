import os, requests, datetime, yfinance as yf

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID")

def get_gold_price():
    ticker = yf.Ticker("GC=F")       # Gold Futures (more reliable)
    data = ticker.history(period="1d", interval="30m")
    if data.empty:
        return None
    last = data.iloc[-1]
    return float(last["Close"])

def generate_signal(price):
    # Simple logic (example): compare current price with 20-period average
    ticker = yf.Ticker("GC=F")       # Gold Futures (more reliable)
    data = ticker.history(period="5d", interval="30m")
    if len(data) < 20:
        return "No Signal"
    sma20 = data["Close"].tail(20).mean()
    
    if price > sma20:
        return f"📈 BUY (Price {price:.2f} > SMA20 {sma20:.2f})"
    elif price < sma20:
        return f"📉 SELL (Price {price:.2f} < SMA20 {sma20:.2f})"
    else:
        return f"⚖️ HOLD (Price {price:.2f} ≈ SMA20 {sma20:.2f})"

def build_message():
    now_utc = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    price = get_gold_price()
    if price is None:
        return f"🟡 GOLD SIGNAL\nTime: {now_utc}\n⚠️ Could not fetch price."
    signal = generate_signal(price)
    return f"🟡 GOLD SIGNAL\nTime: {now_utc}\nPrice: {price:.2f}\nSignal: {signal}"

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    r = requests.post(url, json=payload, timeout=15)
    r.raise_for_status()

if __name__ == "__main__":
    msg = build_message()
    send_telegram(msg)
