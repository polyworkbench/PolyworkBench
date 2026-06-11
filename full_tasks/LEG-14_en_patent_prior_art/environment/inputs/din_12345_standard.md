# DIN 12345:2022-06

## Wärmeleitfähige Grenzflächenmaterialien — Prüfverfahren für die thermische und mechanische Charakterisierung

**Thermal Interface Materials — Test Methods for Thermal and Mechanical Characterization**

Ausgabedatum: 2022-06-01  
Herausgeber: Deutsches Institut für Normung e.V.  
ICS: 19.020; 29.035.20

---

## Vorwort

Diese Norm legt Prüfverfahren für die Charakterisierung von wärmeleitfähigen Grenzflächenmaterialien (Thermal Interface Materials, TIM) fest. Sie gilt für alle Arten von TIM einschließlich Wärmeleitpasten, Phasenwechselmaterialien, thermisch leitfähigen Klebstoffen und Pad-Materialien.

---

## 1 Anwendungsbereich

Diese Norm gilt für die Prüfung von wärmeleitfähigen Grenzflächenmaterialien, die in elektronischen Baugruppen zwischen wärmeerzeugenden Bauelementen und Kühlkörpern eingesetzt werden.

## 2 Normative Verweisungen

- DIN EN ISO 22007-2: Bestimmung der Wärmeleitfähigkeit
- DIN EN 60068-2-14: Temperaturwechselprüfung
- DIN EN ISO 527-1: Zugversuch

## 3 Begriffe und Definitionen

### 3.1 Wärmeleitfähiger Grenzflächenmaterial (TIM)
Material, das zwischen eine Wärmequelle und eine Wärmesenke eingefügt wird, um den thermischen Kontaktwiderstand zu minimieren.

### 3.2 Thermischer Widerstand (Rth)
Widerstand gegen den Wärmefluss durch das Material, angegeben in K·cm²/W.

### 3.3 Bondline-Dicke (BLT)
Dicke des TIM im eingebauten Zustand unter definiertem Anpressdruck.

## 4 Prüfung der Wärmeleitfähigkeit

### 4.1 Prüfverfahren — Stationäre Methode

#### 4.1.1 Probenherstellung
Die Probe ist auf eine Abmessung von **20 mm × 20 mm** quadratisch zuzuschneiden. Die Dicke der Probe soll zwischen 0,1 mm und 5 mm liegen und ist mit einer Genauigkeit von ±0,01 mm zu bestimmen.

#### 4.1.2 Prüfaufbau
Die Probe wird zwischen zwei Referenzplatten aus Kupfer (Reinheit ≥ 99,9%, Oberflächenrauheit **Ra ≤ 0,4 μm**) eingespannt. Der Anpressdruck beträgt **0,3 MPa** (±0,02 MPa).

#### 4.1.3 Prüfbedingungen
- Messtemperatur: **25 ± 2°C**
- Relative Luftfeuchtigkeit: **50 ± 10%**
- Temperaturstabilisierung: mindestens 30 Minuten vor Messbeginn
- Mindestens drei Messungen pro Probe

#### 4.1.4 Auswertung
Die Wärmeleitfähigkeit λ wird nach folgender Gleichung berechnet:

λ = (Q · d) / (A · ΔT)

wobei:
- Q = Wärmefluss (W)
- d = Probendicke (m)
- A = Probenfläche (m²)
- ΔT = Temperaturdifferenz zwischen den Referenzplatten (K)

### 4.2 Alternative Prüfverfahren
Für dünne Proben (< 0,5 mm) kann die Laser-Flash-Methode nach DIN EN ISO 22007-2 angewendet werden.

## 5 Mechanische Prüfungen

### 5.1 Druckversuch
Die Druckfestigkeit ist nach DIN EN ISO 604 bei einer Verformungsgeschwindigkeit von 1 mm/min zu bestimmen.

### 5.2 Haftfestigkeitsprüfung
Die Haftung des TIM an der Substratoberfläche ist durch einen Zugversuch senkrecht zur Klebfläche zu bestimmen (Pull-off-Test).

## 6 Prüfung der Selbstheilungseigenschaften

### 6.1 Anwendungsbereich
Dieser Abschnitt gilt für TIM mit deklarierten Selbstheilungseigenschaften.

### 6.2 Prüfverfahren für die Selbstheilung

#### 6.2.1 Probenherstellung
Die Probe ist gemäß Abschnitt 4.1.1 herzustellen.

#### 6.2.2 Einbringung definierter Schäden
Ein kontrollierter Riss ist in die Probe einzubringen:
- **Risslänge: 5 mm** (±0,2 mm)
- **Risstiefe: 50% der Probendicke** (±5%)
- Werkzeug: Mikroskalpell oder Rasierklingenhalter
- Rissbreite: maximal 50 μm

#### 6.2.3 Heilungsbedingungen
Die geschädigte Probe wird unter folgenden Bedingungen gelagert:
- **Temperatur: 60-80°C** (je nach Herstellerangabe)
- **Dauer: 2-24 Stunden** (je nach Herstellerangabe)
- Atmosphäre: Luft oder Stickstoff
- Anpressdruck: 0 MPa (druckfrei)

#### 6.2.4 Bewertung der Heilungseffizienz
Nach der Heilungsphase wird die Wärmeleitfähigkeit gemäß Abschnitt 4.1 erneut gemessen. Die Heilungsrate η wird berechnet als:

η = (λ_geheilt / λ_initial) × 100%

#### 6.2.5 Akzeptanzkriterium
Ein TIM mit deklarierten Selbstheilungseigenschaften gilt als konform, wenn:
- **Die Heilungsrate η ≥ 80%** erreicht wird
- Die Heilung innerhalb der vom Hersteller angegebenen Bedingungen (Temperatur, Zeit) erfolgt

## 7 Umweltprüfungen

### 7.1 Temperaturwechselprüfung
Gemäß DIN EN 60068-2-14:
- Temperaturbereich: -40°C bis +150°C
- Zyklenanzahl: 1000
- Verweilzeit je Temperatur: 30 Minuten
- Übergangszeit: maximal 10 Minuten

### 7.2 Feuchtebeständigkeit
85°C / 85% r.F. für 1000 Stunden gemäß IPC-TM-650

## 8 Dokumentation und Berichterstattung

### 8.1 Prüfbericht
Der Prüfbericht muss mindestens folgende Angaben enthalten:
- Probenbezeichnung und Herstellerangaben
- Prüfbedingungen (Temperatur, Feuchtigkeit, Druck)
- Messergebnisse mit Standardabweichung
- Angabe der verwendeten Prüfnorm und Abweichungen

---

## Anhang A (informativ) — Typische Kennwerte

| Material-Typ | λ (W/m·K) | Rth (K·cm²/W) | BLT (μm) |
|-------------|-----------|----------------|-----------|
| Wärmeleitpaste | 1-5 | 0.05-0.20 | 25-75 |
| Phasenwechsel | 3-8 | 0.03-0.10 | 20-50 |
| Gap Pad | 1-6 | 0.5-3.0 | 500-3000 |
| Thermischer Klebstoff | 1-3 | 0.10-0.30 | 50-150 |

---

*© DIN Deutsches Institut für Normung e.V. Alle Rechte vorbehalten.*
