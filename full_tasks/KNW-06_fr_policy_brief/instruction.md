# Note de politique : Régulation de l'intelligence artificielle

Dans `/workspace/inputs/` se trouvent des documents de recherche multilingues sur la gouvernance de l'IA :

- `policy_paper_en.md` — article de politique sur la gouvernance de l'IA (anglais)
- `china_ai_policy_zh.md` — extraits du plan de développement de l'IA du gouvernement chinois (chinois)
- `russia_analysis_ru.md` — analyse d'un think-tank russe sur la gouvernance de l'IA (russe)
- `eu_ai_act_summary_fr.txt` — résumé de l'AI Act européen (français, pour contexte)
- `statistics_en.json` — statistiques du marché mondial de l'IA (anglais)

## Exigences

- Rédiger une **note de politique** en français (`note_politique_fr.md`) de 1500–2500 mots synthétisant les trois perspectives (américaine, chinoise, russe) sur la régulation de l'IA
- La note doit suivre la structure classique : contexte, enjeux, analyse comparative, recommandations
- Créer un fichier `synthese_sources.json` avec pour chaque source : titre, langue d'origine, points clés extraits (en français), et pertinence pour la politique européenne (note 1–5)
- Produire un fichier `recommandations_fr.json` contenant au minimum 6 recommandations structurées (titre, description, priorité haute/moyenne/basse, horizon temporel court/moyen/long terme, sources appuyant la recommandation)
- Créer une `bibliographie.json` au format structuré (auteur, titre, année, langue, type de document)
- Intégrer les statistiques du marché dans l'analyse (au moins 5 chiffres clés cités)
- Le style doit être celui d'une note de politique française officielle (vocabulaire institutionnel, formulations impersonnelles, structure argumentative rigoureuse)

## Sorties attendues

Enregistrer tous les fichiers dans `/workspace/output/` :
- `note_politique_fr.md`
- `synthese_sources.json`
- `recommandations_fr.json`
- `bibliographie.json`

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
