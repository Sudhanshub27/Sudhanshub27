"""Isometric / S-curve contribution chart + streak widget, appended below the main card.

build_card.py reserves the canvas space for this widget using panel_height().
today.py calls render_widget() each run to fill that reserved space with the current data.
"""
from xml.sax.saxutils import escape
import math

MARGIN = 15                 # matches build_card.py's IMG_X, so both sections line up
INSET = 20                  # padding between the widget's edge and its content
ASPECT = 0.35               # proportioned panel height for the S-curve path
N_ASSUMED_WEEKS = 53        # GitHub's calendar is never wider than this
TILE_RATIO = 0.46           # tile_h / tile_w
MAX_H_RATIO = 2.6
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"

WIDGET_THEMES = {
    'card_dark.svg': dict(
        is_dark=True,
        fg='#F5E6D3', label='#C9A896', val='#E8CBB0', accent='#C85A3D', border='#30363D', bg='#0D1117',
        empty='#21262D', low='#F5D6B8', high='#7A2E1F', trunk='#5C524E', path='#21262D',
        ramp=['#F5D6B8', '#E8946B', '#C85A3D', '#7A2E1F']),
    'card_light.svg': dict(
        is_dark=False,
        fg='#4A3040', label='#8C6D58', val='#A85A3D', accent='#C85A3D', border='#D8C2D3', bg='#FAF5F0',
        empty='#C4B0C2', low='#F5D6B8', high='#7A2E1F', trunk='#6B5963', path='#F0E5EF',
        ramp=['#F5D6B8', '#E8946B', '#C85A3D', '#7A2E1F']),
}


def lerp_color(c1, c2, t):
    c1, c2 = c1.lstrip('#'), c2.lstrip('#')
    r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
    r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)
    r, g, b = (round(a + (b - a) * t) for a, b in ((r1, r2), (g1, g2), (b1, b2)))
    return f'#{r:02x}{g:02x}{b:02x}'


def panel_width(card_width):
    return card_width - 2 * MARGIN


def tile_size(card_width):
    chart_w_target = panel_width(card_width) - 2 * INSET
    tile_w = chart_w_target / ((N_ASSUMED_WEEKS + 7) / 2)
    return tile_w, tile_w * TILE_RATIO


def panel_height(card_width):
    """Recomputed for S-curve path + bottom-left mini-tree streaks element."""
    return round(panel_width(card_width) * ASPECT)


def shade(hex_color, factor):
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r, g, b = (max(0, min(255, int(c * factor))) for c in (r, g, b))
    return f'#{r:02x}{g:02x}{b:02x}'


def render_lantern(px, py, theme):
    """Renders a small glowing Japanese stone lantern (Tōrō) along the mountain path."""
    parts = []
    is_dark = theme.get('is_dark', True)
    glow_color = '#F5D6B8' if is_dark else '#E8946B'
    stone_color = theme.get('trunk', '#5C524E')

    # Soft glowing light aura
    parts.append(f'<circle cx="{px:.1f}" cy="{py - 7:.1f}" r="9" fill="{glow_color}" opacity="{0.30 if is_dark else 0.15}"/>')
    parts.append(f'<circle cx="{px:.1f}" cy="{py - 7:.1f}" r="4" fill="{glow_color}" opacity="{0.75 if is_dark else 0.45}"/>')
    # Post & Base
    parts.append(f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{px:.1f}" y2="{py - 5:.1f}" stroke="{stone_color}" stroke-width="1.4" stroke-linecap="round"/>')
    # Firebox window
    parts.append(f'<rect x="{px - 2.5:.1f}" y="{py - 8.5:.1f}" width="5" height="4" rx="0.5" fill="{stone_color}"/>')
    parts.append(f'<circle cx="{px:.1f}" cy="{py - 6.5:.1f}" r="1.2" fill="{glow_color}"/>')
    # Pagoda roof cap
    parts.append(f'<path d="M {px - 4.5:.1f},{py - 8.5:.1f} L {px:.1f},{py - 11.5:.1f} L {px + 4.5:.1f},{py - 8.5:.1f} Z" fill="{stone_color}"/>')
    return ''.join(parts)


def render_torii(px, py, theme):
    """Renders a vibrant Vermilion Japanese Torii gate framing the mountain path entrance."""
    parts = []
    vermilion = '#D44A32'   # Traditional Vermilion Torii Red
    dark_cap = '#1A1420'    # Dark charcoal for base pads and top roof cap

    # Torii Gate (~24px tall, ~22px wide)
    # Base foundation pads (Koshimaki)
    parts.append(f'<rect x="{px - 7.5:.1f}" y="{py - 2.0:.1f}" width="3" height="2" fill="{dark_cap}"/>')
    parts.append(f'<rect x="{px + 4.5:.1f}" y="{py - 2.0:.1f}" width="3" height="2" fill="{dark_cap}"/>')

    # Two main vertical posts (Hashira) angled slightly inwards
    parts.append(f'<line x1="{px - 6.0:.1f}" y1="{py - 2.0:.1f}" x2="{px - 5.0:.1f}" y2="{py - 20.0:.1f}" stroke="{vermilion}" stroke-width="2.2" stroke-linecap="square"/>')
    parts.append(f'<line x1="{px + 6.0:.1f}" y1="{py - 2.0:.1f}" x2="{px + 5.0:.1f}" y2="{py - 20.0:.1f}" stroke="{vermilion}" stroke-width="2.2" stroke-linecap="square"/>')

    # Lower crossbar (Nuki)
    parts.append(f'<line x1="{px - 9.0:.1f}" y1="{py - 13.0:.1f}" x2="{px + 9.0:.1f}" y2="{py - 13.0:.1f}" stroke="{vermilion}" stroke-width="1.8"/>')

    # Secondary upper bar (Shimaki)
    parts.append(f'<line x1="{px - 8.0:.1f}" y1="{py - 18.0:.1f}" x2="{px + 8.0:.1f}" y2="{py - 18.0:.1f}" stroke="{vermilion}" stroke-width="1.8"/>')

    # Upper main curved lintel (Kasagi) with upturned ends
    kasagi_d = f"M {px - 11.5:.1f},{py - 20.5:.1f} Q {px:.1f},{py - 19.2:.1f} {px + 11.5:.1f},{py - 20.5:.1f}"
    parts.append(f'<path d="{kasagi_d}" stroke="{vermilion}" stroke-width="2.6" stroke-linecap="round" fill="none"/>')

    # Top dark protective roof cap over Kasagi
    cap_d = f"M {px - 12.0:.1f},{py - 21.8:.1f} Q {px:.1f},{py - 20.5:.1f} {px + 12.0:.1f},{py - 21.8:.1f}"
    parts.append(f'<path d="{cap_d}" stroke="{dark_cap}" stroke-width="1.2" stroke-linecap="round" fill="none"/>')

    # Center vertical tablet strut (Gakuzuka / Plaque)
    parts.append(f'<rect x="{px - 1.2:.1f}" y="{py - 18.0:.1f}" width="2.4" height="5.0" fill="{dark_cap}"/>')

    return ''.join(parts)


def render_background_scenery(theme, chart_w, panel_h):
    """Renders distant mountain silhouettes, celestial body (Moon in Dark Mode, Sun in Light Mode), stars/clouds and birds."""
    parts = []
    is_dark = theme.get('is_dark', True)
    low_color = theme.get('low', '#F5D6B8')
    bg_color = theme.get('bg', '#0D1117')

    # Gradient defs for smooth glow without concentric circle rings
    defs = [
        '<defs>',
        '  <radialGradient id="moon_glow" cx="50%" cy="50%" r="50%">',
        '    <stop offset="0%" stop-color="#F5E6D3" stop-opacity="0.35"/>',
        '    <stop offset="45%" stop-color="#F5E6D3" stop-opacity="0.10"/>',
        '    <stop offset="100%" stop-color="#F5E6D3" stop-opacity="0"/>',
        '  </radialGradient>',
        '  <radialGradient id="sun_glow" cx="50%" cy="50%" r="50%">',
        '    <stop offset="0%" stop-color="#F5D6B8" stop-opacity="0.55"/>',
        '    <stop offset="45%" stop-color="#E8946B" stop-opacity="0.20"/>',
        '    <stop offset="100%" stop-color="#E8946B" stop-opacity="0"/>',
        '  </radialGradient>',
        '  <radialGradient id="firefly_glow" cx="50%" cy="50%" r="50%">',
        f'    <stop offset="0%" stop-color="{low_color}" stop-opacity="0.60"/>',
        f'    <stop offset="100%" stop-color="{low_color}" stop-opacity="0"/>',
        '  </radialGradient>',
        '  <linearGradient id="ground_fog" x1="0%" y1="0%" x2="0%" y2="100%">',
        f'    <stop offset="0%" stop-color="{bg_color}" stop-opacity="0"/>',
        f'    <stop offset="100%" stop-color="{bg_color}" stop-opacity="0.40"/>',
        '  </linearGradient>',
        '</defs>'
    ]
    parts.append(''.join(defs))

    # 1. Distant Mountain Range Silhouettes
    if is_dark:
        far_mtn = '#131822'
        near_mtn = '#181E2A'
        celestial_color = '#F5E6D3'
    else:
        far_mtn = '#EFE4DA'
        near_mtn = '#E6D9CE'
        celestial_color = '#E8946B'

    # Far mountain range
    d_far = f"M 0,{panel_h*0.70:.1f} Q {chart_w*0.18:.1f},{panel_h*0.30:.1f} {chart_w*0.38:.1f},{panel_h*0.52:.1f} T {chart_w*0.72:.1f},{panel_h*0.35:.1f} T {chart_w:.1f},{panel_h*0.48:.1f} L {chart_w:.1f},{panel_h:.1f} L 0,{panel_h:.1f} Z"
    parts.append(f'<path d="{d_far}" fill="{far_mtn}" opacity="0.60"/>')

    # Near mountain range
    d_near = f"M 0,{panel_h*0.80:.1f} Q {chart_w*0.28:.1f},{panel_h*0.48:.1f} {chart_w*0.52:.1f},{panel_h*0.62:.1f} T {chart_w*0.82:.1f},{panel_h*0.46:.1f} T {chart_w:.1f},{panel_h*0.58:.1f} L {chart_w:.1f},{panel_h:.1f} L 0,{panel_h:.1f} Z"
    parts.append(f'<path d="{d_near}" fill="{near_mtn}" opacity="0.45"/>')

    # 2. Celestial Object (Moon in Dark Mode, Sun in Light Mode)
    if is_dark:
        mx, my = chart_w * 0.86, panel_h * 0.22
        # Smooth continuous radial glow (No target rings!)
        parts.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="45" fill="url(#moon_glow)"/>')

        # Pure SVG Crescent Moon path
        moon_d = (
            f"M {mx:.1f},{my-15.0:.1f} "
            f"A 15 15 0 1 0 {mx+11.0:.1f},{my+10.0:.1f} "
            f"A 13 13 0 1 1 {mx:.1f},{my-15.0:.1f} Z"
        )
        parts.append(f'<path d="{moon_d}" fill="{celestial_color}" opacity="0.95"/>')

        # Subtle craters on crescent
        parts.append(f'<circle cx="{mx-6.0:.1f}" cy="{my+2.0:.1f}" r="1.5" fill="#C9A896" opacity="0.35"/>')
        parts.append(f'<circle cx="{mx-3.0:.1f}" cy="{my-5.0:.1f}" r="1.2" fill="#C9A896" opacity="0.30"/>')

        # Stars in night sky
        stars = [
            (0.06, 0.12, 1.2, 0.75), (0.16, 0.20, 0.9, 0.50), (0.26, 0.08, 1.5, 0.85),
            (0.36, 0.22, 1.0, 0.60), (0.44, 0.10, 1.4, 0.75), (0.54, 0.18, 0.8, 0.45),
            (0.64, 0.06, 1.3, 0.80), (0.74, 0.16, 1.1, 0.65), (0.92, 0.10, 1.4, 0.80),
            (0.96, 0.26, 0.9, 0.50), (0.10, 0.32, 0.8, 0.40), (0.48, 0.28, 1.0, 0.55)
        ]
        for sx_r, sy_r, sr, sop in stars:
            sx, sy = chart_w * sx_r, panel_h * sy_r
            parts.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{sr}" fill="{celestial_color}" opacity="{sop}"/>')

        # 4-point sparkle stars
        sparkles = [(0.26, 0.08, 6), (0.64, 0.06, 7), (0.44, 0.10, 5)]
        for spx_r, spy_r, sp_sz in sparkles:
            spx, spy = chart_w * spx_r, panel_h * spy_r
            s_d = f"M {spx:.1f},{spy-sp_sz:.1f} Q {spx:.1f},{spy:.1f} {spx+sp_sz:.1f},{spy:.1f} Q {spx:.1f},{spy:.1f} {spx:.1f},{spy+sp_sz:.1f} Q {spx:.1f},{spy:.1f} {spx-sp_sz:.1f},{spy:.1f} Q {spx:.1f},{spy:.1f} {spx:.1f},{spy-sp_sz:.1f}"
            parts.append(f'<path d="{s_d}" fill="{celestial_color}" opacity="0.85"/>')

        # Firefly dots scattered in lower-mid area near tree line
        fireflies = [
            (0.12, 0.62, 1.1, "2.8s", "0.2s"),
            (0.24, 0.75, 0.9, "3.4s", "1.1s"),
            (0.38, 0.58, 1.3, "2.3s", "0.6s"),
            (0.52, 0.70, 1.0, "3.1s", "1.8s"),
            (0.67, 0.61, 1.4, "2.6s", "0.4s"),
            (0.79, 0.78, 0.8, "3.8s", "1.3s"),
            (0.88, 0.65, 1.2, "2.9s", "2.1s")
        ]
        for fx_r, fy_r, fr, dur, begin in fireflies:
            fx, fy = chart_w * fx_r, panel_h * fy_r
            parts.append(
                f'<g>'
                f'<animate attributeName="opacity" values="0.2;0.9;0.2" dur="{dur}" begin="{begin}" repeatCount="indefinite"/>'
                f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="4" fill="url(#firefly_glow)"/>'
                f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="{fr}" fill="{low_color}"/>'
                f'</g>'
            )

        # Rare shooting star / meteor streak in top-right quadrant
        ss_x, ss_y = chart_w * 0.78, panel_h * 0.14
        parts.append(
            f'<g transform="translate({ss_x:.1f},{ss_y:.1f})" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;0.8;0" keyTimes="0;0.65;0.75;1" dur="12s" begin="2s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0 0; 0 0; -45 26; -60 35" keyTimes="0;0.65;0.75;1" dur="12s" begin="2s" repeatCount="indefinite" additive="sum"/>'
            f'<line x1="0" y1="0" x2="-26" y2="15" stroke="{celestial_color}" stroke-width="1" stroke-linecap="round"/>'
            f'</g>'
        )

        # Sharp black owl silhouette perched on near mountain ridge point
        ox, oy = chart_w * 0.82, panel_h * 0.46
        parts.append(f'<circle cx="{ox:.1f}" cy="{oy - 2.8:.1f}" r="2.8" fill="#070A10" opacity="0.95"/>')
        parts.append(f'<circle cx="{ox:.1f}" cy="{oy - 6.2:.1f}" r="2.0" fill="#070A10" opacity="0.95"/>')
        ear_l = f"M {ox - 1.8:.1f},{oy - 7.0:.1f} L {ox - 0.7:.1f},{oy - 9.0:.1f} L {ox - 0.2:.1f},{oy - 7.0:.1f} Z"
        ear_r = f"M {ox + 1.8:.1f},{oy - 7.0:.1f} L {ox + 0.7:.1f},{oy - 9.0:.1f} L {ox + 0.2:.1f},{oy - 7.0:.1f} Z"
        parts.append(f'<path d="{ear_l}" fill="#070A10" opacity="0.95"/>')
        parts.append(f'<path d="{ear_r}" fill="#070A10" opacity="0.95"/>')
        parts.append(f'<circle cx="{ox - 0.8:.1f}" cy="{oy - 6.3:.1f}" r="0.6" fill="#FFDF9E" opacity="0.90"/>')
        parts.append(f'<circle cx="{ox + 0.8:.1f}" cy="{oy - 6.3:.1f}" r="0.6" fill="#FFDF9E" opacity="0.90"/>')

    else:
        sx, sy = chart_w * 0.86, panel_h * 0.24
        # Smooth continuous radial glow (No target rings!)
        parts.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="48" fill="url(#sun_glow)"/>')

        # Sun Disk
        parts.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="14" fill="#C85A3D" opacity="0.85"/>')
        parts.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="11" fill="#F5D6B8" opacity="0.95"/>')

        # Delicate Sunburst Rays (8 radiating rays)
        for angle in (0, 45, 90, 135, 180, 225, 270, 315):
            rad = math.radians(angle)
            x1 = sx + 17 * math.cos(rad)
            y1 = sy + 17 * math.sin(rad)
            x2 = sx + 25 * math.cos(rad)
            y2 = sy + 25 * math.sin(rad)
            parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#E8946B" stroke-width="1.2" stroke-linecap="round" opacity="0.55"/>')

        # Morning clouds
        clouds = [
            (chart_w * 0.12, panel_h * 0.18),
            (chart_w * 0.42, panel_h * 0.12),
            (chart_w * 0.68, panel_h * 0.28)
        ]
        for cx_c, cy_c in clouds:
            c_d = f"M {cx_c:.1f},{cy_c:.1f} a 8,8 0 0,1 12,-4 a 12,12 0 0,1 18,2 a 8,8 0 0,1 10,8 L {cx_c-4:.1f},{cy_c+6:.1f} Z"
            parts.append(f'<path d="{c_d}" fill="#C4B0C2" opacity="0.35"/>')

        # Birds flying in sky
        birds = [(0.22, 0.14), (0.26, 0.11), (0.58, 0.20)]
        for bx_r, by_r in birds:
            bx, by = chart_w * bx_r, panel_h * by_r
            b_d = f"M {bx:.1f},{by:.1f} Q {bx+4:.1f},{by-4:.1f} {bx+8:.1f},{by:.1f} Q {bx+12:.1f},{by-4:.1f} {bx+16:.1f},{by:.1f}"
            parts.append(f'<path d="{b_d}" stroke="#8C6D58" stroke-width="1.2" stroke-linecap="round" fill="none" opacity="0.60"/>')

        # Sharp black owl silhouette perched on near mountain ridge point
        ox, oy = chart_w * 0.82, panel_h * 0.46
        parts.append(f'<circle cx="{ox:.1f}" cy="{oy - 2.8:.1f}" r="2.8" fill="#1C1622" opacity="0.95"/>')
        parts.append(f'<circle cx="{ox:.1f}" cy="{oy - 6.2:.1f}" r="2.0" fill="#1C1622" opacity="0.95"/>')
        ear_l = f"M {ox - 1.8:.1f},{oy - 7.0:.1f} L {ox - 0.7:.1f},{oy - 9.0:.1f} L {ox - 0.2:.1f},{oy - 7.0:.1f} Z"
        ear_r = f"M {ox + 1.8:.1f},{oy - 7.0:.1f} L {ox + 0.7:.1f},{oy - 9.0:.1f} L {ox + 0.2:.1f},{oy - 7.0:.1f} Z"
        parts.append(f'<path d="{ear_l}" fill="#1C1622" opacity="0.95"/>')
        parts.append(f'<path d="{ear_r}" fill="#1C1622" opacity="0.95"/>')
        parts.append(f'<circle cx="{ox - 0.8:.1f}" cy="{oy - 6.3:.1f}" r="0.6" fill="#E8946B" opacity="0.90"/>')
        parts.append(f'<circle cx="{ox + 0.8:.1f}" cy="{oy - 6.3:.1f}" r="0.6" fill="#E8946B" opacity="0.90"/>')

    # Soft horizontal ground fog band
    parts.append(f'<rect x="0" y="{panel_h*0.75:.1f}" width="{chart_w:.1f}" height="{panel_h*0.25:.1f}" fill="url(#ground_fog)"/>')

    return ''.join(parts)


def render_falling_petals(theme, chart_w, panel_h):
    """Renders small falling sakura petals floating across the top half of the panel."""
    ramp = theme.get('ramp', ['#F5D6B8', '#E8946B', '#C85A3D', '#7A2E1F'])
    is_dark = theme.get('is_dark', True)
    petal_fill = ramp[0] if is_dark else ramp[1]

    # 6 small petals scattered across top half of panel
    # (x_ratio, y_ratio, dx, dy, rot_from, rot_to, dur, begin, opacity)
    petals = [
        (0.14, 0.12, 18, 22, -15, 35, "7.5s", "0.0s", 0.65),
        (0.28, 0.25, 22, 20, 10, -40, "9.0s", "1.5s", 0.75),
        (0.45, 0.10, 15, 24, -20, 25, "6.8s", "0.8s", 0.55),
        (0.62, 0.32, 20, 18, 0, 45, "8.2s", "2.2s", 0.70),
        (0.78, 0.16, 17, 25, -30, 15, "7.0s", "1.0s", 0.60),
        (0.90, 0.28, 24, 21, 15, -35, "8.6s", "2.8s", 0.80)
    ]

    parts = []
    for px_r, py_r, dx, dy, r1, r2, dur, begin, op in petals:
        px, py = chart_w * px_r, panel_h * py_r
        parts.append(
            f'<g transform="translate({px:.1f},{py:.1f})">'
            f'<animateTransform attributeName="transform" type="translate" values="0 0; {dx} {dy}; 0 0" dur="{dur}" begin="{begin}" repeatCount="indefinite" additive="sum"/>'
            f'<animateTransform attributeName="transform" type="rotate" values="{r1}; {r2}; {r1}" dur="{dur}" begin="{begin}" repeatCount="indefinite" additive="sum"/>'
            f'<ellipse cx="0" cy="0" rx="1.5" ry="1.0" fill="{petal_fill}" opacity="{op:.2f}"/>'
            f'</g>'
        )

    return ''.join(parts)


def render_chart(weeks, theme, tile_w, tile_h):
    """Renders the calendar as a Sakura forest along an S-curve switchback path using 4 discrete growth tiers."""
    all_days = [d for w in weeks for d in w['contributionDays']]
    N = len(all_days)
    if N == 0:
        return '<g></g>', 0, 0

    ramp = theme.get('ramp', ['#F5D6B8', '#E8946B', '#C85A3D', '#7A2E1F'])
    trunk_color = theme.get('trunk', '#5A4A52')
    path_color = theme.get('path', '#271F30')

    # Path geometry parameters
    chart_w = tile_w * 26.0
    amplitude = 42.0
    frequency = 2 * math.pi * 2.5
    center_y = 100.0

    # 1. Calculate path points and roadside positions
    path_line_pts = []
    day_nodes = []
    for i, d in enumerate(all_days):
        t = i / max(1, N - 1)
        x_base = t * chart_w
        y_base = center_y + amplitude * math.sin(t * frequency)
        path_line_pts.append((x_base, y_base))

        # Perpendicular normal vector for roadside jitter
        dx = chart_w / max(1, N - 1)
        dy = amplitude * frequency * math.cos(t * frequency) / max(1, N - 1)
        len_v = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / len_v, dx / len_v

        # Deterministic roadside jitter
        jitter = (math.sin(i * 12.9898 + 78.233) * 0.5 + math.cos(i * 45.123) * 0.5) * 14.0
        pos_x = x_base + nx * jitter
        pos_y = y_base + ny * jitter
        day_nodes.append({'index': i, 'day': d, 'pos_x': pos_x, 'pos_y': pos_y, 'y_base': y_base})

    parts = []
    minx = miny = float('inf')
    maxx = maxy = float('-inf')

    # 2. Draw the winding mountain road line
    if path_line_pts:
        d_str = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in path_line_pts)
        parts.append(f'<path d="{d_str}" stroke="{path_color}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" fill="none" opacity="0.65"/>')
        parts.append(f'<path d="{d_str}" stroke="{theme["border"]}" stroke-width="1.2" stroke-dasharray="3,4" fill="none" opacity="0.35"/>')
        for px, py in path_line_pts:
            minx, maxx = min(minx, px - 6), max(maxx, px + 6)
            miny, maxy = min(miny, py - 6), max(maxy, py + 6)

        # Vermilion Torii Gate framing the entrance of the mountain path
        if len(path_line_pts) > 3:
            t_x, t_y = path_line_pts[3]
            parts.append(render_torii(t_x + 2.0, t_y + 4.0, theme))

    # 3. Sort trees back-to-front by vertical position (pos_y) for proper occlusion
    day_nodes.sort(key=lambda item: item['pos_y'])

    # 4. Render day nodes using 4 discrete growth tiers based on commit count
    for item in day_nodes:
        i = item['index']
        d = item['day']
        px, py = item['pos_x'], item['pos_y']
        c = d['contributionCount']

        # Japanese stone lanterns (Tōrō) along roadside
        if i in (18, 72, 135, 205, 270, 330):
            parts.append(render_lantern(px + 9.0, py + 2.0, theme))

        if c == 0:
            # Empty day: small faint dot on path
            parts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="1.5" fill="{theme["empty"]}" opacity="0.75"/>')
            minx, maxx = min(minx, px - 2), max(maxx, px + 2)
            miny, maxy = min(miny, py - 2), max(maxy, py + 2)
        elif c in (1, 2):
            # Tier 1: Sapling (1-2 commits)
            # Thin single trunk (width 1.0, no branches), 2-3 small light circles (#F5D6B8)
            trunk_h = 10.0
            tx, ty = px, py - trunk_h
            parts.append(f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{tx:.1f}" y2="{ty:.1f}" stroke="{trunk_color}" stroke-width="1.0" stroke-linecap="round"/>')

            cx, cy = tx, ty - 2.5
            color_1 = ramp[0]  # #F5D6B8
            parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.8" fill="{color_1}" opacity="0.90"/>')
            parts.append(f'<circle cx="{cx - 2.2:.1f}" cy="{cy + 1.0:.1f}" r="3.0" fill="{color_1}" opacity="0.85"/>')
            parts.append(f'<circle cx="{cx + 2.2:.1f}" cy="{cy - 0.8:.1f}" r="2.8" fill="{color_1}" opacity="0.85"/>')

            minx, maxx = min(minx, cx - 6), max(maxx, cx + 6)
            miny, maxy = min(miny, cy - 6), max(maxy, py)
        elif c in (3, 4, 5):
            # Tier 2: Young tree (3-5 commits)
            # Trunk width 1.4, 1-2 branch lines, canopy 4-5 circles in looser cluster (#E8946B)
            trunk_h = 16.0
            tx, ty = px, py - trunk_h
            parts.append(f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{tx:.1f}" y2="{ty:.1f}" stroke="{trunk_color}" stroke-width="1.4" stroke-linecap="round"/>')

            b1_y = py - trunk_h * 0.50
            parts.append(f'<line x1="{px:.1f}" y1="{b1_y:.1f}" x2="{px - 4.2:.1f}" y2="{b1_y - 2.8:.1f}" stroke="{trunk_color}" stroke-width="1.0" stroke-linecap="round"/>')
            b2_y = py - trunk_h * 0.70
            parts.append(f'<line x1="{px:.1f}" y1="{b2_y:.1f}" x2="{px + 3.8:.1f}" y2="{b2_y - 2.2:.1f}" stroke="{trunk_color}" stroke-width="0.9" stroke-linecap="round"/>')

            cx, cy = tx, ty - 3.2
            c_primary = ramp[1]     # #E8946B
            c_highlight = ramp[0]   # #F5D6B8
            parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="5.2" fill="{c_primary}" opacity="0.92"/>')
            parts.append(f'<circle cx="{cx - 3.2:.1f}" cy="{cy - 1.2:.1f}" r="4.0" fill="{c_highlight}" opacity="0.90"/>')
            parts.append(f'<circle cx="{cx + 3.5:.1f}" cy="{cy - 0.8:.1f}" r="3.8" fill="{c_primary}" opacity="0.90"/>')
            parts.append(f'<circle cx="{cx - 1.8:.1f}" cy="{cy + 2.2:.1f}" r="3.5" fill="{c_primary}" opacity="0.88"/>')
            parts.append(f'<circle cx="{cx + 2.0:.1f}" cy="{cy + 1.8:.1f}" r="3.2" fill="{c_highlight}" opacity="0.88"/>')

            minx, maxx = min(minx, cx - 8), max(maxx, cx + 8)
            miny, maxy = min(miny, cy - 8), max(maxy, py)
        elif c in (6, 7, 8):
            # Tier 3: Mature tree (6-8 commits)
            # Trunk width 2.0, 2-3 branches, canopy 7-9 circles in fuller dense ring + core (#C85A3D)
            trunk_h = 22.0
            tx, ty = px, py - trunk_h
            parts.append(f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{tx:.1f}" y2="{ty:.1f}" stroke="{trunk_color}" stroke-width="2.0" stroke-linecap="round"/>')

            b1_y = py - trunk_h * 0.45
            parts.append(f'<line x1="{px:.1f}" y1="{b1_y:.1f}" x2="{px - 6.2:.1f}" y2="{b1_y - 3.8:.1f}" stroke="{trunk_color}" stroke-width="1.3" stroke-linecap="round"/>')
            b2_y = py - trunk_h * 0.65
            parts.append(f'<line x1="{px:.1f}" y1="{b2_y:.1f}" x2="{px + 5.8:.1f}" y2="{b2_y - 3.2:.1f}" stroke="{trunk_color}" stroke-width="1.2" stroke-linecap="round"/>')
            b3_y = py - trunk_h * 0.82
            parts.append(f'<line x1="{px:.1f}" y1="{b3_y:.1f}" x2="{px - 4.8:.1f}" y2="{b3_y - 2.4:.1f}" stroke="{trunk_color}" stroke-width="1.0" stroke-linecap="round"/>')

            cx, cy = tx, ty - 4.0
            R = 8.2
            c_primary = ramp[2]   # #C85A3D
            c_mid = ramp[1]       # #E8946B
            c_deep = ramp[3]      # #7A2E1F

            n_outer = 8
            for k in range(n_outer):
                angle = (2 * math.pi * k / n_outer) + math.sin(k * 3.7 + i) * 0.3
                ox = cx + R * 0.58 * math.cos(angle)
                oy = cy + R * 0.58 * math.sin(angle)
                orad = R * (0.38 + math.cos(k * 2.1 + i) * 0.08)
                color_k = c_primary if oy >= cy else c_mid
                parts.append(f'<circle cx="{ox:.1f}" cy="{oy:.1f}" r="{orad:.1f}" fill="{color_k}" opacity="0.90"/>')

            parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R*0.40:.1f}" fill="{c_deep}" opacity="0.95"/>')
            parts.append(f'<circle cx="{cx - 1.8:.1f}" cy="{cy - 1.2:.1f}" r="{R*0.34:.1f}" fill="{c_primary}" opacity="0.95"/>')
            parts.append(f'<circle cx="{cx + 1.8:.1f}" cy="{cy + 0.8:.1f}" r="{R*0.32:.1f}" fill="{c_mid}" opacity="0.95"/>')

            minx, maxx = min(minx, cx - R * 1.3), max(maxx, cx + R * 1.3)
            miny, maxy = min(miny, cy - R * 1.3), max(maxy, py)
        else:
            # Tier 4: Ancient tree (9+ commits)
            # Thickest trunk (width 2.8), gnarled with slight bend/curve, 3-4 branches, canopy 10-12 circles (#7A2E1F)
            # ONLY tier that gets floating petal dots above it
            trunk_h = 27.0
            bend_dir = 1.0 if (i % 2 == 0) else -1.0
            bend_amount = 3.2 * bend_dir
            mid_x = px + bend_amount
            mid_y = py - trunk_h * 0.5
            tx = px + bend_amount * 0.6
            ty = py - trunk_h

            parts.append(f'<path d="M {px:.1f},{py:.1f} Q {mid_x:.1f},{mid_y:.1f} {tx:.1f},{ty:.1f}" stroke="{trunk_color}" stroke-width="2.8" stroke-linecap="round" fill="none"/>')

            b1_x, b1_y = px + bend_amount * 0.4, py - trunk_h * 0.40
            parts.append(f'<line x1="{b1_x:.1f}" y1="{b1_y:.1f}" x2="{b1_x - 7.5*bend_dir:.1f}" y2="{b1_y - 4.5:.1f}" stroke="{trunk_color}" stroke-width="1.6" stroke-linecap="round"/>')
            b2_x, b2_y = px + bend_amount * 0.6, py - trunk_h * 0.62
            parts.append(f'<line x1="{b2_x:.1f}" y1="{b2_y:.1f}" x2="{b2_x + 7.0*bend_dir:.1f}" y2="{b2_y - 4.0:.1f}" stroke="{trunk_color}" stroke-width="1.4" stroke-linecap="round"/>')
            b3_x, b3_y = px + bend_amount * 0.8, py - trunk_h * 0.80
            parts.append(f'<line x1="{b3_x:.1f}" y1="{b3_y:.1f}" x2="{b3_x - 6.0*bend_dir:.1f}" y2="{b3_y - 3.2:.1f}" stroke="{trunk_color}" stroke-width="1.2" stroke-linecap="round"/>')

            cx, cy = tx, ty - 4.8
            R = 11.5
            c_deep = ramp[3]    # #7A2E1F
            c_mid = ramp[2]     # #C85A3D
            c_light = ramp[1]   # #E8946B

            n_outer = 10
            for k in range(n_outer):
                angle = (2 * math.pi * k / n_outer) + math.sin(k * 3.1 + i) * 0.3
                ox = cx + R * 0.60 * math.cos(angle)
                oy = cy + R * 0.60 * math.sin(angle)
                orad = R * (0.38 + math.cos(k * 2.3 + i) * 0.09)
                color_k = c_deep if oy >= cy else c_mid
                if k % 4 == 0:
                    color_k = c_light
                parts.append(f'<circle cx="{ox:.1f}" cy="{oy:.1f}" r="{orad:.1f}" fill="{color_k}" opacity="0.92"/>')

            parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R*0.42:.1f}" fill="{c_deep}" opacity="0.95"/>')
            parts.append(f'<circle cx="{cx - 2.8:.1f}" cy="{cy - 1.8:.1f}" r="{R*0.35:.1f}" fill="{c_mid}" opacity="0.95"/>')
            parts.append(f'<circle cx="{cx + 2.8:.1f}" cy="{cy - 0.8:.1f}" r="{R*0.34:.1f}" fill="{c_deep}" opacity="0.95"/>')
            parts.append(f'<circle cx="{cx:.1f}" cy="{cy + 2.2:.1f}" r="{R*0.30:.1f}" fill="{c_mid}" opacity="0.95"/>')

            # Floating petal dots (ONLY tier 4 gets floating petals)
            p_color = ramp[0]  # #F5D6B8
            p1_x, p1_y = cx + R * 0.75, cy - R * 1.12
            p2_x, p2_y = cx - R * 0.85, cy - R * 0.92
            p3_x, p3_y = cx + R * 1.10, cy - R * 0.42
            parts.append(f'<circle cx="{p1_x:.1f}" cy="{p1_y:.1f}" r="1.3" fill="{p_color}" opacity="0.88"/>')
            parts.append(f'<circle cx="{p2_x:.1f}" cy="{p2_y:.1f}" r="1.0" fill="{p_color}" opacity="0.78"/>')
            parts.append(f'<circle cx="{p3_x:.1f}" cy="{p3_y:.1f}" r="1.1" fill="{p_color}" opacity="0.68"/>')

            minx, maxx = min(minx, cx - R * 1.4), max(maxx, cx + R * 1.4)
            miny, maxy = min(miny, cy - R * 1.4), max(maxy, py)

    frag = f'<g transform="translate({-minx:.1f},{-miny:.1f})">' + ''.join(parts) + '</g>'
    return frag, maxx - minx, maxy - miny


def compute_stats(days):
    """Total, best day, and longest/current streaks from a chronological list of days."""
    total = sum(d['contributionCount'] for d in days)
    best = max(days, key=lambda d: d['contributionCount'])

    longest_len, longest_start, longest_end = 0, None, None
    run_start, run = None, 0
    for d in days:
        if d['contributionCount'] > 0:
            if run == 0:
                run_start = d['date']
            run += 1
            if run > longest_len:
                longest_len, longest_start, longest_end = run, run_start, d['date']
        else:
            run = 0

    idx = len(days) - 1
    if days[idx]['contributionCount'] == 0:
        idx -= 1
    current_len, current_start, current_end = 0, None, days[idx]['date'] if idx >= 0 else None
    while idx >= 0 and days[idx]['contributionCount'] > 0:
        current_start = days[idx]['date']
        current_len += 1
        idx -= 1

    return dict(total=total, best_count=best['contributionCount'], best_date=best['date'],
                longest_len=longest_len, longest_start=longest_start, longest_end=longest_end,
                current_len=current_len, current_start=current_start, current_end=current_end,
                range_start=days[0]['date'], range_end=days[-1]['date'])


def month_day(iso_date):
    import datetime
    return datetime.date.fromisoformat(iso_date).strftime('%b %-d')


def render_mini_tree(cx, cy, color, theme, is_empty=False):
    """Renders a small sakura tree icon for streak displays using overlapping canopy circles."""
    parts = []
    trunk_color = theme.get('trunk', '#5A4A52')
    if is_empty:
        parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.0" fill="{theme["empty"]}"/>')
        return ''.join(parts)

    trunk_h = 18.0
    tx, ty = cx, cy - trunk_h

    # Thin trunk line
    parts.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{tx:.1f}" y2="{ty:.1f}" stroke="{trunk_color}" stroke-width="1.6" stroke-linecap="round"/>')
    # 2 short branch lines
    parts.append(f'<line x1="{cx:.1f}" y1="{cy - trunk_h*0.45:.1f}" x2="{cx - 5.0:.1f}" y2="{cy - trunk_h*0.65:.1f}" stroke="{trunk_color}" stroke-width="1.1" stroke-linecap="round"/>')
    parts.append(f'<line x1="{cx:.1f}" y1="{cy - trunk_h*0.65:.1f}" x2="{cx + 4.5:.1f}" y2="{cy - trunk_h*0.80:.1f}" stroke="{trunk_color}" stroke-width="1.1" stroke-linecap="round"/>')

    # Fluffy canopy made of small overlapping circles
    ramp = theme.get('ramp', ['#F5D6B8', '#E8946B', '#C85A3D', '#7A2E1F'])
    try:
        c_idx = ramp.index(color)
    except ValueError:
        c_idx = 3
    highlight_color = ramp[max(0, c_idx - 1)]

    # 7 outer ring circles + 3 core circles
    canopy_cx, canopy_cy = tx, ty - 2.0
    R = 9.0
    n_outer = 7
    for k in range(n_outer):
        angle = 2 * math.pi * k / n_outer
        ox = canopy_cx + R * 0.55 * math.cos(angle)
        oy = canopy_cy + R * 0.55 * math.sin(angle)
        orad = R * (0.40 if k % 2 == 0 else 0.33)
        c_fill = color if oy >= canopy_cy else highlight_color
        parts.append(f'<circle cx="{ox:.1f}" cy="{oy:.1f}" r="{orad:.1f}" fill="{c_fill}" opacity="0.92"/>')

    # 3 core volume circles
    parts.append(f'<circle cx="{canopy_cx - 1.5:.1f}" cy="{canopy_cy - 1.0:.1f}" r="3.4" fill="{color}" opacity="0.95"/>')
    parts.append(f'<circle cx="{canopy_cx + 1.5:.1f}" cy="{canopy_cy - 1.0:.1f}" r="3.2" fill="{highlight_color}" opacity="0.95"/>')
    parts.append(f'<circle cx="{canopy_cx:.1f}" cy="{canopy_cy + 1.2:.1f}" r="3.0" fill="{color}" opacity="0.95"/>')

    return ''.join(parts)


def render_streaks(x, y, stats, theme):
    """Renders the Streaks display as two mini sakura trees side by side with stats beneath."""
    ramp = theme.get('ramp', ['#F5D6B8', '#E8946B', '#C85A3D', '#7A2E1F'])
    parts = []

    longest_len = stats['longest_len']
    longest_color = ramp[3]  # Deepest color for peak achievement
    longest_range = f"{month_day(stats['longest_start'])} → {month_day(stats['longest_end'])}" if stats['longest_start'] else '—'

    current_len = stats['current_len']
    if current_len <= 0:
        current_color = theme['empty']
        is_curr_empty = True
    else:
        is_curr_empty = False
        ratio = min(1.0, current_len / max(1, longest_len))
        tier = min(3, int(ratio * 3.99))
        current_color = ramp[tier]
    current_range = f"{month_day(stats['current_start'])} → {month_day(stats['current_end'])}" if stats['current_start'] else '—'

    # Column 1: Longest streak
    col1_x = x
    tree1_cx = col1_x + 14
    tree1_cy = y + 26
    parts.append(render_mini_tree(tree1_cx, tree1_cy, longest_color, theme))

    t1_x = col1_x + 36
    parts.append(f'<text x="{t1_x:.1f}" y="{y+16:.1f}" font-size="18" font-weight="700" fill="{theme["accent"]}">{longest_len} days</text>')
    parts.append(f'<text x="{t1_x:.1f}" y="{y+32:.1f}" font-size="11" font-weight="600" fill="{theme["label"]}">Longest streak</text>')
    parts.append(f'<text x="{t1_x:.1f}" y="{y+46:.1f}" font-size="10" fill="{theme["val"]}">{escape(longest_range)}</text>')

    # Column 2: Current streak
    col2_x = x + 185
    tree2_cx = col2_x + 14
    tree2_cy = y + 26
    parts.append(render_mini_tree(tree2_cx, tree2_cy, current_color, theme, is_empty=is_curr_empty))

    t2_x = col2_x + 36
    parts.append(f'<text x="{t2_x:.1f}" y="{y+16:.1f}" font-size="18" font-weight="700" fill="{theme["accent"]}">{current_len} days</text>')
    parts.append(f'<text x="{t2_x:.1f}" y="{y+32:.1f}" font-size="11" font-weight="600" fill="{theme["label"]}">Current streak</text>')
    parts.append(f'<text x="{t2_x:.1f}" y="{y+46:.1f}" font-size="10" fill="{theme["val"]}">{escape(current_range)}</text>')

    return ''.join(parts)


def render_widget(theme, card_width, weeks):
    """Returns the SVG markup for the whole widget, in local coordinates starting at (0,0)."""
    avail_w = panel_width(card_width)
    panel_h = panel_height(card_width)
    tile_w, tile_h = tile_size(card_width)
    chart_frag, cw, ch = render_chart(weeks, theme, tile_w, tile_h)

    days = [d for w in weeks for d in w['contributionDays']]
    stats = compute_stats(days)

    parts = [f'<g font-family="{FONT}">']

    # Background Scenery (Mountain Silhouettes, Crescent Moon / Sun, Stars / Clouds & Birds)
    bg_scenery = render_background_scenery(theme, avail_w, panel_h)
    parts.append(f'<g id="bg_landscape">{bg_scenery}</g>')

    # Falling Sakura Petals (sitting behind trees/chart)
    falling_petals = render_falling_petals(theme, avail_w, panel_h)
    parts.append(f'<g id="falling_petals">{falling_petals}</g>')

    # Vertically center the S-curve chart in the full panel height
    chart_y = max(0.0, (panel_h - ch) / 2.0)
    parts.append(f'<g transform="translate({INSET},{chart_y:.1f})">{chart_frag}</g>')

    # Redesigned Streaks display in bottom-left corner
    streak_y = panel_h - INSET - 48
    parts.append(render_streaks(INSET, streak_y, stats, theme))

    parts.append('</g>')
    return ''.join(parts)
