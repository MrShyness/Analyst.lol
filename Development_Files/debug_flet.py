import sys
import os
import flet as ft

# Ensure src is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "src")
sys.path.insert(0, src_path)

modules_to_test = [
    "core.config",
    "core.datadragon",
    "core.env_analyzer",
    "views.dashboard",
    "views.summoner_search",
    "views.team_builder",
    "views.analytics",
    "views.pro_players",
    "views.settings_view",
    "views.agentic_console",
    "app"
]

for mod_name in modules_to_test:
    print(f"Testing {mod_name}...")
    try:
        import importlib
        mod = importlib.import_module(mod_name)
        # If it' a view, it might have internal flet calls. 
        # Most errors happen at import time or when building the UI.
        # We can try to call the 'build' function if it exists.
        if hasattr(mod, "build_dashboard"):
            mod.build_dashboard(None, None)
        elif hasattr(mod, "build_summoner_search"):
             mod.build_summoner_search(None, None)
        elif hasattr(mod, "build_team_builder"):
             mod.build_team_builder(None, None)
        elif hasattr(mod, "build_analytics"):
             mod.build_analytics(None, None)
        elif hasattr(mod, "build_pro_players"):
             mod.build_pro_players(None, None)
        elif hasattr(mod, "build_settings"):
             mod.build_settings(None, None, None)
        elif hasattr(mod, "build_agentic_console"):
             mod.build_agentic_console(None, None)
             
        print(f"  {mod_name} imports OK")
    except AttributeError as e:
        print(f"  FAILED {mod_name}: {e}")
    except Exception as e:
        # Ignore other errors like 'None' as page
        if "AttributeError" in str(type(e)) and "ImageFit" in str(e):
             print(f"  CRITICAL Flet Error in {mod_name}: {e}")
        else:
             print(f"  (Ignored expected error in {mod_name}: {e})")

print("Audit complete.")
