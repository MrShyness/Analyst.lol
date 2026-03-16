import sys
import os

# Aggiunge la cartella src al path per permettere gli import modulari
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "src")
sys.path.insert(0, src_path)

if __name__ == "__main__":
    try:
        from app import main
        import flet as ft
        
        # Avvio dell'app usando ft.app(target=main) per massima stabilità
        ft.app(target=main)
    except ImportError as e:
        print(f"[ERRORE] Impossibile trovare i moduli in src/: {e}")
        input("Premi Invio per uscire...")
    except Exception as e:
        print(f"[ERRORE CRITICO] {e}")
        input("Premi Invio per uscire...")
