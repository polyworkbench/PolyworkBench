# 取締役会議事録の作成

## 課題

英語の取締役会議題、中国語の四半期財務データ、韓国語の子会社報告書に基づき、日本語で正式な取締役会議事録を作成してください。すべての成果物は日本語で作成する必要があります。

## 入力ファイル

- `/workspace/inputs/board_agenda_en.md` — 取締役会議題（英語、6議案）
- `/workspace/inputs/financials_zh.csv` — 四半期財務実績（中国語）
- `/workspace/inputs/subsidiary_report_ko.md` — 韓国子会社四半期報告書（韓国語）
- `/workspace/inputs/shareholder_info_en.json` — 株主名簿と議決権情報（英語）

## 要求事項

- 正式な取締役会議事録（`board_minutes_ja.md`）を作成：開催日時・場所・出席者・各議案の審議内容・決議結果を含む
- 決議事項一覧（`resolutions_ja.json`）：各議案の決議内容、賛否、担当取締役をJSON形式で整理
- 財務サマリー（`financial_summary_ja.json`）：中国語CSVデータを日本語に変換し、主要KPIを構造化
- アクションアイテム一覧（`action_items_ja.json`）：議事録から抽出した各担当者のToDo、期限を記載
- 日本の会社法に準拠した議事録形式を使用（取締役会議事録の法定記載事項を含む）
- 敬体・丁寧語で記載（「〜について審議した」「本議案は全会一致で承認された」等）
- 財務数値は中国語原資料の数値を正確に反映すること
- 韓国子会社の報告内容を第4号議案として正確に要約すること
- answer.jsonに記載：`{"total_resolutions": 6, "approved_unanimously": int, "total_revenue_cny": number, "action_items_count": int}`

## 出力ファイル

結果を `/workspace/output/` に保存：
- `/workspace/output/board_minutes_ja.md`
- `/workspace/output/resolutions_ja.json`
- `/workspace/output/financial_summary_ja.json`
- `/workspace/output/action_items_ja.json`

要約ファイル：`/workspace/answer.json`

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
