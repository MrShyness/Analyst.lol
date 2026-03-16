"""
core/sync_agent.py — Logica agentica per la sincronizzazione dei dati pro player.
Implementa fuzzy matching e gestione della memoria basale.
"""
import json
import time
import random
import os
from difflib import SequenceMatcher
from core.pro_players_data import PRO_PLAYERS

MEMORY_FILE = 'core/session_memory.json'

def fuzzy_ratio(a, b):
    return SequenceMatcher(None, str(a).lower(), str(b).lower()).ratio()

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"last_index": 0, "history": [], "conflicts": []}

def save_memory(data):
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def sync_players_logic(batch_size=10):
    """
    Esegue il sync dei dati pro player incrociando più fonti:
    TrackingThePros, ProBuildStats, DPM.lol, ecc.
    """
    memory = load_memory()
    if "sync_status" not in memory:
        memory["sync_status"] = {"last_index": 0, "history": [], "conflicts": []}
        
    start_idx = memory["sync_status"].get("last_index", 0)
    print(f"🚀 [SyncAgent] Ripresa sync dall'indice: {start_idx}")

    # Lista delle fonti supportate (basal knowledge)
    SOURCES = ["TrackingThePros", "ProBuildStats", "DPM.lol", "OP.GG"]
    
    end_idx = min(start_idx + batch_size, len(PRO_PLAYERS))
    
    for i in range(start_idx, end_idx):
        player = PRO_PLAYERS[i]
        player_name = player['name']
        
        # In un'implementazione reale, qui verrebbe eseguita una ricerca parallela
        # Simuliamo la risposta aggregata da più fonti
        source_responses = []
        for src in SOURCES:
            # Placeholder per logica di scraping/API specifica per fonte
            if player_name == "Faker":
                res = "Hide on bush#KR1" if src == "OP.GG" else "Faker#T1"
            elif player_name == "Gumayusi":
                res = "T1 Gumayusi#K R1" if src == "ProBuildStats" else "Gumayusi#T1"
            else:
                res = f"{player_name}#VERIFIED" # Default simulato
            source_responses.append((src, res))

        # Maggioranza o miglior match
        best_match = source_responses[0][1] # Fallback
        max_score = 0
        
        for src, acc in source_responses:
            score = fuzzy_ratio(player['account'], acc)
            if score > max_score:
                max_score = score
                best_match = acc
        
        entry = {
            "player": player_name,
            "old_acc": player['account'],
            "new_acc": best_match,
            "score": round(max_score, 2),
            "sources": [s[0] for s in source_responses],
            "timestamp": time.time()
        }

        if max_score >= 0.85:
            entry["status"] = "AUTO_UPDATED"
        else:
            entry["status"] = "MANUAL_REVIEW_REQUIRED"
            memory["sync_status"]["conflicts"].append(entry)

        memory["sync_status"]["history"].append(entry)
        memory["sync_status"]["last_index"] = i + 1
        save_memory(memory)
        print(f"✅ [SyncAgent] Elaborato {player_name} (Fonti: {len(SOURCES)}, Score: {max_score})")


if __name__ == "__main__":
    sync_players_logic()
