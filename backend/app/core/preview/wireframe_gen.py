from app.models import ScreenSpec

ZONE_COLORS = {
    "NAV": "#E8EDF2",
    "HERO": "#D4E6F1",
    "FEATURES": "#EAF4FB",
    "FOOTER": "#F0F3F4",
    "FORM": "#FEF9E7",
    "LIST": "#EAF7F1",
    "CTA": "#FDEBD0",
    "STATS": "#E8F8F5",
    "PROFILE": "#F4ECF7",
    "SECTIONS": "#FDFEFE",
    "DANGER": "#FDEDEC",
    "PAYMENT": "#EBF5FB",
    "SUMMARY": "#F0FFF4",
    "PROGRESS": "#FFF3CD",
    "LINKS": "#F8F9FA",
    "DEFAULT": "#F5F5F5",
}


def generate_svg(screen: ScreenSpec, width: int = 375, padding: int = 16) -> str:
    total_height = sum(z.height for z in screen.zones) + padding * 2
    rects = []

    y_cursor = padding
    for zone in screen.zones:
        color = ZONE_COLORS.get(zone.type, ZONE_COLORS["DEFAULT"])
        rect = f'''  <rect x="{padding}" y="{y_cursor}" width="{width - padding * 2}" height="{zone.height}" fill="{color}" stroke="#CBD5E0" stroke-width="1" rx="4"/>
  <text x="{padding + 8}" y="{y_cursor + zone.height // 2 + 5}" font-family="system-ui,sans-serif" font-size="11" fill="#4A5568">{zone.type}: {zone.description[:50]}</text>'''
        rects.append(rect)
        y_cursor += zone.height + 4

    header = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{total_height}" viewBox="0 0 {width} {total_height}">
  <rect width="{width}" height="{total_height}" fill="white"/>
  <text x="{padding}" y="14" font-family="system-ui,sans-serif" font-size="12" font-weight="bold" fill="#2D3748">{screen.name}</text>'''

    return header + "\n" + "\n".join(rects) + "\n</svg>"


def generate_all(screens: list[ScreenSpec]) -> list[ScreenSpec]:
    for screen in screens:
        screen.svg = generate_svg(screen)
    return screens
