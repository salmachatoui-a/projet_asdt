# Projet ASDT — Corpus de critiques littéraires & analyse TXM

Projet universitaire de constitution d'un corpus de critiques de livres (réelles et générées par IA) suivi d'une analyse textométrique avec TXM.

---

## Objectif

Construire un corpus bipartite composé de :
- critiques **humaines** extraites de Goodreads pour les 100 livres les plus lus sur Project Gutenberg
- critiques **synthétiques** générées par un LLM local (Mistral Nemo 12b via Ollama)

puis comparer les deux sous-corpus via une analyse structurelle et lexicale dans TXM.

---

## Architecture du projet

```
projet_asdt/
├── extract_books.py       # Scraping des livres (Project Gutenberg top 100)
├── get_review.py          # Scraping des critiques Goodreads
├── main.py                # Pipeline principal : livres → critiques → JSON
├── Book.py                # Modèle Book
├── BookManager.py         # Gestionnaire de collection de livres
├── Rapport_asdt.pdf       # Rapport du projet 
├── Review.py              # Modèle Review
├── LangDetector.py        # Filtrage des critiques en anglais (lingua)
├── prompting/
│   ├── main.py            # Génération de critiques via Ollama (Mistral Nemo)
│   ├── book_cleaner.py    # Nettoyage des textes Gutenberg
│   └── count_generated_tokens.py
└── analyses_txm/
    ├── Analyse Structurelle et lexical.pdf
    └── Image analyse annexxe/
```

---

## Pipeline

### 1. Extraction des livres (Paul)

```bash
python extract_books.py
```

- Ouvre Project Gutenberg `/browse/scores/top` avec Selenium (Firefox)
- Télécharge les 100 livres les plus lus en format Plain Text UTF-8
- Exporte `book_manager.json` (titres, liens, chemins locaux)

### 2. Scraping des critiques Goodreads

```bash
python main.py
```

- Charge `book_manager.json`
- Recherche chaque livre sur Goodreads et collecte les critiques en anglais (max ~2 500 tokens / livre)
- Filtre la langue avec `lingua`
- Exporte `all_reviews.json`

### 3. Génération de critiques synthétiques

```bash
cd prompting
python main.py
```

- Nettoie les textes avec `gutenberg_cleaner`
- Envoie chaque livre (tronqué à 20 000 caractères) à Mistral Nemo 12b via Ollama
- Génère des critiques jusqu'à atteindre 250 000 tokens
- Synchronise les fichiers produits vers un serveur distant (`sync.sh`)

### 4. Analyse TXM (Marie)

Les fichiers générés sont importés dans TXM pour une analyse structurelle et lexicale comparative (critiques humaines vs. générées). Voir `analyses_txm/Analyse Structurelle et lexical.pdf`.

---

## Dépendances

| Bibliothèque | Usage |
|---|---|
| `selenium` | Scraping Gutenberg & Goodreads |
| `lingua-language-detector` | Détection de la langue (anglais) |
| `ollama` | Interface locale avec Mistral Nemo 12b |
| `gutenberg_cleaner` | Nettoyage des textes Project Gutenberg |
| `requests` | Téléchargement des livres |

**Pilotes requis :** Firefox + geckodriver (`/usr/bin/geckodriver`, `/usr/bin/firefox`)

**Modèle LLM :** `mistral-nemo:12b` via [Ollama](https://ollama.com/)

### Installation

```bash
pip install selenium lingua-language-detector ollama gutenberg-cleaner requests
```

---

## Auteurs

- **Paul** — scraping, pipeline de collecte, génération LLM
- **Marie** — analyse TXM
- **Salma, Damien** - Rapport
