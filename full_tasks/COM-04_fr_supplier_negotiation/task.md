# French Negotiation Memo from Chinese Supplier Quotes and English Contracts

## Overview
Tests the agent's ability to analyze Chinese supplier quotes, calculate landed costs in EUR, produce a professional French negotiation memo, and draft a counter-proposal integrating English contract terms and French market benchmarks.

## Scenario
A French company is negotiating with Chinese suppliers for 8 product references. The agent must analyze Chinese-language supplier quotes with pricing, MOQ, lead times, and payment terms; calculate complete landed costs in EUR including FOB price, maritime freight, insurance, EU customs duties, clearance fees, and inland transport; write a professional French negotiation memo with comparative analysis and strategic recommendations; compare against French market benchmarks to identify negotiation margins; draft a formal French counter-proposal; and evaluate risks across currency, delivery, quality, and supplier concentration dimensions.

## Language Configuration
- **Instruction Language**: French
- **Source Material Languages**: Chinese (supplier quotes), English (contract terms), French (logistics costs, market benchmarks)
- **Target Output Language(s)**: French
- **Complexity Level**: L4

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Summary: total landed cost, potential savings, recommended supplier, risk score |
| `memo_negociation_fr.md` | Professional French negotiation memo with analysis and recommendations |
| `landed_cost_analysis.json` | Complete landed cost breakdown per product in EUR |
| `counter_proposal_fr.md` | Formal French counter-proposal with target prices and conditions |
| `risk_matrix.json` | Risk assessment with probability and impact for each risk category |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Memo Quality (FR) | 0.30 | Professional French business writing, structure, strategic insight |
| Landed Cost Accuracy | 0.25 | Correctness of cost calculations including all cost components |
| Counter Proposal | 0.20 | Quality of counter-proposal with realistic targets and conditions |
| Risk Assessment | 0.15 | Completeness of risk matrix with probability/impact scoring |
| French Professionalism | 0.10 | Business French terminology, formal register, professional tone |

## Key Challenges
- Understanding Chinese supplier quotes with pricing conventions and trade terms
- Calculating EU-specific landed costs (customs duties, dédouanement fees)
- Professional business French writing with procurement-specific terminology
- Integrating English legal/contract terms into a French negotiation strategy
- Balancing multiple factors (cost, risk, quality) in supplier recommendations
