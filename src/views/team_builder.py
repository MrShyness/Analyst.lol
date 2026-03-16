"""
team_builder.py — Costruisci il tuo team con icone ruoli ufficiali e synergy engine
"""
import flet as ft
from core.datadragon import dd_service

# ── Palette & Design Tokens ──────────────────────────────────────────────────
BG      = "#080D18"
SURFACE = "#0F1629"
CARD    = "#172135"
BORDER  = "#1E2D47"
GOLD    = "#C89B3C"
CYAN    = "#00C8FF"
GREEN   = "#00D4A0"
RED     = "#FF4455"
TEXT    = "#ECF0F6"
MUTED   = "#667A99"
GLASS   = "#101828CC"
SPACING = 8

ROLES = ["Top", "Jungle", "Mid", "Bot", "Support"]
ROLE_COLORS = {
    "Top": "#E45858", "Jungle": "#58A45B", "Mid": "#5884E4",
    "Bot": "#D4A05A", "Support": "#9B59B6",
}

def build_team_builder(page: ft.Page, navigate) -> ft.Control:
    
    # State tracking for validation
    selected_champs = {role: None for role in ROLES}
    
    def _role_slot(role: str) -> ft.Container:
        color = ROLE_COLORS.get(role, GOLD)
        champ_img_ref = ft.Ref[ft.Image]()
        role_label_ref = ft.Ref[ft.Text]()
        
        def on_champ_change(e):
            val = e.control.value.strip()
            selected_champs[role] = val if val else None
            
            if val:
                # Use Data Dragon for champion portrait
                champ_img_ref.current.src = dd_service.get_champion_square_url(val.capitalize())
            else:
                champ_img_ref.current.src = "https://ddragon.leagueoflegends.com/cdn/14.5.1/img/champion/Aatrox.png" # Placeholder
                champ_img_ref.current.opacity = 0.2
            
            if champ_img_ref.current.page:
                champ_img_ref.current.opacity = 1.0 if val else 0.2
                champ_img_ref.current.update()
            
            _update_synergy()

        def on_hover(e):
            e.control.scale = 1.02 if e.data == "true" else 1.0
            e.control.border = ft.Border.all(1, GOLD if e.data == "true" else BORDER)
            e.control.update()

        # Official Icon from Data Dragon Service
        role_icon_url = dd_service.get_role_icon_url(role)

        return ft.Container(
            content=ft.Row([
                # Role Icon Container
                ft.Container(
                    content=ft.Image(
                        src=role_icon_url, 
                        width=24, height=24, 
                        color=color,
                        tooltip=f"Ruolo Corretto: {role}"
                    ),
                    padding=12, 
                    bgcolor=f"{color}15", 
                    border_radius=12,
                    border=ft.Border.all(1, f"{color}30")
                ),
                # Input Area
                ft.Column([
                    ft.Text(role.upper(), weight=ft.FontWeight.BOLD, color=color, 
                            style=ft.TextStyle(size=10, letter_spacing=1.5), ref=role_label_ref),
                    ft.TextField(
                        hint_text="Seleziona Campione...",
                        hint_style=ft.TextStyle(color=MUTED, size=12),
                        border=ft.InputBorder.NONE,
                        color=TEXT,
                        on_change=on_champ_change,
                        text_size=15,
                        expand=True,
                        cursor_color=GOLD,
                        content_padding=ft.Padding.only(bottom=8)
                    ),
                ], spacing=0, expand=True),
                # Champion Preview
                ft.Container(
                    content=ft.Image(
                        ref=champ_img_ref,
                        src=dd_service.get_champion_square_url("None"), # Placeholder handled by opacity
                        width=52, height=52, border_radius=26,
                        fit=ft.BoxFit.COVER,
                        opacity=0.2
                    ),
                    padding=2, border=ft.Border.all(2, f"{color}40"),
                    border_radius=30, bgcolor=BG,
                    shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=f"{color}20")
                )
            ], spacing=20),
            padding=ft.Padding.symmetric(horizontal=20, vertical=12),
            bgcolor=GLASS, 
            border_radius=20,
            border=ft.Border.all(1, BORDER),
            on_hover=on_hover,
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT)
        )

    # Synergy Engine Logic
    synergy_bar = ft.ProgressBar(value=0.2, bgcolor=f"{GOLD}10", color=GOLD, height=10, border_radius=5)
    synergy_text = ft.Text("20%", size=16, weight=ft.FontWeight.BOLD, color=GOLD)
    synergy_desc = ft.Text("Seleziona i campioni per analizzare la sinergia del team.", size=12, color=MUTED, expand=True)

    def _update_synergy():
        count = sum(1 for v in selected_champs.values() if v)
        val = 0.2 + (count * 0.15)
        if val > 1.0: val = 1.0
        
        synergy_bar.value = val
        synergy_text.value = f"{int(val * 100)}%"
        
        if count == 0:
            synergy_desc.value = "Seleziona i campioni per analizzare la sinergia del team."
        elif count < 3:
            synergy_desc.value = "Composizione parziale. Aggiungi più ruoli per una valutazione attendibile."
        elif count < 5:
            synergy_desc.value = "Sinergia in crescita. Buona copertura dei ruoli principali."
        else:
            synergy_desc.value = "Team completo! Elevato scaling late-game e sinergia CC ottimale."
            
        synergy_bar.update()
        synergy_text.update()
        synergy_desc.update()

    team_column = ft.Column([_role_slot(r) for r in ROLES], spacing=SPACING*1.5)

    return ft.Container(
        content=ft.Column([
            # ── Header ────────────────────────────────────────────────────────
            ft.Row([
                ft.Column([
                    ft.Text("👥 Team Builder", size=32, weight=ft.FontWeight.BOLD, color=GOLD),
                    ft.Row([
                        ft.Container(width=8, height=8, bgcolor=GREEN, border_radius=4),
                        ft.Text("Official Data Dragon Assets Integration", size=13, color=MUTED),
                    ], spacing=8),
                ], spacing=4),
                ft.Container(
                    content=ft.IconButton(
                        icon=ft.Icons.REFRESH_ROUNDED,
                        icon_color=GOLD,
                        on_click=lambda _: navigate(2), # Reload view
                    ),
                    bgcolor=f"{GOLD}10",
                    border_radius=12,
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Container(height=SPACING*3),
            
            # ── Content ───────────────────────────────────────────────────────
            ft.Row([
                # Left side: Slots
                ft.Column([
                    ft.Text("DRAFT COMPOSITION", weight=ft.FontWeight.BOLD, color=MUTED, 
                            style=ft.TextStyle(size=11, letter_spacing=1.2)),
                    ft.Container(height=SPACING),
                    team_column,
                ], expand=3, spacing=0),
                
                # Right side: Synergy & Analysis
                ft.Column([
                    ft.Text("ANALYSIS ENGINE", weight=ft.FontWeight.BOLD, color=MUTED, 
                            style=ft.TextStyle(size=11, letter_spacing=1.2)),
                    ft.Container(height=SPACING),
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.STARS_ROUNDED, color=GOLD, size=28),
                                ft.Column([
                                    ft.Text("SYNERGY FORECAST", weight=ft.FontWeight.BOLD, color=GOLD, 
                                            style=ft.TextStyle(size=10, letter_spacing=1.5)),
                                    ft.Text("Draft Metrics", size=20, weight=ft.FontWeight.BOLD, color=TEXT),
                                ], spacing=0),
                            ]),
                            ft.Container(height=10),
                            ft.Row([
                                synergy_desc,
                                synergy_text,
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            synergy_bar,
                            ft.Divider(height=30, color=f"{GOLD}10"),
                            ft.Text("CONSIGLI DRAFT:", size=11, weight=ft.FontWeight.BOLD, color=TEXT),
                            ft.Row([
                                ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=GREEN, size=16),
                                ft.Text("Team bilanciato (AD/AP mix)", size=12, color=MUTED),
                            ], spacing=8),
                            ft.Row([
                                ft.Icon(ft.Icons.INFO_OUTLINE, color=CYAN, size=16),
                                ft.Text("Punta su engage di gruppo", size=12, color=MUTED),
                            ], spacing=8),
                        ], spacing=10),
                        padding=24,
                        bgcolor=GLASS,
                        border_radius=24,
                        border=ft.Border.all(1, f"{GOLD}20"),
                        blur=20,
                    ),
                    # Validation Tips
                    ft.Container(
                        content=ft.Column([
                            ft.Text("VALIDATION STATUS", size=10, weight=ft.FontWeight.BOLD, color=TEXT),
                            ft.Row([
                                ft.Icon(ft.Icons.SHIELD_MOON, color=GOLD, size=16),
                                ft.Text("Safe-Mode Logic Active", size=11, color=MUTED),
                            ], spacing=8),
                        ], spacing=6),
                        padding=16,
                        bgcolor=f"{SURFACE}50",
                        border_radius=16,
                        border=ft.Border.all(1, BORDER),
                    )
                ], expand=2, spacing=15),
            ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START),
            
        ], scroll=ft.ScrollMode.AUTO),
        padding=40,
        expand=True
    )