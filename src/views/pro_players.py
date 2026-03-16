"""
pro_players.py — Database pro players con filtri e link rapido a Summoner Search
"""
import flet as ft
from core.riot_api import get_champion_icon_url, get_role_icon_url
from core.pro_players_data import PRO_PLAYERS

BG = "#080D18"; SURFACE = "#0F1629"; CARD = "#172135"; CARD2 = "#1E2A40"
GOLD = "#C89B3C"; CYAN = "#00C8FF"; GREEN = "#00D4A0"; RED = "#FF4455"
TEXT = "#ECF0F6"; MUTED = "#667A99"; BORDER = "#1E2D47"
GLASS = "#101828AA"
ROSETTE = "#C89B3C33"

ROLE_COLORS = {
    "Top": "#E45858", "Jungle": "#58A45B", "Mid": "#5884E4",
    "Bot": "#D4A05A", "Support": "#9B59B6",
}

def build_pro_players(page: ft.Page, navigate) -> ft.Control:
    filtered = ft.Ref[ft.Column]()
    search_val = ft.Ref[ft.TextField]()
    role_dd = ft.Ref[ft.Dropdown]()
    region_dd = ft.Ref[ft.Dropdown]()

    def _player_card(p: dict, navigate) -> ft.Container:
        role_color = ROLE_COLORS.get(p["role"], GOLD)
        champs_text = " · ".join(p["champs"])
        
        # Player Photo logic - Use photo_url if present, else fallback to Team Initial
        if p.get("photo_url"):
            photo_display = ft.Container(
                content=ft.Image(
                    src=p["photo_url"],
                    fit=ft.ImageFit.COVER,
                    error_content=ft.Text(p["team"][:1], weight="bold", color=TEXT),
                    width=48, height=48,
                ),
                width=48, height=48, border_radius=12,
                bgcolor=f"{role_color}20",
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                border=ft.border.all(1, f"{role_color}40")
            )
        else:
            photo_display = ft.Container(
                content=ft.Text(p["team"][:1], size=20, weight="bold", color=TEXT),
                width=48, height=48, bgcolor=f"{role_color}20",
                border_radius=12, alignment=ft.alignment.center,
                border=ft.border.all(1, f"{role_color}40")
            )

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    photo_display,
                    ft.Column([
                        ft.Text(p["name"], size=16, weight="bold", color=TEXT),
                        ft.Text(f"{p['team']} • {p['region']}", size=12, color=MUTED),
                    ], spacing=2, expand=True),
                    ft.Container(
                        content=ft.Image(src=get_role_icon_url(p["role"]), width=16, height=16, color=role_color),
                        padding=6, border_radius=8, bgcolor=f"{role_color}10"
                    )
                ], spacing=12),
                ft.Divider(height=1, color=BORDER),
                ft.Row([
                    ft.Row([
                        ft.Image(src=get_champion_icon_url(c), width=24, height=24, border_radius=12)
                        for c in p["champs"][:3]
                    ], spacing=4),
                    ft.Row([
                        ft.ElevatedButton(
                            "Confronta",
                            icon=ft.icons.COMPARE_ARROWS,
                            style=ft.ButtonStyle(
                                color=CYAN, bgcolor="transparent",
                                side={"": ft.BorderSide(1, f"{CYAN}40")},
                                padding=ft.Padding.symmetric(vertical=4, horizontal=10)
                            ),
                            on_click=lambda _: navigate(3, initial_benchmark=p['name']) # Go to Analytics (index 3)
                        ),
                        ft.ElevatedButton(
                            "Analizza",
                            icon=ft.icons.ANALYTICS,
                            style=ft.ButtonStyle(
                                color=GOLD, bgcolor="transparent",
                                side={"": ft.BorderSide(1, f"{GOLD}40")},
                                padding=ft.Padding.symmetric(vertical=4, horizontal=10)
                            ),
                            on_click=lambda _: navigate(1, initial_name=p["account"]) # Go to Search view (index 1)
                        )
                    ], spacing=10)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ], spacing=12),
            bgcolor=GLASS,
            border_radius=20,
            padding=20,
            border=ft.border.all(1, BORDER),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=10, color="#00000022"),
            on_hover=lambda e: setattr(e.control, "bgcolor",
                f"{SURFACE}99" if e.data == "true" else GLASS) or (e.control.update() if e.control.page else None),
            animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT)
        )

    def refresh(e=None):
        search = (search_val.current.value or "").lower()
        role = role_dd.current.value or "All"
        region = region_dd.current.value or "All"

        result = [
            p for p in PRO_PLAYERS
            if (search in p["name"].lower() or search in p["team"].lower())
            and (role == "All" or p["role"] == role)
            and (region == "All" or p["region"] == region)
        ]
        
        # Pagination or Grid update
        filtered.current.controls = [
            ft.Row([
                _player_card(p, navigate) for p in result[i:i+3]
            ], spacing=10) for i in range(0, len(result), 3)
        ]
        if filtered.current.page:
            filtered.current.update()

    all_roles = ["All"] + sorted(list(set(p["role"] for p in PRO_PLAYERS)))
    all_regions = ["All"] + sorted(list(set(p["region"] for p in PRO_PLAYERS)))

    search_field = ft.TextField(
        ref=search_val, hint_text="Cerca player o team...",
        prefix_icon=ft.icons.SEARCH, on_change=refresh, expand=True,
        bgcolor=CARD, border_color=BORDER, border_radius=10, color=TEXT
    )
    
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("🏆 Pro Players", size=28, weight="bold", color=GOLD),
                ft.Container(expand=True),
                ft.Text(f"Total: {len(PRO_PLAYERS)}", color=MUTED, size=12)
            ]),
            ft.Row([
                search_field,
                ft.Dropdown(
                    ref=role_dd, value="All", width=120,
                    options=[ft.dropdown.Option(r) for r in all_roles],
                    on_change=refresh, bgcolor=CARD, border_color=BORDER
                ),
                ft.Dropdown(
                    ref=region_dd, value="All", width=120,
                    options=[ft.dropdown.Option(r) for r in all_regions],
                    on_change=refresh, bgcolor=CARD, border_color=BORDER
                ),
            ], spacing=10),
            ft.Container(height=10),
            ft.Column(
                ref=filtered,
                controls=[
                    ft.Row([
                        _player_card(p, navigate) for p in PRO_PLAYERS[i:i+3]
                    ], spacing=10) for i in range(0, 15, 3) # Load first 15 by default
                ],
                spacing=10, scroll=ft.ScrollMode.AUTO, expand=True
            )
        ], spacing=15),
        padding=30, expand=True
    )

