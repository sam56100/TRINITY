import json
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer

TELEGRAM_TOKEN = "8777643449:AAEFWP7NA3Vp25rKMemnGplgI0zxxQYcSAI"
TELEGRAM_CHAT  = "716888269"
TELEGRAM_URL   = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"


def send_telegram(text: str) -> bool:
    resp = requests.post(TELEGRAM_URL, json={"chat_id": TELEGRAM_CHAT, "text": text})
    return resp.ok


class Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        print(f"[{self.address_string()}] {fmt % args}")

    def _respond(self, code: int, body: dict):
        payload = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(payload))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path == "/health":
            self._respond(200, {"status": "ok"})
        else:
            self._respond(404, {"status": "not_found"})

    def do_POST(self):
        if self.path != "/webhook":
            self._respond(404, {"status": "not_found"})
            return

        length = int(self.headers.get("Content-Length", 0))
        raw    = self.rfile.read(length)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            self._respond(400, {"status": "bad_json"})
            return

        alert_type = data.get("type", "")
        symbol     = data.get("symbol", "EURUSD")

        if alert_type == "TRINITY_LONG":
            message = f"🟢 TRINITY LONG — {symbol} — Va check le graph"
        elif alert_type == "TRINITY_SHORT":
            message = f"🔴 TRINITY SHORT — {symbol} — Va check le graph"
        else:
            self._respond(200, {"status": "ignored", "type": alert_type})
            return

        ok = send_telegram(message)
        print(f"  → Telegram {'OK' if ok else 'ERREUR'} : {message}")
        self._respond(200 if ok else 500, {"status": "sent" if ok else "telegram_error"})


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8080), Handler)
    print("TRINITY Agent démarré sur http://0.0.0.0:8080")
    print("  POST /webhook  — reçoit les alertes TradingView")
    print("  GET  /health   — vérification")
    server.serve_forever()
