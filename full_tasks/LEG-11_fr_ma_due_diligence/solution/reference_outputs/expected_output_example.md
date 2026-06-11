# Mémorandum de Due Diligence Préliminaire

**Cible** : AsiaCommerce Holdings Pte. Ltd. (Singapour) et ses filiales opérationnelles (RPC, Japon, Corée du Sud)
**Acquéreur** : LuxParis Holdings S.A.
**Date** : 2024-11-20
**Auteur** : Agent DD (auto-généré, à valider par le cabinet d'arbitrage parisien)
**Statut** : Préliminaire — version 1.0

---

## 1. Synthèse Exécutive

L'acquisition envisagée pour un prix de base de **280 M EUR** présente un profil de risque **modéré à élevé**, principalement en raison de :

(i) une **divergence comptable non résolue** d'environ **100 M CNY** sur le résultat net consolidé 2023 entre les comptes du siège chinois et la déclaration faite au conseil d'administration japonais, à clarifier impérativement avant la signature [Source: board_minutes_ja.txt, lignes 35-45 ; financials_zh.csv, ligne 4] ;

(ii) un **contentieux fiscal coréen actif** d'un montant maximal de **12 milliards KRW (≈ 8,5 M EUR)** devant le Tribunal administratif de Séoul, dont le jugement de première instance n'est attendu qu'au T2 2025 [Source: corporate_registry_ko.txt, section "계류 중 사건" ; board_minutes_ja.txt, ligne 40] ;

(iii) une **gouvernance dispersée** sur quatre juridictions, avec un actionnariat coréen incluant un nantissement bancaire de 5 % auprès de Woori Bank [Source: corporate_registry_ko.txt, table actionnariat] ;

(iv) le **droit applicable anglais** et l'arbitrage à Singapour selon les règles ICC, ce qui s'écarte des standards habituels du Groupe (droit français / arbitrage CCI Paris) [Source: spa_draft.md, §7].

Sous réserve de la résolution de la divergence comptable et d'un mécanisme adéquat de cantonnement (escrow / specific indemnity) du contentieux coréen, la transaction reste **recommandée pour passer en phase 2 de DD**.

## 2. Structure Capitalistique de la Cible (filiale coréenne)

| Actionnaire | Actions | Quote-part |
|---|---|---|
| AsiaCommerce Holdings Pte. Ltd. (Singapour) | 800 000 | 80,00 % |
| Park Ji-hoon (DG) | 100 000 | 10,00 % |
| Kim Cheol-soo | 50 000 | 5,00 % |
| Woori Bank (nantissement, sans droit de vote) | 50 000 | 5,00 % |

Capital social : **5 Mrd KRW (≈ 3,33 M EUR au taux spot 2024-10-25)**

[Source: corporate_registry_ko.txt, sections 자본금 et 주주명부]

**Point d'attention** : le nantissement Woori Bank doit faire l'objet d'une mainlevée préalable au Closing ou d'une cession spécifique consentie par la banque.

## 3. Performance Financière 2021-2023 (consolidée groupe)

Conversion en EUR aux taux moyens annuels CNY/EUR fournis (cf. inputs/fx_rates.json) :

| Indicateur | 2021 | 2022 | 2023 |
|---|---|---|---|
| Chiffre d'affaires (M CNY) | 985,0 | 1 243,0 | 1 568,0 |
| Chiffre d'affaires (M EUR) | 129,6 | 175,4 | 204,6 |
| Résultat net (M CNY, source siège chinois) | 82,0 | 115,0 | **152,0** |
| Résultat net (M CNY, déclaré au CA japonais) | n/a | n/a | **142,0** ⚠️ |
| Résultat net (M EUR, hypothèse haute / source CN) | 10,8 | 16,2 | 19,8 |
| Résultat net (M EUR, hypothèse basse / source JP) | n/a | n/a | 18,5 |

**Croissance CA** : +29,5 % (2022) puis +26,1 % (2023) — trajectoire saine.
**Marge nette** : ~9,7 % (2023, hypothèse haute) — cohérente avec le secteur e-commerce premium.

[Source: financials_zh.csv ; board_minutes_ja.txt, lignes 35-55 ; fx_rates.json]

⚠️ **Drapeau rouge financier majeur** : écart d'environ **10 M CNY (≈ 1,3 M EUR)** sur le résultat net 2023 entre la source chinoise (152 M) et la communication japonaise (142 M). Le PDG de la filiale chinoise attribue l'écart au traitement de consolidation de la sous-filiale hongkongaise [Source: board_minutes_ja.txt, ligne 50]. **Recommandation** : exiger un audit complémentaire par un Big Four avant signature.

## 4. Gouvernance et Résolutions Récentes

Le procès-verbal du Conseil d'administration du 18 octobre 2024 (Tokyo) atteste :

- Présence des dirigeants des trois filiales opérationnelles ;
- Communication de la divergence comptable (cf. §3 supra) ;
- Communication explicite du contentieux fiscal coréen, avec exposition maximale chiffrée à 12 Mrd KRW [Source: board_minutes_ja.txt, ligne 60] ;
- **Mandat unanime** donné aux dirigeants exécutifs pour négocier la transaction et conduire les diligences supplémentaires [Source: board_minutes_ja.txt, lignes 80-85].

**Points d'incertitude** : la transcription audio comporte des balises `[unclear]` autour des chiffres financiers exacts (lignes 42-50), reflétant une qualité ASR imparfaite. Une copie écrite signée du procès-verbal devra être obtenue.

## 5. Termes Clés du SPA

| Sujet | Stipulation | Évaluation |
|---|---|---|
| Prix de base | 280 M EUR, paiement intégralement en numéraire | Conforme aux pratiques de marché |
| Ajustement du prix | Au pair sur la variation du BFR cible (18 M EUR) | Standard |
| Conditions précédentes | Autorisations antitrust UE/SAMR/JFTC ; consentements clients ≥ 80 % du CA 2023 ; **résolution du contentieux coréen** | La condition (e) est très contraignante au regard du calendrier judiciaire (T2 2025) |
| Représentations & Garanties | Comptes fidèles ; absence de passifs non divulgués > 500 K EUR ; conformité PIPL/APPI/PIPA | Standard, à compléter par des warranties spécifiques sur les sujets §3 et §4 |
| Plafonds d'indemnités | Cap général 25 % (70 M EUR) ; basket 100 K / 1 M EUR ; survie 24 mois (général), 7 ans (fiscal) | Plafond légèrement bas pour une opération de cette taille ; **survie fiscale 7 ans appropriée** au regard du litige coréen |
| Droit applicable / arbitrage | Droit anglais ; arbitrage CCI siège Singapour, langue anglaise, procédures supplémentaires SIAC | **Divergence avec les standards du Groupe** ; à renégocier (cf. §7 ci-dessous) |

[Source: spa_draft.md, §§ 2–7]

## 6. Drapeaux Rouges (Synthèse)

1. **🔴 Critique** — Divergence comptable RN 2023 (10 M CNY)
2. **🟠 Élevé** — Contentieux fiscal coréen (jusqu'à 8,5 M EUR), CP non maîtrisable au regard du calendrier
3. **🟠 Élevé** — Nantissement Woori Bank sur 5 % du capital coréen
4. **🟡 Moyen** — Droit anglais / arbitrage Singapour incompatible avec la pratique du Groupe
5. **🟡 Moyen** — Cap d'indemnité à 25 % (70 M EUR) potentiellement insuffisant si matérialisation simultanée des risques 1 et 2
6. **🟡 Moyen** — Conformité PIPL/APPI/PIPA non documentée (R&W §5(e) seul ne suffit pas)

## 7. Recommandations / Prochaines Étapes

1. **Avant signature** : audit complémentaire Big Four sur les comptes 2023 (focus sous-filiale HK) — délai 30 j.
2. **Avant signature** : demander l'inscription d'une **specific indemnity** dédiée au contentieux coréen, sans plafond ni basket, avec escrow d'au moins 10 M EUR.
3. **Renégocier §7 SPA** : proposer droit français / arbitrage CCI Paris, ou à défaut maintenir le droit anglais mais déplacer le siège à Paris.
4. **Augmenter le cap général** d'indemnité de 25 % à 30 % au minimum.
5. **Obtenir mainlevée écrite** de Woori Bank avant Closing.
6. **Documenter conformité PIPL/APPI/PIPA** : audit dédié protection des données.
7. **Prolonger la survie générale** des R&W de 24 à 36 mois.

---

> *Le présent mémorandum est rédigé sous réserve de la confirmation des éléments factuels par les sources primaires (audit, registres officiels, contrat signé) et ne saurait être interprété comme un avis juridique définitif au sens de l'article 54 de la loi n° 71-1130 du 31 décembre 1971.*
