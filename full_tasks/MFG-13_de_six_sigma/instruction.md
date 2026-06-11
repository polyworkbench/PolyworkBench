# Six Sigma DMAIC-Analyse — Prozessfähigkeitsuntersuchung

## Ziel

Sie sind Qualitätsingenieur in einem Präzisionsfertigungsunternehmen. Führen Sie eine vollständige Six-Sigma-DMAIC-Analyse der Messdaten durch. Berechnen Sie die Prozessfähigkeitsindizes und identifizieren Sie zuweisbare Ursachen.

## Eingabedateien

- `/workspace/inputs/messdaten_de.csv` — Qualitätsmessdaten (80 Messungen, Deutsch)
- `/workspace/inputs/process_spec.json` — Prozessspezifikation (USL/LSL/Target, Englisch)
- `/workspace/inputs/measurement_system.json` — Gage R&R Daten (Englisch)

## Aufgaben

1. **Define**: Identifizieren Sie das Qualitätsproblem aus den Messdaten
2. **Measure**: Berechnen Sie Mittelwert, Standardabweichung, Cp, Cpk
3. **Analyze**: Identifizieren Sie zuweisbare Ursachen (Schichtwechsel, Werkzeugverschleiß, Ausreißer)
4. **Improve**: Empfehlungen zur Prozessverbesserung
5. **Control**: Vorschläge für Regelkarten und Überwachung

## Erwartete Ergebnisse
- USL=10.05mm, LSL=9.95mm, Target=10.00mm
- Prozessmittelwert ca. 10.012mm
- Standardabweichung ca. 0.015mm
- Cp = (USL-LSL)/(6*sigma) = 0.10/0.09 = 1.111
- Cpk = min((USL-mu)/(3*sigma), (mu-LSL)/(3*sigma)) = min(0.844, 1.378) = 0.844
- 3 zuweisbare Ursachen: Schichtwechsel (Zeile 20), Trend (Zeilen 50-80), Ausreißer (Zeile 67)

## Ausgabedateien (/workspace/output/)

### dmaic_report_de.md
Vollständiger DMAIC-Bericht auf Deutsch

### capability_analysis.json
{"cp": float, "cpk": float, "mean": float, "std_dev": float, "usl": 10.05, "lsl": 9.95}

### control_chart_data.json
{"measurements": [...], "ucl": float, "lcl": float, "center_line": float, "out_of_control": [...]}

### /workspace/answer.json
{"cp": 1.111, "cpk": 0.844, "mean": 10.012, "std_dev": 0.015, "assignable_causes": 3, "out_of_spec_count": int, "process_capable": false}

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
