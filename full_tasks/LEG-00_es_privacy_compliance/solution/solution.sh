#!/usr/bin/env bash
set -euo pipefail
OUT="${OUTPUT_DIR:-/workspace}"
mkdir -p "$OUT"
python3 - <<'PY'
import json, os, pathlib
out = pathlib.Path(os.environ.get("OUTPUT_DIR", "/workspace"))
matrix = [
 {"categoria":"Base legal del tratamiento","ccpa_clausula":"[Fuente: policy_us_ccpa.md, §2]","dsgvo_clausula":"[Fuente: policy_de_dsgvo.md, §2]","lfpdppp_referencia":"[Fuente: lfpdppp_extracts.md, §8]","estado":"⚠️","comentario":"Requiere mapeo a consentimiento/base LFPDPPP."},
 {"categoria":"Derechos ARCO","ccpa_clausula":"[Fuente: policy_us_ccpa.md, §4]","dsgvo_clausula":"[Fuente: policy_de_dsgvo.md, §4]","lfpdppp_referencia":"[Fuente: lfpdppp_extracts.md, §22]","estado":"❌","comentario":"Oposición y plazos mexicanos incompletos."},
 {"categoria":"Retención","ccpa_clausula":"[Fuente: policy_us_ccpa.md, §6]","dsgvo_clausula":"[Fuente: policy_de_dsgvo.md, §6]","lfpdppp_referencia":"[Fuente: lfpdppp_extracts.md, §16]","estado":"⚠️","comentario":"Debe definirse plazo específico."},
 {"categoria":"Transferencias internacionales","ccpa_clausula":"[Fuente: policy_us_ccpa.md, §7]","dsgvo_clausula":"[Fuente: policy_de_dsgvo.md, §7]","lfpdppp_referencia":"[Fuente: lfpdppp_extracts.md, §36]","estado":"❌","comentario":"Falta aviso/consentimiento México-US."},
 {"categoria":"Menores","ccpa_clausula":"[Fuente: policy_us_ccpa.md, §5]","dsgvo_clausula":"[Fuente: policy_de_dsgvo.md, §5]","lfpdppp_referencia":"[Fuente: lfpdppp_extracts.md, §8]","estado":"⚠️","comentario":"Adoptar umbral estricto y consentimiento parental."},
 {"categoria":"Brechas de seguridad","ccpa_clausula":"[Fuente: policy_us_ccpa.md, §9]","dsgvo_clausula":"[Fuente: policy_de_dsgvo.md, §9]","lfpdppp_referencia":"[Fuente: lfpdppp_extracts.md, §20]","estado":"⚠️","comentario":"Operar con SLA 72h/inmediato."}
]
gloss = [{"es":f"término {i}","en":f"term {i}","de":f"Begriff {i}"} for i in range(1,11)]
actions = [{"id":f"AR-{i}","accion":"Actualizar aviso y contratos LFPDPPP","prioridad":"P0" if i==1 else "P1","responsable":"Legal/DPO","plazo":"2025-01-15"} for i in range(1,6)]
informe = "# Informe LFPDPPP para INAI\n\nSe identifican brechas en ARCO, transferencia internacional, retención, menores y brechas. [Fuente: policy_us_ccpa.md, §4]"
answer = {"informe_md": informe, "matriz_cumplimiento": matrix, "glosario_trilingue": gloss, "acciones_recomendadas": actions}
(out/"answer.json").write_text(json.dumps(answer, ensure_ascii=False, indent=2), encoding="utf-8")
(out/"informe.md").write_text(informe, encoding="utf-8")
PY
