# Audit de conformité RGPD : Analyse multi-juridictionnelle

## Mission

Vous disposez de la politique de confidentialité (en anglais) d'une entreprise SaaS, des orientations de la CNIL (en français), d'une décision de justice allemande sur le consentement, et d'une description des flux de données. Réalisez un audit RGPD complet et produisez un rapport en français.

## Fichiers d'entrée

- `/workspace/inputs/privacy_policy_en.md` — Politique de confidentialité de l'entreprise (anglais)
- `/workspace/inputs/cnil_guidance_fr.md` — Recommandations de la CNIL sur le traitement des données (français)
- `/workspace/inputs/german_ruling_de.txt` — Décision du tribunal allemand sur les exigences de consentement (allemand)
- `/workspace/inputs/data_flows_en.json` — Description des flux de données de l'entreprise (anglais)

## Exigences

- Analyser la politique de confidentialité au regard du RGPD, des recommandations CNIL et de la jurisprudence allemande
- Produire un rapport d'audit complet (`rapport_audit_fr.md`) identifiant toutes les non-conformités
- Créer une matrice de conformité (`conformite_matrix.json`) : pour chaque article pertinent du RGPD, indiquer le statut (conforme/non-conforme/partiellement conforme)
- Élaborer un plan d'action (`plan_action_fr.json`) : mesures correctives avec priorité et délais
- Rédiger une synthèse des risques (`synthese_risques_fr.md`) avec analyse d'impact
- Identifier spécifiquement les violations relatives à : mécanisme de consentement (Schrems II), durée de conservation, AIPD pour le profilage
- Utiliser la terminologie juridique française (responsable de traitement, sous-traitant, personne concernée, etc.)
- Dans answer.json indiquer : `{"total_nonconformities": int, "critical_issues": int, "schrems_ii_violation": bool, "dpia_required": bool}`

## Livrables

Enregistrer les résultats dans `/workspace/output/` :
- `/workspace/output/rapport_audit_fr.md`
- `/workspace/output/conformite_matrix.json`
- `/workspace/output/plan_action_fr.json`
- `/workspace/output/synthese_risques_fr.md`

Synthèse finale : `/workspace/answer.json`

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
