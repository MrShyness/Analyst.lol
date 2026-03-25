"""
team_builder.py — Team Builder avanzato con icone ruoli ufficiali LoL,
autocomplete campioni, synergy engine avanzato AD/AP/CC/Engage/Peel.
"""
import flet as ft
from core.datadragon import dd_service

# ── Palette & Design Tokens ─────────────────────────────────────────────────
BG      = "#080D18"
SURFACE = "#0F1629"
CARD    = "#172135"
CARD2   = "#1E2A40"
BORDER  = "#1E2D47"
GOLD    = "#C89B3C"
GOLD2   = "#E8C96C"
CYAN    = "#00C8FF"
GREEN   = "#00D4A0"
RED     = "#FF4455"
ORANGE  = "#FF8C42"
PURPLE  = "#9B59B6"
TEXT    = "#ECF0F6"
MUTED   = "#667A99"
GLASS   = "#101828CC"
SPACING = 8

ROLES = ["Top", "Jungle", "Mid", "Bot", "Support"]

ROLE_COLORS = {
    "Top":     "#E45858",
    "Jungle":  "#58A45B",
    "Mid":     "#5884E4",
    "Bot":     "#D4A05A",
    "Support": "#9B59B6",
}

ROLE_DESCRIPTIONS = {
    "Top":     "Solo lane — tank, fighter, split pusher",
    "Jungle":  "Objectives, ganks, dragon/baron control",
    "Mid":     "Mage, assassino, roaming, priority",
    "Bot":     "ADC — damage range, late-game carry",
    "Support": "Peel, engage, vision, utility",
}

# ── Champion Pool & Tags ───────────────────────────────────────────────────
CHAMPION_POOL = [
    "Aatrox","Ahri","Akali","Akshan","Alistar","Amumu","Anivia","Annie",
    "Aphelios","Ashe","Aurelion Sol","Azir","Bard","Blitzcrank","Brand",
    "Braum","Caitlyn","Camille","Cassiopeia","Cho'Gath","Corki","Darius",
    "Diana","Draven","Dr. Mundo","Ekko","Elise","Evelynn","Ezreal","Fiddlesticks",
    "Fiora","Fizz","Galio","Gangplank","Garen","Gnar","Gragas","Graves",
    "Gwen","Hecarim","Heimerdinger","Illaoi","Irelia","Ivern","Janna",
    "Jarvan IV","Jax","Jayce","Jhin","Jinx","K'Sante","Kai'Sa","Kalista",
    "Karma","Karthus","Kassadin","Katarina","Kayle","Kayn","Kennen","Kha'Zix",
    "Kindred","Kled","Lee Sin","Leona","Lillia","Lissandra","Lucian",
    "Lulu","Lux","Malphite","Malzahar","Maokai","Master Yi","Miss Fortune",
    "Mordekaiser","Morgana","Nami","Nasus","Nautilus","Neeko","Nidalee","Nilah",
    "Nocturne","Nunu","Olaf","Orianna","Ornn","Pantheon","Poppy","Pyke",
    "Qiyana","Quinn","Rakan","Rammus","Rek'Sai","Rell","Renata Glasc",
    "Renekton","Rengar","Riven","Rumble","Ryze","Samira","Sejuani","Senna",
    "Seraphine","Sett","Shaco","Shen","Shyvana","Singed","Sion","Sivir",
    "Sona","Soraka","Swain","Sylas","Syndra","Tahm Kench","Taliyah",
    "Talon","Taric","Teemo","Thresh","Tristana","Trundle","Tryndamere",
    "Twisted Fate","Twitch","Udyr","Urgot","Varus","Vayne","Veigar","Vel'Koz",
    "Vex","Vi","Viego","Viktor","Vladimir","Volibear","Warwick","Wukong",
    "Xayah","Xerath","Xin Zhao","Yasuo","Yone","Yorick","Yuumi","Zac",
    "Zed","Zeri","Ziggs","Zilean","Zoe","Zyra",
]

CHAMPION_TAGS = {
    "Aatrox": ["Fighter","Tank"],
    "Ahri": ["Mage","Assassin"],
    "Akali": ["Assassin"],
    "Akshan": ["ADC","Assassin"],
    "Alistar": ["Tank","Support"],
    "Amumu": ["Tank","AP"],
    "Anivia": ["Mage","CC"],
    "Annie": ["Mage","Burst"],
    "Aphelios": ["ADC"],
    "Ashe": ["ADC","Utility"],
    "Aurelion Sol": ["Mage","AP"],
    "Azir": ["Mage","Control"],
    "Bard": ["Support","Utility"],
    "Blitzcrank": ["Tank","CC"],
    "Brand": ["Mage","Burst"],
    "Braum": ["Tank","Support"],
    "Caitlyn": ["ADC","Range"],
    "Camille": ["Fighter","Assassin"],
    "Cassiopeia": ["Mage","DoT"],
    "Cho'Gath": ["Tank","AP"],
    "Corki": ["ADC","AP"],
    "Darius": ["Fighter","AD"],
    "Diana": ["Fighter","AP"],
    "Draven": ["ADC","AD"],
    "Dr. Mundo": ["Tank","AD"],
    "Ekko": ["Assassin","AP"],
    "Elise": ["Fighter","AP"],
    "Evelynn": ["Assassin","AP"],
    "Ezreal": ["ADC","AP"],
    "Fiddlesticks": ["Mage","CC"],
    "Fiora": ["Fighter","AD"],
    "Fizz": ["Assassin","AP"],
    "Galio": ["Tank","Mage"],
    "Gangplank": ["Fighter","AD"],
    "Garen": ["Fighter","Tank"],
    "Gnar": ["Fighter","Tank"],
    "Gragas": ["Fighter","AP"],
    "Graves": ["ADC","AD"],
    "Gwen": ["Fighter","AP"],
    "Hecarim": ["Fighter","AD"],
    "Heimerdinger": ["Mage","CC"],
    "Illaoi": ["Fighter","AD"],
    "Irelia": ["Fighter","AD"],
    "Ivern": ["Support","Utility"],
    "Janna": ["Support","Peel"],
    "Jarvan IV": ["Tank","Fighter"],
    "Jax": ["Fighter","AD"],
    "Jayce": ["Fighter","AD"],
    "Jhin": ["ADC","AD"],
    "Jinx": ["ADC","AD"],
    "K'Sante": ["Tank","Fighter"],
    "Kai'Sa": ["ADC","AP"],
    "Kalista": ["ADC","AD"],
    "Karma": ["Support","Utility"],
    "Karthus": ["Mage","DoT"],
    "Kassadin": ["Assassin","AP"],
    "Katarina": ["Assassin","AP"],
    "Kayle": ["Fighter","AD"],
    "Kayn": ["Fighter","AP"],
    "Kennen": ["Mage","Assassin"],
    "Kha'Zix": ["Assassin","AD"],
    "Kindred": ["Fighter","AD"],
    "Kled": ["Fighter","AD"],
    "Lee Sin": ["Fighter","AD"],
    "Leona": ["Tank","CC","Engage"],
    "Lillia": ["Mage","AP"],
    "Lissandra": ["Mage","CC"],
    "Lucian": ["ADC","AD"],
    "Lulu": ["Support","Utility"],
    "Lux": ["Mage","Support","CC"],
    "Malphite": ["Tank","CC","Engage"],
    "Malzahar": ["Mage","DoT"],
    "Maokai": ["Tank","CC"],
    "Master Yi": ["Fighter","AD"],
    "Miss Fortune": ["ADC","AD"],
    "Mordekaiser": ["Fighter","AP"],
    "Morgana": ["Support","CC"],
    "Nami": ["Support","CC"],
    "Nasus": ["Fighter","AD"],
    "Nautilus": ["Tank","CC","Engage"],
    "Neeko": ["Mage","CC"],
    "Nidalee": ["Fighter","AD"],
    "Nilah": ["Fighter","AD"],
    "Nocturne": ["Assassin","AD"],
    "Nunu": ["Fighter","AP"],
    "Olaf": ["Fighter","AD"],
    "Orianna": ["Mage","CC","Control"],
    "Ornn": ["Tank","Fighter"],
    "Pantheon": ["Fighter","AD"],
    "Poppy": ["Tank","Peel"],
    "Pyke": ["Assassin","AD"],
    "Qiyana": ["Assassin","AD"],
    "Quinn": ["ADC","AD"],
    "Rakan": ["Support","Engage"],
    "Rammus": ["Tank","CC"],
    "Rek'Sai": ["Fighter","AD"],
    "Rell": ["Tank","Support"],
    "Renata Glasc": ["Support","CC"],
    "Renekton": ["Fighter","AD"],
    "Rengar": ["Assassin","AD"],
    "Riven": ["Fighter","AD"],
    "Rumble": ["Mage","AP"],
    "Ryze": ["Mage","Control"],
    "Samira": ["ADC","AD"],
    "Sejuani": ["Tank","CC","Engage"],
    "Senna": ["ADC","Support"],
    "Seraphine": ["Support","Utility"],
    "Sett": ["Fighter","AD"],
    "Shaco": ["Assassin","AD"],
    "Shen": ["Tank","Peel"],
    "Shyvana": ["Fighter","AD"],
    "Singed": ["Fighter","AP"],
    "Sion": ["Tank","AD"],
    "Sivir": ["ADC","Utility"],
    "Sona": ["Support","Utility"],
    "Soraka": ["Support","Heal"],
    "Swain": ["Fighter","Mage"],
    "Sylas": ["Fighter","AP"],
    "Syndra": ["Mage","Burst"],
    "Tahm Kench": ["Tank","Support"],
    "Taliyah": ["Mage","CC"],
    "Talon": ["Assassin","AD"],
    "Taric": ["Support","Heal"],
    "Teemo": ["Fighter","Utility"],
    "Thresh": ["Support","CC","Engage"],
    "Tristana": ["ADC","Range"],
    "Trundle": ["Tank","AD"],
    "Tryndamere": ["Fighter","AD"],
    "Twisted Fate": ["Mage","Control"],
    "Twitch": ["ADC","Assassin"],
    "Udyr": ["Fighter","AD"],
    "Urgot": ["Fighter","AD"],
    "Varus": ["ADC","Mage"],
    "Vayne": ["ADC","AD"],
    "Veigar": ["Mage","Burst"],
    "Vel'Koz": ["Mage","DoT"],
    "Vex": ["Mage","Assassin"],
    "Vi": ["Fighter","AD","Engage"],
    "Viego": ["Assassin","AD"],
    "Viktor": ["Mage","Control"],
    "Vladimir": ["Mage","DoT"],
    "Volibear": ["Tank","AD","Engage"],
    "Warwick": ["Fighter","AD"],
    "Wukong": ["Fighter","AD"],
    "Xayah": ["ADC","AD"],
    "Xerath": ["Mage","Burst"],
    "Xin Zhao": ["Fighter","AD","Engage"],
    "Yasuo": ["Fighter","AD"],
    "Yone": ["Fighter","AD"],
    "Yorick": ["Fighter","AD"],
    "Yuumi": ["Support","Utility"],
    "Zac": ["Tank","CC"],
    "Zed": ["Assassin","AD"],
    "Zeri": ["ADC","AD"],
    "Ziggs": ["Mage","Burst"],
    "Zilean": ["Support","Utility"],
    "Zoe": ["Mage","Assassin"],
    "Zyra": ["Mage","CC"],
}

# ── Helper Functions ─────────────────────────────────────────────────────
def _get_tags(champ):
    if not champ:
        return []
    for k, v in CHAMPION_TAGS.items():
        if k.lower() == champ.lower():
            return v
    return ["Unknown"]

def _analyze_synergy(selected):
    champs = [v for v in selected.values() if v]
    count = len(champs)
    if count == 0:
        return {"score":0.15,"pct":15,"color":MUTED,
                "label":"VUOTO",
                "desc":"Seleziona i campioni per analizzare la composizione.",
                "metrics":{}}
    all_tags = []
    for c in champs:
        all_tags.extend(_get_tags(c))
    has_ad  = "AD" in all_tags
    has_ap  = "AP" in all_tags
    has_peel = any(t in all_tags for t in ["Peel","Shield","Heal"])
    has_tank = "Tank" in all_tags
    has_assassin = "Assassin" in all_tags
    has_engage   = "Engage" in all_tags
    cc_count = all_tags.count("CC") + all_tags.count("Engage")
    score = 0.15 + count * 0.10
    if has_ad and has_ap: score += 0.12
    if cc_count >= 2: score += 0.08
    if cc_count >= 4: score += 0.05
    if has_tank: score += 0.06
    if has_peel: score += 0.05
    if has_assassin and not has_tank: score -= 0.08
    if count == 5: score += 0.05
    score = max(0.05, min(score, 1.0))
    pct = int(score * 100)
    color = GREEN if pct>=75 else (GOLD if pct>=55 else (ORANGE if pct>=35 else RED))
    label = "OTTIMA" if pct>=80 else ("BUONA" if pct>=65 else ("DISCRETA" if pct>=50 else ("DEBOLE" if pct>=35 else "CRITICA")))
    
    # Build detailed description
    desc_parts = []
    if has_ad and has_ap:
        desc_parts.append("Mix bilanciato AD/AP")
    elif has_ad:
        desc_parts.append("Danno prevalentemente AD")
    elif has_ap:
        desc_parts.append("Danno prevalentemente AP")
    
    if cc_count >= 3:
        desc_parts.append("Controllo Crowd abbondante")
    elif cc_count >= 1:
        desc_parts.append("Controllo Crowd moderato")
    
    if has_tank:
        desc_parts.append("Presenza tank per frontline")
    if has_peel:
        desc_parts.append("Supporto peel per proteggere carry")
    if has_engage:
        desc_parts.append("Opzioni engage per iniziare combattimenti")
    
    desc = "Composizione " + ", ".join(desc_parts) if desc_parts else "Composizione base"
    
    # Build metrics
    metrics = {
        "Frontline": "✅ Forte" if has_tank else ("⚠️ Moderato" if any("Fighter" in _get_tags(c) for c in champs) else "❌ Debole"),
        "AD/AP": "✅ Bilanciato" if has_ad and has_ap else ("⚠️ Sbilanciato" if has_ad or has_ap else "❌ Mancante"),
        "CC": "✅ Alto" if cc_count >= 3 else ("⚠️ Medio" if cc_count >= 1 else "❌ Basso"),
        "Peel": "✅ Buono" if has_peel else ("⚠️ Limitato" if any("Support" in _get_tags(c) for c in champs) else "❌ Assente"),
        "Engage": "✅ Disponibile" if has_engage else ("⚠️ Limitato" if any("Tank" in _get_tags(c) for c in champs) else "❌ Assente"),
    }
    
    return {"score":score,"pct":pct,"color":color,"label":label,"desc":desc,"metrics":metrics}

def _clean_champ_id(champ_name):
    c = champ_name.replace("'","").replace(" ","").replace(".","") 
    if c.lower() == "wukong": return "MonkeyKing"
    if c.lower() == "renataglasc": return "Renata"
    if c.lower() == "nunu": return "Nunu"
    if c: return c[0].upper() + c[1:]
    return c

# ── Main Build Function ───────────────────────────────────────────────────
def build_team_builder(page: ft.Page, navigate) -> ft.Control:
    # State
    selected_champs = {role: None for role in ROLES}
    synergy_result = ft.Ref[ft.Container]()
    
    def update_synergy():
        result = _analyze_synergy(selected_champs)
        synergy_result.current.content = ft.Column([
            ft.Row([
                ft.Text(result["label"], size=24, weight=ft.FontWeight.BOLD, color=result["color"]),
                ft.Text(f"{result['pct']}%", size=20, weight=ft.FontWeight.BOLD, color=result["color"]),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Text(result["desc"], size=14, color=MUTED),
            ft.Divider(height=1, thickness=0.5, color=BORDER),
            ft.Column([
                ft.Row([
                    ft.Text(metric, size=12, color=TEXT, weight=ft.FontWeight.BOLD),
                    ft.Text(value, size=12, color=value.replace("✅", GREEN).replace("⚠️", GOLD).replace("❌", RED)),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                for metric, value in result["metrics"].items()
            ], spacing=4),
        ], spacing=8, tight=True)
        if synergy_result.current.page:
            synergy_result.current.update()
    
    def _role_slot(role: str) -> ft.Container:
        color = ROLE_COLORS.get(role, GOLD)
        champ_img_ref = ft.Ref[ft.Image]()
        input_ref = ft.Ref[ft.TextField]()
        clear_btn_ref = ft.Ref[ft.IconButton]()
        
        def on_champ_change(e):
            val = e.control.value.strip()
            selected_champs[role] = val if val else None
            
            if val:
                try:
                    champ_img_ref.current.src = dd_service.get_champion_square_url(_clean_champ_id(val))
                    champ_img_ref.current.opacity = 1.0
                except:
                    champ_img_ref.current.opacity = 0.2
            else:
                champ_img_ref.current.opacity = 0.2
            
            clear_btn_ref.current.visible = bool(val)
            update_synergy()
            
            if champ_img_ref.current.page:
                champ_img_ref.current.update()
            if clear_btn_ref.current.page:
                clear_btn_ref.current.update()
        
        def clear_slot(e):
            input_ref.current.value = ""
            selected_champs[role] = None
            champ_img_ref.current.opacity = 0.2
            clear_btn_ref.current.visible = False
            update_synergy()
            if champ_img_ref.current.page:
                champ_img_ref.current.update()
            if clear_btn_ref.current.page:
                clear_btn_ref.current.update()
        
        # Get role icon URL
        role_icon_url = dd_service.get_role_icon_url(role)
        
        # Create controls
        champ_img = champ_img_ref.current = ft.Image(
            src="https://ddragon.leagueoflegends.com/cdn/14.24.1/img/champion/Aatrox.png",
            width=60,
            height=60,
            fit=ft.BoxFit.CONTAIN,
            opacity=0.2,
        )
        
        input_field = input_ref.current = ft.Dropdown(
            label=role,
            hint_text=f"Select {role} champion...",
            border_color=BORDER,
            focused_border_color=color,
            text_size=12,
            on_change=on_champ_change,
            options=[
                ft.dropdown.Option(champ)
                for champ in CHAMPION_POOL
            ],
        )
        
        clear_btn = clear_btn_ref.current = ft.IconButton(
            icon=ft.icons.CLOSE,
            icon_size=16,
            icon_color=MUTED,
            visible=False,
            on_click=clear_slot,
            tooltip="Clear slot"
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Image(
                        src=role_icon_url,
                        width=24,
                        height=24,
                        error_content=ft.Text(role[0], size=16, color=color, weight=ft.FontWeight.BOLD)
                    ),
                    ft.Text(role, size=14, color=color, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    clear_btn
                ], spacing=8),
                ft.Container(
                    content=ft.Stack([
                        champ_img,
                        ft.Container(
                            width=60,
                            height=60,
                            border_radius=8,
                            bgcolor=f"{color}20",
                        ),
                    ]),
                    width=60,
                    height=60,
                    border_radius=8,
                ),
                ft.Container(
                    content=input_field,
                    margin=ft.margin.only(top=4),
                ),
            ], spacing=4, tight=True),
            width=140,
            padding=12,
            bgcolor=CARD,
            border_radius=12,
            border=ft.Border.all(1, BORDER),
        )
    
    def reset_draft(e):
        for role in ROLES:
            selected_champs[role] = None
        update_synergy()
        # Reset all inputs
        for control in page.controls:
            if hasattr(control, 'content') and hasattr(control.content, 'controls'):
                for child in control.content.controls:
                    if isinstance(child, ft.TextField):
                        child.value = ""
                        if child.page:
                            child.update()
        if synergy_result.current.page:
            synergy_result.current.update()
    
    # Main layout
    content = ft.Column([
        ft.Row([
            ft.Text("Team Builder", size=28, weight=ft.FontWeight.BOLD, color=TEXT),
            ft.Container(expand=True),
            ft.ElevatedButton(
                "Reset Draft",
                icon=ft.Icons.REFRESH,
                style=ft.ButtonStyle(
                    color=TEXT,
                    bgcolor=CARD2,
                    side=ft.BorderSide(1, BORDER),
                ),
                on_click=reset_draft,
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Text(
            "Build the perfect team composition with role-based champion selection and synergy analysis.",
            size=14,
            color=MUTED,
        ),
        ft.Container(height=SPACING),
        ft.Row([
            _role_slot(role) for role in ROLES
        ], spacing=SPACING, alignment=ft.MainAxisAlignment.SPACE_AROUND),
        ft.Container(height=SPACING*2),
        ft.Container(
            content=ft.Container(
                ref=synergy_result,
                content=ft.Text("Select champions to analyze team synergy...", size=14, color=MUTED),
                padding=16,
                bgcolor=CARD,
                border_radius=12,
                border=ft.Border.all(1, BORDER),
            ),
            margin=ft.margin.symmetric(vertical=SPACING),
        ),
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Role Guide", size=16, weight=ft.FontWeight.BOLD, color=TEXT),
                ]),
                ft.Column([
                    ft.Row([
                        ft.Image(
                            src=dd_service.get_role_icon_url(role),
                            width=16,
                            height=16,
                            error_content=ft.Text(role[0], size=12, color=ROLE_COLORS.get(role, GOLD))
                        ),
                        ft.Text(f"{role}: {ROLE_DESCRIPTIONS[role]}", size=12, color=MUTED),
                    ], spacing=8)
                    for role in ROLES
                ], spacing=4),
            ], spacing=8),
            padding=16,
            bgcolor=CARD2,
            border_radius=12,
        ),
    ], spacing=SPACING, scroll=ft.ScrollMode.AUTO)
    
    return ft.Container(
        content=content,
        padding=SPACING*2,
        bgcolor=BG,
        expand=True,
    )
