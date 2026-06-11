# Recommandations de la CNIL relatives au traitement de données à caractère personnel à des fins d'analyse comportementale

**Référence :** Délibération n° 2023-089 du 14 septembre 2023
**Objet :** Lignes directrices sur les cookies et autres traceurs – Mise à jour 2023

---

## 1. Principes généraux applicables aux traceurs

### 1.1 Consentement préalable

Conformément à l'article 82 de la loi Informatique et Libertés et à l'article 5(3) de la directive ePrivacy :

- **Le consentement doit être libre, spécifique, éclairé et univoque** (article 4(11) du RGPD)
- Le dépôt de cookies analytiques nécessite le consentement préalable de l'utilisateur, sauf exception prévue pour les cookies strictement nécessaires
- **L'absence d'action ne peut être assimilée à un consentement** (pas de consentement par défilement, ni par poursuite de la navigation)
- Le consentement recueilli par une case pré-cochée n'est pas valide (arrêt CJUE, Planet49, C-673/17)

### 1.2 Modalités de recueil du consentement

La CNIL exige que :

- Un bouton **« Tout refuser »** soit proposé au même niveau et avec le même format que le bouton « Tout accepter »
- Les utilisateurs puissent **refuser les cookies aussi facilement qu'ils les acceptent**
- L'interface ne doit pas utiliser de « dark patterns » (schémas trompeurs)
- Le bandeau de cookies ne doit pas être conçu pour inciter l'utilisateur à accepter (couleurs, taille, positionnement)
- La poursuite de la navigation **ne constitue pas** un consentement valide

### 1.3 Information des personnes

- L'identité de tous les responsables de traitement et destinataires doit être clairement indiquée
- Les finalités de chaque traceur doivent être décrites de manière intelligible
- La durée de conservation des traceurs et des données collectées doit être précisée

## 2. Durée de conservation des données

### 2.1 Cookies et traceurs

- La durée de vie d'un cookie ne doit pas excéder **13 mois** à compter du premier dépôt
- Le consentement doit être renouvelé au terme de cette période de 13 mois

### 2.2 Données collectées par les traceurs

- Les données à caractère personnel collectées par l'intermédiaire de traceurs ne doivent pas être conservées au-delà de **25 mois** à compter de leur collecte
- Au-delà, les données doivent être supprimées ou irréversiblement anonymisées
- La conservation à des fins statistiques au-delà de 25 mois requiert une anonymisation complète et irréversible

### 2.3 Profils comportementaux

- Les profils créés à partir de données de navigation ne doivent pas être conservés plus de **12 mois** sans renouvellement du consentement
- Les scores et inférences doivent être supprimés en même temps que les données sources

## 3. Transferts internationaux de données

### 3.1 Conséquences de l'arrêt Schrems II (CJUE, 16 juillet 2020, C-311/18)

- L'invalidation du Privacy Shield implique que le simple recours aux Clauses Contractuelles Types (CCT/SCC) **ne suffit pas** à garantir un niveau de protection adéquat pour les transferts vers les États-Unis
- Le responsable de traitement doit réaliser une **évaluation d'impact du transfert** (Transfer Impact Assessment - TIA)
- Des **mesures supplémentaires** (techniques, organisationnelles, contractuelles) doivent être mises en œuvre si la législation du pays tiers ne garantit pas un niveau de protection essentiellement équivalent
- Le chiffrement de bout en bout, avec clés détenues exclusivement dans l'UE, est recommandé comme mesure technique supplémentaire
- L'hébergement des données dans des centres de données situés dans l'UE/EEE est privilégié

### 3.2 Exigences documentaires

- Documentation de l'évaluation du niveau de protection du pays tiers
- Inventaire des mesures supplémentaires mises en place
- Réévaluation régulière (au moins annuelle)

## 4. Analyse d'Impact relative à la Protection des Données (AIPD)

### 4.1 Cas dans lesquels une AIPD est obligatoire

Conformément à l'article 35 du RGPD et à la liste publiée par la CNIL, une AIPD est obligatoire notamment lorsque le traitement :

- Met en œuvre du **profilage** produisant des effets juridiques ou affectant significativement les personnes
- Porte sur des données à grande échelle
- Combine des ensembles de données
- Implique un **suivi systématique** des personnes (tracking comportemental)
- Concerne des personnes vulnérables (dont les mineurs)
- Met en œuvre de la prise de décision automatisée

### 4.2 Contenu de l'AIPD

L'AIPD doit comprendre :
- Description systématique des opérations de traitement
- Évaluation de la nécessité et de la proportionnalité
- Évaluation des risques pour les droits et libertés
- Mesures envisagées pour faire face aux risques
- Consultation préalable de la CNIL si les risques résiduels demeurent élevés

## 5. Droits des personnes concernées

### 5.1 Délais de réponse

- Le responsable de traitement doit répondre aux demandes d'exercice des droits dans un délai d'**un mois** (article 12(3) du RGPD)
- Ce délai peut être prolongé de deux mois supplémentaires en cas de complexité, sous réserve d'informer la personne dans le délai initial d'un mois
- Le délai de 60 jours mentionné dans certaines politiques de confidentialité **n'est pas conforme** au RGPD

### 5.2 Gratuité

- L'exercice des droits est en principe gratuit
- Des frais raisonnables ne peuvent être facturés qu'en cas de demandes manifestement infondées ou excessives

## 6. Sanctions

- La CNIL peut prononcer des amendes administratives allant jusqu'à 20 millions d'euros ou 4% du chiffre d'affaires annuel mondial
- Les manquements relatifs au consentement constituent les infractions les plus fréquemment sanctionnées
- En 2023, la CNIL a prononcé des sanctions de 40 millions d'euros (Criteo) et 8 millions d'euros pour des manquements liés aux cookies
