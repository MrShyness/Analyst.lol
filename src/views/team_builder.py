"""
team_builder.py — Costruisci il tuo team con icone ruoli ufficiali
"""
import flet as ft
from core.riot_api import get_champion_icon_url, get_role_icon_url

BG = "#080D18"; SURFACE = "#0F1629"; CARD = "#172135"; BORDER = "#1E2D47"
GOLD = "#C89B3C"; CYAN = "#00C8FF"; TEXT = "#ECF0F6"; MUTED = "#667A99"; RED = "#FF4455"

ROLES = ["Top", "Jungle", "Mid", "Bot", "Support"]
ROLE_COLORS = {
    "Top": "#E45858", "Jungle": "#58A45B", "Mid": "#5884E4",
    "Bot": "#D4A05A", "Support": "#9B59B6",
}
GLASS = "#101828AA"

def build_team_builder(page: ft.Page, navigate) -> ft.Control:
    
    def _role_slot(role: str) -> ft.Container:
        color = ROLE_COLORS.get(role, GOLD)
        champ_img_ref = ft.Ref[ft.Image]()
        
        def on_champ_change(e):
            val = e.control.value
            if val:
                champ_img_ref.current.src = get_champion_icon_url(val)
                # Soft check if asset exists mentally (DataDragon fallback is usually handled by URL)
            else:
                champ_img_ref.current.src = get_champion_icon_url("None")
            if champ_img_ref.current.page:
                champ_img_ref.current.update()

        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Image(src=get_role_icon_url(role), width=28, height=28, color=color),
                    padding=10, bgcolor=f"{color}15", border_radius=12,
                    border=ft.border.all(1, f"{color}30")
                ),
                ft.Column([
                    ft.Text(role.upper(), size=10, weight="bold", color=color, letter_spacing=1),
                    ft.TextField(
                        hint_text="Seleziona Campione...",
                        hint_style=ft.TextStyle(color=MUTED, size=12),
                        border=ft.InputBorder.NONE,
                        color=TEXT,
                        on_change=on_champ_change,
                        text_size=16,
                        expand=True,
                        cursor_color=color,
                        content_padding=ft.Padding.only(bottom=5)
                    ),
                ], spacing=0, expand=True),
                ft.Container(
                    content=ft.Image(
                        ref=champ_img_ref,
                        src=get_champion_icon_url("None"),
                        width=56, height=56, border_radius=28,
                        fit=ft.ImageFit.COVER
                    ),
                    padding=2, border=ft.border.all(2, f"{color}40"),
                    border_radius=30, bgcolor=BG,
                    shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=f"{color}20")
                )
            ], spacing=15),
            padding=ft.Padding.symmetric(horizontal=15, vertical=10),
            bgcolor=GLASS, border_radius=16,
            border=ft.border.all(1, BORDER),
            animate=ft.animation.Animation(400, ft.AnimationCurve.EASE_OUT)
        )

    team_column = ft.Column([_role_slot(r) for r in ROLES], spacing=12)

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("👥 Team Builder", size=28, weight="bold", color=GOLD),
                    ft.Text("Costruisci la tua draft ideale con icone ufficiali", size=14, color=MUTED),
                ]),
                ft.IconButton(
                    icon=ft.icons.REPLAY_CIRCLE_FILLED,
                    icon_color=MUTED,
                    tooltip="Reset Team",
                    on_click=lambda _: page.go("/team-builder")
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=20),
            team_column,
            ft.Container(height=20),
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.icons.STARS, color=GOLD, size=24),
                        ft.Column([
                            ft.Text("SYNERGY ENGINE v2.0", size=10, weight="bold", color=GOLD, letter_spacing=1.5),
                            ft.Text("In-Game Performance Forecast", size=16, weight="bold", color=TEXT),
                        ], spacing=0),
                        ft.Container(expand=True),
                        ft.Text("PRESTAZIONE: OTTIMALE", size=10, weight="bold", color=GREEN),
                    ]),
                    ft.Container(height=5),
                    ft.ProgressBar(value=0.88, bgcolor=f"{GOLD}10", color=GOLD, height=8, border_radius=4),
                    ft.Row([
                        ft.Text("Your team composition has extremely high late-game scaling and crowd control synergy.",
                                size=11, color=MUTED, expand=True),
                        ft.Text("88%", size=14, weight="bold", color=GOLD),
                    ])
                ], spacing=10),
                padding=24, bgcolor=f"{GOLD}05", border_radius=20, 
                border=ft.border.all(1, f"{GOLD}20"),
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=30, color="#00000033"),
                blur=10
            )
        ], scroll=ft.ScrollMode.AUTO),
        padding=30, expand=True
    )
