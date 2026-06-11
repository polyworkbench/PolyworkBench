# Due Diligence M&A — mémo préliminaire

Les fichiers dans `/workspace/inputs/` contiennent le dossier de due diligence pour l'acquisition d'AsiaCommerce Holdings : états financiers chinois (CSV), PV du conseil japonais, registre coréen, taux de change, et draft du SPA.

J'ai besoin d'un mémo DD complet en français avec :
- Analyse financière sur 3 ans (CNY → EUR, croissance, ratios) — fais un script Python pour extraire et calculer
- Détection des contradictions entre sources (il y a un écart de ~1亿 CNY sur le net income entre deux docs, trouve-le)
- Registre des risques (≥ 5 risques, sévérité, source, mitigation)
- Glossaire 5 langues (fr/en/zh/ja/ko)
- Checklist de closing avec conditions suspensives
- Analyse de valorisation (prix vs multiples)
- Traçabilité : chaque affirmation doit citer sa source

Résultats dans `/workspace/output/`, consolidation dans `/workspace/answer.json`.

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash/shell 命令创建目录、写文件、执行脚本。**
