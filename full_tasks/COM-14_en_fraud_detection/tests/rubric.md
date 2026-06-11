# Rubric: COM-14 Cross-Border Fraud Detection

## Overview
This task evaluates the ability to process transaction data in Russian and Vietnamese, apply English-language fraud rules, and identify fraudulent transactions.

## Scoring Criteria (7 points total)

### 1. Fraud Report Exists (1 point)
- File `fraud_report.md` exists
- References all 5 fraudulent transactions
- Comprehensive content (>500 characters)

### 2. Flagged Transactions JSON Exists (1 point)
- File `flagged_transactions.json` exists with valid JSON structure

### 3. Correct Transactions Identified (1 point)
- All 5 fraudulent transactions correctly flagged:
  - TXN-037 (velocity)
  - TXN-012 (amount anomaly)
  - TXN-041 (geographic mismatch)
  - TXN-048 (new seller high value)
  - TXN-003 (payment pattern)

### 4. Flagged Count (1 point)
- At least 5 transactions flagged

### 5. Fraud Types Assigned (1 point)
- Velocity fraud type identified
- Amount anomaly type identified
- Geographic mismatch type identified

### 6. Risk Scores Exist (1 point)
- File `risk_scores.json` exists
- Contains scores for all 5 flagged transactions

### 7. Risk Levels Correct (1 point)
- Transactions classified with appropriate severity levels (critical/high)

## Ground Truth

### Fraudulent Transactions
| TXN ID | Fraud Type | Amount | Key Indicator |
|--------|-----------|--------|---------------|
| TXN-037 | Velocity | $1,850 | 8 transactions in 10 minutes from IP 77.88.55.12 |
| TXN-012 | Amount Anomaly | $4,200 | Seller SEL-RU-110 average is $50 (84x above) |
| TXN-041 | Geographic Mismatch | $2,100 | Billing: Moscow, Shipping: Lagos, Nigeria |
| TXN-048 | New Seller + High Value | $3,800 | Account created 2024-03-16, same day as transaction |
| TXN-003 | Payment Pattern | $2,750 | 6 attempts, cardholder name change (Смирнов/Козлов) |

### Total Fraud Amount: $14,700
### Fraud Rate: 5/50 = 10%
