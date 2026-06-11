# Chinese Product Catalog to Russian Marketplace Listings

## Overview
Tests the agent's ability to adapt a Chinese supplier product catalog into localized Russian marketplace listings for Ozon, requiring marketing adaptation, SEO optimization, size conversion, and regulatory compliance tagging.

## Scenario
A cross-border e-commerce operation needs to list 20 products from a Chinese supplier on the Russian marketplace Ozon. The agent must perform marketing-quality localization (not literal translation) of product titles and descriptions into Russian, generate Russian SEO keywords for each product, convert Chinese sizing to Russian sizing standards, add Russian regulatory compliance tags (TR TS / EAC marking), create a validation script for Ozon mandatory fields, and calculate recommended retail prices in rubles using provided exchange rates.

## Language Configuration
- **Instruction Language**: Russian
- **Source Material Languages**: Chinese (product catalog), English (brand guidelines)
- **Target Output Language(s)**: Russian
- **Complexity Level**: L3

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Consolidated summary results |
| `listings_ru.json` | 20 adapted Russian product cards with all required Ozon fields |
| `seo_keywords_ru.txt` | SEO keywords in Russian (5-8 per product) |
| `size_conversion_table.json` | CN-to-RU size correspondence table |
| `compliance_tags.json` | Russian regulatory compliance tags (TR TS, EAC) |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Listings Quality | 0.35 | Product count, Russian language quality, field completeness, pricing accuracy |
| SEO Keywords | 0.20 | Presence, Russian language, coverage across all products |
| Size Conversion | 0.15 | CN-to-RU mapping presence and accuracy of size values |
| Compliance Tags | 0.20 | TR TS and EAC marking references with specific regulation numbers |
| Validation Script | 0.10 | Existence of a Python validation script for Ozon field completeness |

## Key Challenges
- Marketing-quality adaptation (not literal translation) from Chinese to Russian
- Domain knowledge of Russian e-commerce platform (Ozon) mandatory fields
- Knowledge of Russian regulatory standards (TR TS technical regulations, EAC conformity marking)
- CN-to-RU clothing/shoe size conversion standards
- Currency conversion with proper ruble pricing conventions
