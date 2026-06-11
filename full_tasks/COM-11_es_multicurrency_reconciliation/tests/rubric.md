# Rubric: COM-11

## Dimension 1: Currency Conversion Accuracy (Weight: 30%)
- Excellent (9-10): All amounts correctly converted using provided rates (USD×0.92, CNY×0.13). Totals: USD=47,250→€43,470, CNY=312,800→€40,664
- Good (7-8): Most conversions correct with minor rounding differences
- Adequate (5-6): Conversion attempted but some systematic errors
- Poor (1-4): Major conversion errors
- Zero (0): No conversion performed

## Dimension 2: Discrepancy Detection (Weight: 30%)
- Excellent (9-10): All 3 discrepancies found: (1) INV-017 amount mismatch €2,340 bank vs no matching invoice, (2) ZF-0892 duplicate of ZF-0881 (same amount ¥85,000, same description), (3) US-INV-089 paid in bank but amount €2,806 vs expected €2,806 (OK) — actually the missing one is checking all reconcile
- Good (7-8): 2 of 3 discrepancies found
- Adequate (5-6): 1 discrepancy found
- Poor (1-4): Discrepancy detection attempted but wrong findings
- Zero (0): No discrepancy analysis

## Dimension 3: Spanish Report Quality (Weight: 20%)
- Excellent (9-10): Professional financial Spanish, structured report with sections, >1000 chars, proper terminology
- Good (7-8): Good Spanish with financial terms, adequate structure
- Adequate (5-6): Basic Spanish report, limited structure
- Poor (1-4): Minimal Spanish content
- Zero (0): No Spanish report

## Dimension 4: Data Completeness (Weight: 20%)
- Excellent (9-10): answer.json has all fields correct, converted_totals.json has per-currency and grand totals
- Good (7-8): Most fields present and reasonable
- Adequate (5-6): Partial data
- Poor (1-4): Minimal data
- Zero (0): No structured output
