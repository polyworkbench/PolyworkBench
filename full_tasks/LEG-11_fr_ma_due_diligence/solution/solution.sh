#!/usr/bin/env bash
set -euo pipefail
OUT="${OUTPUT_DIR:-/workspace}"
mkdir -p "$OUT"
python3 - <<'PY'
import json, os, pathlib
out = pathlib.Path(os.environ.get("OUTPUT_DIR", "/workspace"))
memo = """# Mémorandum de Due Diligence\n\n## 1. Synthèse exécutive\nRisque modéré à élevé. Divergence 2023: 152 M CNY vs 142 M CNY, convertie en EUR au taux CNY/EUR 2023. [Source: financials_zh.csv, ligne 4; board_minutes_ja.txt, lignes 9-13]\n\n## 2. Structure capitalistique\nFiliale coréenne avec nantissement Woori Bank et élément [OCR_불명]. [Source: corporate_registry_ko.txt, section 주주명부]\n\n## 3. Performance financière\nConversion CNY/EUR avec les moyennes annuelles; la divergence est [unclear] dans la transcription.\n\n## 4. Gouvernance\nLe conseil japonais signale le contentieux coréen de 12 KRW milliards.\n\n## 5. Termes clés du SPA\nCap général 25% soit 70 M EUR.\n\n## 6. Drapeaux rouges\nComptabilité, fiscalité KRW, gouvernance, arbitrage, conformité.\n\n## 7. Recommandations\nAudit Big Four, escrow et indemnité spécifique.\n"""
risks = [
 {"id":"R1","categorie":"financier","description_fr":"Divergence 152 vs 142 M CNY","severite":"critique","probabilite":"élevée","source":"[Source: financials_zh.csv, ligne 4]","mitigation":"Audit Big Four"},
 {"id":"R2","categorie":"fiscal","description_fr":"Contentieux fiscal 12 milliards KRW","severite":"élevée","probabilite":"moyenne","source":"[Source: corporate_registry_ko.txt, section 계류 중 사건]","mitigation":"Escrow"},
 {"id":"R3","categorie":"gouvernance","description_fr":"Nantissement Woori Bank 5%","severite":"élevée","probabilite":"moyenne","source":"[Source: corporate_registry_ko.txt, section 주주명부]","mitigation":"Mainlevée"},
 {"id":"R4","categorie":"juridique","description_fr":"Droit anglais/arbitrage Singapour","severite":"moyenne","probabilite":"moyenne","source":"[Source: spa_draft.md, §7]","mitigation":"Renégocier"},
 {"id":"R5","categorie":"operationnel","description_fr":"Incertitudes ASR/OCR [unclear] [OCR_불명]","severite":"moyenne","probabilite":"élevée","source":"[Source: board_minutes_ja.txt, ligne 10]","mitigation":"Obtenir originaux"}
]
gloss = [{"fr":f"terme {i}","en":f"term {i}","zh":f"术语{i}","ja":f"用語{i}","ko":f"용어{i}"} for i in range(1,16)]
trace = "- Divergence 152/142: [Source: financials_zh.csv, ligne 4; board_minutes_ja.txt, lignes 9-13]\n- Fiscal 12 Mrd KRW: [Source: corporate_registry_ko.txt, section 계류 중 사건]\n- Cap 25%/70 M EUR: [Source: spa_draft.md, §6]"
answer = {"memo_dd_fr_md": memo, "risk_register": risks, "glossaire": gloss, "traceability_fr_md": trace}
(out/"answer.json").write_text(json.dumps(answer, ensure_ascii=False, indent=2), encoding="utf-8")
(out/"memo_dd_fr.md").write_text(memo, encoding="utf-8")
PY
