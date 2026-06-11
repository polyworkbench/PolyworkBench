# Rubric: COM-02

## Dimension 1: Reconciliation Accuracy (Weight: 30%)
- **Excellent (9-10)**: All 10 orders reconciled with complete fields (order_id, quantity, hs_code), proper VND currency conversion, structured JSON output
- **Good (7-8)**: 8+ orders reconciled with most fields, VND values present
- **Adequate (5-6)**: 5+ orders with partial reconciliation and some currency conversion
- **Poor (1-4)**: Few orders reconciled, missing critical fields
- **Zero (0)**: No reconciliation output

## Dimension 2: Customs Compliance (Weight: 25%)
- **Excellent (9-10)**: All 10 declarations with valid HS codes (XXXX.XX format), Vietnamese content throughout, complete customs documentation
- **Good (7-8)**: 8+ declarations with valid HS codes and Vietnamese text
- **Adequate (5-6)**: 5+ declarations with some valid HS codes
- **Poor (1-4)**: Few declarations, invalid HS codes, or no Vietnamese content
- **Zero (0)**: No customs declarations

## Dimension 3: Shipping Labels (Weight: 20%)
- **Excellent (9-10)**: 10 shipping labels with complete addresses (recipient, address, phone, postal), Vietnamese names and addresses
- **Good (7-8)**: 8+ labels with complete address fields in Vietnamese
- **Adequate (5-6)**: 5+ labels with partial address information
- **Poor (1-4)**: Few labels or missing critical address fields
- **Zero (0)**: No shipping labels

## Dimension 4: Discrepancy Detection (Weight: 15%)
- **Excellent (9-10)**: All 5 known discrepancies detected (ORD-VN-001, 003, 005, 006, 007) with detailed explanations in Vietnamese
- **Good (7-8)**: 4+ discrepancies detected with adequate detail
- **Adequate (5-6)**: 2-3 discrepancies detected
- **Poor (1-4)**: 1 discrepancy or vague detection
- **Zero (0)**: No discrepancy report

## Dimension 5: Vietnamese Quality (Weight: 10%)
- **Excellent (9-10)**: Professional Vietnamese with proper diacritics across all outputs (report, customs, labels)
- **Good (7-8)**: Vietnamese present in most outputs with correct diacritics
- **Adequate (5-6)**: Some Vietnamese content but inconsistent quality
- **Poor (1-4)**: Minimal Vietnamese or missing diacritics
- **Zero (0)**: No Vietnamese content

## Language Quality Assessment
- Target language output must be professional quality Vietnamese
- No English fallback in official customs/shipping documents
- Technical terminology must follow Vietnamese trade conventions
