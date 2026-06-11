# Russian Customs Declarations from Chinese Invoices and English Packing Lists

## Overview
Tests the ability to process Chinese commercial invoices and English packing lists to prepare Russian customs declaration documents with correct HS code classification and duty calculations.

## Scenario
A shipment of goods from China to Russia requires complete customs documentation. The agent must process 5 Chinese-language commercial invoices and English packing lists, classify all goods using 10-digit EAEU HS codes, calculate customs value using Method 1 (transaction value), compute import duties and VAT (20%), and produce properly formatted Russian customs declaration forms. Total shipment: $47,850 FOB, $51,335 CIF.

## Language Configuration
- **Instruction Language**: Russian
- **Source Material Languages**: Chinese, English
- **Target Output Language(s)**: Russian
- **Complexity Level**: L4

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Consolidated results summary |
| `customs_declarations_ru.json` | Structured declaration data per invoice |
| `hs_classification.json` | Goods classification with 10-digit HS codes and justification |
| `value_calculation.json` | Customs value calculation: FOB, freight, insurance, CIF, duties, VAT |
| `declaration_forms_ru.md` | Formatted customs declaration forms in Russian |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| HS Classification | 30% | Correct 10-digit EAEU HS code assignment |
| Calculation Accuracy | 25% | Correct customs value, duty, and VAT calculations |
| Chinese Source Processing | 20% | Accurate extraction of data from Chinese invoices |
| Russian Documentation | 15% | Proper customs form formatting in Russian |
| Completeness | 10% | All 5 invoices fully processed with all fields |

## Key Challenges
- Extracting product information from Chinese-language commercial invoices
- Correctly classifying goods into 10-digit EAEU HS codes
- Performing multi-step financial calculations (FOB→CIF→duty→VAT)
- Producing properly formatted Russian customs documentation
