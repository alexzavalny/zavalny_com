#!/usr/bin/env python3
import datetime as dt
import html
import json
import re
import sys
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'chess.md'
UA = 'Hermes zavalny.com chess sync (+https://zavalny.com/chess/)'
MONTHS = ['января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря']

def fetch(url):
    req = Request(url, headers={'User-Agent': UA, 'Accept': 'application/json,text/html;q=0.9,*/*;q=0.8'})
    with urlopen(req, timeout=30) as r:
        return r.read().decode('utf-8', errors='replace')

def jfetch(url):
    return json.loads(fetch(url))

def fmt(n):
    if n is None: return '—'
    if isinstance(n, str): return n
    return f'{n:,}'.replace(',', ' ')

def pct(part,total):
    return '—' if not total else f'{part/total*100:.1f} %'

def fide_value(html_text, cls):
    m = re.search(rf'class="[^"]*{re.escape(cls)}[^"]*"[\s\S]*?<p[^>]*>(.*?)</p>', html_text, re.I)
    if not m: return '—'
    val = re.sub(r'<[^>]+>', '', m.group(1)).strip()
    if val.lower() == 'not rated': return '— не рейтингован'
    return int(val) if val.isdigit() else val

def chess_stat(stats, key):
    d = stats.get(key, {})
    rec = d.get('record', {})
    w,l,dr = rec.get('win',0), rec.get('loss',0), rec.get('draw',0)
    total = w+l+dr
    return {
        'rating': d.get('last',{}).get('rating'),
        'best': d.get('best',{}).get('rating'),
        'w': w, 'l': l, 'd': dr, 'total': total,
    }

def main():
    fide_html = fetch('https://ratings.fide.com/profile/11654651')
    lichess = jfetch('https://lichess.org/api/user/AlexIsNot')
    cc_profile = jfetch('https://api.chess.com/pub/player/SonicSpeedMate')
    cc_stats = jfetch('https://api.chess.com/pub/player/SonicSpeedMate/stats')

    fide = {
        'Standard': fide_value(fide_html, 'profile-standart'),
        'Rapid': fide_value(fide_html, 'profile-rapid'),
        'Blitz': fide_value(fide_html, 'profile-blitz'),
    }
    lp = lichess['perfs']
    lc = lichess['count']
    l_total, l_w, l_d, l_l, l_rated = lc.get('all',0), lc.get('win',0), lc.get('draw',0), lc.get('loss',0), lc.get('rated',0)
    cc = {name: chess_stat(cc_stats, key) for name,key in [('Rapid','chess_rapid'),('Blitz','chess_blitz'),('Bullet','chess_bullet'),('Daily','chess_daily')]}
    cc_total = sum(x['total'] for x in cc.values())
    cc_w, cc_d, cc_l = sum(x['w'] for x in cc.values()), sum(x['d'] for x in cc.values()), sum(x['l'] for x in cc.values())
    puzzle = lp.get('puzzle',{})
    best_current = max([lp.get(k,{}).get('rating',0) for k in ['rapid','blitz','bullet','classical']] + [cc[k]['rating'] or 0 for k in cc])
    best_any = max([puzzle.get('rating',0)] + [v for v in fide.values() if isinstance(v,int)] + [lp.get(k,{}).get('rating',0) for k in ['rapid','blitz','bullet','classical']] + [cc[k]['rating'] or 0 for k in cc])
    date = dt.datetime.now().strftime(f'%-d {MONTHS[dt.datetime.now().month-1]} %Y')
    mast_date = 'Обновлено ' + date
    storm = lichess.get('storm',{}).get('score') or lichess.get('perfs',{}).get('storm',{}).get('score')
    racer = lichess.get('racer',{}).get('score') or lichess.get('perfs',{}).get('racer',{}).get('score')
    streak = lichess.get('streak',{}).get('score') or lichess.get('perfs',{}).get('streak',{}).get('score')
    tactics = cc_stats.get('tactics',{})
    rush = cc_stats.get('puzzle_rush',{})
    rush_best = rush.get('best',{})
    rush_score = rush_best.get('score')
    rush_total = rush_best.get('total') or rush_best.get('total_attempts')
    rush_text = f'{rush_score} / {rush_total}' if rush_score is not None and rush_total is not None else fmt(rush_score)

    rows = []
    for k in ['Standard','Rapid','Blitz']:
        rows.append(f'<tr><td>FIDE</td><td>{k}</td><td>{fmt(fide[k])}</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>')
    for k,label in [('rapid','Rapid'),('blitz','Blitz'),('bullet','Bullet'),('classical','Classical'),('puzzle','Puzzle')]:
        rating = lp.get(k,{}).get('rating')
        games = lp.get(k,{}).get('games')
        rtxt = f'<span style="color:var(--red);font-weight:600;">{fmt(rating)}</span>' if k=='puzzle' else fmt(rating)
        rows.append(f'<tr><td>Lichess</td><td>{label}</td><td>{rtxt}</td><td>—</td><td>{fmt(games)}</td><td>—</td><td>—</td></tr>')
    for k in ['Rapid','Blitz','Bullet','Daily']:
        x=cc[k]
        rows.append(f'<tr><td>Chess.com</td><td>{k}</td><td>{fmt(x["rating"])}</td><td>{fmt(x["best"])}</td><td>{fmt(x["total"])}</td><td>{fmt(x["w"])} — {fmt(x["d"])} — {fmt(x["l"])}</td><td>{pct(x["w"],x["total"])}</td></tr>')
    content = f'''---
layout: page
title: Шахматы
permalink: /chess/
masthead_left:
  - "Раздел IV"
  - "Шахматы"
  - "{mast_date}"
masthead_right:
  - "FIDE 11654651"
  - "Lichess @AlexIsNot"
  - "Chess.com SonicSpeedMate"
---

<section class="page-hero">
  <div class="h-left">
    <span class="tag reveal">Раздел IV · Хобби</span>
    <h1 class="split-line">Шах<em>маты</em></h1>
  </div>
  <div class="h-right reveal">
    <p class="h-stand">Три аккаунта, два цвета фигур, один игрок. FIDE, Lichess и Chess.com — рейтинги, статистика и баланс партий за всё время.</p>
    <div class="h-figures">
      <div class="fig"><strong>{fmt(puzzle.get('rating'))}</strong><span class="tag">Lichess puzzle</span></div>
      <div class="fig"><strong>{fmt(l_total + cc_total)}</strong><span class="tag">партии</span></div>
      <div class="fig"><strong>{pct(l_w + cc_w, l_total + cc_total)}</strong><span class="tag">победы</span></div>
    </div>
  </div>
</section>

<section class="chess-stat-row reveal" aria-label="Коротко">
  <div class="cs"><span class="label">Лучший рейтинг</span><span class="v">{fmt(best_any)}</span><span class="sub">головоломки / рейтинги</span></div>
  <div class="cs"><span class="label">Лучший в игре</span><span class="v">{fmt(best_current)}</span><span class="sub">актуальный рейтинг</span></div>
  <div class="cs"><span class="label">Партий на Lichess</span><span class="v">{fmt(l_total)}</span><span class="sub">{fmt(l_w)}‑{fmt(l_d)}‑{fmt(l_l)}</span></div>
  <div class="cs"><span class="label">Партий на Chess.com</span><span class="v">{fmt(cc_total)}</span><span class="sub">{fmt(cc_w)}‑{fmt(cc_d)}‑{fmt(cc_l)}</span></div>
</section>

<section class="section reveal" style="padding-top: 40px; padding-bottom: 0;">
  <div class="section-head"><div class="num">№ 01</div><h2>Рейтинги по платформам</h2><div class="meta tag">{date}</div></div>
  <div class="rating-grid">
    <div class="rcard"><div class="head"><h3>FIDE</h3><a href="https://ratings.fide.com/profile/11654651" class="link" target="_blank" rel="noopener">ratings.fide.com</a></div><div class="rows"><div class="rr"><span class="k">Standard</span><span class="vv muted">{fmt(fide['Standard'])}</span></div><div class="rr"><span class="k">Rapid</span><span class="vv">{fmt(fide['Rapid'])}</span></div><div class="rr"><span class="k">Blitz</span><span class="vv">{fmt(fide['Blitz'])}</span></div></div></div>
    <div class="rcard"><div class="head"><h3>Lichess</h3><a href="https://lichess.org/@/AlexIsNot" class="link" target="_blank" rel="noopener">@AlexIsNot</a></div><div class="rows"><div class="rr"><span class="k">Rapid</span><span class="vv">{fmt(lp['rapid']['rating'])}</span></div><div class="rr"><span class="k">Blitz</span><span class="vv">{fmt(lp['blitz']['rating'])}</span></div><div class="rr"><span class="k">Bullet</span><span class="vv">{fmt(lp['bullet']['rating'])}</span></div><div class="rr"><span class="k">Puzzle</span><span class="vv" style="color:var(--red);">{fmt(puzzle.get('rating'))}</span></div></div></div>
    <div class="rcard"><div class="head"><h3>Chess.com</h3><a href="https://www.chess.com/member/SonicSpeedMate" class="link" target="_blank" rel="noopener">SonicSpeedMate</a></div><div class="rows"><div class="rr"><span class="k">Rapid</span><span class="vv">{fmt(cc['Rapid']['rating'])}</span></div><div class="rr"><span class="k">Blitz</span><span class="vv">{fmt(cc['Blitz']['rating'])}</span></div><div class="rr"><span class="k">Bullet</span><span class="vv">{fmt(cc['Bullet']['rating'])}</span></div><div class="rr"><span class="k">Daily</span><span class="vv">{fmt(cc['Daily']['rating'])}</span></div></div></div>
  </div>
</section>

<section class="section reveal" style="padding-bottom: 0;">
  <div class="section-head"><div class="num">№ 02</div><h2>Статистика по контролям</h2><div class="meta tag">таблица</div></div>
  <div class="ctable-wrap"><table class="ctable"><thead><tr><th>Платформа</th><th>Контроль</th><th>Рейтинг</th><th>Лучший</th><th>Партии</th><th>W‑D‑L</th><th>Победы</th></tr></thead><tbody>
        {chr(10).join(rows)}
      </tbody></table></div>
</section>

<section class="section reveal">
  <div class="section-head"><div class="num">№ 03</div><h2>Сводка аккаунтов</h2><div class="meta tag">Lichess · Chess.com</div></div>
  <div class="rating-grid" style="grid-template-columns: 1fr 1fr;">
    <div class="rcard"><div class="head"><h3>Lichess</h3><a href="https://lichess.org/@/AlexIsNot" class="link" target="_blank" rel="noopener">@AlexIsNot</a></div><div class="rows"><div class="rr"><span class="k">Всего партий</span><span class="vv">{fmt(l_total)}</span></div><div class="rr"><span class="k">Rated</span><span class="vv">{fmt(l_rated)}</span></div><div class="rr"><span class="k">Баланс W‑D‑L</span><span class="vv" style="font-size:1.2rem;">{fmt(l_w)} · {fmt(l_d)} · {fmt(l_l)}</span></div><div class="rr"><span class="k">Победы</span><span class="vv">{pct(l_w,l_total)}</span></div><div class="rr"><span class="k">Score rate</span><span class="vv">{pct(l_w + 0.5*l_d,l_total)}</span></div><div class="rr"><span class="k">Puzzle Storm</span><span class="vv">{fmt(storm)}</span></div><div class="rr"><span class="k">Puzzle Racer</span><span class="vv">{fmt(racer)}</span></div><div class="rr"><span class="k">Puzzle Streak</span><span class="vv">{fmt(streak)}</span></div></div></div>
    <div class="rcard"><div class="head"><h3>Chess.com</h3><a href="https://www.chess.com/member/SonicSpeedMate" class="link" target="_blank" rel="noopener">SonicSpeedMate</a></div><div class="rows"><div class="rr"><span class="k">Всего партий</span><span class="vv">{fmt(cc_total)}</span></div><div class="rr"><span class="k">Баланс W‑D‑L</span><span class="vv" style="font-size:1.2rem;">{fmt(cc_w)} · {fmt(cc_d)} · {fmt(cc_l)}</span></div><div class="rr"><span class="k">Победы</span><span class="vv">{pct(cc_w,cc_total)}</span></div><div class="rr"><span class="k">Score rate</span><span class="vv">{pct(cc_w + 0.5*cc_d,cc_total)}</span></div><div class="rr"><span class="k">Tactics high</span><span class="vv">{fmt(tactics.get('highest',{}).get('rating'))}</span></div><div class="rr"><span class="k">Puzzle Rush</span><span class="vv">{rush_text}</span></div><div class="rr"><span class="k">Статус</span><span class="vv muted" style="font-size:1.05rem;">{html.escape(str(cc_profile.get('status','—')))}</span></div><div class="rr"><span class="k">Followers</span><span class="vv">{fmt(cc_profile.get('followers'))}</span></div></div></div>
  </div>
</section>

<p class="tag reveal" style="text-align:center;padding-bottom:48px;">Данные из публичных профилей · обновлено {date}</p>
'''
    OUT.write_text(content, encoding='utf-8')
    print(date)
    print('FIDE', fide)
    print('Lichess rapid/blitz/bullet/puzzle', lp['rapid']['rating'], lp['blitz']['rating'], lp['bullet']['rating'], puzzle.get('rating'))
    print('Chess.com rapid/blitz/bullet/daily', cc['Rapid']['rating'], cc['Blitz']['rating'], cc['Bullet']['rating'], cc['Daily']['rating'])

if __name__ == '__main__':
    main()
