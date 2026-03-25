#!/usr/bin/env python3
"""
Test script per verificare la validità dell'API key di Riot Games
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.config import get_env
from core.riot_api import RiotAPI, RiotAPIError

def test_api_key():
    """Test dell'API key"""
    print("🔍 Test API Key Riot Games...")
    
    # Verifica configurazione
    api_key = get_env("RIOT_API_KEY", "")
    if not api_key:
        print("❌ API Key non configurata")
        return False
    
    print(f"📝 API Key: {api_key[:10]}...{api_key[-4:]}")
    print(f"📏 Lunghezza: {len(api_key)} caratteri")
    
    if not api_key.startswith("RGAPI-"):
        print("❌ Formato API Key non valido (deve iniziare con RGAPI-)")
        return False
    
    # Test connessione
    try:
        riot = RiotAPI()
        print("🌐 Test connessione con Riot API...")
        
        # Test semplice con un endpoint base
        test_result = riot._get("https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/Faker")
        
        if test_result:
            print("✅ API Key valida e funzionante!")
            print(f"📊 Test response: Summoner ID trovato")
            return True
        else:
            print("❌ Risposta vuota dall'API")
            return False
            
    except RiotAPIError as e:
        if e.status_code == 403:
            print("❌ API Key non valida o scaduta (errore 403)")
            print("💡 Genera una nuova API key su: https://developer.riotgames.com/")
        elif e.status_code == 401:
            print("❌ API Key non valida (errore 401)")
        else:
            print(f"❌ Errore API: {e}")
        return False
    except Exception as e:
        print(f"❌ Errore di connessione: {e}")
        return False

if __name__ == "__main__":
    success = test_api_key()
    print(f"\n🎯 Risultato: {'SUCCESSO' if success else 'FALLIMENTO'}")
    sys.exit(0 if success else 1)
