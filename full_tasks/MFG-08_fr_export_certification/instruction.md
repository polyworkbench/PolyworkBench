# Génération de documentation CE pour l'export européen

Dans `/workspace/inputs/` vous trouverez les fichiers suivants :

- `test_reports_zh.csv` — Résultats d'essais du laboratoire chinois (en chinois)
- `en_standards_reference.json` — Normes harmonisées EN applicables (en anglais)
- `product_description_zh.md` — Description technique du produit (en chinois)
- `notified_body_info_en.txt` — Informations sur l'organisme notifié et la certification (en anglais)

## Exigences

- Analyser les rapports d'essais chinois et les mapper aux exigences des normes EN correspondantes
- Rédiger une **Déclaration UE de conformité** en français (`declaration_conformite_fr.md`) conforme au format réglementaire, incluant :
  - Identification du fabricant (nom, adresse, coordonnées)
  - Description et identification du produit
  - Référence aux directives européennes applicables (LVD 2014/35/UE, EMC 2014/30/UE, RoHS 2011/65/UE)
  - Liste des normes harmonisées appliquées
  - Mention de l'organisme notifié (le cas échéant)
  - Lieu, date et signature
- Rédiger un **rapport technique** en français (`rapport_technique_fr.md`) résumant :
  - Caractéristiques techniques du produit
  - Résultats d'essais avec correspondance norme ↔ résultat
  - Évaluation des risques
  - Conclusion de conformité
- Créer un résumé structuré des essais (`test_summary.json`) mappant chaque essai chinois à la norme EN correspondante
- Créer une checklist CE (`checklist_ce.json`) indiquant l'état de chaque exigence (conforme/non conforme/non applicable)

## Sortie

Enregistrer tous les fichiers dans `/workspace/output/` :
- `declaration_conformite_fr.md`
- `rapport_technique_fr.md`
- `test_summary.json`
- `checklist_ce.json`

Enregistrer le résumé final dans `/workspace/answer.json`.

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
