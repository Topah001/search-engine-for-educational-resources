# Search Engine for Educational Resources

A small local full-text search engine that indexes the included, original
educational text samples. It uses a token-to-document inverted index and ranks
matches with normalized term frequency times a smoothed IDF weight.

## Run (Python 3.13)

```powershell
python -m edu_search resources "cells ecosystems"
python -m unittest discover -s tests -v
```

Only UTF-8 `.txt` files immediately within the supplied directory are indexed.
Results include deterministic tie-breaking, a score, and a short matching
snippet. Documents are kept in memory; there is no network access or external
content source. This intentionally small ranking model does not provide
stemming, stop-word handling, phrase search, or production-scale indexing.
