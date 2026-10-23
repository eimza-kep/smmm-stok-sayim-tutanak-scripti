import unittest
import os
import sys
import sqlite3

# Ensure parent directory and scripts directory are in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import server
from eirsaliye_mutabakat_engine import reconcile_inventory_with_eirsaliye, parse_ubl_eirsaliye_xml

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

    def test_table_has_barcode_and_eirsaliye_columns(self):
        cur = self.conn.cursor()
        cur.execute("PRAGMA table_info(inventory_protocols)")
        columns = [row["name"] for row in cur.fetchall()]
        self.assertIn("barcode_count_used", columns)
        self.assertIn("eirsaliye_matched", columns)
        self.assertIn("eirsaliye_no", columns)
        self.assertIn("reconciliation_summary", columns)

    def test_protocol_insert_and_retrieve_with_features(self):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO inventory_protocols (
                tracking_code, company_title, tax_id, tax_office,
                warehouse_name, count_date, count_type, head_officer,
                count_officer, auditor_name, items_json, total_items,
                status, created_at,
                barcode_count_used, eirsaliye_matched, eirsaliye_no,
                reconciliation_summary
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            "2026-09-20T11:00:00Z",
            1,
            1,
            "GIB2026-IRS-000456",
            "e-İrsaliye ile tam mutabık"
        ))
        self.conn.commit()

        cur.execute("SELECT * FROM inventory_protocols WHERE tracking_code = 'SAYIM-TEST-001'")
        record = cur.fetchone()
        self.assertIsNotNone(record)
        self.assertEqual(record["company_title"], "Örnek Sanayi A.Ş.")
        self.assertEqual(record["barcode_count_used"], 1)
        self.assertEqual(record["eirsaliye_matched"], 1)
        self.assertEqual(record["eirsaliye_no"], "GIB2026-IRS-000456")

    def test_eirsaliye_reconciliation_engine(self):
        counted = [
            {"stock_code": "STK-001", "name": "A4 Fotokopi Kağıdı", "book_qty": 100, "phys_qty": 95, "unit_cost": 250.0},
            {"stock_code": "STK-002", "name": "Toner Kartuş", "book_qty": 40, "phys_qty": 42, "unit_cost": 850.0},
            {"stock_code": "STK-003", "name": "Klasör Dosya", "book_qty": 50, "phys_qty": 50, "unit_cost": 40.0}
        ]
        eirsaliye_items = [
            {"stock_code": "STK-001", "name": "A4 Fotokopi Kağıdı", "quantity": 100},
            {"stock_code": "STK-002", "name": "Toner Kartuş", "quantity": 40},
            {"stock_code": "STK-003", "name": "Klasör Dosya", "quantity": 50}
        ]

        rec = reconcile_inventory_with_eirsaliye(counted, eirsaliye_items, "GIB2026-IRS-001")
        self.assertFalse(rec["is_full_reconciled"])
        self.assertEqual(rec["total_shortage_qty"], 5)  # 100 - 95 = 5 noksan
        self.assertEqual(rec["total_surplus_qty"], 2)   # 42 - 40 = 2 fazla
        self.assertEqual(rec["total_shortage_amount"], 1250.0) # 5 * 250
        self.assertEqual(rec["total_surplus_amount"], 1700.0)  # 2 * 850
        self.assertIn("197", rec["accounting_note"])
        self.assertIn("397", rec["accounting_note"])

    def test_parse_ubl_eirsaliye_xml(self):
        sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <DespatchAdvice xmlns="urn:oasis:names:specification:ubl:schema:xsd:DespatchAdvice-2">
            <DespatchLine>
                <ID>1</ID>
                <DeliveredQuantity unitCode="C62">150.00</DeliveredQuantity>
                <Item>
                    <Name>Lojistik Sevk Malzemesi X</Name>
                </Item>
            </DespatchLine>
        </DespatchAdvice>"""

        items = parse_ubl_eirsaliye_xml(sample_xml)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["quantity"], 150.0)
        self.assertEqual(items[0]["name"], "Lojistik Sevk Malzemesi X")

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
        self.assertTrue(os.path.exists(os.path.join(base_dir, "server.py")), "server.py bulunamadı")
        self.assertTrue(os.path.exists(os.path.join(base_dir, "api.php")), "api.php bulunamadı")
        self.assertTrue(os.path.exists(os.path.join(base_dir, "scripts", "eirsaliye_mutabakat_engine.py")), "eirsaliye_mutabakat_engine.py bulunamadı")

if __name__ == "__main__":
    unittest.main()
