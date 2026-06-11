# サプライチェーンリスク評価 — 多言語サプライヤーデータに基づく日本語リスクレジスター

## タスク概要

あなたはサプライチェーン管理者です。中国、韓国、ベトナムのサプライヤーデータ（各国語）と英語のリスクフレームワークを分析し、日本語でリスク評価報告書とリスク軽減計画を作成してください。

## 入力データ

- `/workspace/inputs/suppliers_china_zh.csv` — 中国サプライヤーのプロファイルと実績データ（中国語）
- `/workspace/inputs/suppliers_korea_ko.csv` — 韓国サプライヤーデータ（韓国語）
- `/workspace/inputs/suppliers_vietnam_vi.csv` — ベトナムサプライヤーデータ（ベトナム語）
- `/workspace/inputs/risk_framework_en.json` — ISO 31000に基づくリスクフレームワーク（英語）
- `/workspace/inputs/geopolitical_factors_en.md` — 地政学的リスク要因（英語）

## 要求事項

- リスクレジスター（`risk_register_ja.json`）の作成：各サプライヤーに対し、リスクカテゴリー、発生可能性、影響度、リスクスコア、優先順位を記載
- リスク評価報告書（`assessment_report_ja.md`）の作成：全体サマリー、国別リスク分析、サプライヤー比較、地政学的リスク評価を含む
- サプライヤースコアカード（`supplier_scorecard.json`）の生成：品質、納期、コスト、柔軟性、財務安定性の5軸評価
- リスク軽減計画（`mitigation_plan_ja.md`）の策定：リスク別の対策、代替サプライヤー戦略、安全在庫計画
- ISO 31000フレームワークに準拠したリスク分析手法を使用すること
- 各国サプライヤーの地政学的リスクを考慮すること
- サプライヤーの単一依存（集中リスク）を特定し警告すること
- 総合リスクスコアに基づく優先順位付けを行うこと
- `answer.json` の作成：`{"total_suppliers": int, "high_risk_suppliers": int, "critical_risks": int, "single_source_items": int, "avg_risk_score": float, "highest_risk_country": str, "recommended_actions": int}`

## 出力

全ファイルを `/workspace/output/` に保存：
- `risk_register_ja.json`
- `assessment_report_ja.md`
- `supplier_scorecard.json`
- `mitigation_plan_ja.md`

および `/workspace/answer.json`

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
