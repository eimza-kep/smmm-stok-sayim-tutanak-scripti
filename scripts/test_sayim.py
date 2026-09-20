import unittest
import os
import sys
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import server

class TestInventorySystem(unittest.TestCase):
    def setUp(self):
        server.init_db()
        self.conn = sqlite3.connect(server.DB_FILE)
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()
        cur.execute("DELETE FROM inventory_protocols WHERE tracking_code LIKE 'SAYIM-TEST%'")
        self.conn.commit()

    def tearDown(self):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM inventory_protocols WHERE tracking_code LIKE 'SAYIM-TEST%'")
        self.conn.commit()
        self.conn.close()

    def test_database_table_exists(self):
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='inventory_protocols'")
        row = cur.fetchone()
        self.assertIsNotNone(row, "inventory_protocols tablosu oluşturulmuş olmalıdır.")

    def test_protocol_insert_and_retrieve(self):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO inventory_protocols (
                tracking_code, company_title, tax_id, tax_office,
                warehouse_name, count_date, count_type, head_officer,
                count_officer, auditor_name, items_json, total_items,
                status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "SAYIM-TEST-001",
            "Örnek Sanayi A.Ş.",
            "1234567890",
            "Kadıköy V.D.",
            "Merkez Depo",
            "2026-09-20T10:00:00",
            "Dönem Sonu (Yıl Sonu) Genel Envanteri",
            "Ali Vural (Depo Müdürü)",
            "Hasan Can (Memur)",
            "Mehmet Kaya (SMMM)",
            '[{"stock_code":"STK-01","name":"Ürün A","book_qty":100,"phys_qty":98,"unit_cost":50}]',
            1,
            "Tutanak Tanzim Edildi",
            "2026-09-20T11:00:00Z"
        ))
        self.conn.commit()

        cur.execute("SELECT * FROM inventory_protocols WHERE tracking_code = 'SAYIM-TEST-001'")
        record = cur.fetchone()
        self.assertIsNotNone(record)
        self.assertEqual(record["company_title"], "Örnek Sanayi A.Ş.")
        self.assertEqual(record["tax_id"], "1234567890")
        self.assertEqual(record["total_items"], 1)

    def test_protocol_status_update(self):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO inventory_protocols (tracking_code, company_title, status)
            VALUES (?, ?, ?)
        """, ("SAYIM-TEST-002", "Delta Ltd.", "Tutanak Tanzim Edildi"))
        self.conn.commit()

        cur.execute("""
            UPDATE inventory_protocols
            SET status = ?
            WHERE tracking_code = ?
        """, ("SMMM Tarafından Tasdik Edildi", "SAYIM-TEST-002"))
        self.conn.commit()

        cur.execute("SELECT status FROM inventory_protocols WHERE tracking_code = 'SAYIM-TEST-002'")
        row = cur.fetchone()
        self.assertEqual(row["status"], "SMMM Tarafından Tasdik Edildi")

    def test_files_exist(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assertTrue(os.path.exists(os.path.join(base_dir, "index.html")), "index.html bulunamadı")
        self.assertTrue(os.path.exists(os.path.join(base_dir, "admin.html")), "admin.html bulunamadı")
        self.assertTrue(os.path.exists(os.path.join(base_dir, "api.php")), "api.php bulunamadı")

if __name__ == "__main__":
    unittest.main()
