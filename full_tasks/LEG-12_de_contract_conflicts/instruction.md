# Vertragskonfliktanalyse: Rahmenvertrag und Nachträge

## Aufgabenstellung

Sie erhalten einen deutschen Rahmenvertrag (Master Agreement) und drei englischsprachige Nachträge (Amendments), sowie ein Änderungsprotokoll (Change Log). Ihre Aufgabe ist es, alle Konflikte und Widersprüche zwischen dem Rahmenvertrag und den Nachträgen systematisch zu identifizieren und zu analysieren.

## Eingabedokumente

1. `rahmenvertrag.md` — Deutscher Rahmenvertrag (Hauptvertrag)
2. `amendment_1.md` — Erster Nachtrag (Englisch)
3. `amendment_2.md` — Zweiter Nachtrag (Englisch)
4. `amendment_3.md` — Dritter Nachtrag (Englisch)
5. `change_log.csv` — Änderungsprotokoll

## Durchzuführende Analyse

1. **Klausel-für-Klausel-Vergleich**: Vergleichen Sie jede Klausel des Rahmenvertrags mit den entsprechenden Bestimmungen in allen Nachträgen.
2. **Konfliktidentifikation**: Identifizieren Sie alle Fälle, in denen ein Nachtrag dem Rahmenvertrag oder einem anderen Nachtrag widerspricht.
3. **Kategorisierung**: Ordnen Sie jeden Konflikt einer Kategorie zu (Zahlungsbedingungen, Haftung, Gerichtsstand, Kündigung, Geistiges Eigentum, Höhere Gewalt).
4. **Lösungsempfehlung**: Geben Sie für jeden Konflikt eine rechtliche Empfehlung zur Auflösung.

## Erforderliche Ausgabedateien

### `konfliktanalyse.md`
Ein deutschsprachiger Analysebericht mit:
- Zusammenfassung der Ergebnisse
- Detaillierte Analyse jedes Konflikts mit Klauselverweisen
- Rechtliche Einschätzung und Empfehlungen
- Prioritätsranking der Konflikte nach Risiko

### `conflicts.json`
```json
{
  "total_conflicts": <int>,
  "conflicts": [
    {
      "id": 1,
      "category": "<category>",
      "master_clause": "<§ reference>",
      "amendment_clause": "<amendment + section>",
      "master_text": "<relevant German text>",
      "amendment_text": "<relevant English text>",
      "conflict_type": "<direct_contradiction|ambiguity|supersession>",
      "severity": "<high|medium|low>",
      "resolution": "<recommendation>"
    }
  ]
}
```

### `resolution_matrix.json`
```json
{
  "conflicts_by_category": {
    "<category>": [<conflict_ids>]
  },
  "priority_ranking": [<conflict_ids in priority order>],
  "recommended_actions": [
    {
      "conflict_id": <int>,
      "action": "<description>",
      "legal_basis": "<reasoning>"
    }
  ]
}
```

## Bewertungskriterien
- Vollständigkeit: Alle 6 Konflikte müssen gefunden werden
- Genauigkeit: Korrekte Klauselverweise
- Rechtliche Qualität: Fundierte Empfehlungen
- Struktur: Valide JSON-Dateien

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
