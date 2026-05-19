#!/usr/bin/env python3
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import random

import db
from pages import scenario as scenario_page
from pages import words as words_page
from pages import flashcards as flashcards_page

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(fmt % args)

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html, status=200):
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path == "/api/add-word":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            hanzi = body.get("hanzi", "").strip()
            if not hanzi:
                self._send_json({"status": "error", "message": "no hanzi"}, 400)
                return
            if db.word_exists(hanzi):
                self._send_json({"status": "exists"})
                return
            try:
                data = db.generate_word_data(hanzi)
                db.save_word(hanzi, data["pinyin"], data["examples"])
                self._send_json({"status": "added"})
            except Exception as e:
                self._send_json({"status": "error", "message": str(e)}, 500)
        elif self.path == "/api/import-words":
            try:
                inserted, skipped = db.import_words_json()
                self._send_json({"status": "ok", "inserted": inserted, "skipped": skipped})
            except Exception as e:
                self._send_json({"status": "error", "message": str(e)}, 500)
        elif self.path == "/api/delete-word":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            hanzi = body.get("hanzi", "").strip()
            if not hanzi:
                self._send_json({"status": "error", "message": "no hanzi"}, 400)
                return
            try:
                with db.get_conn() as conn, conn.cursor() as cur:
                    cur.execute(
                        "UPDATE words SET deleted_at = NOW() WHERE hanzi = %s AND deleted_at IS NULL RETURNING id",
                        (hanzi,),
                    )
                    updated = cur.fetchone()
                    conn.commit()
                if updated:
                    self._send_json({"status": "deleted"})
                else:
                    self._send_json({"status": "not_found"}, 404)
            except Exception as e:
                self._send_json({"status": "error", "message": str(e)}, 500)
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)

        if parsed.path.startswith("/audio/"):
            audio_path = os.path.join(AUDIO_DIR, os.path.basename(parsed.path))
            if not os.path.exists(audio_path):
                self.send_response(404)
                self.end_headers()
                return
            size = os.path.getsize(audio_path)
            range_header = self.headers.get("Range")
            if range_header:
                start, end = range_header.replace("bytes=", "").split("-")
                start = int(start)
                end = int(end) if end else size - 1
                length = end - start + 1
                with open(audio_path, "rb") as f:
                    f.seek(start)
                    data = f.read(length)
                self.send_response(206)
                self.send_header("Content-Type", "audio/mp4")
                self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
                self.send_header("Content-Length", str(length))
                self.send_header("Accept-Ranges", "bytes")
                self.end_headers()
                self.wfile.write(data)
            else:
                with open(audio_path, "rb") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "audio/mp4")
                self.send_header("Content-Length", str(size))
                self.send_header("Accept-Ranges", "bytes")
                self.end_headers()
                self.wfile.write(data)
            return

        if parsed.path == "/words":
            self._send_html(words_page.render(db.load_words()))
            return

        if parsed.path == "/flashcards":
            all_words = db.load_words()
            sample = random.sample(all_words, min(10, len(all_words)))
            self._send_html(flashcards_page.render(sample))
            return

        scenarios = scenario_page.list_scenarios()
        scenario_name = qs.get("scenario", [scenarios[0]])[0]
        show_pinyin = qs.get("pinyin", ["0"])[0] != "0"
        show_translation = qs.get("translation", ["0"])[0] != "0"

        try:
            words = scenario_page.load_scenario(scenario_name)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            return

        self._send_html(scenario_page.render(scenario_name, words, show_pinyin, show_translation))


if __name__ == "__main__":
    port = 8000
    server = HTTPServer(("", port), Handler)
    print(f"http://localhost:{port}")
    server.serve_forever()
