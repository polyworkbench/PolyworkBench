# Trilingual Patent Landscape Analysis into Japanese Report

## Overview
Tests the ability to analyze patent data from three patent offices (USPTO, CNIPA, KIPO) in English, Chinese, and Korean, producing a comprehensive Japanese patent landscape report with whitespace mapping.

## Scenario
A patent analyst needs to map the solid-state battery technology landscape. The agent must process 45 patents across three offices — 20 US patents (English CSV), 15 Chinese patents (Chinese CSV), and 10 Korean patents (Korean CSV) — classify them by IPC codes and technology taxonomy, identify filing trends, analyze top assignees, and discover technology whitespace areas. All analysis output in Japanese with professional patent analytics style.

## Language Configuration
- **Instruction Language**: Japanese
- **Source Material Languages**: English, Chinese, Korean
- **Target Output Language(s)**: Japanese
- **Complexity Level**: L5

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Summary: total_patents, top_assignee, dominant_ipc, whitespace_count, emerging_technology, year_peak_filings |
| `landscape_report_ja.md` | Japanese patent landscape report (min. 3000 characters) |
| `patent_matrix.json` | Cross-reference matrix: patents by assignee × technology category |
| `trend_analysis_ja.json` | Technology trend analysis with Japanese commentary |
| `whitespace_map.json` | Whitespace map identifying R&D opportunity areas |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Coverage Analysis | 25% | Comprehensive processing of all 45 patents |
| Trend Identification | 25% | Accurate technology trend detection |
| Japanese Quality | 20% | Professional patent analysis document quality |
| Whitespace Precision | 15% | Logical identification of technology gaps |
| Classification Accuracy | 15% | Correct IPC-to-technology category mapping |

## Key Challenges
- Processing CSV patent data in three different languages
- Correctly mapping IPC classification hierarchy to technology categories
- Identifying meaningful filing trends across jurisdictions
- Discovering whitespace areas where no patents have been filed
- Writing in professional Japanese patent analytics style
