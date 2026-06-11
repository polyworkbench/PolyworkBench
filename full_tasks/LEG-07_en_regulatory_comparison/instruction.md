# Comparative Analysis of Asian Data Protection Regulations

## Background

Your company is expanding into four Asian markets (China, South Korea, Vietnam, Japan) and needs a comprehensive comparative analysis of their data protection regulations to develop a unified compliance strategy.

## Input Files

In `/workspace/inputs/` you will find:

- `pipl_china_zh.md` — Key excerpts from China's Personal Information Protection Law (PIPL) in Chinese
- `pipa_korea_ko.md` — Key excerpts from South Korea's Personal Information Protection Act (PIPA) in Korean
- `pdpd_vietnam_vi.md` — Key excerpts from Vietnam's Personal Data Protection Decree (PDPD) in Vietnamese
- `appi_japan_ja.md` — Key excerpts from Japan's Act on Protection of Personal Information (APPI) in Japanese
- `comparison_framework_en.json` — Framework with comparison dimensions and evaluation criteria

## Requirements

- Read and analyze each regulation in its original language
- Create a comprehensive comparative analysis document (`comparative_analysis.md`) in English covering:
  - Scope and applicability of each regulation
  - Data subject rights comparison
  - Cross-border transfer mechanisms
  - Consent requirements
  - Breach notification obligations
  - Penalties and enforcement
  - Data Protection Officer requirements
- Generate a structured regulation matrix (`regulation_matrix.json`) mapping each requirement dimension across all 4 jurisdictions
- Produce a gap summary (`gap_summary.json`) identifying key differences and potential conflicts between jurisdictions
- Develop a compliance roadmap (`compliance_roadmap.json`) with prioritized action items, timelines, and estimated effort

## Output

Save all results to `/workspace/output/` and a summary to `/workspace/answer.json`.

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
