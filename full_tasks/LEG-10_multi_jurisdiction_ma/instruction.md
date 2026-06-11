# Revue Juridique Multi-Juridictionnelle — Opération de Fusion-Acquisition

## Contexte du projet

Dans le répertoire `/workspace/inputs/` se trouvent les documents relatifs à une opération d'acquisition transfrontalière impliquant cinq juridictions. Votre mission est de produire une analyse juridique complète en français identifiant les conflits réglementaires et les risques.

## Fichiers d'entrée

- `target_financials_zh.csv` — États financiers de la société cible chinoise (en chinois)
- `board_resolution_ja.md` — Résolution du conseil d'administration de la société mère japonaise (en japonais)
- `korean_regulatory_ko.md` — Exigences antitrust coréennes pour la notification de concentration (en coréen)
- `russian_sanctions_ru.md` — Vérification de conformité aux sanctions russes (en russe)
- `deal_structure_en.md` — Structure de l'opération et calendrier (en anglais)
- `valuation_model_en.json` — Paramètres de valorisation (en anglais)

## Exigences

### 1. Mémo de Synthèse (`memo_synthese_fr.md`)
Rédiger un mémorandum juridique complet en français comprenant :
- Résumé exécutif de l'opération
- Analyse par juridiction (Chine, Japon, Corée, Russie, structure anglaise)
- Identification des conflits réglementaires entre juridictions
- Recommandations stratégiques
- Calendrier critique avec jalons réglementaires

### 2. Registre des Conflits Réglementaires (`regulatory_conflicts.json`)
Document JSON structuré identifiant :
- Chaque conflit détecté entre juridictions
- Juridictions impliquées
- Nature du conflit
- Niveau de gravité (critique/élevé/moyen/faible)
- Impact sur le calendrier de l'opération
- Mesures d'atténuation proposées

### 3. Matrice Juridictionnelle (`jurisdiction_matrix.json`)
Matrice comparant les exigences réglementaires dans chaque juridiction :
- Approbations requises
- Délais légaux
- Seuils de notification
- Conditions suspensives

### 4. Registre des Risques (`risk_register_fr.json`)
Registre complet des risques en français :
- Description du risque
- Probabilité (1-5)
- Impact (1-5)
- Score de risque
- Propriétaire du risque
- Mesures d'atténuation

### 5. Glossaire Multilingue (`glossaire_multilingue.json`)
Glossaire des termes juridiques clés dans les 5 langues (FR, EN, ZH, JA, KO, RU)

## Points Clés à Détecter

- **Contradiction financière** : La résolution japonaise approuve une acquisition à $50M, mais les états financiers chinois montrent des actifs nets de seulement $38M
- **Seuil antitrust coréen** : Le chiffre d'affaires combiné dépasse le seuil de notification coréen
- **Sanctions russes** : Un membre du conseil d'administration est visé par des sanctions

## Résultats

Enregistrer tous les fichiers dans `/workspace/output/` et le résumé dans `/workspace/answer.json`.

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
