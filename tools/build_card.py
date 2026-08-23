"""Generate dark_mode.svg / light_mode.svg for Sudhanshub27's profile README.

Run once to lay out the card. today.py then patches only the id-tagged values daily.
"""
import datetime
from xml.sax.saxutils import escape
from dateutil import relativedelta

import build_contrib

IMG_X, IMG_Y = 25, 28
INFO_FS = 12
CHAR_W = 7.2                          # ConsolasFallback character advance at 12px
CARD_H = 460                         # height of the boxed-sections header + grid
WIDGET_GAP = 25                      # gap between the card grid and the widget
WIDGET_BOTTOM_PAD = 20

THEMES = {
    'dark_mode.svg': dict(
        bg='#17121C', card_bg='#211A26', border='#4A3040',
        hdr='#F5E6D3', label='#C9A896', val='#E8CBB0',
        subtext='#C9A896', sep='#5A4A52', add='#C85A3D', dele='#7A2E1F'
    ),
    'light_mode.svg': dict(
        bg='#FAF5F0', card_bg='#F2E8E0', border='#D8C2D3',
        hdr='#4A3040', label='#8C6D58', val='#A85A3D',
        subtext='#8C6D58', sep='#C4B0C2', add='#C85A3D', dele='#7A2E1F'
    ),
}


def compute_card_width():
    return 870


H = CARD_H + WIDGET_GAP + build_contrib.panel_height(compute_card_width()) + WIDGET_BOTTOM_PAD


def uptime(birth=datetime.date(2004, 9, 27), today=None):
    today = today or datetime.date.today()
    d = relativedelta.relativedelta(today, birth)
    p = lambda n, u: f"{n} {u}{'s' if n != 1 else ''}"
    return f"{p(d.years,'year')}, {p(d.months,'month')}, {p(d.days,'day')}"


def build(theme_file):
    t = THEMES[theme_file]
    W = compute_card_width()
    out = [
        "<?xml version='1.0' encoding='UTF-8'?>",
        f'<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" '
        f'width="{W}px" height="{H}px" font-size="{INFO_FS}px">',
        '<style>',
        '@font-face {',
        "src: local('Consolas'), local('Consolas Bold');",
        "font-family: 'ConsolasFallback';",
        'font-display: swap;',
        '-webkit-size-adjust: 109%;',
        'size-adjust: 109%;',
        '}',
        'text {white-space: pre;}',
        '</style>',
        f'<rect width="{W}px" height="{H}px" fill="{t["bg"]}" rx="15"/>',
    ]

    # --- Header Row
    out.append(f'<text x="25" y="36" font-size="18" font-weight="700" fill="{t["hdr"]}">@Sudhanshub27</text>')
    out.append(f'<text x="175" y="36" font-size="13" font-weight="400" fill="{t["label"]}">• Full Stack Software Developer</text>')
    out.append(f'<text x="25" y="56" font-size="12" fill="{t["subtext"]}">VIT University, Vellore • India</text>')

    # --- 2x2 Grid of Cards
    grid_y = 75
    gap_x, gap_y = 20, 18
    card_w = int((W - 50 - gap_x) / 2)  # 400px
    card_h = 172

    cards_data = [
        ('ABOUT', 0, 0, [
            ('OS', 'Linux, Windows 11', None),
            ('Uptime', uptime(), 'age_data'),
            ('Host', 'VIT University, Vellore', None),
            ('Kernel', 'Full Stack Software Developer', None),
            ('IDE', 'VS Code, Antigravity', None),
        ]),
        ('LANGUAGES', 1, 0, [
            ('Programming', 'TypeScript, JavaScript, Python', None),
            ('Computer', 'HTML, CSS, React, Next.js, Node.js, SQL', None),
            ('Real', 'English, Hindi, Punjabi', None),
        ]),
        ('HOBBIES', 0, 1, [
            ('Software', 'Building products, AI experiments', None),
            ('Hardware', 'Gaming, Cricket', None),
        ]),
        ('CONTACT', 1, 1, [
            ('Email', 'sudhanshubatra27@gmail.com', None),
            ('LinkedIn', 'sudhanshu-batra', None),
            ('Instagram', 'batra_sudhanshu', None),
            ('Portfolio', 'sudhanshubatra.in', None),
        ]),
    ]

    for title, col, row, items in cards_data:
        cx = 25 + col * (card_w + gap_x)
        cy = grid_y + row * (card_h + gap_y)

        # Rounded card container
        out.append(
            f'<rect x="{cx}" y="{cy}" width="{card_w}" height="{card_h}" rx="8" '
            f'fill="{t["card_bg"]}" stroke="{t["border"]}" stroke-width="1.2"/>'
        )

        # Card Title Header
        out.append(
            f'<text x="{cx + 18}" y="{cy + 26}" font-size="11" font-weight="700" '
            f'letter-spacing="1.5" fill="{t["hdr"]}">{title}</text>'
        )

        # Header divider line
        out.append(
            f'<line x1="{cx + 18}" y1="{cy + 34}" x2="{cx + card_w - 18}" y2="{cy + 34}" '
            f'stroke="{t["border"]}" stroke-width="0.8" opacity="0.6"/>'
        )

        # Content rows
        row_start_y = cy + 54
        LH = 22
        for idx, (lbl, val, vid) in enumerate(items):
            ry = row_start_y + idx * LH
            id_attr = f' id="{vid}"' if vid else ''
            lbl_text = f'{lbl} — '
            lbl_len = len(lbl_text)
            val_x = cx + 18 + int(round(lbl_len * CHAR_W))

            out.append(f'<text x="{cx + 18}" y="{ry}" font-size="12" fill="{t["label"]}">{escape(lbl_text)}</text>')
            out.append(f'<text x="{val_x}" y="{ry}" font-size="12" fill="{t["val"]}"{id_attr}>{escape(val)}</text>')

    # Activity widget container -- today.py updates this group
    divider_y = CARD_H + WIDGET_GAP / 2
    out.append(f'<line x1="25" y1="{divider_y}" x2="{W-25}" y2="{divider_y}" stroke="{t["border"]}" stroke-width="1" opacity="0.4"/>')
    out.append(f'<g id="activity_widget" transform="translate({build_contrib.MARGIN},{CARD_H+WIDGET_GAP})"></g>')

    out.append('</svg>')
    return '\n'.join(out) + '\n'


if __name__ == '__main__':
    import sys
    dest = sys.argv[1] if len(sys.argv) > 1 else '.'
    for name in THEMES:
        svg = build(name)
        open(f'{dest}/{name}', 'w').write(svg)
        print(f'wrote {dest}/{name:16s} svg {len(svg)/1024:4.0f} KB')
    print('uptime today:', uptime())
