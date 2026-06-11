# Recommandations de la CNIL relatives au traitement des données personnelles dans le cadre des services numériques (SaaS)

**Référence :** Délibération n° 2024-012 du 18 janvier 2024
**Objet :** Lignes directrices sur la conformité RGPD des plateformes d'analyse de données

---

## 1. Principes fondamentaux rappelés

### 1.1 Base légale du traitement (Article 6 RGPD)

La CNIL rappelle que le recours à l'intérêt légitime comme base légale pour le profilage des utilisateurs et l'entraînement de modèles d'apprentissage automatique (machine learning) nécessite une analyse de pondération documentée démontrant que :

- L'intérêt du responsable de traitement est réel, actuel et suffisamment défini
- Le traitement est nécessaire à la poursuite de cet intérêt
- Les droits et libertés des personnes concernées ne prévalent pas sur cet intérêt

**Position de la CNIL :** Le profilage à grande échelle ayant des effets significatifs sur les personnes concernées (notamment la tarification personnalisée) ne peut reposer sur le seul intérêt légitime. Le consentement explicite est requis conformément à l'article 22 du RGPD.

### 1.2 Durée de conservation

La CNIL recommande les durées maximales suivantes pour les données de plateformes SaaS :

| Type de données | Durée maximale recommandée |
|----------------|---------------------------|
| Données de compte | Durée du contrat + 3 ans (prescription) |
| Données d'utilisation | 13 mois maximum |
| Données clients (sous-traitance) | Durée du contrat + 1 an |
| Données marketing | 3 ans après dernier contact |
| Journaux serveur | 12 mois |
| Données d'entraînement ML | Durée strictement nécessaire, avec revue annuelle |

### 1.3 Consentement pour les cookies

Conformément aux lignes directrices « cookies et traceurs » (délibération n° 2020-091) :

- Le refus des cookies doit être aussi simple que leur acceptation
- Les boutons « Accepter tout » et « Refuser tout » doivent être présentés de manière équivalente
- Les cookies analytiques ne sont **pas** des cookies essentiels et nécessitent le consentement
- Le simple fait de continuer la navigation ne constitue pas un consentement valide
- Les pratiques de type « cookie wall » sont interdites sauf dans des cas très limités

---

## 2. Transferts internationaux de données

### 2.1 Post-Schrems II

Suite à l'arrêt Schrems II (CJUE, C-311/18, 16 juillet 2020), la CNIL rappelle :

- Les clauses contractuelles types (CCT) ne suffisent pas à elles seules pour les transferts vers les États-Unis
- Une **évaluation d'impact du transfert (TIA)** doit être réalisée **pour chaque flux de données** individuellement
- Les mesures supplémentaires doivent être adaptées au contexte spécifique de chaque transfert
- Le EU-US Data Privacy Framework (DPF) fournit une base d'adéquation depuis juillet 2023, mais le responsable de traitement doit vérifier que le destinataire est effectivement inscrit au DPF

### 2.2 Sous-traitants dans des pays tiers

Pour chaque sous-traitant situé hors EEE :
- Documenter la base juridique du transfert
- Réaliser une TIA spécifique
- Mettre en œuvre des mesures supplémentaires (chiffrement, pseudonymisation, etc.)
- Informer les personnes concernées du transfert et des garanties

---

## 3. Analyse d'Impact relative à la Protection des Données (AIPD)

### 3.1 Cas nécessitant une AIPD (Article 35 RGPD)

La CNIL a publié une liste de traitements nécessitant une AIPD. Parmi ceux-ci :

- Profilage systématique et automatisé produisant des effets juridiques ou significatifs
- Traitement à grande échelle de données sensibles (santé, données financières)
- Surveillance systématique à grande échelle (tracking comportemental)
- Combinaison de jeux de données provenant de sources multiples
- Utilisation innovante de technologies (IA, apprentissage automatique)

**Application aux plateformes d'analyse :** Une plateforme SaaS qui effectue du profilage automatisé influençant la tarification, des décisions automatiques, ou qui traite des données sensibles à grande échelle est **tenue** de réaliser une AIPD avant le déploiement du traitement.

### 3.2 Contenu de l'AIPD

L'AIPD doit inclure :
- Description systématique du traitement
- Évaluation de la nécessité et de la proportionnalité
- Évaluation des risques pour les droits et libertés
- Mesures envisagées pour atténuer les risques

---

## 4. Droits des personnes concernées

### 4.1 Délais de réponse

- Délai standard : **1 mois** à compter de la réception de la demande
- Extension possible : **2 mois** supplémentaires en cas de complexité (avec information du demandeur dans le premier mois)
- **Attention :** Un délai de 45 jours (courant dans les pratiques américaines) n'est **pas** conforme au RGPD qui impose un délai d'un mois calendaire

### 4.2 Droit d'opposition au profilage

- Le droit d'opposition doit être exercé sans frais
- La procédure doit être simple et accessible (pas uniquement par email à un service support)
- Le responsable de traitement doit informer de ce droit de manière claire et distincte

---

## 5. Obligations du responsable de traitement

### 5.1 Information des personnes (Articles 13-14 RGPD)

La politique de confidentialité doit :
- Être rédigée en termes clairs et simples
- Préciser la durée de conservation pour chaque catégorie de données
- Détailler les destinataires ou catégories de destinataires
- Informer de l'existence de décisions automatisées et du droit de s'y opposer
- Mentionner le droit de déposer une réclamation auprès d'une autorité de contrôle

### 5.2 Notification des modifications

- Toute modification substantielle de la politique de confidentialité doit faire l'objet d'un consentement renouvelé (et non d'une simple notification)
- La poursuite de l'utilisation du service ne peut constituer un consentement implicite
