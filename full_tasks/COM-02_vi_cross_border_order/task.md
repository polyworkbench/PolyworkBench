# Cross-Border Order Reconciliation with Vietnamese Customs Declarations

## Overview
Tests the agent's ability to reconcile Chinese supplier invoices against Vietnamese customs declarations, detect discrepancies, generate Vietnamese shipping labels, and produce customs documentation with proper HS code classification.

## Scenario
A cross-border trade operation between China and Vietnam requires processing 10 orders. The agent must reconcile Chinese supplier invoices (in Chinese) with Vietnamese customs forms, checking quantities, values, and HS codes. It must generate Vietnamese-language shipping labels with complete recipient information, create customs declarations in Vietnamese with proper HS codes and applicable duty rates, identify and report discrepancies between invoices and declarations, and perform CNY-to-VND currency conversion at the specified exchange rate (1 CNY = 3,450 VND).

## Language Configuration
- **Instruction Language**: Vietnamese
- **Source Material Languages**: Chinese (supplier invoices), Vietnamese (customs forms), English (HS codes reference)
- **Target Output Language(s)**: Vietnamese
- **Complexity Level**: L4

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Consolidated reconciliation summary |
| `orders_reconciled.json` | Full reconciliation of 10 orders with status |
| `shipping_labels_vi.json` | Vietnamese shipping labels for all orders |
| `customs_declarations_vi.json` | Vietnamese customs declarations with HS codes and duties |
| `discrepancy_report.md` | Report of discrepancies between invoices and declarations |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Reconciliation Accuracy | 0.30 | Correctness of order matching, quantity/price/HS code validation |
| Customs Compliance | 0.25 | Proper HS code classification, duty rate application, declaration format |
| Shipping Labels | 0.20 | Completeness of label information (recipient, address, postal code, weight) |
| Discrepancy Detection | 0.15 | Identification of price, quantity, and HS code mismatches |
| Vietnamese Quality | 0.10 | Natural Vietnamese language in all output documents |

## Key Challenges
- Cross-referencing data between Chinese invoices and Vietnamese customs forms
- Correct 8-digit HS code classification and corresponding duty rates
- CNY to VND currency conversion with proper handling of large numbers
- Understanding Vietnamese customs declaration requirements
- Detecting subtle discrepancies across multilingual source documents
