#!/usr/bin/env bash
set -euo pipefail
OUT="${OUTPUT_DIR:-/workspace}"
mkdir -p "$OUT"
python3 - <<'PY'
import json, os, pathlib
out = pathlib.Path(os.environ.get("OUTPUT_DIR", "/workspace"))
rca = """# Post-Mortem: Payment Service Outage\n\n## Summary\nSuccess rate dropped to 45% after redis-master-0 flap and 18s Sentinel failover.\n## Impact\nKafka lag reached 18,900.\n## Timeline (KST)\nSee structured timeline.\n## Root Cause\nRedis failover prevented lock renewal; locks on SKU8821/SKU3301 expired/stalled.\n## Contributing Factors\n30s TTL too short, single Redis lock topology, Kafka consumer lag.\n## Detection\nGrafana payment_success_rate alert.\n## Resolution\nzhang.wei changed TTL 30 -> 60 seconds.\n## Lessons Learned\nAdopt Redlock and safer TTL such as 90s with jitter.\n## Action Items\nSee JSON.\n"""
timeline = [
 {"time_kst":"2024-11-19 22:58:12","event":"Normal order succeeds","source":"[source: payment_service.log, line 1]"},
 {"time_kst":"2024-11-19 23:00:03","event":"Redis latency spike 850ms","source":"[source: payment_service.log, line 3]"},
 {"time_kst":"2024-11-19 23:00:12","event":"redis-master-0 connection failed","source":"[source: payment_service.log, line 4]"},
 {"time_kst":"2024-11-19 23:00:18","event":"Lock renewal failed","source":"[source: payment_service.log, line 5]"},
 {"time_kst":"2024-11-19 23:00:31","event":"New master elected after 18s","source":"[source: payment_service.log, line 7]"},
 {"time_kst":"2024-11-19 23:10:13","event":"Kafka lag peaked at 18,900","source":"[source: payment_service.log, line 13]"},
 {"time_kst":"2024-11-19 23:15:02","event":"TTL changed 30 to 60","source":"[source: payment_service.log, line 14]"},
 {"time_kst":"2024-11-19 23:30:00","event":"Service restored","source":"[source: payment_service.log, line 17]"}
]
answer = {"rca_md": rca, "summary_ko_md":"Redis 장애로 결제 성공률 45% 하락, TTL 조정 후 복구.", "timeline_kst": timeline, "action_items":[
 {"id":"AI-1","description_en":"Migrate locks to Redlock","owner":"platform-team","due_date":"2024-12-10","priority":"P0"},
 {"id":"AI-2","description_en":"Increase default lock TTL to 90s with jitter","owner":"payment-team","due_date":"2024-11-26","priority":"P0"},
 {"id":"AI-3","description_en":"Investigate redis-master-0 network flap","owner":"infra-team","due_date":"2024-12-03","priority":"P1"}
]}
(out/"answer.json").write_text(json.dumps(answer, ensure_ascii=False, indent=2), encoding="utf-8")
(out/"rca.md").write_text(rca, encoding="utf-8")
PY
