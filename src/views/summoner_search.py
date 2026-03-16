"""
summoner_search.py — Ricerca summoner singola e batch con Riot API
Esegue chiamate API reali in thread separato per non bloccare la UI.
"""
from __future__ import annotations
import flet as ft
import threading
from core.riot_api import riot, RiotAPIError, TIER_COLORS, REGIONS, get_profile_icon_url
from core.config import get_riot_region

TEXT = "#ECF0F6"; MUTED = "#667A99"; BORDER = "#1E2D47"
GLASS = "#101828AA"


def _rank_badge(entry: dict | None) -> ft.Container:
    if not entry:
        return ft.Container(
            content=ft.Text("Unranked", size=11, color=MUTED),
            bgcolor=f"{MUTED}18", border_radius=6,
            padding=ft.Padding.symmetric(vertical=4, horizontal=10),
        )
    tier = entry.get("tier", "UNRANKED")
    rank = entry.get("rank", "")
    lp   = entry.get("leaguePoints", 0)
    color = TIER_COLORS.get(tier, MUTED)
    return ft.Container(
        content=ft.Text(f"{tier} {rank}  {lp} LP", size=11, color=color,
                        weight=ft.FontWeight.W_600),
        bgcolor=f"{color}18",
        border=ft.Border.all(1, f"{color}50"),
        border_radius=6,
        padding=ft.Padding.symmetric(vertical=4, horizontal=10),
    )


def _profile_card(profile: dict) -> ft.Container:
    solo  = profile.get("solo")
    flex  = profile.get("flex")
    winrate = profile.get("winrate", 0)
    name    = profile.get("name", "?")
    level   = profile.get("level", 0)
    mastery = profile.get("mastery", [])

    wr_color = GREEN if winrate >= 55 else (GOLD if winrate >= 50 else RED)

    mastery_row = ft.Row([
        ft.Container(
            content=ft.Text(f"#{m.get('championId', '?')}", size=10, color=GOLD),
            bgcolor=f"{GOLD}15", border_radius=6,
            padding=ft.Padding.symmetric(vertical=3, horizontal=8),
            tooltip=f"Pts: {m.get('championPoints', 0):,}",
        )
        for m in mastery[:5]
    ], spacing=4, wrap=True)

    return ft.Container(
        content=ft.Column([
            # Header
            ft.Row([
                ft.Container(
                    content=ft.Image(
                        src=get_profile_icon_url(profile.get("profileIconId", 0)),
                        width=52, height=52, fit=ft.ImageFit.COVER,
                        border_radius=26,
                    ),
                    width=52, height=52, bgcolor=f"{GOLD}20",
                    border_radius=26, border=ft.Border.all(2, GOLD),
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Column([
                    ft.Text(name, size=16, weight=ft.FontWeight.BOLD, color=TEXT),
                    ft.Text(f"Level {level}", size=11, color=MUTED),
                ], spacing=2, expand=True),
                ft.Column([
                    ft.Text(f"{winrate}% WR", size=14, weight=ft.FontWeight.BOLD,
                            color=wr_color),
                    ft.Text("Solo/Duo", size=10, color=MUTED),
                ], horizontal_alignment=ft.CrossAxisAlignment.END),
            ], spacing=12),

            ft.Divider(height=12, color=BORDER),

            # Rank badges
            ft.Row([
                ft.Column([ft.Text("Solo/Duo", size=10, color=MUTED), _rank_badge(solo)], spacing=4),
                ft.Column([ft.Text("Flex", size=10, color=MUTED), _rank_badge(flex)], spacing=4),
            ], spacing=20),

            # Mastery
            ft.Container(height=8),
            ft.Text("Top Champions (ID)", size=10, color=MUTED),
            ft.Container(height=4),
            mastery_row,
        ], spacing=0),
        bgcolor=GLASS,
        border_radius=20,
        padding=24,
        border=ft.Border.all(1, BORDER),
        margin=ft.Margin.only(bottom=15),
        shadow=ft.BoxShadow(spread_radius=0, blur_radius=20, color="#00000033"),
        animate=ft.animation.Animation(400, ft.AnimationCurve.EASE_OUT)
    )


def build_summoner_search(page: ft.Page, navigate, initial_name: str = None) -> ft.Control:
    region_ref   = ft.Ref[ft.Dropdown]()
    input_ref    = ft.Ref[ft.TextField]()
    results_ref  = ft.Ref[ft.Column]()
    status_ref   = ft.Ref[ft.Text]()
    spinner_ref  = ft.Ref[ft.ProgressRing]()
    search_btn   = ft.Ref[ft.ElevatedButton]()

    def set_loading(is_loading: bool):
        spinner_ref.current.visible = is_loading
        search_btn.current.disabled = is_loading
        page.update()

    def _do_search(name: str):
        set_loading(True)
        results_ref.current.controls.clear()
        status_ref.current.value = ""
        try:
            profile = riot.get_full_profile(name.strip())
            results_ref.current.controls.append(_profile_card(profile))
            status_ref.current.value = f"✅ Profilo caricato per '{profile['name']}'"
            status_ref.current.color = GREEN
        except RiotAPIError as e:
            status_ref.current.value = f"❌ {e}"
            status_ref.current.color = RED
        except Exception as e:
            status_ref.current.value = f"⚠️ Errore imprevisto: {e}"
            status_ref.current.color = GOLD
        finally:
            set_loading(False)

    def do_search(e=None):
        name = (input_ref.current.value or "").strip()
        if not name:
            status_ref.current.value = "⚠️ Inserisci un nome summoner"
            status_ref.current.color = GOLD
            page.update()
            return
        threading.Thread(target=_do_search, args=(name,), daemon=True).start()

    # Batch search
    batch_ref   = ft.Ref[ft.TextField]()
    batch_btn   = ft.Ref[ft.ElevatedButton]()

    def _do_batch(names: list[str]):
        set_loading(True)
        results_ref.current.controls.clear()
        status_ref.current.value = f"🔄 Caricamento batch ({len(names)} summoners)…"
        status_ref.current.color = CYAN
        page.update()
        ok, failed = 0, 0
        for n in names:
            if not n.strip():
                continue
            try:
                profile = riot.get_full_profile(n.strip())
                results_ref.current.controls.append(_profile_card(profile))
                ok += 1
            except Exception:
                failed += 1
        status_ref.current.value = f"✅ Batch completato — {ok} trovati, {failed} falliti"
        status_ref.current.color = GREEN if failed == 0 else GOLD
        set_loading(False)

    def do_batch(e=None):
        raw = (batch_ref.current.value or "").strip()
        if not raw:
            return
        names = [n.strip() for n in raw.replace("\n", ",").split(",") if n.strip()]
        if not names:
            return
        threading.Thread(target=_do_batch, args=(names,), daemon=True).start()

    region_options = [ft.dropdown.Option(r) for r in REGIONS]
    tab_singolo_content = ft.Container(
        content=ft.Column([
            ft.Container(height=16),
            ft.Row([
                ft.TextField(
                    ref=input_ref,
                    hint_text="Nome Summoner (es. Faker)",
                    prefix_icon="person_search",
                    bgcolor=CARD, border_radius=10,
                    border_color=BORDER, focused_border_color=CYAN,
                    color=TEXT, hint_style=ft.TextStyle(color=MUTED),
                    on_submit=do_search, expand=True,
                ),
                ft.Dropdown(
                    ref=region_ref, label="Regione",
                    value=get_riot_region(),
                    options=region_options,
                    bgcolor=CARD, border_radius=10,
                    border_color=BORDER, focused_border_color=CYAN,
                    color=TEXT, width=130,
                    on_select=lambda e: None,
                ),
                ft.ElevatedButton(
                    "Cerca",
                    ref=search_btn,
                    icon="search",
                    on_click=do_search,
                    style=ft.ButtonStyle(
                        bgcolor=GOLD, color="#000",
                        shape=ft.RoundedRectangleBorder(radius=10),
                        padding=ft.Padding.symmetric(vertical=16, horizontal=20),
                    ),
                ),
            ], spacing=10),
        ], spacing=0),
        padding=ft.Padding.only(bottom=12),
    )

    tab_batch_content = ft.Container(
        content=ft.Column([
            ft.Container(height=16),
            ft.Text("Inserisci i nomi separati da virgola o a capo", size=12, color=MUTED),
            ft.Container(height=8),
            ft.TextField(
                ref=batch_ref,
                multiline=True, min_lines=4, max_lines=8,
                hint_text="Faker, Chovy, Caps, ...",
                bgcolor=CARD, border_radius=10,
                border_color=BORDER, focused_border_color=CYAN,
                color=TEXT, hint_style=ft.TextStyle(color=MUTED),
            ),
            ft.Container(height=8),
            ft.ElevatedButton(
                "Avvia Batch Search",
                ref=batch_btn,
                icon="batch_prediction",
                on_click=do_batch,
                style=ft.ButtonStyle(
                    bgcolor=CYAN, color="#000",
                    shape=ft.RoundedRectangleBorder(radius=10),
                    padding=ft.Padding.symmetric(vertical=14, horizontal=20),
                ),
            ),
        ], spacing=0),
        padding=ft.Padding.only(bottom=12),
    )

    tabs_content_area = ft.Container(content=tab_singolo_content)
    tab1_btn = ft.ElevatedButton("🔍 Singolo")
    tab2_btn = ft.ElevatedButton("📋 Batch")

    def switch_tab(idx):
        if idx == 0:
            tabs_content_area.content = tab_singolo_content
            tab1_btn.style = ft.ButtonStyle(bgcolor=GOLD, color="#000")
            tab2_btn.style = ft.ButtonStyle(bgcolor=CARD2, color=TEXT)
        else:
            tabs_content_area.content = tab_batch_content
            tab1_btn.style = ft.ButtonStyle(bgcolor=CARD2, color=TEXT)
            tab2_btn.style = ft.ButtonStyle(bgcolor=GOLD, color="#000")
        try:
            if tabs_content_area.page:
                tabs_content_area.update()
                tab1_btn.update()
                tab2_btn.update()
        except Exception:
            pass

    tab1_btn.on_click = lambda _: switch_tab(0)
    tab2_btn.on_click = lambda _: switch_tab(1)
    switch_tab(0)

    tabs = ft.Column([
        ft.Row([tab1_btn, tab2_btn], spacing=10),
        tabs_content_area
    ])

    search_ui = ft.Container(
        content=ft.Column([
            ft.Text("🔍 Summoner Search", size=22, weight=ft.FontWeight.BOLD, color=GOLD),
            ft.Text("Analizza qualsiasi account su tutte le regioni", size=13, color=MUTED),
            ft.Container(height=8),
            tabs,
            # Status + Spinner
            ft.Row([
                ft.ProgressRing(ref=spinner_ref, visible=False, width=18, height=18,
                                stroke_width=2, color=CYAN),
                ft.Text(ref=status_ref, size=12, color=MUTED),
            ], spacing=10),
            ft.Container(height=8),
            # Results
            ft.Column(ref=results_ref, spacing=0, scroll=ft.ScrollMode.AUTO, expand=True),
        ], spacing=0, expand=True),
        padding=32, expand=True,
    )

    if initial_name:
        input_ref.current.value = initial_name
        # Add a delay to ensure UI is ready before background search starts
        threading.Timer(0.5, lambda: do_search()).start()

    return search_ui
