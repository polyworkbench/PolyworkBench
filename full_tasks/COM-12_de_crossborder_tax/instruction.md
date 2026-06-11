# Grenzüberschreitende Steuerkonformitätsberechnung

## Kontext

Sie sind ein internationaler Steuerberater, der für ein Unternehmen mit Geschäftstätigkeit in Deutschland, den USA und Japan arbeitet. Ihre Aufgabe ist es, die korrekten Steuersätze auf alle Transaktionen anzuwenden und einen umfassenden Konformitätsbericht zu erstellen.

## Quelldaten

Die folgenden Dateien befinden sich im Verzeichnis `inputs/`:

1. **de_vat_rules.md** — Deutsche Mehrwertsteuervorschriften (auf Deutsch)
2. **us_sales_tax.md** — US-Verkaufssteuerregeln nach Bundesstaat (auf Englisch)
3. **jp_consumption_tax.md** — Japanische Verbrauchssteuerregeln (auf Japanisch)
4. **transactions.csv** — 20 Transaktionen über alle drei Jurisdiktionen

## Aufgaben

### 1. Steuerregeln analysieren
- Deutsche MwSt: 19% Standardsatz (7% ermäßigter Satz für bestimmte Waren)
- US Sales Tax: Kalifornien 7,25%, New York 8%, Texas 6,25%
- Japan: 10% Verbrauchssteuer (8% ermäßigter Satz für Lebensmittel)

### 2. Steuern berechnen
- Wenden Sie die korrekten Steuersätze auf jede Transaktion an
- Berechnen Sie Nettobetrag, Steuerbetrag und Bruttobetrag
- Gruppieren Sie nach Jurisdiktion

### 3. Ergebnisse zusammenfassen
Erwartete Gesamtsteuern:
- Deutschland: €4.523,70 (Gesamtsteuer)
- USA: $2.187,45 (Gesamtsteuer)
- Japan: ¥89.100 (Gesamtsteuer)

### 4. Ausgabedateien erstellen

#### tax_compliance_report_de.md
Vollständiger Bericht auf Deutsch mit:
- Zusammenfassung der angewandten Steuerregeln
- Detaillierte Berechnung pro Transaktion
- Gesamtbeträge nach Jurisdiktion
- Compliance-Empfehlungen

#### tax_calculations.json
```json
{
  "jurisdictions": {
    "DE": {
      "vat_rate_standard": 0.19,
      "vat_rate_reduced": 0.07,
      "total_net": 23808.95,
      "total_tax": 4523.70,
      "total_gross": 28332.65,
      "transactions_count": 7
    },
    "US": {
      "rates": {
        "CA": 0.0725,
        "NY": 0.08,
        "TX": 0.0625
      },
      "total_net": 30142.00,
      "total_tax": 2187.45,
      "total_gross": 32329.45,
      "transactions_count": 7
    },
    "JP": {
      "consumption_tax_standard": 0.10,
      "consumption_tax_reduced": 0.08,
      "total_net": 891000,
      "total_tax": 89100,
      "total_gross": 980100,
      "transactions_count": 6
    }
  },
  "summary": {
    "total_transactions": 20,
    "currencies": ["EUR", "USD", "JPY"]
  }
}
```

## Erfolgskriterien

- Korrekte Anwendung aller Steuersätze
- Gesamtsteuern: DE=€4.523,70, US=$2.187,45, JP=¥89.100
- Alle Ausgabedateien im spezifizierten Format
- Bericht auf Deutsch mit fachgerechter Steuerterminologie

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
