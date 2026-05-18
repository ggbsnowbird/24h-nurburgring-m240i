---
title: About
---

# À propos de cette application

Cette application a été développée pour analyser les performances des pilotes de la classe **BMW M240i Racing Cup** lors du **54ème ADAC Ravenol 24h Nürburgring** (14-17 mai 2026).

---

## Ce que fait l'application

Les données proviennent de deux sources :
- **Le PDF officiel des temps secteurs** de l'organisation (ADAC / wige Solutions) — contenant les temps par tour et les 9 partiels pour chaque voiture
- **Le flux LiveTiming en temps réel** — permettant d'associer chaque tour à son heure exacte de la course (heure CEST, heure de Nürburgring)

Ces deux sources ont été croisées pour produire une base de données complète : **11 voitures · 127 stints · 791 tours valides**.

> Les outlaps (premier tour d'un relais, pneus froids / sortie des stands) et les tours de plus de 11 minutes 30 (changements de pilote, Safety Car, Code 60) sont systématiquement exclus des analyses.

---

## Les trois pages

### 1. Overview
Vue d'ensemble de la course. Le graphique principal montre **tous les tours valides** de la classe M240i sur l'axe du temps réel. Les lignes superposées représentent :
- **Minimum roulant** (vert) — le meilleur temps réalisé dans la classe sur chaque fenêtre de 60 minutes : révèle l'évolution du potentiel absolu de la piste
- **Moyenne roulante** (bleu) — la pace médiane du peloton sur la même fenêtre
- **Bande ±1σ** (grisée) — le spread du peloton, qui s'élargit visiblement lors des épisodes de pluie ou de Safety Car

### 2. Stint Rankings
Classement comparatif par relais. Pour un pilote donné, chaque relais est mis en regard de **tous les autres pilotes M240i sur la piste au même moment** — c'est la seule comparaison juste, car les conditions de piste (météo, gomme, température) sont alors identiques pour tous. La fenêtre est étendue de 4 minutes avant le début du relais pour inclure les pilotes qui finissaient leur dernier tour juste avant.

### 3. Sector Analysis — le plus intéressant

C'est selon moi la page la plus riche. Elle permet de voir **où se gagne et se perd le temps**, secteur par secteur, à l'intérieur d'un relais.

Le Nordschleife est découpé en 9 secteurs (S1 à S9). Pour chaque relais de référence, tous les pilotes présents sur la piste dans la même fenêtre temporelle sont rankés sur chaque secteur. On obtient ainsi une heatmap qui montre immédiatement :
- Sur quels secteurs un pilote est fort ou faible par rapport au peloton
- Le **delta to best** par secteur — combien de secondes sont perdues par rapport au meilleur temps de la classe sur ce tronçon
- Les secteurs où la variance est forte (conditions changeantes) vs stables

C'est cet outil qui permet de cibler précisément les zones de progrès possibles.

---

## Notes techniques

- Les temps sont exprimés en heure **CEST** (UTC+2), heure locale de Nürburgring
- Le secteur 7 (Nordschleife, ~3:30 à 4:00 min) est correctement pris en compte malgré sa durée atypique
- Des corrections manuelles ont été appliquées sur certains relais (ex. crevaison Boutonnet stint 14) et sont tracées dans l'application

---

*Application développée avec Observable Framework · Données ADAC / wige Solutions · LiveTiming*
