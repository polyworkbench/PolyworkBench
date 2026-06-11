# Cross-Border E-Commerce Fraud Detection

## Context

You are a fraud analyst at a global e-commerce platform. Your task is to analyze transaction data from multiple regions, apply fraud detection rules, and identify fraudulent transactions. The data comes from Russian-speaking and Vietnamese-speaking markets, with fraud rules defined in English.

## Source Data

The following files are in the `inputs/` directory:

1. **ru_transaction_logs.csv** — Transaction logs from Russian/CIS marketplace (in Russian, 30 transactions)
2. **vi_seller_data.csv** — Seller profile data from Vietnamese marketplace (in Vietnamese, 20 transactions)
3. **en_fraud_rules.md** — Fraud detection rules and thresholds (in English)

## Required Tasks

### 1. Apply Fraud Detection Rules
Process all 50 transactions against the fraud rules to identify suspicious patterns:
- Velocity checks (multiple transactions in short time)
- Amount anomalies (significantly above seller average)
- Geographic mismatches (shipping vs billing location)
- New seller + high value combination
- Multiple declined payments followed by success

### 2. Identify Fraudulent Transactions
Out of 50 total transactions, exactly **5 are fraudulent**:
- **TXN-037** — Velocity fraud: 8 transactions in 10 minutes from same IP
- **TXN-012** — Amount anomaly: $4,200 transaction from seller with $50 average
- **TXN-041** — Geographic mismatch: billing in Moscow, shipping to Lagos
- **TXN-048** — New seller fraud: account created 2 hours before $3,800 sale
- **TXN-003** — Payment pattern: 5 declined cards then success with different name

### 3. Output Files

#### fraud_report.md
Comprehensive fraud analysis report including:
- Executive summary
- Methodology applied
- Detailed findings for each flagged transaction
- Risk categorization
- Recommendations for rule updates

#### flagged_transactions.json
```json
{
  "flagged_transactions": [
    {
      "txn_id": "TXN-037",
      "fraud_type": "velocity",
      "confidence": 0.95,
      "amount_usd": 1850.00,
      "description": "8 transactions in 10 minutes from same IP address",
      "recommended_action": "block_and_review"
    },
    {
      "txn_id": "TXN-012",
      "fraud_type": "amount_anomaly",
      "confidence": 0.92,
      "amount_usd": 4200.00,
      "description": "Transaction 84x above seller average of $50",
      "recommended_action": "block_and_investigate"
    },
    {
      "txn_id": "TXN-041",
      "fraud_type": "geographic_mismatch",
      "confidence": 0.88,
      "amount_usd": 2100.00,
      "description": "Billing address Moscow, shipping to Lagos Nigeria",
      "recommended_action": "block_and_verify"
    },
    {
      "txn_id": "TXN-048",
      "fraud_type": "new_seller_high_value",
      "confidence": 0.90,
      "amount_usd": 3800.00,
      "description": "Account created 2 hours before high-value transaction",
      "recommended_action": "hold_funds"
    },
    {
      "txn_id": "TXN-003",
      "fraud_type": "payment_pattern",
      "confidence": 0.93,
      "amount_usd": 2750.00,
      "description": "5 declined payment attempts followed by success with different cardholder name",
      "recommended_action": "block_and_review"
    }
  ],
  "total_transactions_analyzed": 50,
  "total_flagged": 5,
  "total_fraud_amount_usd": 14700.00
}
```

#### risk_scores.json
```json
{
  "transaction_risk_scores": {
    "TXN-037": {"score": 95, "level": "critical"},
    "TXN-012": {"score": 92, "level": "critical"},
    "TXN-041": {"score": 88, "level": "high"},
    "TXN-048": {"score": 90, "level": "critical"},
    "TXN-003": {"score": 93, "level": "critical"}
  },
  "summary": {
    "critical_count": 4,
    "high_count": 1,
    "total_flagged": 5,
    "fraud_rate_percent": 10.0
  }
}
```

## Success Criteria

- All 5 fraudulent transactions correctly identified (TXN-037, TXN-012, TXN-041, TXN-048, TXN-003)
- Correct fraud types assigned to each transaction
- All output files generated in specified format
- Analysis demonstrates processing of Russian and Vietnamese source data

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
