"""Generate self-contained GitHub profile SVGs. Python 3.11+, Pillow for photos."""
from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta, timezone
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / 'profile.json').read_text(encoding='utf-8'))
USER = CONFIG['username']
PALETTE = ['#161b22', '#0e4429', '#006d32', '#26a641', '#39d353']


def download(url):
    request = urllib.request.Request(url, headers={'User-Agent': f'{USER}-profile-art', 'Accept': 'text/html'})
    with urllib.request.urlopen(request, timeout=45) as response:
        return response.read()


class CalendarParser(HTMLParser):
    """Read GitHub cells and their separate accessible tooltip counts."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.cells = {}
        self.tips = {}
        self.tip_id = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        day = attrs.get('data-date')
        if day and 'data-level' in attrs:
            self.cells[day] = {
                'date': day, 'level': int(attrs['data-level']),
                'count': int(attrs['data-count']) if 'data-count' in attrs else None,
                'id': attrs.get('id', ''),
            }
        if tag == 'tool-tip' and attrs.get('for'):
            self.tip_id = attrs['for']
            self.tips[self.tip_id] = ''

    def handle_data(self, value):
        if self.tip_id:
            self.tips[self.tip_id] += value

    def handle_endtag(self, tag):
        if tag == 'tool-tip':
            self.tip_id = None

    def days(self):
        result = []
        for day in sorted(self.cells.values(), key=lambda item: item['date']):
            if day['count'] is None:
                tip = self.tips.get(day['id'], '').strip()
                match = re.match(r'([\d,]+) contributions?\b', tip, re.I)
                if match:
                    day['count'] = int(match[1].replace(',', ''))
                elif re.match(r'No contributions?\b', tip, re.I):
                    day['count'] = 0
                else:
                    raise ValueError(f'Missing contribution count for {day["date"]}; refusing to invent data')
            result.append({key: day[key] for key in ('date', 'level', 'count')})
        if len(result) < 350:
            raise ValueError(f'Expected a full contribution calendar, found {len(result)} days')
        return result


def fetch_calendar():
    parser = CalendarParser()
    parser.feed(download(f'https://github.com/users/{USER}/contributions').decode('utf-8'))
    payload = {'username': USER, 'fetched_at': datetime.now(timezone.utc).isoformat(), 'days': parser.days()}
    target = ROOT / 'data/contributions.json'
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
    return payload


def svg_open(width, height, title, desc):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>',
            '<style>text{font-family:Consolas,"Liberation Mono",monospace} .muted{fill:#8b949e} @keyframes enter{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:translateY(0)}} .reveal{animation:enter .3s both} @media(prefers-reduced-motion:reduce){.reveal{animation:none}}</style>',
            f'<rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="14" fill="#0d1117" stroke="#30363d"/>']


def text(x, y, value, fill='#c9d1d9', size=12, extra=''):
    return f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" {extra}>{escape(str(value))}</text>'


def chrome(parts, label, width):
    for i, color in enumerate(['#ff5f57', '#febc2e', '#28c840']):
        parts.append(f'<circle cx="{21+i*17}" cy="22" r="4" fill="{color}"/>')
    parts.append(text(82, 26, label, '#8b949e', 11))
    parts.append(f'<path d="M1 43H{width-1}" stroke="#21262d"/>')


def save(name, parts):
    (ROOT / name).write_text('\n'.join(parts + ['</svg>']) + '\n', encoding='utf-8')


def render_card():
    parts = svg_open(490, 365, f'{USER} | developer terminal', 'Full-stack developer working with Flutter, PHP and Python.')
    chrome(parts, 'profile.json', 490)
    parts += [text(26, 81, f'{USER}@github', CONFIG['accent'], 19), text(26, 105, '─' * 34, '#30363d')]
    rows = [('Name', CONFIG['name']), ('Role', CONFIG['role']), ('Stack', ' · '.join(CONFIG['stack'])),
            ('Profile', f'github.com/{USER}'), ('Graph', 'Real contributions · daily sync'), ('Theme', 'Monochrome / terminal green')]
    for index, (key, value) in enumerate(rows):
        y = 135 + index * 28
        parts.append(f'<g class="reveal" style="animation-delay:{index*.14+.15:.2f}s">')
        parts += [text(26, y, key, CONFIG['accent']), text(100, y, value, size=11), '</g>']
    for index, color in enumerate(['#161b22', '#30363d', '#8b949e', '#c9d1d9', '#0e4429', '#006d32', '#26a641', '#39d353']):
        parts.append(f'<rect x="{26+index*21}" y="311" width="21" height="14" fill="{color}"/>')
    save('info-card.svg', parts)


def portrait_rows():
    source = ROOT / CONFIG['portrait']
    if source.exists():
        from PIL import Image, ImageOps, ImageEnhance
        with Image.open(source) as original:
            rgba = original.convert('RGBA')
            white = Image.new('RGBA', rgba.size, 'white')
            white.alpha_composite(rgba)
            gray = ImageOps.grayscale(white.convert('RGB'))
            gray = ImageOps.autocontrast(gray, cutoff=1)
            gray = ImageEnhance.Contrast(gray).enhance(1.4)
            gray = ImageOps.fit(gray, (76, 42))
            ramp = '@%#*+=-:. '
            return [''.join(ramp[gray.getpixel((x,y))*len(ramp)//256] for x in range(76)) for y in range(42)]
    # Honest first-run fallback; replaced automatically when the workflow fetches the avatar.
    letters = ['    ###     ##   ## ', '   ## ##    ##   ## ', '  ##   ##   ##   ## ', '  #######   ####### ', '  ##   ##   ##   ## ', '  ##   ##   ##   ## ', '  ##   ##   ##   ## ']
    result = [''] * 8
    for line in letters:
        expanded = ''.join(ch*3 for ch in line)
        result.extend([expanded.center(76)] * 3)
    return result + [''] * (42-len(result))


def render_portrait():
    parts = svg_open(370, 365, f'{USER} | ASCII portrait', 'Monochrome ASCII art reveals row by row. A monogram is used until an avatar is available.')
    chrome(parts, 'avatar --ascii', 370)
    rows = portrait_rows()
    parts.append('<defs>')
    for index in range(len(rows)):
        delay = index * .045
        timing = f'values="0;0;338" keyTimes="0;{delay/(delay+.16):.6f};1"' if delay else 'from="0" to="338"'
        parts.append(f'<clipPath id="row{index}"><rect x="16" y="{61+index*6.3}" width="338" height="8"><animate attributeName="width" {timing} dur="{delay+.16:.3f}s" begin="0s" fill="freeze"/></rect></clipPath>')
    parts.append('</defs>')
    for index, row in enumerate(rows):
        parts.append(text(16, 67+index*6.3, row, '#c9d1d9', 7.3, f'xml:space="preserve" clip-path="url(#row{index})"'))
    parts.append(text(18, 346, f'~/users/{USER}', '#8b949e', 10))
    save('avi-ascii.svg', parts)


def statistics(days):
    ordered = sorted(days, key=lambda item: item['date'])
    longest = run = 0
    for day in ordered:
        run = run + 1 if day['count'] else 0
        longest = max(longest, run)
    # An unfinished zero-contribution day does not break yesterday's streak.
    streak_days = ordered[:-1] if ordered and ordered[-1]['count'] == 0 else ordered
    current = 0
    for day in reversed(streak_days):
        if not day['count']:
            break
        current += 1
    return sum(day['count'] for day in ordered), current, longest


def render_calendar(payload=None):
    parts = svg_open(860, 275, f'{USER} | contribution calendar', 'Daily GitHub contributions, updated by GitHub Actions. Cells appear in a diagonal wave.')
    chrome(parts, f'{USER} / contributions', 860)
    if payload is None:
        parts += [text(30, 96, '$ waiting for first GitHub sync', CONFIG['accent'], 16),
                  text(30, 132, 'Run the Update profile art workflow to load your real activity.', '#8b949e'),
                  text(30, 162, 'No sample counts. Your calendar appears after a successful fetch.', '#8b949e')]
        save('contrib-heatmap.svg', parts)
        return
    if payload['username'].lower() != USER.lower():
        raise ValueError('Contribution data belongs to another account')
    days = payload['days']
    end = max(date.fromisoformat(item['date']) for item in days)
    end = min(end, datetime.now(timezone.utc).date())
    # First day of this 53-column calendar is Sunday.
    start = end - timedelta(days=(end.weekday()+1)%7 + 52*7)
    last_month = None
    for week in range(53):
        day = start + timedelta(days=week*7)
        if day.month != last_month:
            parts.append(text(49+week*14.6, 72, day.strftime('%b'), '#8b949e', 10))
            last_month = day.month
    for row, label in [(1, 'Mon'), (3, 'Wed'), (5, 'Fri')]:
        parts.append(text(14, 92+row*15, label, '#8b949e', 9))
    visible = []
    for item in days:
        day = date.fromisoformat(item['date'])
        if not start <= day <= end:
            continue
        visible.append(item)
        delta = (day-start).days
        col, row = divmod(delta, 7)
        level = max(0, min(4, item['level']))
        parts.append(f'<rect class="reveal" x="{49+col*14.6:.1f}" y="{82+row*15}" width="11.6" height="11.6" rx="2.5" fill="{PALETTE[level]}" style="animation-delay:{(col+row)*.023:.3f}s"><title>{item["date"]}: {item["count"]} contributions</title></rect>')
    total, current, longest = statistics(visible)
    parts += [text(26, 220, f'{total:,} contributions in displayed period', '#c9d1d9', 13),
              text(26, 248, f'Current streak {current}d  ·  Longest streak {longest}d', '#8b949e', 11),
              text(652, 220, 'Less', '#8b949e', 10)]
    for i, color in enumerate(PALETTE):
        parts.append(f'<rect x="{685+i*17}" y="210" width="12" height="12" rx="2" fill="{color}"/>')
    parts += [text(778, 220, 'More', '#8b949e', 10), text(652, 248, 'Updated '+payload['fetched_at'][:10], '#8b949e', 10)]
    save('contrib-heatmap.svg', parts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true', help='Fetch live public contribution data')
    parser.add_argument('--avatar', action='store_true', help='Download your public GitHub avatar')
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?', USER):
        raise ValueError('Invalid GitHub username')
    if args.avatar:
        target = ROOT / CONFIG['portrait']
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(download(f'https://github.com/{USER}.png?size=512'))
    cache = ROOT / 'data/contributions.json'
    payload = fetch_calendar() if args.fetch else (json.loads(cache.read_text(encoding='utf-8')) if cache.exists() else None)
    render_portrait()
    render_card()
    render_calendar(payload)
    print(f'Generated all three SVGs for {USER}')


if __name__ == '__main__':
    main()
