"""Generate dark_mode.svg / light_mode.svg for Sudhanshub27's profile README.

Run once to lay out the card. today.py then patches only the id-tagged values daily.

The left panel is the portrait, embedded as a base64 JPEG and blended into the card
background; the right panel is the neofetch-style info block.
"""
import datetime
from xml.sax.saxutils import escape
import base64
import io
from PIL import Image
import numpy as np
from dateutil import relativedelta

import build_contrib

SRC = 'giphy.gif'

IMG_X, IMG_Y, IMG_H = 15, 28, 474    # width is derived from the source aspect (never crops)
IMG_SCALE = 1
IMG_GAP = 22                         # gutter between portrait and info column

INFO_W, INFO_FS, LH = 64, 16, 20     # info column: chars per line, font size, line height
INFO_SLACK = 3
ADV = 0.5995                         # ConsolasFallback advance, in em
CARD_H = 530                         # height of the neofetch card itself

# Below the card sits the activity widget (isometric contribution chart + streak
# stats), rendered fresh by today.py on every run. Its layout constants live in
# build_contrib.py so both scripts size it identically -- this script only reserves
# the canvas space, today.py fills it. H is set further down, once compute_card_width
# is defined.
WIDGET_GAP = 25                      # gap between the card and the widget
WIDGET_BOTTOM_PAD = 20

THEMES = {
    'dark_mode.svg': dict(
        invert=False, bg='#0B1020', fg='#F8FAFC', handle='#3B82F6', rule='#8B5CF6', cc='#94A3B8',
        sys_k='#06B6D4', sys_v='#F59E0B',
        lang_k='#8B5CF6', lang_v='#10B981',
        hob_k='#EC4899', hob_v='#3B82F6',
        con_k='#10B981', con_v='#06B6D4',
        stat_k='#3B82F6', stat_v='#F8FAFC',
        add='#10B981', dele='#EC4899'
    ),
    'light_mode.svg': dict(
        invert=True, bg='#f6f8fa', fg='#24292f', handle='#0969da', rule='#8250df', cc='#57606a',
        sys_k='#0969da', sys_v='#bf8700',
        lang_k='#8250df', lang_v='#1a7f37',
        hob_k='#cf222e', hob_v='#0969da',
        con_k='#1a7f37', con_v='#0969da',
        stat_k='#0969da', stat_v='#24292f',
        add='#1a7f37', dele='#cf222e'
    ),
}


# ---------------------------------------------------------------- portrait panel
def panel_width():
    """Panel width that matches the source aspect exactly, so nothing is ever cropped."""
    w, h = Image.open(SRC).size
    return int(round(IMG_H * w / h))


def compute_card_width():
    iw = panel_width()
    info_x = IMG_X + iw + IMG_GAP
    return int(round(info_x + (INFO_W + INFO_SLACK) * INFO_FS * ADV)) + 15


H = CARD_H + WIDGET_GAP + build_contrib.panel_height(compute_card_width()) + WIDGET_BOTTOM_PAD


def portrait_data_uri(theme):
    """Embed the animated GIF directly as base64."""
    with open(SRC, 'rb') as f:
        raw = f.read()
    return 'data:image/gif;base64,' + base64.b64encode(raw).decode('ascii'), len(raw)


# ---------------------------------------------------------------- info rows
def uptime(birth=datetime.date(2004, 9, 27), today=None):
    today = today or datetime.date.today()
    d = relativedelta.relativedelta(today, birth)
    p = lambda n, u: f"{n} {u}{'s' if n != 1 else ''}"
    return f"{p(d.years,'year')}, {p(d.months,'month')}, {p(d.days,'day')}"


ROWS_DATA = [
    ('OS',                    'Linux, Windows 11',                   None),
    ('Uptime',                uptime(),                                     'age_data'),
    ('Host',                  'VIT University, Vellore',                    None),
    ('Kernel',                'Full Stack Software Developer',              None),
    ('IDE',                   'VS Code, Antigravity',                             None),
    (None, None, None),
    ('Languages.Programming', 'TypeScript, JavaScript, Python',  None),
    ('Languages.Computer',    'HTML, CSS, React, Next.js, Node.js, SQL',    None),
    ('Languages.Real',        'English, Hindi, Punjabi',                       None),
    (None, None, None),
    ('Hobbies.Software',      'Building products, AI experiments',          None),
    ('Hobbies.Hardware',      'Gaming, Cricket',                            None),
]
CONTACT = [
    ('Email',     'sudhanshubatra27@gmail.com'),
    ('LinkedIn',  'sudhanshu-batra'),
    ('Instagram', 'batra_sudhanshu'),
    ('Portfolio', 'sudhanshubatra.in'),
]


def kv(x, y, key, value, key_clr, val_clr, vid=None, cc_clr='#94A3B8'):
    """`. Key: ....... value`, padded so the whole line is INFO_W chars."""
    keytxt = '.'.join(f'<tspan fill="{key_clr}">{escape(p)}</tspan>' for p in key.split('.'))
    dots = max(3, INFO_W - len(f'. {key}:{value}') - 2)
    idattr = f' id="{vid}"' if vid else ''
    dotid = f' id="{vid}_dots"' if vid else ''
    return (f'<tspan x="{x}" y="{y}" fill="{cc_clr}">. </tspan>{keytxt}:'
            f'<tspan fill="{cc_clr}"{dotid}> {"." * dots} </tspan>'
            f'<tspan fill="{val_clr}"{idattr}>{escape(value)}</tspan>')


def rule(x, y, label, rule_clr, cc_clr='#94A3B8'):
    return f'<tspan x="{x}" y="{y}" fill="{rule_clr}">{escape(label)}</tspan> <tspan fill="{cc_clr}">-{"—" * (INFO_W - len(label) - 5)}-—-</tspan>'


def blank(x, y, cc_clr='#94A3B8'):
    return f'<tspan x="{x}" y="{y}" fill="{cc_clr}">. </tspan>'


def build(theme_file):
    t = THEMES[theme_file]
    uri, nbytes = portrait_data_uri(t)
    iw = panel_width()
    info_x = IMG_X + iw + IMG_GAP
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
        f'.addColor {{fill: {t["add"]};}}',
        f'.delColor {{fill: {t["dele"]};}}',
        'text, tspan {{white-space: pre;}}',
        '</style>',
        f'<rect width="{W}px" height="{H}px" fill="{t["bg"]}" rx="15"/>',
        f'<image x="{IMG_X}" y="{IMG_Y}" width="{iw}" height="{IMG_H}" href="{uri}"/>',
    ]

    out.append(f'<text x="{info_x}" y="30">')
    y = 30
    handle = '@Sudhanshub27'
    out.append(f'<tspan x="{info_x}" y="{y}" fill="{t["handle"]}">{handle}</tspan> <tspan fill="{t["cc"]}">-{"—" * (INFO_W - len(handle) - 5)}-—-</tspan>')

    # 1. System Info
    for key, val, vid in ROWS_DATA[0:5]:
        y += LH
        out.append(kv(info_x, y, key, val, t['sys_k'], t['sys_v'], vid, t['cc']))

    y += LH; out.append(blank(info_x, y, t['cc']))

    # 2. Languages
    for key, val, vid in ROWS_DATA[6:9]:
        y += LH
        out.append(kv(info_x, y, key, val, t['lang_k'], t['lang_v'], vid, t['cc']))

    y += LH; out.append(blank(info_x, y, t['cc']))

    # 3. Hobbies
    for key, val, vid in ROWS_DATA[10:12]:
        y += LH
        out.append(kv(info_x, y, key, val, t['hob_k'], t['hob_v'], vid, t['cc']))

    y += LH; out.append(blank(info_x, y, t['cc']))
    y += LH; out.append(rule(info_x, y, '- Contact', t['rule'], t['cc']))

    # 4. Contact
    for key, val in CONTACT:
        y += LH
        out.append(kv(info_x, y, key, val, t['con_k'], t['con_v'], None, t['cc']))

    y += LH; out.append(blank(info_x, y, t['cc']))
    y += LH; out.append(rule(info_x, y, '- GitHub Stats', t['rule'], t['cc']))

    # 5. GitHub Stats
    y += LH
    out.append(
        f'{blank(info_x, y, t["cc"])}<tspan fill="{t["stat_k"]}">Repos</tspan>:'
        f'<tspan fill="{t["cc"]}" id="repo_data_dots"> ......... </tspan><tspan fill="{t["stat_v"]}" id="repo_data">0</tspan>'
        f' {{<tspan fill="{t["stat_k"]}">Contributed</tspan>: <tspan fill="{t["stat_v"]}" id="contrib_data">0</tspan>}}'
        f' | <tspan fill="{t["stat_k"]}">Stars</tspan>:<tspan fill="{t["cc"]}" id="star_data_dots"> ............. </tspan>'
        f'<tspan fill="{t["stat_v"]}" id="star_data">0</tspan>')
    y += LH
    out.append(
        f'{blank(info_x, y, t["cc"])}<tspan fill="{t["stat_k"]}">Commits</tspan>:'
        f'<tspan fill="{t["cc"]}" id="commit_data_dots"> ........................ </tspan>'
        f'<tspan fill="{t["stat_v"]}" id="commit_data">0</tspan>'
        f' | <tspan fill="{t["stat_k"]}">Followers</tspan>:<tspan fill="{t["cc"]}" id="follower_data_dots"> ........... </tspan>'
        f'<tspan fill="{t["stat_v"]}" id="follower_data">0</tspan>')
    y += LH
    out.append(
        f'{blank(info_x, y, t["cc"])}<tspan fill="{t["stat_k"]}">Lines of Code on GitHub</tspan>:'
        f'<tspan fill="{t["cc"]}" id="loc_data_dots">. </tspan><tspan fill="{t["stat_v"]}" id="loc_data">0</tspan>'
        f' ( <tspan class="addColor" id="loc_add">0</tspan><tspan class="addColor">++</tspan>, '
        f'<tspan id="loc_del_dots"> </tspan><tspan class="delColor" id="loc_del">0</tspan>'
        f'<tspan class="delColor">--</tspan> )')
    out.append('</text>')

    # activity widget -- today.py replaces this group's children every run
    divider_y = CARD_H + WIDGET_GAP / 2
    out.append(f'<line x1="{IMG_X}" y1="{divider_y}" x2="{W-IMG_X}" y2="{divider_y}" stroke="{t["cc"]}" stroke-width="1" opacity="0.4"/>')
    out.append(f'<g id="activity_widget" transform="translate({build_contrib.MARGIN},{CARD_H+WIDGET_GAP})"></g>')

    out.append('</svg>')
    return '\n'.join(out) + '\n'


if __name__ == '__main__':
    import sys
    dest = sys.argv[1] if len(sys.argv) > 1 else '.'
    for name in THEMES:
        svg = build(name)
        open(f'{dest}/{name}', 'w').write(svg)
        _, nbytes = portrait_data_uri(THEMES[name])
        inv = 'RGB inverted' if THEMES[name]['invert'] else 'untouched   '
        print(f'wrote {dest}/{name:16s} {inv}  png {nbytes/1024:4.0f} KB  svg {len(svg)/1024:4.0f} KB')
    iw = panel_width()
    info_x = IMG_X + iw + IMG_GAP
    print(f'panel: {iw}x{IMG_H} (source aspect, no crop), encoded at {IMG_SCALE}x')
    print(f'info : x={info_x}, {INFO_W}(+{INFO_SLACK}) chars -> card {int(round(info_x + (INFO_W+INFO_SLACK)*INFO_FS*ADV))+15}x{H}')
    print('uptime today:', uptime())
