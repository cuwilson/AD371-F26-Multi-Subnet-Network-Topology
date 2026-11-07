import json
import os
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

SERVER_ID = os.getenv("SERVER_ID") or socket.gethostname()
PORT = int(os.getenv("PORT", "3000"))

HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Network Load Balancer Demo</title>
  <link rel="icon" href="data:,">
  <style>
    body { font: 16px system-ui, sans-serif; margin: 10vh auto; padding: 0 1rem;
           max-width: 640px; background: #f5f8fc; color: #183047; }
    main { background: white; border-radius: 16px; padding: 2rem;
           box-shadow: 0 6px 24px #1232; }
    strong { color: #246b99; }
    button { background: #246b99; color: white; border: 0; border-radius: 8px;
             padding: .8rem 1.2rem; cursor: pointer; }
    pre { background: #edf3f8; padding: 1rem; border-radius: 8px; overflow: auto; }
  </style>
</head>
<body><main>
  <h1>Network Load Balancer Demo</h1>
  <p>This page was served by <strong>__SERVER_ID__</strong>.</p>
  <p>Use the button to make new requests through the load balancer.</p>
  <button onclick="check()">Send test request</button>
  <pre id="output">Click to test...</pre>
  <script>
    async function check() {
      const res = await fetch('/api/instance', {cache: 'no-store'});
      document.getElementById('output').textContent =
        JSON.stringify(await res.json(), null, 2);
    }
  </script>
</main></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def respond(self, status, payload, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/healthz":
            self.respond(200, b'{"status":"ok"}', "application/json")
        elif path == "/api/instance":
            payload = json.dumps({"server_id": SERVER_ID, "hostname": socket.gethostname()}).encode()
            self.respond(200, payload, "application/json")
        elif path == "/":
            payload = HTML.replace("__SERVER_ID__", SERVER_ID).encode()
            self.respond(200, payload, "text/html; charset=utf-8")
        else:
            self.respond(404, b'{"error":"not found"}', "application/json")


if __name__ == "__main__":
    print(f"Starting {SERVER_ID} on port {PORT}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
