"""Run a deterministic local demo without depending on the public internet."""

from __future__ import annotations

import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class DemoHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/healthy":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"healthy")
        elif self.path == "/moved":
            self.send_response(302)
            self.send_header("Location", "/healthy")
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        return


def run() -> int:
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "src"))
    from oss_link_auditor.cli import main

    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]
    try:
        with tempfile.TemporaryDirectory() as directory:
            sample = Path(directory) / "demo.md"
            sample.write_text(
                "\n".join(
                    [
                        f"[Healthy](http://127.0.0.1:{port}/healthy)",
                        f"[Moved](http://127.0.0.1:{port}/moved)",
                        f"[Broken](http://127.0.0.1:{port}/missing)",
                    ]
                ),
                encoding="utf-8",
            )
            return main([str(sample), "--allow-private", "--markdown"])
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    raise SystemExit(run())
