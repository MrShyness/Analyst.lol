"""
views/agentic_console.py — Visualizzatore della memoria agentica e dello stato progetto.
Ispirato al mockup "Agentic Memory System".
"""
import flet as ft
import json
import os

# ── Palette ──────────────────────────────────────────────────────────────────
BG      = "#080D18"
SURFACE = "#0F1629"
CARD    = "#172135"
GOLD    = "#C89B3C"
CYAN    = "#00C8FF"
GREEN   = "#00D4A0"
RED     = "#FF4455"
TEXT    = "#ECF0F6"
MUTED   = "#667A99"
BORDER  = "#1E2D47"

MEMORY_FILE = "core/session_memory.json"

def build_agentic_console(page: ft.Page, navigate, **kwargs) -> ft.Control:
    
    # --- Refs ---
    mem_col    = ft.Ref[ft.Column]()
    proj_col   = ft.Ref[ft.Column]()
    chat_col   = ft.Ref[ft.Column]()
    stat_turns = ft.Ref[ft.Text]()
    stat_mem   = ft.Ref[ft.Text]()
    stat_proj  = ft.Ref[ft.Text]()
    stat_upd   = ft.Ref[ft.Text]()

    def load_data():
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def start_deep_sync(e=None):
        chat_col.current.controls.append(
            ft.Text("> [USER] Avvio Deep Search Sync...", color=GOLD, size=12, font_family="monospace")
        )
        chat_col.current.controls.append(
            ft.Text("> Avvio ricerca automatica su TrackingThePros e OP.GG...", color=CYAN, size=12, font_family="monospace")
        )
        page.update()
        
        # In a real app, this would trigger the python -m core.sync_agent
        # Here we simulate the progress in the console
        import threading
        def _run_sync():
            try:
                from core.sync_agent import sync_players_logic
                sync_players_logic()
                chat_col.current.controls.append(
                    ft.Text("> Sincronizzazione completata con successo.", color=GREEN, size=12, font_family="monospace")
                )
            except Exception as ex:
                chat_col.current.controls.append(
                    ft.Text(f"> [ERRORE] Sincronizzazione fallita: {ex}", color=RED, size=12, font_family="monospace")
                )
            refresh_ui()
            
        threading.Thread(target=_run_sync, daemon=True).start()

    def refresh_ui(e=None):
        data = load_data()
        memory = data.get("sync_status", {}).get("history", [])
        project = data.get("basal_knowledge", {})
        
        # Aggiorna Stats
        stat_turns.current.value = str(len(data.get("sync_status", {}).get("history", [])))
        stat_mem.current.value   = str(len(data.get("sync_status", {}).get("conflicts", [])))
        stat_proj.current.value  = str(len(project.get("verified_accounts", {})))
        stat_upd.current.value   = str(data.get("sync_status", {}).get("last_index", 0))

        # Aggiorna Episodic Memory (Sync Logs)
        mem_col.current.controls = [
            ft.Container(
                content=ft.Column([
                    ft.Text(f"PLAYER: {m.get('player')}", size=10, weight="bold", color=MUTED),
                    ft.Text(f"{m.get('old_acc')} → {m.get('new_acc')}", size=12, color=TEXT),
                    ft.Text(f"Sources: {', '.join(m.get('sources', []))}", size=9, color=MUTED),
                    ft.Text(f"Score: {m.get('score')} | {m.get('status')}", size=10, color=CYAN if m.get('status')=="AUTO_UPDATED" else GOLD),
                ], spacing=2),
                padding=10, border=ft.border.all(1, BORDER), border_radius=8, bgcolor=f"{SURFACE}50"
            ) for m in memory[-10:] # Ultimi 10
        ]

        # Aggiorna Project State
        proj_rows = []
        for sect, details in project.items():
            if isinstance(details, dict):
                proj_rows.append(ft.Text(sect.replace("_", " ").upper(), size=11, weight="bold", color=GOLD))
                for k, v in details.items():
                    if isinstance(v, dict): continue # Salta nested per ora
                    proj_rows.append(
                        ft.Row([
                            ft.Text(f"{k}:", size=11, color=MUTED, width=100),
                            ft.Text(str(v), size=11, color=TEXT, expand=True),
                        ], spacing=10)
                    )
                proj_rows.append(ft.Divider(height=1, color=f"{BORDER}40"))

        proj_col.current.controls = proj_rows

        page.update()

    # --- UI Components ---
    def _stat_box(ref, label):
        return ft.Container(
            content=ft.Column([
                ft.Text(ref=ref, value="0", size=24, weight="bold", color=GOLD),
                ft.Text(label, size=10, color=MUTED),
            ], spacing=1, horizontal_alignment="center"),
            bgcolor=CARD, padding=15, border_radius=10, border=ft.border.all(1, BORDER), expand=True
        )

    header = ft.Row([
        ft.Text("🧠 Agentic Console", size=28, weight="bold", color=GOLD),
        ft.Container(expand=True),
        ft.ElevatedButton(
            "Deep Search Sync",
            icon=ft.icons.STARS,
            on_click=start_deep_sync,
            style=ft.ButtonStyle(
                color=GOLD,
                bgcolor=f"{GOLD}10",
                side={"": ft.BorderSide(1, f"{GOLD}40")}
            )
        ),
        ft.ElevatedButton("Ricarica", icon=ft.icons.REFRESH, on_click=refresh_ui, 
                          style=ft.ButtonStyle(color=GOLD, bgcolor="transparent"))
    ], spacing=10)

    stats = ft.Row([
        _stat_box(stat_turns, "Sync History"),
        _stat_box(stat_mem, "Conflicts"),
        _stat_box(stat_proj, "Verified Pros"),
        _stat_box(stat_upd, "Last Index"),
    ], spacing=10)

    # Main Grid Sections
    search_input = ft.TextField(
        hint_text="Cerca nuovi pro o aggiorna account (es: T1 Faker, G2 Caps)...",
        bgcolor=SURFACE, border_radius=10, border_color=BORDER,
        expand=True, on_submit=start_deep_sync
    )

    console_panel = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("SYSTEM LOGS", size=12, weight="bold", color=MUTED, expand=True),
                ft.IconButton(ft.icons.CLEANING_SERVICES, on_click=lambda _: chat_col.current.controls.clear() or page.update(), icon_size=16)
            ]),
            ft.Column(ref=chat_col, controls=[
                ft.Text("> Inizializzazione Basal Memory...", color=CYAN, size=12, font_family="monospace"),
                ft.Text("> Caricamento decisioni architetturali...", color=CYAN, size=12, font_family="monospace"),
                ft.Text("> Pronto.", color=GREEN, size=12, font_family="monospace"),
            ], spacing=5, scroll=ft.ScrollMode.AUTO, expand=True),
            ft.Row([
                search_input,
                ft.IconButton(ft.icons.SEND, on_click=start_deep_sync, icon_color=GOLD)
            ])
        ], spacing=10, expand=True),
        bgcolor=GLASS, padding=20, border_radius=12, border=ft.border.all(1, BORDER), expand=2
    )

    memory_panel = ft.Container(
        content=ft.Column([
            ft.Text("EPISODIC MEMORY (SYNC)", size=12, weight="bold", color=MUTED),
            ft.Column(ref=mem_col, spacing=8, scroll=ft.ScrollMode.AUTO, expand=True),
        ], spacing=10, expand=True),
        bgcolor=GLASS, padding=20, border_radius=12, border=ft.border.all(1, BORDER), expand=1
    )

    project_panel = ft.Container(
        content=ft.Column([
            ft.Text("PROJECT STATE / ROADMAP", size=12, weight="bold", color=MUTED),
            ft.Column(ref=proj_col, spacing=8, scroll=ft.ScrollMode.AUTO, expand=True),
        ], spacing=10, expand=True),
        bgcolor=GLASS, padding=20, border_radius=12, border=ft.border.all(1, BORDER), expand=1
    )

    layout = ft.Column([
        header,
        stats,
        ft.Row([
            console_panel,
            ft.Column([memory_panel, project_panel], expand=1, spacing=10)
        ], expand=True, spacing=10)
    ], spacing=20, expand=True)

    # Initial Load
    ft.app_bar = None # Clear any app bar
    
    # Auto-refresh on build
    page.run_task(lambda: refresh_ui())

    return ft.Container(content=layout, padding=30, expand=True)
