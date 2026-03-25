# Guide.Analyst - Struttura Progetto

## 📁 Cartella Principale
```
Analyst.lol/
├── Guide.Analyst.Unified.py     # Applicazione unificata principale
├── Guide.Analyst.py              # Applicazione base
├── .git/                         # Repository Git
├── Development_Files/            # File di sviluppo e test
└── src/                          # Codice sorgente
```

## 📁 Cartella Development_Files
Contiene file di sviluppo non necessari per l'esecuzione:
- `.cache/` - Cache Python
- `.pytest_cache/` - Cache test
- `.venv/` - Ambiente virtuale
- `debug_flet.py` - Debug script
- `guide_analyst_opencode_prompt.*` - Documentazione prompt
- `output.log` - Log di output
- `.deps_installed` - Marker dipendenze
- `.env` - Variabili ambiente
- `test_imports.py` - Script test
- `tests/` - Cartella test

## 📁 Cartella src
Codice sorgente pulito e ottimizzato:
```
src/
├── .gitignore                     # File ignorati da Git
├── README.md                      # Documentazione
├── app.py                         # Entry point applicazione
├── requirements.txt               # Dipendenze Python
├── core/                          # Servizi core
│   ├── datadragon.py             # Data Dragon service
│   └── riot_api.py               # Riot API service
└── views/                         # Interfacce utente
    ├── team_builder.py           # Team builder avanzato
    ├── agentic_console.py        # Console agentica
    ├── summoner_search.py        # Ricerca summoner
    ├── analytics.py              # Analisi statistiche
    └── pro_players.py            # Database pro players
```

## 🚀 Avvio
Eseguire `Guide.Analyst.Unified.py` per avviare l'applicazione completa con tutte le ottimizzazioni applicate.
