"""Render profile cards; --refresh updates public GitHub statistics."""
import argparse
from datetime import datetime, timezone
from html import escape
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
USERNAME = 'dayrentjiang'

def api(path):
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'dayrentjiang-profile'}
    if os.environ.get('GH_TOKEN'):
        headers['Authorization'] = f"Bearer {os.environ['GH_TOKEN']}"
    with urlopen(Request(f'https://api.github.com/{path}', headers=headers), timeout=30) as response:
        return json.load(response)

def refresh():
    user = api(f'users/{USERNAME}')
    repos, page = [], 1
    while True:
        batch = api(f'users/{USERNAME}/repos?per_page=100&page={page}')
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    stats = {
        'repos': user['public_repos'],
        'stars': sum(repo['stargazers_count'] for repo in repos if not repo['fork']),
        'followers': user['followers'],
        'updated': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
    }
    (ROOT / 'assets/stats.json').write_text(json.dumps(stats, indent=2) + '\n')

def render(theme, stats, portrait):
    c = {
        'dark': {'bg': '#161b22', 'text': '#c9d1d9', 'key': '#ffa657', 'value': '#a5d6ff', 'muted': '#586575', 'accent': '#7ee787', 'border': '#30363d'},
        'light': {'bg': '#f6f8fa', 'text': '#24292f', 'key': '#953800', 'value': '#0550ae', 'muted': '#8c959f', 'accent': '#1a7f37', 'border': '#d0d7de'},
    }[theme]
    svg = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="570" viewBox="0 0 1100 570" role="img" aria-labelledby="title desc">
<title id="title">Dayrent Tjiang — full stack developer</title>
<desc id="desc">ASCII portrait of Dayrent alongside his stack, contact details, and public GitHub statistics.</desc>
<style>
text {{ font-family: 'DejaVu Sans Mono', Menlo, Consolas, monospace; fill: {c['text']}; font-size: 14px; }}
.key {{ fill: {c['key']}; }} .value {{ fill: {c['value']}; }}
.muted {{ fill: {c['muted']}; }} .accent {{ fill: {c['accent']}; }}
.portrait {{ font-size: 11.4px; }}
</style>
<rect x=".5" y=".5" width="1099" height="569" rx="14" fill="{c['bg']}" stroke="{c['border']}"/>
''']
    for index, line in enumerate(portrait):
        svg.append(f'<text class="portrait" x="24" y="{30 + index * 10.4:.1f}" xml:space="preserve">{escape(line)}</text>')
    x, right, y = 462, 1068, 39
    def heading(label, first=False):
        nonlocal y
        if not first:
            y += 16
        svg.append(f'<text x="{x}" y="{y}">{escape(label)}</text>')
        line_start = x + len(label) * 8.5 + 16
        svg.append(f'<path d="M{line_start} {y-5}H{right}" stroke="{c["muted"]}" stroke-width="1"/>')
        y += 24
    def row(key, value, accent=False):
        nonlocal y
        dots = max(2, 70 - len(key) - len(value) - 4)
        cls = 'accent' if accent else 'value'
        svg.append(f'<text x="{x}" y="{y}" xml:space="preserve"><tspan class="key">{escape(key)}</tspan><tspan class="muted">: {"." * dots} </tspan><tspan class="{cls}">{escape(value)}</tspan></text>')
        y += 22
    heading('dayrent@github', first=True)
    row('Name', 'Dayrent Tjiang')
    row('Role', 'Full stack developer')
    row('Focus', 'Idea to shipped product')
    row('Approach', 'Clean code. Useful AI.')
    row('Availability', 'Open to freelance work', True)
    heading('Stack')
    row('Languages', 'TypeScript, JavaScript, Python, PHP')
    row('Frontend', 'React, Next.js, Vue, Flutter')
    row('Backend', 'Node.js, Express, FastAPI')
    row('Cloud', 'Supabase, Docker, Google Cloud')
    row('Tools', 'Tailwind CSS, Raspberry Pi')
    heading('Contact')
    row('Website', 'dayrentjiang.com')
    row('Email', 'dayrentjiang@gmail.com')
    row('LinkedIn', 'in/dayrent-tjiang')
    heading('GitHub Stats')
    row('Public repos', str(stats['repos']))
    row('Stars / Followers', f"{stats['stars']} / {stats['followers']}")
    svg.append(f'<text x="{right}" y="549" text-anchor="end" class="muted" style="font-size:10px">Public data · updated {escape(stats["updated"])}</text>')
    svg.append('</svg>\n')
    (ROOT / f'assets/profile-{theme}.svg').write_text('\n'.join(svg))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh', action='store_true')
    if parser.parse_args().refresh:
        refresh()
    stats = json.loads((ROOT / 'assets/stats.json').read_text())
    portrait = (ROOT / 'assets/portrait.txt').read_text().splitlines()
    for theme in ('dark', 'light'):
        render(theme, stats, portrait)
