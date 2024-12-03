# Projet_Python

## Arborescence
```
Projet_Python/
├── data/
├── output/
├── grobid/
└── scripts/
    └── grobid_extraction.py
```

## Extraction Reference et Citation à l'aide de [GROBID](https://github.com/kermitt2/grobid/tree/master)
```bash
[Projet_Python]$ python3 scripts/grobid_extraction.py
```

Va télécharger le zip de GROBID, puis l'unzipper pour utiliser processFullText, afin d'obtenir les fichier XML des PDFs, avec les annotations suivantes :

Les balises XML générées incluent :

- `ref` : Pour les marqueurs de référence bibliographique, de figure, de tableau et de formule  
  *Exemple : (Toto et al. 1999), voir Fig. 1, comme montré par la formule (245), etc.*

- `biblStruct` : Pour une référence bibliographique

- `persName` : Pour un nom d'auteur complet

- `figure` : Pour les figures ET les tableaux

- `formula` : Pour les équations mathématiques

- `head` : Pour les titres de section

- `s` : Pour la structure optionnelle des phrases  
  *Note : le service GROBID fulltext doit être appelé avec le paramètre segmentSentences pour fournir les éléments optionnels au niveau des phrases*

- `p` : Pour la structure des paragraphes

- `note` : Pour les éléments de notes de bas de page

- `title` : Pour les éléments de titre  
  *Inclut le titre principal de l'article et titres des références citées*

- `affiliation` : Pour la partie affiliation et adresse
