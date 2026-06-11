# Localisation juridique en français v2 — Glossaire obligatoire et références croisées

## Objectif

Vous êtes traducteur juridique spécialisé. Traduisez 3 documents juridiques de l'anglais vers le français. La version v2 ajoute :
1. **NOUVEAU** : Glossaire juridique obligatoire avec correspondances imposées
2. **NOUVEAU** : Cohérence des références croisées entre les 3 documents
3. **NOUVEAU** : Renumérotation correcte des notes de bas de page

## Fichiers d'entrée

- `/workspace/inputs/terms_of_service_en.md` — Conditions d'utilisation (anglais)
- `/workspace/inputs/privacy_policy_en.md` — Politique de confidentialité (anglais)
- `/workspace/inputs/cookie_policy_en.md` — Politique cookies (anglais)
- `/workspace/inputs/legal_glossary.json` — **NOUVEAU** Glossaire juridique obligatoire

## Tâches

1. Traduire les 3 documents en français juridique professionnel
2. **NOUVEAU** : Appliquer systématiquement le glossaire (termes imposés)
3. **NOUVEAU** : Vérifier que les références croisées entre documents sont correctes
4. **NOUVEAU** : Renuméroter les notes de bas de page correctement
5. Produire les rapports de conformité

## Fichiers de sortie (/workspace/output/)

### cgu_fr.md — Conditions générales d'utilisation
### privacy_policy_fr.md — Politique de confidentialité
### cookie_policy_fr.md — Politique relative aux cookies
### glossary_compliance.json
{"total_terms": 20, "correctly_applied": int, "violations": [{"term_en": str, "expected_fr": str, "actual_fr": str, "document": str}]}
### cross_reference_validation.json
{"total_references": int, "valid": int, "broken": [], "footnotes_renumbered": bool}

### /workspace/answer.json
{"documents_translated": 3, "glossary_compliance_percent": float, "cross_refs_valid": int, "cross_refs_total": int, "footnotes_correct": bool, "total_words_fr": int}

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
