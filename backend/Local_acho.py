# שמור כקובץ local_echo.py והריץ: python local_echo.py
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class LocalEchoHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/echo":
            self.send_response(404); self.end_headers(); return
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length > 0 else b""
        try:
            body = json.loads(raw.decode("utf-8")) if raw else None
        except Exception:
            body = raw.decode("utf-8", errors="replace")
        resp = json.dumps({"received": body, "ok": True}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(resp)))
        self.end_headers()
        self.wfile.write(resp)

if __name__ == "__main__":
    print("Listening on http://127.0.0.1:8000/echo (POST only)")
    HTTPServer(("127.0.0.1", 8000), LocalEchoHandler).serve_forever()