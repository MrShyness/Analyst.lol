"""
Data Dragon Service - Integration with Riot Games static assets
"""
import requests
from functools import lru_cache
from typing import Optional, Dict, List
import os
import json

class DataDragonService:
    BASE_URL = "https://ddragon.leagueoflegends.com/cdn"
    ROLE_KEYS = ["top", "jungle", "mid", "bot", "utility"]
    
    def __init__(self, cache_dir: str = ".cache/ddragon"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self._version = None
    
    @lru_cache(maxsize=1)
    def get_latest_version(self) -> str:
        """Fetch latest Data Dragon version from the official versions endpoint"""
        try:
            resp = requests.get(f"https://ddragon.leagueoflegends.com/api/versions.json", timeout=10)
            resp.raise_for_status()
            versions = resp.json()
            # The first version in the list is the most recent
            self._version = versions[0] if versions else "14.5.1"
            return self._version
        except Exception as e:
            print(f"[ERROR] Failed to fetch DD version: {e}")
            return "14.5.1"  # Recent fallback
    
    def get_role_icon_url(self, role: str, version: Optional[str] = None) -> str:
        """Return official role icon URL from Data Dragon"""
        version = version or self.get_latest_version()
        role_map = {
            "top": "top",
            "jungle": "jungle",
            "mid": "mid",
            "middle": "mid",
            "bot": "bot",
            "bottom": "bot",
            "support": "utility",
            "utility": "utility",
            "fill": "utility"
        }
        role = role_map.get(role.lower(), "utility")
        return f"{self.BASE_URL}/{version}/img/position/{role.capitalize()}.png"
    
    def get_champion_square_url(self, champion_id: str, version: Optional[str] = None) -> str:
        """Return champion square portrait URL"""
        version = version or self.get_latest_version()
        if not champion_id or champion_id == "None":
            champion_id = "Aatrox" # Default fallback
        return f"{self.BASE_URL}/{version}/img/champion/{champion_id}.png"

    @lru_cache(maxsize=128)
    def get_champion_data(self, champion_id: str, lang: str = "en_US") -> Optional[Dict]:
        """Fetch champion static data with local disk caching"""
        version = self.get_latest_version()
        cache_path = os.path.join(self.cache_dir, f"{champion_id}_{lang}.json")
        
        # 1. Try Disk Cache
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # 2. Fetch from API
        try:
            url = f"{self.BASE_URL}/{version}/data/{lang}/champion/{champion_id}.json"
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            
            # Save to Disk Cache
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Return specific champion data
            return data.get("data", {}).get(champion_id)
        except Exception as e:
            print(f"[ERROR] DataDragon failed for {champion_id}: {e}")
            return None

# Singleton-like instance
dd_service = DataDragonService()
