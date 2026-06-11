# Fraud Detection Rules & Thresholds

## Version: 2024-Q1
## Last Updated: 2024-03-01
## Classification: Internal Use Only

---

## Rule 1: Velocity Check

**Description:** Detects multiple transactions from the same source in a short time period.

**Thresholds:**
- CRITICAL: ≥5 transactions from same IP within 15 minutes
- HIGH: ≥3 transactions from same IP within 10 minutes
- MEDIUM: ≥3 transactions from same seller within 30 minutes

**Action:** Block all subsequent transactions, review first transaction.

**Indicators:**
- Same IP address across multiple transactions
- Same seller ID with different buyer IDs
- Shipping to multiple different cities in rapid succession

---

## Rule 2: Amount Anomaly

**Description:** Transaction amount significantly deviates from seller's historical average.

**Thresholds:**
- CRITICAL: Transaction > 50x seller's average transaction value
- HIGH: Transaction > 20x seller's average transaction value
- MEDIUM: Transaction > 10x seller's average transaction value

**Seller Average Baselines (from last 90 days):**
- SEL-RU-110: Average $50.00 (established seller, books category)
- SEL-RU-114: Average $120.00 (electronics)
- SEL-VN-299: No history (new account)

**Action:** Hold funds, request verification documentation.

---

## Rule 3: Geographic Mismatch

**Description:** Billing location does not match shipping destination, especially cross-border to high-risk regions.

**High-Risk Destinations:**
- Nigeria (Lagos, Abuja)
- Ghana (Accra)
- Cameroon (Douala)
- Philippines (Manila) - above $1000

**Thresholds:**
- CRITICAL: Billing in Russia/CIS + Shipping to West Africa
- HIGH: Billing and shipping in different countries + amount > $1000
- MEDIUM: Billing and shipping in different cities within same country + amount > $2000

**Action:** Block transaction, require address verification.

---

## Rule 4: New Seller + High Value

**Description:** Recently created seller accounts attempting high-value transactions.

**Thresholds:**
- CRITICAL: Account age < 24 hours AND transaction > $2000
- HIGH: Account age < 7 days AND transaction > $1000
- MEDIUM: Account age < 30 days AND transaction > $500 AND no reviews

**Indicators:**
- Account creation timestamp very close to first transaction
- No seller reviews or rating of 0.0
- First transaction significantly above platform average

**Action:** Hold funds for 14 days, require identity verification.

---

## Rule 5: Payment Pattern Anomaly

**Description:** Multiple failed payment attempts followed by success, especially with different card details.

**Thresholds:**
- CRITICAL: ≥4 declines + success with different cardholder name
- HIGH: ≥3 declines + success with same card
- MEDIUM: ≥2 declines + success within 5 minutes

**Indicators:**
- Multiple payment attempts (attempts > 3)
- Different cardholder names in the transaction record (indicated by "/" separator)
- Rapid succession of attempts

**Action:** Block transaction, flag for manual review, notify card issuer.

---

## Composite Scoring

Risk scores are calculated as:
- Base score from highest matching rule severity (CRITICAL=85, HIGH=70, MEDIUM=50)
- +5 points for each additional rule matched
- +5 points for amount > $2000
- +3 points for cross-border element
- Maximum score: 100

## Response Actions by Score

| Score Range | Level | Action |
|------------|-------|--------|
| 90-100 | Critical | Immediate block, escalate to fraud team |
| 80-89 | High | Block transaction, automated review |
| 70-79 | Medium | Hold for manual review |
| 50-69 | Low | Flag for monitoring |
| 0-49 | Normal | No action |

---

## Notes
- All rules apply regardless of transaction currency or marketplace language
- Seller history should be evaluated across all marketplaces (RU + VN)
- When in doubt, prefer false positives over missed fraud
