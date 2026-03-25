"""
config.py — Legge/scrive settings da .env e settings.json
"""
import json
import os
from pathlib import Path
from dotenv import load_dotenv, set_key, dotenv_values

BASE_DIR = Path(__file__).parent.parent
ENV_FILE = BASE_DIR.parent / "Development_Files" / ".env"
SETTINGS_FILE = BASE_DIR / "settings.json"


def load_env() -> dict:
    """Carica tutte le variabili dal file .env."""
    if not ENV_FILE.exists():
        ENV_FILE.touch()
    return dotenv_values(str(ENV_FILE))


def get_env(key: str, default: str = "") -> str:
    """Ottieni un singolo valore dal .env."""
    values = load_env()
    return values.get(key, os.environ.get(key, default))


def set_env(key: str, value: str):
    """Salva/aggiorna una chiave nel .env."""
    if not ENV_FILE.exists():
        ENV_FILE.touch()
    set_key(str(ENV_FILE), key, value)


def read_env_raw() -> str:
    """Leggi il contenuto grezzo del file .env."""
    if ENV_FILE.exists():
        return ENV_FILE.read_text(encoding="utf-8")
    return "# Inserisci le tue API keys qui\n"


def write_env_raw(content: str):
    """Scrivi direttamente il contenuto del file .env."""
    ENV_FILE.write_text(content, encoding="utf-8")


def load_settings() -> dict:
    """Carica settings JSON dell'app (preferenze UI, stato)."""
    if SETTINGS_FILE.exists():
        try:
            return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {}


def save_settings(data: dict):
    """Salva settings JSON dell'app."""
    existing = load_settings()
    existing.update(data)
    SETTINGS_FILE.write_text(
        json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def get_riot_region() -> str:
    """Regione Riot configurata (default EUW1)."""
    return get_env("RIOT_REGION", "EUW1").upper()


def is_safe_mode() -> bool:
    """Ritorna True se la Safe Mode (Software Rendering) è attiva."""
    # Controlla sia .env che variabile d'ambiente (per flag --safe-mode)
    val = get_env("SAFE_MODE", "false").lower()
    return val in ("true", "1", "yes", "on")


def set_safe_mode(enabled: bool):
    """Abilita o disabilita la Safe Mode nel file .env."""
    set_env("SAFE_MODE", "true" if enabled else "false")
