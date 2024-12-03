# Projet 2 : Vérificateur de Cohérence Bibliographique

### Description : 

Le Vérificateur de Cohérence Bibliographique est un outil conçu pour garantir la qualité et l'exactitude des références dans un article scientifique. Il s'adresse aux chercheurs et auteurs qui souhaitent s'assurer que leur bibliographie est en parfaite cohérence avec le contenu de l'article, évitant ainsi les oublis ou les citations incorrectes. Cet outil vérifie non seulement que toutes les références citées dans le texte apparaissent bien dans la bibliographie (et inversement), mais aussi que chaque référence est valide et existe réellement dans les bases de données académiques.

**Fonctionnalités principales** :    
1. Vérification de correspondance texte-bibliographie : Le programme analyse le corps de l'article à la recherche de toutes les citations et les compare à la liste des références bibliographiques. Il s'assure que :
- Chaque référence mentionnée dans le texte est présente dans la bibliographie.
- Chaque entrée de la bibliographie est citée au moins une fois dans le texte.
    
2. Vérification de la validité des références : En s'appuyant sur des API de bases de données académiques (telles que JSTOR, Google Scholar, HAL, ou CrossRef), l'outil vérifie que les références citées existent réellement. Il contrôle l'exactitude des informations bibliographiques (auteur, titre, année, etc.) et signale les erreurs ou les références inexistantes.
    
3. Rapport de vérification : À la fin de l'analyse, le programme génère un rapport complet :
- Une liste des citations présentes dans le texte mais manquantes dans la bibliographie.
- Une liste des références bibliographiques qui ne sont jamais citées dans le texte.
- Les références invalides ou incorrectes avec des suggestions de correction (le cas échéant).

4. Amélioration continue : L'outil peut être amélioré pour intégrer une vérification de la qualité des citations en proposant des corrections sur le format des références selon des standards (APA, MLA, etc.).

**Utilité** : Ce projet est essentiel pour garantir la rigueur académique dans les publications scientifiques. Il aide les auteurs à éviter les erreurs fréquentes de citation, à vérifier la validité des sources, et à assurer une correspondance parfaite entre le texte et la bibliographie. Cet outil est particulièrement utile pour les étudiants, les chercheurs, et les éditeurs qui souhaitent améliorer la qualité de leurs publications.

**NB** : Ce projet nécessitera l'utilisation d'API académiques (comme CrossRef, Google Scholar ou HAL) pour la validation des références, et pourra s'intégrer à des outils de traitement de texte ou de gestion de références (comme Zotero ou Mendeley).