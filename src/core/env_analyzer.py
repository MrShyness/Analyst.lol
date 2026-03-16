"""
env_analyzer.py — Analizza il file .env, rileva servizi, testa connessioni
"""
import requests
from typing import Optional, Callable
from core.config import load_env, get_env

# ─── Definizione servizi noti ───────────────────────────────────────────────

def _test_riot(key: str) -> tuple[bool, str]:
    region = get_env("RIOT_REGION", "EUW1").upper()
    url = f"https://{region}.api.riotgames.com/lol/status/v4/platform-data"
    try:
        r = requests.get(url, headers={"X-Riot-Token": key}, timeout=6)
        if r.status_code == 200:
            data = r.json()
            return True, f"Online — {data.get('name', region)}"
        elif r.status_code == 403:
            return False, "API Key non valida o scaduta"
        elif r.status_code == 401:
            return False, "Autenticazione fallita"
        else:
            return False, f"Errore HTTP {r.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Nessuna connessione internet"
    except requests.exceptions.Timeout:
        return False, "Timeout — server non raggiungibile"
    except Exception as e:
        return False, str(e)[:60]


def _test_openai(key: str) -> tuple[bool, str]:
    url = "https://api.openai.com/v1/models"
    try:
        r = requests.get(url, headers={"Authorization": f"Bearer {key}"}, timeout=6)
        if r.status_code == 200:
            data = r.json()
            count = len(data.get("data", []))
            return True, f"Online — {count} modelli disponibili"
        elif r.status_code == 401:
            return False, "API Key non valida"
        else:
            return False, f"Errore HTTP {r.status_code}"
    except Exception as e:
        return False, str(e)[:60]


def _test_anthropic(key: str) -> tuple[bool, str]:
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    body = {
        "model": "claude-3-haiku-20240307",
        "max_tokens": 1,
        "messages": [{"role": "user", "content": "hi"}],
    }
    try:
        r = requests.post(url, headers=headers, json=body, timeout=8)
        if r.status_code in (200, 400):
            return True, "Online — Chiave valida"
        elif r.status_code == 401:
            return False, "API Key non valida"
        else:
            return False, f"Errore HTTP {r.status_code}"
    except Exception as e:
        return False, str(e)[:60]


def _test_github(key: str) -> tuple[bool, str]:
    url = "https://api.github.com/user"
    try:
        r = requests.get(url, headers={"Authorization": f"Bearer {key}"}, timeout=6)
        if r.status_code == 200:
            data = r.json()
            return True, f"Online — @{data.get('login', 'user')}"
        elif r.status_code == 401:
            return False, "Token non valido"
        else:
            return False, f"Errore HTTP {r.status_code}"
    except Exception as e:
        return False, str(e)[:60]


def _test_discord(key: str) -> tuple[bool, str]:
    url = "https://discord.com/api/v10/users/@me"
    try:
        r = requests.get(url, headers={"Authorization": f"Bot {key}"}, timeout=6)
        if r.status_code == 200:
            data = r.json()
            return True, f"Online — {data.get('username', 'bot')}"
        elif r.status_code == 401:
            return False, "Token non valido"
        else:
            return False, f"Errore HTTP {r.status_code}"
    except Exception as e:
        return False, str(e)[:60]


#  Catalogo servizi: ENV_KEY → info servizio
KNOWN_SERVICES: dict[str, dict] = {
    "RIOT_API_KEY": {
        "name": "Riot Games API",
        "icon": "🎮",
        "color": "#C89B3C",
        "description": "League of Legends analytics, ranked data, match history",
        "test_fn": _test_riot,
        "docs": "https://developer.riotgames.com/",
    },
    "OPENAI_API_KEY": {
        "name": "OpenAI",
        "icon": "🤖",
        "color": "#10A37F",
        "description": "GPT-4, DALL-E, Whisper e altri modelli AI",
        "test_fn": _test_openai,
        "docs": "https://platform.openai.com/",
    },
    "ANTHROPIC_API_KEY": {
        "name": "Anthropic Claude",
        "icon": "🧠",
        "color": "#D4754A",
        "description": "Claude 3 Opus/Sonnet/Haiku — AI conversazionale",
        "test_fn": _test_anthropic,
        "docs": "https://www.anthropic.com/",
    },
    "GITHUB_TOKEN": {
        "name": "GitHub",
        "icon": "🐙",
        "color": "#6E40C9",
        "description": "Accesso a repository, issue, workflow CI/CD",
        "test_fn": _test_github,
        "docs": "https://docs.github.com/en/authentication",
    },
    "DISCORD_TOKEN": {
        "name": "Discord Bot",
        "icon": "💬",
        "color": "#5865F2",
        "description": "Bot Discord per notifiche e integrazione community",
        "test_fn": _test_discord,
        "docs": "https://discord.dev/",
    },
    "TWITCH_CLIENT_ID": {
        "name": "Twitch API",
        "icon": "📺",
        "color": "#9146FF",
        "description": "Stream data, clip, channel points e altro",
        "test_fn": None,
        "docs": "https://dev.twitch.tv/",
    },
    "SPOTIFY_CLIENT_ID": {
        "name": "Spotify API",
        "icon": "🎵",
        "color": "#1DB954",
        "description": "Biblioteca musicale, playlist, riproduzione",
        "test_fn": None,
        "docs": "https://developer.spotify.com/",
    },
    "GOOGLE_API_KEY": {
        "name": "Google APIs",
        "icon": "🔍",
        "color": "#4285F4",
        "description": "Maps, YouTube, Sheets e molti altri servizi Google",
        "test_fn": None,
        "docs": "https://developers.google.com/",
    },
}


def scan_env() -> list[dict]:
    """
    Scansiona il file .env e restituisce lista di servizi rilevati.
    Formato output: [{"env_key", "value", "masked", **service_info}]
    """
    env_values = load_env()
    detected = []

    for env_key, service_info in KNOWN_SERVICES.items():
        value = env_values.get(env_key, "")
        if value and not value.startswith("xxx") and not value.startswith("...") and len(value) > 8:
            masked = value[:6] + "•" * min(len(value) - 10, 20) + value[-4:]
            detected.append({
                "env_key": env_key,
                "value": value,
                "masked": masked,
                "status": "unknown",  # unknown | testing | ok | error
                "status_msg": "Non testato",
                **service_info,
            })

    return detected


def test_service(env_key: str) -> tuple[bool, str]:
    """Testa un singolo servizio e restituisce (ok, messaggio)."""
    service = KNOWN_SERVICES.get(env_key)
    if not service:
        return False, "Servizio sconosciuto"

    env_values = load_env()
    key = env_values.get(env_key, "")
    if not key:
        return False, "Chiave non trovata nel .env"

    test_fn: Optional[Callable] = service.get("test_fn")
    if test_fn is None:
        return False, "Test automatico non disponibile"

    return test_fn(key)
