# 技術ドキュメントのローカライズ v2 — 用語集適用とリンク検証

## 目的

あなたは技術ローカライズエンジニアです。英語の技術ドキュメントを日本語に翻訳します。v2では以下が追加されます：
1. **新規**: コードブロックの完全保持（8ブロック）
2. **新規**: glossary.jsonの用語を一貫して適用
3. **新規**: 内部リンクの検証

## 入力ファイル

- `/workspace/inputs/technical_docs_en.md` — 英語技術ドキュメント（8コードブロック含む）
- `/workspace/inputs/glossary.json` — **新規** 用語集（英日対応、30用語）
- `/workspace/inputs/link_list.json` — **新規** 検証すべきリンク一覧

## タスク

1. 技術ドキュメントを日本語に翻訳
2. **新規**: glossary.jsonの用語を全セクションで一貫して適用
3. **新規**: コードブロック（8個）を変更せずに保持
4. **新規**: 全ての内部リンクが有効であることを確認
5. 各出力ファイルを生成

## 出力ファイル (/workspace/output/)

### api_docs_ja.md — 日本語翻訳ドキュメント
### glossary_applied.json
{"terms_applied": [{"english": str, "japanese": str, "occurrences": int}], "consistency_score": float}
### link_validation.json
{"total_links": int, "valid": int, "broken": [], "internal_refs_valid": bool}
### code_preservation_report.json
{"total_blocks": 8, "preserved": int, "modified": []}

### /workspace/answer.json
{"glossary_terms_applied": int, "consistency_score": float, "code_blocks_preserved": int, "links_valid": int, "total_links": int}

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
