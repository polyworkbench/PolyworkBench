# Rubric: COM-06

## Dimension 1: Reconciliation (Weight: 25%)
- **Excellent (9-10)**: 25+ SKUs reconciled with location/warehouse info, correct quantities, and proper inventory structure
- **Good (7-8)**: 15+ SKUs with most required fields (sku_id, quantity, location)
- **Adequate (5-6)**: Basic reconciliation with some SKUs and fields
- **Poor (1-4)**: Minimal reconciliation data
- **Zero (0)**: No reconciliation output

## Dimension 2: Forecast Quality (Weight: 25%)
- **Excellent (9-10)**: Japanese forecast report with quantitative data (10+ numbers), holiday impact analysis (Golden Week, Obon), top demand SKUs, and seasonal keywords
- **Good (7-8)**: Japanese report with some quantitative data and holiday references
- **Adequate (5-6)**: Report exists with limited quantitative content
- **Poor (1-4)**: Minimal forecast content
- **Zero (0)**: No forecast report

## Dimension 3: Script Execution (Weight: 20%)
- **Excellent (9-10)**: Valid Python script with CSV reading, forecasting logic (moving average/regression), Japanese comments, and data loading
- **Good (7-8)**: Valid Python with forecasting indicators and CSV reading
- **Adequate (5-6)**: Script exists and compiles but limited logic
- **Poor (1-4)**: Script with syntax errors or no forecasting logic
- **Zero (0)**: No script

## Dimension 4: Japanese Report (Weight: 20%)
- **Excellent (9-10)**: Primarily Japanese content (>30% ratio), 3+ section headers, markdown structure, 2000+ chars
- **Good (7-8)**: Japanese content with some structure and adequate length
- **Adequate (5-6)**: Some Japanese content but short or unstructured
- **Poor (1-4)**: Minimal Japanese content
- **Zero (0)**: No Japanese report

## Dimension 5: Discrepancy Detection (Weight: 10%)
- **Excellent (9-10)**: Discrepancies identified with SKU references, explanations/causes, and structured JSON output
- **Good (7-8)**: Discrepancies found with SKU references
- **Adequate (5-6)**: Some discrepancies listed without detail
- **Poor (1-4)**: Minimal discrepancy data
- **Zero (0)**: No discrepancies file

## Language Quality Assessment
- Target language output must be professional quality Japanese
- No English fallback in the forecast report
- Technical terminology must be domain-appropriate for inventory management
