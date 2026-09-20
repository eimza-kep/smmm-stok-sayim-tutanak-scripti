import http.server
import socketserver
import json
import sqlite3
import os
import sys
import random
from urllib.parse import urlparse

PORT = 8088
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stok_sayim.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventory_protocols (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_code TEXT UNIQUE,
            company_title TEXT,
            tax_id TEXT,
            tax_office TEXT,
            warehouse_name TEXT,
            count_date TEXT,
            count_type TEXT,
            head_officer TEXT,
            count_officer TEXT,
            auditor_name TEXT,
            items_json TEXT,
            total_items INTEGER,
            status TEXT DEFAULT 'Tutanak Tanzim Edildi',
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

class InventoryHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            self.send_file("index.html", "text/html; charset=utf-8")
        elif path in ("/admin", "/admin.html"):
            self.send_file("admin.html", "text/html; charset=utf-8")
        elif path == "/health":
            self.send_json({"status": "ok", "app": "smmm-stok-sayim-tutanak-scripti", "port": PORT})
        elif path == "/api/sayimlar":
            self.handle_get_protocols()
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/sayim-kaydet":
            self.handle_create_protocol()
        elif path == "/api/durum-guncelle":
            self.handle_update_status()
        else:
            self.send_error(404, "Endpoint not found")

    def send_file(self, filename, content_type):
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        if not os.path.exists(filepath):
            self.send_error(404, f"File {filename} not found")
            return
        with open(filepath, "rb") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def handle_create_protocol(self):
        length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(length)
        try:
            data = json.loads(post_data.decode("utf-8"))
            tracking_code = data.get("tracking_code") or f"SAYIM-2026-{random.randint(1000, 9999)}"

            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO inventory_protocols (
                    tracking_code, company_title, tax_id, tax_office,
                    warehouse_name, count_date, count_type, head_officer,
                    count_officer, auditor_name, items_json, total_items,
                    status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tracking_code,
                data.get("company_title", ""),
                data.get("tax_id", ""),
                data.get("tax_office", ""),
                data.get("warehouse_name", ""),
                data.get("count_date", ""),
                data.get("count_type", ""),
                data.get("head_officer", ""),
                data.get("count_officer", ""),
                data.get("auditor_name", ""),
                data.get("items_json", "[]"),
                int(data.get("total_items", 0)),
                data.get("status", "Tutanak Tanzim Edildi"),
                data.get("created_at", "")
            ))
            conn.commit()
            conn.close()

            self.send_json({"status": "success", "tracking_code": tracking_code})
        except Exception as e:
            self.send_json({"status": "error", "message": str(e)}, status=500)

    def handle_get_protocols(self):
        try:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM inventory_protocols ORDER BY id DESC")
            rows = [dict(r) for r in cur.fetchall()]
            conn.close()
            self.send_json(rows)
        except Exception as e:
            self.send_json({"status": "error", "message": str(e)}, status=500)

    def handle_update_status(self):
        length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(length)
        try:
            data = json.loads(post_data.decode("utf-8"))
            tracking_code = data.get("tracking_code")
            new_status = data.get("status")

            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            cur.execute("UPDATE inventory_protocols SET status = ? WHERE tracking_code = ?", (new_status, tracking_code))
            conn.commit()
            conn.close()

            self.send_json({"status": "success", "updated": tracking_code})
        except Exception as e:
            self.send_json({"status": "error", "message": str(e)}, status=500)

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", PORT))
    print(f"🚀 Stok Sayim ve Envanter Portali Baslatildi: http://localhost:{port}")
    print(f"📋 SMMM Yonetim Paneli: http://localhost:{port}/admin")
    with socketserver.TCPServer(("", port), InventoryHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nSunucu kapatildi.")
