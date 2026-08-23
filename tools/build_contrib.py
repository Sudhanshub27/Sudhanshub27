"""Isometric contribution chart + streak widget, appended below the main card.

Mirrors GitHub's own "3D" contribution view: a full-width isometric calendar with two
bordered stat cards overlaid in its empty corners -- Contributions top-right, Streaks
bottom-left -- since the ribbon runs from short bars at the top-left down to tall ones
at the bottom-right, leaving those two corners empty.

build_card.py reserves the canvas space for this widget using the same sizing formulas
as here, assuming a 53-week calendar -- the worst case, so a real 52-week calendar never
overflows it. today.py calls render_widget() each run to fill that reserved space with
the current data.
"""
from xml.sax.saxutils import escape

MARGIN = 15                 # matches build_card.py's IMG_X, so both sections line up
INSET = 20                  # padding between the widget's edge and its content
ASPECT = 9 / 16              # widget is a full 16:9 panel, not a tight fit around the chart
N_ASSUMED_WEEKS = 53        # GitHub's calendar is never wider than this
TILE_RATIO = 0.46           # tile_h / tile_w -- steep enough that bars read as tall, not squat
MAX_H_RATIO = 2.6           # tallest bar's height, as a multiple of tile_w
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"

# Card sizing: computed from content, not fixed -- see stat_card().
BOX_PAD = 18
COL_GAP = 125
COL_CONTENT_W = 90
BOX_ROW_H = 94

# Empty days sit close to the background, and color runs smoothly from low to high
# with contribution count -- the same ratio height uses, so two bars of similar
# height always land on similar color, not just similar count. low/high are GitHub's
# own level-1/level-4 greens, so the gradient stays a true green, not lime.
import math

WIDGET_THEMES = {
    'dark_mode.svg': dict(
        fg='#F5E6D3', label='#C9A896', accent='#C85A3D', border='#4A3040', bg='#17121C',
        empty='#4A3E4F', low='#F5D6B8', high='#7A2E1F', trunk='#5A4A52', path='#2B2032',
        ramp=['#F5D6B8', '#E8946B', '#C85A3D', '#7A2E1F']),
    'light_mode.svg': dict(
        fg='#4A3040', label='#8C6D58', accent='#C85A3D', border='#D8C2D3', bg='#FAF5F0',
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
    """Tile footprint sized so the chart fills the widget width, assuming a 53-week
    calendar. A real (<=53 week) calendar comes out narrower, never wider."""
    chart_w_target = panel_width(card_width) - 2 * INSET
    tile_w = chart_w_target / ((N_ASSUMED_WEEKS + 7) / 2)
    return tile_w, tile_w * TILE_RATIO


def panel_height(card_width):
    """A full 16:9 panel -- generously sized, not a tight fit around the chart -- so
    the widget reads as a spacious section rather than a cramped strip. Never smaller
    than the chart's worst case (53 weeks, tallest bar at the top-left corner), so a
    narrow card whose 16:9 height would be too tight still never clips the chart."""
    tile_w, tile_h = tile_size(card_width)
    max_h = tile_w * MAX_H_RATIO
    footprint_h = tile_h * (N_ASSUMED_WEEKS + 5) / 2 + tile_h
    chart_required = footprint_h + max_h + 2 * INSET
    return max(chart_required, panel_width(card_width) * ASPECT)


def shade(hex_color, factor):
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r, g, b = (max(0, min(255, int(c * factor))) for c in (r, g, b))
    return f'#{r:02x}{g:02x}{b:02x}'


def render_chart(weeks, theme, tile_w, tile_h):
    """Renders the calendar as a Sakura forest along an S-curve switchback path.

    Days are distributed in chronological order along a winding sine-wave path.
    Empty days render as faint gray-purple path dots. Contribution days render as trees
    with thin trunks, branch lines, and multi-layered organic sakura blossom canopies.
    """
    all_days = [d for w in weeks for d in w['contributionDays']]
    N = len(all_days)
    if N == 0:
        return '<g></g>', 0, 0

    max_count = max((d['contributionCount'] for d in all_days), default=1) or 1
    ramp = theme.get('ramp', ['#FFB6C1', '#F472B6', '#E91E63', '#BE185D'])
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

    # 3. Sort trees back-to-front by vertical position (pos_y) for proper occlusion
    day_nodes.sort(key=lambda item: item['pos_y'])

    # 4. Render day nodes (faint path dots or sakura trees)
    min_trunk_h, max_trunk_h = 10.0, 28.0
    min_canopy_r, max_canopy_r = 7.0, 18.0

    for item in day_nodes:
        i = item['index']
        d = item['day']
        px, py = item['pos_x'], item['pos_y']
        c = d['contributionCount']

        if c == 0:
            # Empty day: small faint dot on path
            parts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="1.5" fill="{theme["empty"]}" opacity="0.75"/>')
            minx, maxx = min(minx, px - 2), max(maxx, px + 2)
            miny, maxy = min(miny, py - 2), max(maxy, py + 2)
        else:
            ratio = (c / max_count) ** 0.65
            trunk_h = min_trunk_h + (max_trunk_h - min_trunk_h) * ratio
            canopy_r = min_canopy_r + (max_canopy_r - min_canopy_r) * ratio
            trunk_w = max(1.2, 1.0 + ratio * 1.0)
            branch_len = trunk_h * 0.28

            # Trunk top
            tx, ty = px, py - trunk_h

            # Thin trunk line
            parts.append(f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{tx:.1f}" y2="{ty:.1f}" stroke="{trunk_color}" stroke-width="{trunk_w:.1f}" stroke-linecap="round"/>')

            # 2-3 short branch lines
            b1_y = py - trunk_h * 0.45
            parts.append(f'<line x1="{px:.1f}" y1="{b1_y:.1f}" x2="{px - branch_len*0.8:.1f}" y2="{b1_y - branch_len*0.5:.1f}" stroke="{trunk_color}" stroke-width="{trunk_w*0.7:.1f}" stroke-linecap="round"/>')
            b2_y = py - trunk_h * 0.65
            parts.append(f'<line x1="{px:.1f}" y1="{b2_y:.1f}" x2="{px + branch_len*0.7:.1f}" y2="{b2_y - branch_len*0.4:.1f}" stroke="{trunk_color}" stroke-width="{trunk_w*0.7:.1f}" stroke-linecap="round"/>')
            if ratio >= 0.4:
                b3_y = py - trunk_h * 0.80
                parts.append(f'<line x1="{px:.1f}" y1="{b3_y:.1f}" x2="{px - branch_len*0.6:.1f}" y2="{b3_y - branch_len*0.3:.1f}" stroke="{trunk_color}" stroke-width="{trunk_w*0.6:.1f}" stroke-linecap="round"/>')

            # Fluffy Sakura Canopy: 8-9 outer ring circles + 4 inner core circles
            cx, cy = tx, ty - canopy_r * 0.2
            R = canopy_r
            base_tier = min(3, int(ratio * 3.99))

            # Outer ring circles (8-9 circles arranged in a rough ring around offset center)
            n_outer = 8
            for k in range(n_outer):
                angle = (2 * math.pi * k / n_outer) + math.sin(k * 3.7 + i) * 0.35
                dist = R * (0.55 + math.sin(k * 2.5 + i * 1.7) * 0.20)
                ox = cx + dist * math.cos(angle)
                oy = cy + dist * math.sin(angle)
                orad = R * (0.36 + math.cos(k * 1.9 + i) * 0.10)

                # Shade selection across 4-step ramp
                shade_idx = base_tier if oy >= cy else max(0, base_tier - 1)
                if k % 3 == 0:
                    shade_idx = min(3, base_tier + 1)
                color = ramp[shade_idx]
                parts.append(f'<circle cx="{ox:.1f}" cy="{oy:.1f}" r="{orad:.1f}" fill="{color}" opacity="0.90"/>')

            # Inner core cluster (4 smaller circles for volume and depth)
            core_offsets = [
                (-R * 0.15, -R * 0.10, R * 0.38, ramp[base_tier]),
                (R * 0.12, -R * 0.22, R * 0.35, ramp[max(0, base_tier - 1)]),
                (-R * 0.08, R * 0.12, R * 0.32, ramp[min(3, base_tier + 1)]),
                (R * 0.18, R * 0.05, R * 0.30, ramp[base_tier]),
            ]
            for dx_c, dy_c, r_c, color_c in core_offsets:
                parts.append(f'<circle cx="{cx + dx_c:.1f}" cy="{cy + dy_c:.1f}" r="{r_c:.1f}" fill="{color_c}" opacity="0.95"/>')

            # Floating petals for top ~20% high-contribution days
            if ratio >= 0.75:
                p_color = ramp[0]  # Light blush pink
                p1_x, p1_y = cx + R * 0.7, cy - R * 1.1
                p2_x, p2_y = cx - R * 0.8, cy - R * 0.9
                p3_x, p3_y = cx + R * 1.1, cy - R * 0.4
                parts.append(f'<circle cx="{p1_x:.1f}" cy="{p1_y:.1f}" r="1.1" fill="{p_color}" opacity="0.85"/>')
                parts.append(f'<circle cx="{p2_x:.1f}" cy="{p2_y:.1f}" r="0.9" fill="{p_color}" opacity="0.75"/>')
                parts.append(f'<circle cx="{p3_x:.1f}" cy="{p3_y:.1f}" r="1.0" fill="{p_color}" opacity="0.65"/>')

            # Bounds tracking
            minx, maxx = min(minx, cx - R * 1.3), max(maxx, cx + R * 1.3)
            miny, maxy = min(miny, cy - R * 1.3), max(maxy, py)

    frag = f'<g transform="translate({-minx:.1f},{-miny:.1f})">' + ''.join(parts) + '</g>'
    return frag, maxx - minx, maxy - miny


def compute_stats(days):
    """Total, best day, and longest/current streaks from a chronological list of days.

    The current streak treats today specially: if today has 0 contributions the day
    isn't over yet, so it's skipped rather than treated as a break -- the streak is
    evaluated as of yesterday instead. Without that, the streak reads as broken for
    the entire day even though there's still time left to contribute.
    """
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


def stat_cell(x, y, value, label, sub, theme):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="24" font-weight="700" fill="{theme["accent"]}">{escape(value)}</text>'
            f'<text x="{x:.1f}" y="{y+18:.1f}" font-size="12" font-weight="600" fill="{theme["fg"]}">{escape(label)}</text>'
            f'<text x="{x:.1f}" y="{y+32:.1f}" font-size="10" fill="{theme["label"]}">{escape(sub)}</text>')


def stat_card(x, y, title, cells, theme):
    """A bordered rounded-rect card, sized snugly around its content: a title above,
    evenly spaced stat cells inside. Returns (markup, width, height)."""
    w = 2 * BOX_PAD + (len(cells) - 1) * COL_GAP + COL_CONTENT_W
    h = BOX_ROW_H
    parts = [f'<text x="{x:.1f}" y="{y-9:.1f}" font-size="13" font-weight="700" fill="{theme["fg"]}">{escape(title)}</text>',
             f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="8" fill="none" stroke="{theme["border"]}"/>']
    for i, (value, label, sub) in enumerate(cells):
        cx = x + BOX_PAD + COL_GAP * i
        parts.append(stat_cell(cx, y + 39, value, label, sub, theme))
    return ''.join(parts), w, h


def render_widget(theme, card_width, weeks):
    """Returns the SVG markup for the whole widget, in local coordinates starting at (0,0)."""
    avail_w = panel_width(card_width)
    panel_h = panel_height(card_width)
    tile_w, tile_h = tile_size(card_width)
    chart_frag, cw, ch = render_chart(weeks, theme, tile_w, tile_h)

    days = [d for w in weeks for d in w['contributionDays']]
    stats = compute_stats(days)
    this_week = weeks[-1]['contributionDays']
    this_week_total = sum(d['contributionCount'] for d in this_week)
    avg_per_day = stats['total'] / len(days)

    parts = [f'<g font-family="{FONT}">']

    chart_y = INSET + max(0, ((panel_h - 2 * INSET) - ch) / 2)
    parts.append(f'<g transform="translate({INSET},{chart_y:.1f})">{chart_frag}</g>')

    contrib_y = INSET + 22
    contrib_markup, contrib_w, contrib_h = stat_card(0, contrib_y, 'Contributions', [
        (f'{stats["total"]:,}', 'Total', f'{month_day(stats["range_start"])} → {month_day(stats["range_end"])}'),
        (f'{this_week_total:,}', 'This week', f'{month_day(this_week[0]["date"])} → {month_day(this_week[-1]["date"])}'),
        (f'{stats["best_count"]:,}', 'Best day', month_day(stats['best_date'])),
    ], theme)
    contrib_x = avail_w - INSET - contrib_w
    parts.append(f'<g transform="translate({contrib_x:.1f},0)">{contrib_markup}</g>')
    avg_y = contrib_y + contrib_h + 15
    parts.append(f'<text x="{avail_w-INSET:.1f}" y="{avg_y:.1f}" font-size="11" fill="{theme["fg"]}" text-anchor="end">'
                 f'Average: {avg_per_day:.2f} / day</text>')

    streak_markup, streak_w, streak_h = stat_card(INSET, 0, 'Streaks', [
        (f'{stats["longest_len"]} days', 'Longest',
         f'{month_day(stats["longest_start"])} → {month_day(stats["longest_end"])}' if stats['longest_start'] else '—'),
        (f'{stats["current_len"]} days', 'Current',
         f'{month_day(stats["current_start"])} → {month_day(stats["current_end"])}' if stats['current_start'] else '—'),
    ], theme)
    streak_y = panel_h - INSET - streak_h
    parts.append(f'<g transform="translate(0,{streak_y:.1f})">{streak_markup}</g>')

    parts.append('</g>')
    return ''.join(parts)
