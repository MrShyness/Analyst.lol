"""
dashboard.py — Schermata principale con stats rapide e accesso veloce
"""
import flet as ft
from core.config import load_settings, get_env, get_riot_region
from core.env_analyzer import scan_env

# ─── Palette colori (condivisa con app.py) ──────────────────────────────────
BG       = "#080D18"
SURFACE  = "#0F1629"
CARD     = "#172135"
CARD2    = "#1E2A40"
GOLD     = "#C89B3C"
GOLD2    = "#E8C96C"
CYAN     = "#00C8FF"
GREEN    = "#00D4A0"
RED      = "#FF4455"
TEXT     = "#ECF0F6"
MUTED    = "#667A99"
BORDER   = "#1E2D47"
GLASS    = "#101828CC"
ROSETTE  = "#C89B3C33"
SPACING  = 8


def _stat_card(icon: str, label: str, value: str, color: str = GOLD) -> ft.Container:
    return ft.Container(
        content=ft.Column([
            ft.Text(icon, size=32),
            ft.Text(value, size=24, weight=ft.FontWeight.BOLD, color=color),
             ft.Text(label.upper(), weight=ft.FontWeight.BOLD, color=MUTED, style=ft.TextStyle(size=9, letter_spacing=1)),
        ], spacing=SPACING/2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor=GLASS,
        border_radius=18,
        padding=ft.Padding.symmetric(vertical=SPACING*3, horizontal=SPACING*3),
        border=ft.Border.all(1, BORDER),
        expand=True,
        shadow=ft.BoxShadow(spread_radius=0, blur_radius=15, color="#00000022"),
        animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT)
    )


def _quick_action(icon: str, label: str, color: str, on_click=None) -> ft.Container:
    def on_hover(e):
        e.control.bgcolor = f"{SURFACE}BB" if e.data == "true" else GLASS
        e.control.scale = 1.02 if e.data == "true" else 1.0
        e.control.update()

    return ft.Container(
        content=ft.Row([
            ft.Row([
                ft.Container(
                    content=ft.Text(icon, size=18),
                    width=36, height=36, bgcolor=f"{color}15", border_radius=10,
                    alignment=ft.Alignment.CENTER
                ),
                ft.Text(label, size=14, color=TEXT, weight=ft.FontWeight.W_500),
            ], spacing=SPACING*1.5),
            ft.Icon("arrow_forward_ios", size=12, color=MUTED),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        bgcolor=GLASS,
        border_radius=14,
        padding=ft.Padding.symmetric(vertical=SPACING*1.5, horizontal=SPACING*2),
        border=ft.Border.all(1, BORDER),
        on_click=on_click,
        on_hover=on_hover,
        ink=True,
        animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT)
    )


def build_dashboard(page: ft.Page, navigate) -> ft.Control:
    services = scan_env()
    active_keys = len(services)
    region = get_riot_region()
    riot_configured = bool(get_env("RIOT_API_KEY"))

    status_text = f"✅ Riot API configurata — {region}" if riot_configured else "⚠️ Riot API Key non configurata"
    status_color = GREEN if riot_configured else "#F5A623"

    return ft.Container(
        content=ft.Column([
            # ── Header ──────────────────────────────────────────────────────
            ft.Container(
                content=ft.Column([
                    ft.Text("Guide.Analyst", size=42, weight=ft.FontWeight.BOLD,
                            color=GOLD, font_family="Inter"),
                    ft.Text("Professional League of Legends Analytics Suite",
                            size=16, color=MUTED),
                    ft.Container(height=12),
                    ft.Container(
                        content=ft.Row([
                            ft.Container(width=8, height=8, bgcolor=status_color, border_radius=4),
                            ft.Text(status_text, size=12, color=status_color, weight="w600"),
                        ], spacing=8),
                        bgcolor=f"{status_color}10",
                        border=ft.Border.all(1, f"{status_color}30"),
                        border_radius=30, padding=ft.Padding.symmetric(vertical=8, horizontal=16),
                    ),
                ], spacing=4),
                padding=ft.Padding.only(bottom=40),
            ),

            # ── Stats rapide ────────────────────────────────────────────────
            ft.Text("📊 Overview", size=13, color=MUTED, weight=ft.FontWeight.W_600),
            ft.Container(height=6),
            ft.Row([
                _stat_card("🔑", "API Keys attive", str(active_keys), CYAN),
                _stat_card("🌍", "Regione", region, GOLD),
                _stat_card("🎮", "Riot API", "Online" if riot_configured else "N/D",
                           GREEN if riot_configured else RED),
                _stat_card("⚡", "Versione", "2.0", GOLD2),
            ], spacing=12),

            ft.Container(height=24),

            # ── Azioni rapide ──────────────────────────────────────────────
            ft.Text("🚀 Accesso Rapido", size=13, color=MUTED, weight=ft.FontWeight.W_600),
            ft.Container(height=8),
            ft.Column([
                _quick_action("🔍", "Cerca un Summoner",   CYAN,  lambda e: navigate(1)),
                _quick_action("👥", "Team Builder 5v5",    GOLD,  lambda e: navigate(2)),
                _quick_action("📊", "Analytics & Grafici", GREEN, lambda e: navigate(3)),
                _quick_action("🏆", "Pro Players Database",GOLD,  lambda e: navigate(4)),
                _quick_action("🧠", "Console Agentica",   GOLD,  lambda e: navigate(6)),
                _quick_action("⚙️", "Impostazioni & API",  MUTED, lambda e: navigate(5)),
            ], spacing=8),

            ft.Container(height=24),

            # ── Tips ─────────────────────────────────────────────────────
            ft.Container(
                content=ft.Column([
                    ft.Text("💡 Come iniziare", size=13, color=GOLD, weight=ft.FontWeight.W_600),
                    ft.Container(height=6),
                    ft.Text(
                        "1. Vai in Impostazioni (⚙️) e inserisci la tua Riot API Key nel file .env\n"
                        "2. Salva e testa la connessione con il tasto 'Test'\n"
                        "3. Usa 'Cerca Summoner' per analizzare qualsiasi account LoL\n"
                        "4. Esplora Analytics per vedere statistiche avanzate",
                        size=12, color=MUTED, selectable=True,
                    ),
                ]),
                bgcolor=CARD,
                border_radius=12,
                padding=18,
                border=ft.Border.all(1, f"{GOLD}30"),
            ),
        ],
        scroll=ft.ScrollMode.AUTO,
        spacing=0,
        ),
        padding=32,
        expand=True,
    )
