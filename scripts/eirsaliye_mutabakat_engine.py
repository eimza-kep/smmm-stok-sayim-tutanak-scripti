# -*- coding: utf-8 -*-
"""
eirsaliye_mutabakat_engine.py
-----------------------------
GİB e-İrsaliye Sevk Kalemleri ile Fiili Stok Sayım Sonuçlarını
Otomatik Karşılaştırma, Fire/Fark Tespiti ve VUK m.186 Mutabakat Motoru.
"""

import sys
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def reconcile_inventory_with_eirsaliye(
    counted_items: List[Dict[str, Any]],
    eirsaliye_items: List[Dict[str, Any]],
    irsaliye_no: Optional[str] = "GIB2026000001234"
) -> Dict[str, Any]:
    """
    Fiili sayım kalemleri ile resmi e-İrsaliye sevk miktarlarını eşleştirir.
    Eksiklik (197 Noksanlar) ve Fazlalık (397 Fazlalar) analizini çıkarır.
    """
    irsaliye_map = {}
    for irs in eirsaliye_items:
        key = (irs.get("stock_code") or irs.get("barcode") or irs.get("name") or "").strip().lower()
        if key:
            irsaliye_map[key] = irs

    reconciled_rows = []
    total_shortage_qty = 0
    total_surplus_qty = 0
    total_shortage_amount = 0.0
    total_surplus_amount = 0.0
    matched_items_count = 0

    for item in counted_items:
        code_key = (item.get("stock_code") or "").strip().lower()
        name_key = (item.get("name") or "").strip().lower()

        matched_irs = irsaliye_map.get(code_key) or irsaliye_map.get(name_key)

        phys_qty = float(item.get("phys_qty") or 0.0)
        book_qty = float(item.get("book_qty") or 0.0)
        unit_cost = float(item.get("unit_cost") or 0.0)

        irs_qty = float(matched_irs.get("quantity") or 0.0) if matched_irs else book_qty
        is_matched = bool(matched_irs)
        if is_matched:
            matched_items_count += 1

        diff = phys_qty - irs_qty
        diff_val = round(diff * unit_cost, 2)

        if diff < 0:
            status = "EKSIK_TESLIM"
            total_shortage_qty += abs(diff)
            total_shortage_amount += abs(diff_val)
        elif diff > 0:
            status = "FAZLA_TESLIM"
            total_surplus_qty += diff
            total_surplus_amount += diff_val
        else:
            status = "TAM_MUTABIK"

        reconciled_rows.append({
            "stock_code": item.get("stock_code", ""),
            "name": item.get("name", ""),
            "unit": item.get("unit", "Adet"),
            "eirsaliye_qty": irs_qty,
            "phys_counted_qty": phys_qty,
            "unit_cost": unit_cost,
            "diff_qty": diff,
            "diff_amount": diff_val,
            "status": status,
            "is_matched_with_irsaliye": is_matched
        })

    net_difference_amount = round(total_surplus_amount - total_shortage_amount, 2)

    # VUK ve Tekdüzen Hesap Planı açıklaması
    accounting_note = (
        f"213 Sayılı VUK m.186 uyarınca tespit edilen {total_shortage_amount:.2f} TL tutarındaki "
        f"noksanlıklar '197 Sayım ve Tesellüm Noksanları' hesabına, "
        f"{total_surplus_amount:.2f} TL tutarındaki fazlalıklar ise "
        f"'397 Sayım ve Tesellüm Fazlaları' hesabına intikal ettirilmelidir."
    )

    is_full_reconciled = (total_shortage_qty == 0 and total_surplus_qty == 0)

    summary_text = (
        f"e-İrsaliye ({irsaliye_no}) Mutabakatı: "
        f"{'TAM MUTABIK' if is_full_reconciled else f'{total_shortage_qty} Adet Noksan (-{total_shortage_amount:.2f} TL) / {total_surplus_qty} Adet Fazla (+{total_surplus_amount:.2f} TL)'}."
    )

    return {
        "irsaliye_no": irsaliye_no,
        "total_items_checked": len(counted_items),
        "matched_with_eirsaliye_count": matched_items_count,
        "is_full_reconciled": is_full_reconciled,
        "total_shortage_qty": total_shortage_qty,
        "total_surplus_qty": total_surplus_qty,
        "total_shortage_amount": round(total_shortage_amount, 2),
        "total_surplus_amount": round(total_surplus_amount, 2),
        "net_difference_amount": net_difference_amount,
        "accounting_note": accounting_note,
        "summary": summary_text,
        "rows": reconciled_rows
    }

def parse_ubl_eirsaliye_xml(xml_content: str) -> List[Dict[str, Any]]:
    """
    UBL-TR 2.1 e-İrsaliye XML içeriğini ayrıştırarak sevk irsaliyesi kalemlerini listeler.
    """
    items = []
    try:
        root = ET.fromstring(xml_content)
        # Namespace agnostic findall for DespatchLine
        for elem in root.iter():
            if elem.tag.endswith("DespatchLine"):
                code = ""
                name = ""
                qty = 0.0
                unit = "Adet"

                for child in elem.iter():
                    if child.tag.endswith("DeliveredQuantity"):
                        try:
                            qty = float(child.text or 0)
                            unit = child.attrib.get("unitCode", "Adet")
                        except ValueError:
                            pass
                    elif child.tag.endswith("ID") and not code:
                        code = child.text or ""
                    elif child.tag.endswith("Name"):
                        name = child.text or ""

                if name or code:
                    items.append({
                        "stock_code": code,
                        "name": name or code,
                        "quantity": qty,
                        "unit": unit
                    })
    except Exception:
        pass
    return items
