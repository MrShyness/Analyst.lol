"""
riot_api.py — Client Riot Games API con rate limiting e gestione errori
"""
import requests
import time
from typing import Optional
from core.config import get_env, get_riot_region

REGIONS = ["EUW1", "NA1", "KR", "EUN1", "TR1", "BR1", "JP1",
           "OC1", "LA1", "LA2", "RU"]

ROUTING = {
    "EUW1": "europe", "EUN1": "europe", "TR1": "europe", "RU": "europe",
    "NA1": "americas", "BR1": "americas", "LA1": "americas", "LA2": "americas",
    "KR": "asia", "JP1": "asia",
    "OC1": "sea",
}

RANK_ORDER = {
    "IRON": 0, "BRONZE": 1, "SILVER": 2, "GOLD": 3,
    "PLATINUM": 4, "EMERALD": 5, "DIAMOND": 6,
    "MASTER": 7, "GRANDMASTER": 8, "CHALLENGER": 9
}

TIER_COLORS = {
    "IRON": "#7A7A7A", "BRONZE": "#8B6914", "SILVER": "#9AA4AF",
    "GOLD": "#C89B3C", "PLATINUM": "#4ECDC4", "EMERALD": "#2ED573",
    "DIAMOND": "#A8D8EA", "MASTER": "#9B59B6", "GRANDMASTER": "#E74C3C",
    "CHALLENGER": "#00D4FF"
}


class RiotAPIError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"[{status_code}] {message}")


class RiotAPI:
    def __init__(self):
        self._last_call = 0
        self._rate_delay = 0.05  # ~20 req/s (development key: 0.84s)

    def _get_key(self) -> str:
        key = get_env("RIOT_API_KEY", "")
        if not key or key.startswith("RGAPI-xxx"):
            raise RiotAPIError(0, "Riot API Key non configurata. Vai in Impostazioni.")
        return key

    def _region(self) -> str:
        return get_riot_region()

    def _routing(self) -> str:
        return ROUTING.get(self._region(), "europe")

    def _headers(self) -> dict:
        return {"X-Riot-Token": self._get_key()}

    def _get(self, url: str, params: dict = None) -> dict:
        now = time.time()
        elapsed = now - self._last_call
        if elapsed < self._rate_delay:
            time.sleep(self._rate_delay - elapsed)
        self._last_call = time.time()

        try:
            r = requests.get(url, headers=self._headers(), params=params, timeout=8)
        except requests.exceptions.ConnectionError:
            raise RiotAPIError(0, "Nessuna connessione internet o server non raggiungibile.")
        except requests.exceptions.Timeout:
            raise RiotAPIError(0, "Timeout — il server Riot non risponde.")

        if r.status_code == 200:
            return r.json()
        elif r.status_code == 401:
            raise RiotAPIError(401, "API Key non valida o scaduta.")
        elif r.status_code == 403:
            raise RiotAPIError(403, "Accesso negato — verifica la tua API Key.")
        elif r.status_code == 404:
            raise RiotAPIError(404, "Summoner non trovato.")
        elif r.status_code == 429:
            raise RiotAPIError(429, "Rate limit superato — attendi qualche secondo.")
        else:
            raise RiotAPIError(r.status_code, r.text[:200])

    # ─── Status / Test ─────────────────────────────────────────────────────────

    def test_connection(self) -> dict:
        """Testa la connessione e restituisce info sulla piattaforma."""
        region = self._region()
        url = f"https://{region}.api.riotgames.com/lol/status/v4/platform-data"
        return self._get(url)

    # ─── Summoner ──────────────────────────────────────────────────────────────

    def get_summoner_by_name(self, name: str) -> dict:
        region = self._region()
        url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{requests.utils.quote(name)}"
        return self._get(url)

    def get_summoner_by_puuid(self, puuid: str) -> dict:
        region = self._region()
        url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
        return self._get(url)

    # ─── League ────────────────────────────────────────────────────────────────

    def get_ranked_stats(self, summoner_id: str) -> list:
        region = self._region()
        url = f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}"
        return self._get(url)

    # ─── Match ──────────────────────────────────────────────────────────────────

    def get_match_ids(self, puuid: str, count: int = 20, queue: int = None) -> list:
        routing = self._routing()
        url = f"https://{routing}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
        params = {"count": count}
        if queue:
            params["queue"] = queue
        return self._get(url, params=params)

    def get_match(self, match_id: str) -> dict:
        routing = self._routing()
        url = f"https://{routing}.api.riotgames.com/lol/match/v5/matches/{match_id}"
        return self._get(url)

    # ─── Champion Mastery ───────────────────────────────────────────────────────

    def get_top_mastery(self, puuid: str, count: int = 5) -> list:
        region = self._region()
        url = f"https://{region}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top"
        return self._get(url, {"count": count})

    # ─── Aggregated Summoner Data ───────────────────────────────────────────────

    def get_full_profile(self, name: str) -> dict:
        """
        Recupera profilo completo: summoner + ranked + mastery top5.
        Restituisce un dict unificato pronto per la UI.
        """
        summoner = self.get_summoner_by_name(name)
        ranked = self.get_ranked_stats(summoner["id"])
        try:
            mastery = self.get_top_mastery(summoner["puuid"], count=5)
        except Exception:
            mastery = []

        # Solo ranked solo/duo
        solo = next((q for q in ranked if q["queueType"] == "RANKED_SOLO_5x5"), None)
        flex = next((q for q in ranked if q["queueType"] == "RANKED_FLEX_5x5"), None)

        winrate = 0
        if solo:
            total = solo["wins"] + solo["losses"]
            winrate = round(solo["wins"] / total * 100, 1) if total else 0

        return {
            "name": summoner.get("name", name),
            "level": summoner.get("summonerLevel", 0),
            "profileIconId": summoner.get("profileIconId", 0),
            "puuid": summoner.get("puuid", ""),
            "id": summoner.get("id", ""),
            "solo": solo,
            "flex": flex,
            "winrate": winrate,
            "mastery": mastery,
        }


# Singleton globale
riot = RiotAPI()

# ─── Assets ────────────────────────────────────────────────────────────────
DDRAGON_VER = "14.24.1"  # updated fallback

def get_champion_icon_url(champion_name: str) -> str:
    clean_name = champion_name.replace(" ", "").replace("'", "")
    if clean_name.lower() == "wukong": clean_name = "MonkeyKing"
    if clean_name.lower() == "nunu&willump": clean_name = "Nunu"
    if clean_name.lower() == "renataglasc": clean_name = "Renata"
    # Basic capitalization fixes
    if clean_name:
        clean_name = clean_name[0].upper() + clean_name[1:]
    return f"https://ddragon.leagueoflegends.com/cdn/{DDRAGON_VER}/img/champion/{clean_name}.png"

def get_profile_icon_url(icon_id: int) -> str:
    return f"https://ddragon.leagueoflegends.com/cdn/{DDRAGON_VER}/img/profileicon/{icon_id}.png"

def get_role_icon_url(role: str) -> str:
    """Use DataDragon for role icons (most reliable source)."""
    from core.datadragon import dd_service
    if role.lower() == "all": return ""
    return dd_service.get_role_icon_url(role)
