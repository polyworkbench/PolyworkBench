#!/usr/bin/env bash
set -euo pipefail
OUT="${OUTPUT_DIR:-/workspace}"
mkdir -p "$OUT"
python3 - <<'PY'
import json, os, pathlib
out = pathlib.Path(os.environ.get("OUTPUT_DIR", "/workspace"))
csv_text = "\ufeffDate,Vendor,Description,Amount_JPY,Tax_Rate,Amount_CNY,Receipt_ID\n2024-11-15,7-Eleven Shinjuku 3-chome,Business trip incidentals,1149,mixed(8%/10%),53.22,R001\n2024-11-18,JR East,Tokyo - Shin-Osaka Shinkansen,14400,10%,667.01,R002\n2024-11-20,Izakaya Sakura Shibuya,Business meal (PENDING REVIEW),31130,10%,1441.94,R003\n"
answer = {
  "concur_expense_csv": csv_text,
  "extraction": [
    {"receipt_id":"R001","date_iso":"2024-11-15","date_jp_original":"令和6年11月15日","vendor":"7-Eleven Shinjuku 3-chome","addressee":"(blank)","tax_breakdown":[{"rate":0.08,"taxable_amount":860,"tax":69},{"rate":0.10,"taxable_amount":200,"tax":20}],"total_jpy":1149,"total_cny":53.22,"handwritten_notes":"出張交通費","stamp_present":True,"confidence":0.92,"issues":["Handwritten label may be miscategorized."]},
    {"receipt_id":"R002","date_iso":"2024-11-18","date_jp_original":"令和6年11月18日","vendor":"JR East","addressee":"Acme Research Co., Ltd.","tax_breakdown":[{"rate":0.10,"taxable_amount":13091,"tax":1309}],"total_jpy":14400,"total_cny":667.01,"handwritten_notes":"","stamp_present":False,"confidence":0.99,"issues":[]},
    {"receipt_id":"R003","date_iso":"2024-11-20","date_jp_original":"令和6年11月20日","vendor":"Izakaya Sakura Shibuya","addressee":"上様","tax_breakdown":[{"rate":0.10,"taxable_amount":28300,"tax":2830}],"total_jpy":31130,"total_cny":1441.94,"handwritten_notes":"ありがとうございました","stamp_present":True,"confidence":0.55,"issues":["Stamp obscures total.","上様 and amount over 30,000 JPY requires rejection/reissue."]}
  ],
  "exceptions_md": "# Exception Report\n\n## Critical\n\n### R003 — Izakaya Sakura Shibuya\nAddressee is 上様 and amount is 31,130 JPY, above the 30,000 JPY threshold. Reject and request re-issued receipt.\n\n## Warning\n\n### R001\nHandwritten category may be wrong."
}
(out/"answer.json").write_text(json.dumps(answer, ensure_ascii=False, indent=2), encoding="utf-8")
(out/"concur_expense.csv").write_text(csv_text, encoding="utf-8")
PY
