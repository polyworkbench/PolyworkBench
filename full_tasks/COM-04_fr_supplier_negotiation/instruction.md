# Mémo de négociation fournisseur et analyse des coûts débarqués

Dans `/workspace/inputs/` se trouvent les fichiers relatifs à une négociation d'approvisionnement avec des fournisseurs chinois pour le marché français. Votre mission est de rédiger un mémo de négociation en français, calculer les coûts débarqués en EUR, et formuler une contre-proposition.

Exigences :
- Analyser les devis fournisseurs chinois (`supplier_quotes_zh.csv`) contenant les prix unitaires, MOQ, délais de livraison et conditions de paiement pour 8 références produit
- Calculer les coûts débarqués complets en EUR (`landed_cost_analysis.json`) pour chaque référence : prix FOB, fret maritime, assurance, droits de douane UE, frais de dédouanement, transport intérieur (selon `logistics_costs_fr.json`)
- Rédiger un mémo de négociation professionnel en français (`memo_negociation_fr.md`) comprenant : contexte, analyse comparative des offres, points forts/faibles de chaque fournisseur, recommandation stratégique
- Comparer les prix avec les benchmarks du marché français (`market_benchmarks_fr.txt`) et identifier les marges de négociation potentielles
- Rédiger une contre-proposition formelle en français (`counter_proposal_fr.md`) avec : prix cibles, conditions de paiement souhaitées, engagement de volume, clauses de qualité
- Évaluer les risques (`risk_matrix.json`) : risque de change EUR/CNY, risque de délai, risque qualité, dépendance fournisseur unique, avec probabilité et impact pour chaque risque
- Intégrer les termes contractuels anglais (`contract_terms_en.md`) dans l'analyse et la contre-proposition
- Produire un fichier `answer.json` récapitulatif : coût total débarqué, économie potentielle vs. benchmark, fournisseur recommandé, score de risque global

Résultats à enregistrer dans `/workspace/output/`, synthèse finale dans `/workspace/answer.json`.

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
