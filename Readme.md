# Paraglide Compet Analytics

## Description

Cet outils permet d'automatiser l'extraction d'information depuis les trace GPS de pilotes durant une compétition. Il permet de récupérer pour chaque compétiteurs, les horaires de passage des balises et d'extraire le tout au format CSV.

## Rendu

L'export CSV permet de récupérer ce types de données.

![](img/renduCsv.png)

Une fois, les données traitées dans une feuille de calcul préparée voici le rendu final:

![](img/renduFinal.png)

Cet exemple de feuille de calcul est disponible à [`./calc/rendu.ods`](calc/rendu.ods).

## Entrées

### Task

L'outils prend en entrée le descriptif de la manche au format FSTask. Le site [vololiberomontecucco.it](http://www.vololiberomontecucco.it/taskcreator/) permet de générer le descriptif de la manche et de l'exporter.

### Traces GPS

#### Méthode simple

Les traces GPS des pilotes doivent être au format IGC. Il est possible de les récupérer sur le [site de la  FFVL](https://parapente.ffvl.fr) à la page de chaque compétition.

![](img/downloadIGC.png)

Cette méthode à l'avantage d'être simple mais ne permet pas de récupérer les traces de tous les pilotes.

#### Avec le logiciel Cargol

Il est possible de récupérer le projet Cargol de la compétition sur le [site de la  FFVL](https://parapente.ffvl.fr) à la page de chaque compétition.

![](img/downloadCargol.png)

Ensuite avec le logiciel [Cargol](https://parapente.ffvl.fr/telecharger-cargol), il faut charger le fichier .cpt contenu dans le zip. Selectionnez "Pointage & Traces"

![](img/cargolMenu.png)

Puis "Exporter" > "Toutes les traces en IGC" 

![](img/cargolExport.png)

Les traces se trouvent, en partant du dossier contenant le fichier .cpt: `<dossierAuNomDuCpt>/Export/Manche X/`.

