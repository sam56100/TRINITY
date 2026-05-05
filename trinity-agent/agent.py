import requests
from flask import Flask, request, jsonify

TELEGRAM_TOKEN  = "8777643449:AAEFWP7NA3Vp25rKMemnGplgI0zxxQYcSAI"
TELEGRAM_CHAT   = "716888269"
TELEGRAM_URL    = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

app = Flask(__name__)


def send_telegram(text: str) -> bool:
    resp = requests.post(TELEGRAM_URL, json={"chat_id": TELEGRAM_CHAT, "text": text})
    return resp.ok


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    alert_type = data.get("type", "")

    if alert_type == "TRINITY_LONG":
        symbol  = data.get("symbol", "EURUSD")
        message = f"🟢 TRINITY LONG — {symbol} — Va check le graph"
    elif alert_type == "TRINITY_SHORT":
        symbol  = data.get("symbol", "EURUSD")
        message = f"🔴 TRINITY SHORT — {symbol} — Va check le graph"
    else:
        return jsonify({"status": "ignored", "type": alert_type}), 200

    ok = send_telegram(message)
    status = "sent" if ok else "telegram_error"
    return jsonify({"status": status, "type": alert_type}), 200 if ok else 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
