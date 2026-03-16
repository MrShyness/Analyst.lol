"""
settings_view.py — Gestione .env, analisi servizi rilevati, test connessioni
"""
import flet as ft
import threading
from core.config import (
    read_env_raw, write_env_raw, load_env, get_env, set_env, 
    get_riot_region, is_safe_mode, set_safe_mode
)
from core.env_analyzer import scan_env, test_service, KNOWN_SERVICES
from core.riot_api import REGIONS

TEXT = "#ECF0F6"; MUTED = "#667A99"; BORDER = "#1E2D47"
GLASS = "#101828CC"
GOLD = "#C89B3C"; CYAN = "#00C8FF"; GREEN = "#00D4A0"; RED = "#FF4455"; CARD2 = "#1E2A40"
SPACING = 8

STATUS_COLOR = {"unknown": MUTED, "testing": CYAN, "ok": GREEN, "error": RED}
STATUS_ICON  = {"unknown": "⬤", "testing": "⟳", "ok": "✓", "error": "✗"}


def build_settings(page: ft.Page, navigate) -> ft.Control:
    # ── State ────────────────────────────────────────────────────────────────
    env_editor_ref  = ft.Ref[ft.TextField]()
    save_status_ref = ft.Ref[ft.Text]()
    services_col_ref = ft.Ref[ft.Column]()
    region_dd_ref   = ft.Ref[ft.Dropdown]()
    hw_accel_ref    = ft.Ref[ft.Switch]()

    # ── Env Editor ──────────────────────────────────────────────────────────
    def save_env(e=None):
        try:
            write_env_raw(env_editor_ref.current.value or "")
            save_status_ref.current.value = "✅ .env salvato con successo"
            save_status_ref.current.color = GREEN
        except Exception as ex:
            save_status_ref.current.value = f"❌ Errore: {ex}"
            save_status_ref.current.color = RED
        save_status_ref.current.update()
        # Ricarica la sezione servizi
        _rebuild_services()

    def reload_env(e=None):
        env_editor_ref.current.value = read_env_raw()
        env_editor_ref.current.update()
        save_status_ref.current.value = "🔄 .env ricaricato"
        save_status_ref.current.color = CYAN
        save_status_ref.current.update()

    env_editor = ft.TextField(
        ref=env_editor_ref,
        value=read_env_raw(),
        multiline=True, min_lines=10, max_lines=20,
        bgcolor=CARD2, border_radius=10,
        border_color=BORDER, focused_border_color=CYAN,
        color="#7CFC00",  # green terminal color
        text_style=ft.TextStyle(font_family="Courier New", size=12),
        hint_text="# Inserisci le tue API keys nel formato KEY=valore",
        hint_style=ft.TextStyle(color=MUTED),
    )

    # ── Service Card Builder ─────────────────────────────────────────────────
    def _build_service_card(svc: dict) -> ft.Container:
        status_text_ref = ft.Ref[ft.Text]()
        status_dot_ref  = ft.Ref[ft.Container]()
        test_btn_ref    = ft.Ref[ft.ElevatedButton]()
        svc_color = svc.get("color", GOLD)

        def do_test(e=None):
            test_btn_ref.current.disabled = True
            status_dot_ref.current.bgcolor = CYAN
            status_text_ref.current.value = "Testing…"
            status_text_ref.current.color = CYAN
            page.update()

            def _run():
                ok, msg = test_service(svc["env_key"])
                dot_color = GREEN if ok else RED
                status_dot_ref.current.bgcolor = dot_color
                status_text_ref.current.value = msg
                status_text_ref.current.color = dot_color
                test_btn_ref.current.disabled = False
                page.update()
            threading.Thread(target=_run, daemon=True).start()

        has_test = svc.get("test_fn") is not None
        def on_hover(e):
            e.control.scale = 1.02 if e.data == "true" else 1.0
            e.control.border = ft.Border.all(1, GOLD if e.data == "true" else f"{svc_color}30")
            e.control.update()

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    # Icon + Name
                    ft.Text(svc.get("icon", "🔌"), size=22),
                    ft.Column([
                        ft.Text(svc["name"], size=13, weight=ft.FontWeight.BOLD, color=TEXT),
                        ft.Text(svc.get("description", ""), size=10, color=MUTED),
                    ], spacing=1, expand=True),
                    # Status dot
                    ft.Container(
                        ref=status_dot_ref,
                        width=10, height=10,
                        border_radius=5, bgcolor=MUTED,
                    ),
                ], spacing=10),
                ft.Container(height=8),
                # Key preview
                ft.Row([
                    ft.Container(
                        content=ft.Text(svc.get("masked", ""), size=11,
                                        color=svc_color, font_family="Courier New"),
                        bgcolor=f"{svc_color}10",
                        border_radius=6,
                        padding=ft.Padding.symmetric(vertical=4, horizontal=10),
                        expand=True,
                    ),
                    ft.ElevatedButton(
                        "Test",
                        ref=test_btn_ref,
                        icon="wifi_tethering",
                        disabled=not has_test,
                        on_click=do_test if has_test else None,
                        style=ft.ButtonStyle(
                            bgcolor=svc_color if has_test else CARD2,
                            color="#000" if has_test else MUTED,
                            shape=ft.RoundedRectangleBorder(radius=8),
                            padding=ft.Padding.symmetric(vertical=8, horizontal=14),
                        ),
                    ),
                ], spacing=8),
                ft.Text(ref=status_text_ref, value="Non testato", size=11, color=MUTED),
            ], spacing=2),
            bgcolor=GLASS, border_radius=18,
            padding=20, border=ft.Border.all(1, f"{svc_color}30"),
            margin=ft.Margin.only(bottom=10),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=10, color="#00000022"),
            on_hover=on_hover,
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT)
        )

    def _rebuild_services():
        detected = scan_env()
        if not detected:
            services_col_ref.current.controls = [
                ft.Container(
                    content=ft.Text(
                        "⚠️ Nessuna API key rilevata nel file .env\n"
                        "Aggiungi le tue chiavi nell'editor qui sopra e clicca Salva.",
                        size=13, color=MUTED, text_align=ft.TextAlign.CENTER
                    ),
                    alignment=ft.Alignment.CENTER,
                    padding=30,
                )
            ]
        else:
            services_col_ref.current.controls = [
                _build_service_card(svc) for svc in detected
            ]
        if services_col_ref.current:
            services_col_ref.current.update()

    # ── Region Quick Setting ─────────────────────────────────────────────────
    def save_region(e):
        val = region_dd_ref.current.value or "EUW1"
        set_env("RIOT_REGION", val)
        save_status_ref.current.value = f"✅ Regione impostata: {val}"
        save_status_ref.current.color = GREEN
        save_status_ref.current.update()
        # Riflette cambiamento nell'editor
        env_editor_ref.current.value = read_env_raw()
        env_editor_ref.current.update()

    # ── Hardware Acceleration Quick Setting ──────────────────────────────────
    def toggle_hw_accel(e):
        enabled = hw_accel_ref.current.value
        # Safe Mode = NOT Hardware Acceleration
        set_safe_mode(not enabled)
        save_status_ref.current.value = f"✅ {'Accelerazione Hardware' if enabled else 'Safe Mode'} impostata (riavvia l'app)"
        save_status_ref.current.color = CYAN
        save_status_ref.current.update()
        # Riflette cambiamento nell'editor
        env_editor_ref.current.value = read_env_raw()
        env_editor_ref.current.update()

    # Init
    detected_services = scan_env()

    services_col = ft.Column(
        ref=services_col_ref,
        controls=[_build_service_card(svc) for svc in detected_services] if detected_services else [
            ft.Container(
                content=ft.Text(
                    "⚠️ Nessuna API key rilevata nel file .env\n"
                    "Aggiungi le tue chiavi nell'editor qui sopra e clicca Salva.",
                    size=13, color=MUTED, text_align=ft.TextAlign.CENTER
                ),
                alignment=ft.Alignment.CENTER, padding=30
            )
        ],
        spacing=0,
    )

    return ft.Container(
        content=ft.Column([
            ft.Text("⚙️ Impostazioni", size=22, weight=ft.FontWeight.BOLD, color=GOLD),
            ft.Text("Gestisci le tue API keys e le preferenze dell'app",
                    size=13, color=MUTED),
            ft.Container(height=20),

            # ── Editor .env ───────────────────────────────────────────────
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("📄 Editor .env", size=14, weight=ft.FontWeight.BOLD, color=TEXT, expand=True),
                        ft.TextButton("🔄 Ricarica", on_click=reload_env,
                                      style=ft.ButtonStyle(color=CYAN)),
                    ]),
                    ft.Text("Modifica direttamente il file .env — una variabile per riga (NOME=valore)",
                            size=11, color=MUTED),
                    ft.Container(height=8),
                    env_editor,
                    ft.Container(height=8),
                    ft.Row([
                        ft.ElevatedButton(
                            "💾 Salva .env", on_click=save_env,
                            style=ft.ButtonStyle(
                                bgcolor=GOLD, color="#000",
                                shape=ft.RoundedRectangleBorder(radius=10),
                                padding=ft.Padding.symmetric(vertical=12, horizontal=20),
                            ),
                        ),
                        ft.Text(ref=save_status_ref, size=12, color=MUTED),
                    ], spacing=12),
                ], spacing=0),
                bgcolor=GLASS, border_radius=20,
                padding=24, border=ft.Border.all(1, BORDER),
            ),

            ft.Container(height=16),

            # ── Quick region ─────────────────────────────────────────────
            ft.Container(
                content=ft.Column([
                    ft.Text("🌍 Regione Riot (scorciatoia)", size=13,
                            weight=ft.FontWeight.BOLD, color=TEXT),
                    ft.Container(height=8),
                    ft.Row([
                        ft.Dropdown(
                            ref=region_dd_ref,
                            value=get_riot_region(),
                            options=[ft.dropdown.Option(r) for r in REGIONS],
                            bgcolor=CARD2, border_radius=10,
                            border_color=BORDER, focused_border_color=CYAN,
                            color=TEXT, width=180,
                            on_select=save_region,
                        ),
                        ft.Text("Cambia regione senza editare il .env",
                                size=11, color=MUTED),
                    ], spacing=12),
                ], spacing=0),
                bgcolor=GLASS, border_radius=20,
                padding=24, border=ft.Border.all(1, BORDER),
            ),

            ft.Container(height=16),

            # ── Rendering Options ──────────────────────────────────────────
            ft.Container(
                content=ft.Column([
                    ft.Text("🖥️ Opzioni Rendering", size=13,
                            weight=ft.FontWeight.BOLD, color=TEXT),
                    ft.Container(height=8),
                    ft.Row([
                        ft.Switch(
                            ref=hw_accel_ref,
                            label="Accelerazione Hardware (GPU)",
                            value=not is_safe_mode(),
                            on_change=toggle_hw_accel,
                            active_color=GOLD,
                        ),
                        ft.Text("Disabilita se l'app flickera o crasha (Safe Mode)",
                                size=11, color=MUTED),
                    ], spacing=12),
                ], spacing=0),
                bgcolor=GLASS, border_radius=20,
                padding=24, border=ft.Border.all(1, BORDER),
            ),

            ft.Container(height=16),

            # ── Servizi rilevati ─────────────────────────────────────────
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("🔌 Servizi Rilevati", size=14,
                                weight=ft.FontWeight.BOLD, color=TEXT, expand=True),
                        ft.Text(f"{len(detected_services)} servizi attivi",
                                size=12, color=CYAN),
                    ]),
                    ft.Text("API keys trovate nel .env — clicca Test per verificare la connessione",
                            size=11, color=MUTED),
                    ft.Container(height=12),
                    services_col,
                ], spacing=0),
                bgcolor=GLASS, border_radius=20,
                padding=24, border=ft.Border.all(1, BORDER),
            ),
        ],
        spacing=0, scroll=ft.ScrollMode.AUTO,
        ),
        padding=32, expand=True,
    )
