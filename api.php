<?php
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type");
header("Content-Type: application/json; charset=UTF-8");

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

$dataFile = __DIR__ . '/stok_sayimlar.json';

function getStoredData($file) {
    if (!file_exists($file)) return [];
    $content = file_get_contents($file);
    return json_decode($content, true) ?: [];
}

function saveStoredData($file, $data) {
    file_put_contents($file, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
}

function reconcileEirsaliye($counted, $irsItems, $irsNo = 'GIB2026-IRS-001') {
    $map = [];
    foreach ($irsItems as $it) {
        $key = strtolower(trim($it['stock_code'] ?? ($it['name'] ?? '')));
        if ($key) $map[$key] = $it;
    }

    $rows = [];
    $totShortage = 0;
    $totSurplus = 0;
    $totShortageAmt = 0;
    $totSurplusAmt = 0;
    $matchedCount = 0;

    foreach ($counted as $c) {
        $cKey = strtolower(trim($c['stock_code'] ?? ''));
        $nKey = strtolower(trim($c['name'] ?? ''));
        $m = $map[$cKey] ?? ($map[$nKey] ?? null);

        $phys = floatval($c['phys_qty'] ?? 0);
        $book = floatval($c['book_qty'] ?? 0);
        $cost = floatval($c['unit_cost'] ?? 0);

        $irsQty = $m ? floatval($m['quantity'] ?? $book) : $book;
        if ($m) $matchedCount++;

        $diff = $phys - $irsQty;
        $diffVal = round($diff * $cost, 2);

        $st = 'TAM_MUTABIK';
        if ($diff < 0) {
            $st = 'EKSIK_TESLIM';
            $totShortage += abs($diff);
            $totShortageAmt += abs($diffVal);
        } elseif ($diff > 0) {
            $st = 'FAZLA_TESLIM';
            $totSurplus += $diff;
            $totSurplusAmt += $diffVal;
        }

        $rows[] = [
            'stock_code' => $c['stock_code'] ?? '',
            'name' => $c['name'] ?? '',
            'unit' => $c['unit'] ?? 'Adet',
            'eirsaliye_qty' => $irsQty,
            'phys_counted_qty' => $phys,
            'diff_qty' => $diff,
            'diff_amount' => $diffVal,
            'status' => $st
        ];
    }

    $isReconciled = ($totShortage == 0 && $totSurplus == 0);
    return [
        'irsaliye_no' => $irsNo,
        'total_items_checked' => count($counted),
        'matched_with_eirsaliye_count' => $matchedCount,
        'is_full_reconciled' => $isReconciled,
        'total_shortage_qty' => $totShortage,
        'total_surplus_qty' => $totSurplus,
        'total_shortage_amount' => $totShortageAmt,
        'total_surplus_amount' => $totSurplusAmt,
        'summary' => "e-İrsaliye ({$irsNo}) Mutabakatı: " . ($isReconciled ? "TAM MUTABIK" : "{$totShortage} Noksan, {$totSurplus} Fazla"),
        'rows' => $rows
    ];
}

$action = $_GET['action'] ?? '';
$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'POST') {
    $raw = file_get_contents('php://input');
    $input = json_decode($raw, true) ?: [];

    if ($action === 'durum-guncelle' || (isset($input['action']) && $input['action'] === 'durum-guncelle')) {
        $tracking = $input['tracking_code'] ?? '';
        $newStatus = $input['status'] ?? 'Tutanak Tanzim Edildi';

        $records = getStoredData($dataFile);
        $updated = false;
        foreach ($records as &$item) {
            if (($item['tracking_code'] ?? '') === $tracking) {
                $item['status'] = $newStatus;
                $updated = true;
                break;
            }
        }
        saveStoredData($dataFile, $records);
        echo json_encode(['status' => 'success', 'updated' => $updated]);
        exit();
    }

    if ($action === 'eirsaliye-mutabakat' || (isset($input['action']) && $input['action'] === 'eirsaliye-mutabakat')) {
        $counted = $input['counted_items'] ?? [];
        $irsItems = $input['eirsaliye_items'] ?? [];
        $irsNo = $input['irsaliye_no'] ?? 'GIB2026-IRS-001';
        echo json_encode(reconcileEirsaliye($counted, $irsItems, $irsNo), JSON_UNESCAPED_UNICODE);
        exit();
    }

    $trackingCode = $input['tracking_code'] ?? ('SAYIM-2026-' . rand(1000, 9999));
    $input['tracking_code'] = $trackingCode;
    $input['status'] = $input['status'] ?? 'Tutanak Tanzim Edildi';
    $input['created_at'] = $input['created_at'] ?? date('c');

    $records = getStoredData($dataFile);
    array_unshift($records, $input);
    saveStoredData($dataFile, $records);

    echo json_encode(['status' => 'success', 'tracking_code' => $trackingCode]);
    exit();
}

if ($method === 'GET') {
    $records = getStoredData($dataFile);
    echo json_encode($records, JSON_UNESCAPED_UNICODE);
    exit();
}
