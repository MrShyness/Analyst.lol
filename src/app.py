"""
app.py — Guide.Analyst | Entry point principale
Dark Esports Luxury UI — Flet native desktop app
"""
import flet as ft
from core.config import is_safe_mode, load_settings, get_env, get_riot_region
from views.dashboard       import build_dashboard
from views.summoner_search import build_summoner_search
from views.team_builder    import build_team_builder
from views.analytics       import build_analytics
from views.pro_players     import build_pro_players
from views.settings_view   import build_settings
from views.agentic_console import build_agentic_console

# ── Palette ──────────────────────────────────────────────────────────────────
BG      = "#080D18"
SURFACE = "#0F1629"
CARD    = "#172135"
CARD2   = "#1E2A40"
GOLD    = "#C89B3C"
GOLD2   = "#E8C96C"
CYAN    = "#00C8FF"
GREEN   = "#00D4A0"
RED     = "#FF4455"
TEXT    = "#ECF0F6"
MUTED   = "#667A99"
BORDER  = "#1E2D47"
GLASS   = "#101828CC" # Semi-transparent for glassmorphism
GLASS_BORDER = "#C89B3C33"
BLUR    = 20

NAV_ITEMS = [
    ("🏠", "Dashboard",    build_dashboard),
    ("🔍", "Ricerca",      build_summoner_search),
    ("👥", "Team Builder", build_team_builder),
    ("📊", "Analytics",    build_analytics),
    ("🏆", "Pro Players",  build_pro_players),
    ("⚙️", "Impostazioni", build_settings),
    ("🧠", "Console",      build_agentic_console),
]


def main(page: ft.Page):
    # ── Window setup ─────────────────────────────────────────────────────────
    page.title           = "Guide.Analyst — LoL Analytics Suite"
    page.window_width    = 1280
    page.window_height   = 820
    page.window_min_width  = 900
    page.window_min_height = 600
    page.theme_mode      = ft.ThemeMode.DARK
    page.bgcolor         = BG
    page.padding         = 0

    page.theme = ft.Theme(
        color_scheme_seed=GOLD,
    )

    # ── State ─────────────────────────────────────────────────────────────────
    current_index = {"value": 0}
    nav_buttons: list[ft.Control] = []
    content_area = ft.Container(expand=True, bgcolor=BG)

    def navigate(index: int, **kwargs):
        if index == current_index["value"] and not kwargs:
            return
        current_index["value"] = index

        # Aggiorna evidenziazione sidebar
        for i, btn in enumerate(nav_buttons):
            inner: ft.Container = btn
            is_active = (i == index)
            inner.bgcolor = f"{GOLD}18" if is_active else "transparent"
            if inner.content and isinstance(inner.content, ft.Row):
                row: ft.Row = inner.content
                if row.controls:
                    bar = row.controls[0]
                    bar.bgcolor = GOLD if is_active else "transparent"
                    label_col: ft.Column = row.controls[1]
                    em, lbl = label_col.controls
                    em.color  = GOLD if is_active else TEXT
                    lbl.color = GOLD if is_active else MUTED

        # Carica nuovo contenuto
        builder = NAV_ITEMS[index][2]
        content_area.content = builder(page, navigate, **kwargs)
        page.update()

    # ── Sidebar builder ───────────────────────────────────────────────────────
    def _nav_btn(index: int, emoji: str, label: str) -> ft.Container:
        is_active = (index == 0)

        active_bar = ft.Container(
            width=4, height=40,
            bgcolor=GOLD if is_active else "transparent",
            border_radius=ft.BorderRadius.only(top_right=4, bottom_right=4),
        )
        emoji_text = ft.Text(emoji, size=20, color=GOLD if is_active else TEXT)
        label_text = ft.Text(label, size=12, color=GOLD if is_active else MUTED,
                             weight=ft.FontWeight.W_500 if is_active else ft.FontWeight.NORMAL)

        def _on_hover(e, idx=index):
            is_active = (current_index["value"] == idx)
            if e.data == "true":
                e.control.bgcolor = f"{GOLD}18" if is_active else f"{GOLD}0D"
            else:
                e.control.bgcolor = f"{GOLD}18" if is_active else "transparent"
            page.update()

        btn = ft.Container(
            content=ft.Row([
                active_bar,
                ft.Column([emoji_text, label_text], spacing=1,
                           horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ], spacing=12, alignment=ft.MainAxisAlignment.START),
            bgcolor=f"{GOLD}18" if is_active else "transparent",
            border_radius=ft.BorderRadius.only(top_right=10, bottom_right=10),
            height=64,
            padding=ft.Padding.only(right=14, top=10, bottom=10),
            on_click=lambda e, idx=index: navigate(idx),
            on_hover=_on_hover,
            ink=True,
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
        )
        nav_buttons.append(btn)
        return btn

    # Logo area
    logo_container = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Text("G.A", size=22, weight=ft.FontWeight.BOLD,
                                color=GOLD, font_family="monospace"),
                width=48, height=48,
                bgcolor=f"{GOLD}20",
                border=ft.Border.all(2, GOLD),
                border_radius=12,
                alignment=ft.Alignment.CENTER,
            ),
            ft.Text("Guide", size=10, color=MUTED),
            ft.Text("Analyst", size=10, color=GOLD, weight=ft.FontWeight.BOLD),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
        padding=ft.Padding.symmetric(vertical=20, horizontal=16),
    )

    # Nav buttons
    nav_col_controls = [
        logo_container,
        ft.Divider(height=1, color=BORDER),
        ft.Container(height=8),
        *[_nav_btn(i, e, l) for i, (e, l, _) in enumerate(NAV_ITEMS)],
    ]

    sidebar = ft.Container(
        content=ft.Column(nav_col_controls, spacing=0),
        width=160,
        bgcolor=GLASS,
        blur=BLUR,
        border=ft.Border.only(right=ft.BorderSide(1, BORDER)),
    )

    # ── Status bar ────────────────────────────────────────────────────────────
    from core.config import get_env, get_riot_region, is_safe_mode
    has_key = bool(get_env("RIOT_API_KEY"))
    status_bar = ft.Container(
        content=ft.Row([
            ft.Container(width=6, height=6, bgcolor=GREEN if has_key else RED,
                         border_radius=3),
            ft.Text(
                f"Riot API: {'Configurata' if has_key else 'Non configurata'}  •  "
                f"Regione: {get_riot_region()}  •  "
                f"{'🛡️ Safe Mode Attiva' if is_safe_mode() else '🚀 GPU Accelerated'}  •  "
                f"Guide.Analyst v2.0",
                size=10, color=MUTED,
            ),
        ], spacing=8),
        height=28,
        bgcolor=SURFACE,
        border=ft.Border.only(top=ft.BorderSide(1, BORDER)),
        padding=ft.Padding.symmetric(horizontal=16),
    )

    # ── Initial view ─────────────────────────────────────────────────────────
    content_area.content = build_dashboard(page, navigate)

    # ── Layout ───────────────────────────────────────────────────────────────
    main_row = ft.Row(
        controls=[sidebar, content_area],
        spacing=0, expand=True,
        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
    )
    page.add(
        ft.Column(
            controls=[main_row, status_bar],
            spacing=0,
            expand=True,
        )
    )
    page.update()


if __name__ == "__main__":
    import os
    
    # Se la Safe Mode è attiva, forza il renderer software (evita flickering GPU)
    if is_safe_mode():
        os.environ["FLET_RENDERER"] = "software"
        os.environ["FLUTTER_RENDERER"] = "software"
        os.environ["SKIA_RENDERER"] = "software"
        os.environ["FLET_FORCE_WARP"] = "1"
        os.environ["FLUTTER_GPU"] = "disabled"
        os.environ["ANGLE_DEFAULT_PLATFORM"] = "warp"
        print("[INFO] Safe Mode attiva: utilizzo software rendering estremo (WARP).")

    try:
        ft.run(target=main)
    except ConnectionResetError:
        # Silenzia l'errore socket alla chiusura su Windows (bug noto Flet/asyncio)
        pass
    except Exception as e:
        print(f"[ERRORE] Errore critico all'avvio: {e}")
