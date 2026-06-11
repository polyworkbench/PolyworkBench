# Post-Mortem: Payment Service Outage 2024-11-19

**Status**: Resolved
**Severity**: SEV-2
**Duration**: 30 min (23:00 - 23:30 KST)
**Author**: SRE Agent (auto-generated)

## Summary

On 2024-11-19 between 23:00 and 23:30 KST, the `payment-service` experienced a sharp degradation, with success rate dropping from 99.8% to a low of 45.0%. Root cause: a Redis master node (`redis-master-0`) connectivity flap triggered an 18-second Sentinel failover, during which distributed locks held by in-flight orders could not be renewed. Stuck inventory locks (`stock:SKU8821`, `stock:SKU3301`) caused cascading order failures, compounded by Kafka consumer lag on `payment-events` reaching 18,900 messages. A manual TTL extension (30s → 60s) by on-call engineer zhang.wei restored throughput by 23:18 KST.

## Impact

- Payment success rate: 99.8% → 45.0% (worst at 23:05 KST) [source: redis_metrics.txt, line 19]
- Estimated affected orders: ~6,500 (extrapolated from log error frequency)
- Kafka consumer lag peaked at 18,900 on `payment-events` [source: redis_metrics.txt, line 14]
- No data loss confirmed; all events consumed by 23:25 KST [source: payment_service.log, line 16]

## Timeline (KST)

| Time (KST) | Event | Source |
|---|---|---|
| 22:58:12 | Normal traffic, order ORD...001 succeeds | [source: payment_service.log, line 1] |
| 23:00:03 | Redis master-0 latency spike (850ms) | [source: payment_service.log, line 3] |
| 23:00:12 | Redis master-0 connection failure, sentinel triggered | [source: payment_service.log, line 4] |
| 23:00:18 | Distributed lock renewal failure on stock:SKU8821 | [source: payment_service.log, line 5] |
| 23:00:25 | First "下单失败-库存锁未释放" error | [source: payment_service.log, line 6] |
| 23:00:31 | Sentinel elected redis-master-1 (18s elapsed) | [source: payment_service.log, line 7] |
| 23:03:44 | Kafka lag begins to climb | [source: payment_service.log, line 10] |
| 23:10:00 | Kafka lag peaks at 18,900 | [source: redis_metrics.txt, line 14] |
| 23:15:02 | Engineer zhang.wei manually extends lock TTL 30s → 60s | [source: payment_service.log, line 14] |
| 23:18:44 | First successful order after intervention | [source: payment_service.log, line 15] |
| 23:25:11 | Kafka lag fully drained | [source: payment_service.log, line 16] |
| 23:30:00 | Service fully restored, success rate 99.7% | [source: payment_service.log, line 17] |

## Root Cause

The primary trigger was a transient connectivity issue on `redis-master-0` (cause TBD; suspected upstream network event per voice memo [source: audio_memo_zh.txt, line 7]). The Sentinel failover took 18 seconds — longer than the 30-second distributed lock TTL with a typical 10-second renewal cadence — meaning locks held during the failover window could not be renewed and were eventually orphaned for the remainder of the original TTL. New order requests blocked on the same SKU keys (`SKU8821`, `SKU3301`) failed.

## Contributing Factors

1. **Lock TTL too aggressive**: 30s TTL leaves no headroom for failover events.
2. **Single-master Redis topology** for distributed locking. Redlock not adopted.
3. **Kafka consumer parallelism insufficient** to absorb the burst once orders backed up.

## Detection

- Alert fired at 23:01 KST on `payment_success_rate < 95%` (Grafana panel "支付成功率") [source: grafana_screenshot.txt, Panel 1]
- On-call engineer (zhang.wei) acknowledged within 4 min.

## Resolution

- 23:15 KST: TTL hot-patched 30s → 60s via Spring Cloud Config refresh [source: payment_service.log, line 14]
- 23:18 KST: Throughput recovers
- 23:30 KST: Full recovery confirmed

## Lessons Learned

- A 30s lock TTL is incompatible with a Sentinel failover budget of up to 30s.
- Voice memo from local SRE (in Chinese with Cantonese accent) was a critical input but had ASR uncertainty on numbers (e.g., "万八/一万八千") — multilingual ops should standardize structured incident notes alongside voice.
- Cross-timezone coordination: Korea HQ requires KST timeline; Chinese ops report in CST; Prometheus stores UTC. Unified timeline must be auto-generated.

## Action Items

| ID | Description | Owner | Priority | Due |
|---|---|---|---|---|
| AI-1 | Migrate distributed lock from single-Redis to Redlock with 5-node quorum | platform-team (lead: kim.hyun) | P0 | 2024-12-10 |
| AI-2 | Increase default lock TTL to 90s and add automatic renewal jitter | payment-service team (lead: zhang.wei) | P0 | 2024-11-26 |
| AI-3 | Investigate redis-master-0 network flap; coordinate with infra team | infra-team (lead: lee.ji) | P1 | 2024-12-03 |
| AI-4 | Add Kafka consumer auto-scaling on lag > 5,000 | data-platform | P1 | 2024-12-17 |
| AI-5 | Standardize bilingual (zh/ko) incident voice memo template with required structured fields | sre-process (lead: park.sun) | P2 | 2024-12-31 |
