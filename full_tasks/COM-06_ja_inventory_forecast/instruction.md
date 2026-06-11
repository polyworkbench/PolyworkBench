# 多拠点在庫照合と需要予測レポート作成

## タスク概要

中国倉庫、韓国3PL（サードパーティ・ロジスティクス）、英語の販売履歴データを照合し、日本市場向けの需要予測レポートを作成してください。

## 入力ファイル

- `/workspace/inputs/warehouse_zh.csv` — 中国倉庫の在庫レベル（30 SKU、中国語）
- `/workspace/inputs/korean_3pl_ko.csv` — 韓国3PLのフルフィルメントデータ（韓国語）
- `/workspace/inputs/sales_history_en.csv` — 過去6ヶ月の英語販売データ
- `/workspace/inputs/holidays_calendar_ja.json` — 日本の祝日カレンダー（需要スパイク予測用）

## 要件

- 中国倉庫と韓国3PLの在庫データを照合し、SKU単位で不一致を特定すること
- 過去6ヶ月の販売履歴から今後3ヶ月の需要を予測するPythonスクリプトを作成すること
- 日本の祝日（ゴールデンウィーク、お盆、年末年始等）による需要スパイクを予測に反映すること
- 在庫照合結果をJSON形式で出力すること（各SKUの在庫数、場所、ステータス）
- 不一致（discrepancy）がある場合は原因推定を含めて別ファイルに出力すること
- 需要予測レポートは日本語で作成し、グラフ用データを含むこと
- 予測スクリプトは実行可能で、コメントは日本語で記述すること

## 出力

以下を `/workspace/output/` に保存してください：

1. `inventory_reconciliation.json` — 在庫照合結果
2. `forecast_report_ja.md` — 日本語需要予測レポート
3. `forecast_script.py` — 需要予測Pythonスクリプト
4. `discrepancies.json` — 不一致詳細

また、`/workspace/answer.json` にサマリー情報を出力してください：
```json
{
  "total_skus": <int>,
  "discrepancy_count": <int>,
  "forecast_period": "<YYYY-MM to YYYY-MM>",
  "top_demand_skus": [<list of top 5 SKU IDs>],
  "holiday_impact_percentage": <float>
}
```

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
