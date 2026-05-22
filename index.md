---
layout: default
title: Главная
masthead_left:
  - "Выпуск № XII · 2026"
  - "Том первый"
  - "Рига · Латвия"
---

{% assign travel_posts = site.posts | where_exp: "p", "p.categories contains 'travel'" | sort: "date" | reverse %}
{% assign travel_posts_asc = site.posts | where_exp: "p", "p.categories contains 'travel'" | sort: "date" %}
{% assign featured = travel_posts.first %}
{% assign first_year = travel_posts_asc.first.date | date: "%Y" | plus: 0 %}
{% assign last_year = travel_posts.first.date | date: "%Y" | plus: 0 %}
{% assign years_span = last_year | minus: first_year | plus: 1 %}

<section class="cover">
  <div class="issue tag reveal">
    <span class="dash"></span>
    <span>Архив одной жизни</span>
    <span class="dash"></span>
  </div>
  <h1 class="cover-title split-line">zavalny<em>.com</em></h1>
  <p class="cover-standfirst reveal">
    Личный сайт: поездки, фильмы, шахматы, гаджеты и заметки. Путевые истории — восстановлены из старого zavalny.com.
  </p>
  <div class="cover-meta tag">
    <span class="reveal"><strong>{{ travel_posts | size }}</strong>поездок</span>
    <span class="reveal"><strong>{{ years_span }}</strong>лет</span>
    <span class="reveal"><strong>{{ first_year }}</strong>→ {{ last_year }}</span>
    <span class="reveal"><strong>Riga</strong>LV</span>
  </div>
</section>

<section class="section">
  <div class="section-head reveal">
    <div class="num">№ 01</div>
    <h2>Последняя поездка</h2>
    <div class="meta tag">рекомендуем</div>
  </div>

  {% if featured %}
    {% assign feature_image = featured.hero_image %}
    {% assign md_img_chunks = featured.content | split: '](' %}
    {% if feature_image == nil and md_img_chunks.size > 1 %}
      {% assign feature_image = md_img_chunks[1] | split: ')' | first %}
    {% endif %}
    <div class="feature">
      <div class="reveal">
        <div class="tag f-kicker">{{ featured.date | date: "%B %Y" }}</div>
        <h3 class="f-title">{{ featured.title }}</h3>
        <p class="f-stand">{{ featured.excerpt | strip_html | strip_newlines }}</p>
        <div class="f-byline tag">
          <a href="{{ featured.url | relative_url }}" class="link">Читать историю →</a>
        </div>
      </div>
      <div class="f-image reveal">
        {% if feature_image %}
          <img src="{{ feature_image }}" alt="{{ featured.title | escape }}" loading="lazy">
        {% endif %}
        <div class="f-caption">Plate 01 · {{ featured.date | date: "%Y" }}</div>
      </div>
    </div>
  {% endif %}
</section>

<section class="section">
  <div class="section-head reveal">
    <div class="num">№ 02</div>
    <h2>Свежие поездки</h2>
    <div class="meta tag">последние · 6</div>
  </div>

  <div class="travel-cards">
    {% assign latest = travel_posts | slice: 0, 6 %}
    {% for post in latest %}
      {% assign image = post.hero_image %}
      {% assign chunks = post.content | split: '](' %}
      {% if image == nil and chunks.size > 1 %}
        {% assign image = chunks[1] | split: ')' | first %}
      {% endif %}
      <a class="tcard reveal" href="{{ post.url | relative_url }}">
        <div class="tcard__img">
          {% if image %}
            <img src="{{ image }}" alt="{{ post.title | escape }}" loading="lazy">
          {% else %}
            <div class="tcard__ph tag">No photo</div>
          {% endif %}
        </div>
        <div class="tcard__body">
          <div class="tag tcard__meta">{{ post.date | date: "%B %Y" }}</div>
          <div class="tcard__title">{{ post.title }}</div>
        </div>
      </a>
    {% endfor %}
  </div>

  <div class="reveal" style="margin-top: 22px; text-align:center;">
    <a href="{{ '/travel/' | relative_url }}" class="link mono">Смотреть весь архив поездок →</a>
  </div>
</section>

<section class="section" style="padding-top: 56px;">
  <div class="section-head reveal">
    <div class="num">№ 03</div>
    <h2>Разделы</h2>
    <div class="meta tag">быстрый вход</div>
  </div>

  <div class="depts">
    <a class="dept reveal" href="{{ '/travel/' | relative_url }}">
      <div class="tag d-tag">Раздел II</div>
      <div class="d-title">Путе<em>шествия</em></div>
      <div class="d-desc">Полный архив фотоотчётов по годам.</div>
      <div class="d-more">Открыть →</div>
    </a>
    <a class="dept reveal" href="{{ '/movies/' | relative_url }}">
      <div class="tag d-tag">Раздел III</div>
      <div class="d-title">Фильмы <em>из Obsidian</em></div>
      <div class="d-desc">Личная подборка без оценок — просто список.</div>
      <div class="d-more">Открыть →</div>
    </a>
    <a class="dept reveal" href="{{ '/chess/' | relative_url }}">
      <div class="tag d-tag">Раздел IV</div>
      <div class="d-title">Шахматы <em>и рейтинг</em></div>
      <div class="d-desc">Профили, статусы и заметки про игру.</div>
      <div class="d-more">Открыть →</div>
    </a>
    <a class="dept reveal" href="{{ '/gadgets/' | relative_url }}">
      <div class="tag d-tag">Раздел V</div>
      <div class="d-title">Гаджеты <em>из Obsidian</em></div>
      <div class="d-desc">Личная полка техники — без машины, зато с фото.</div>
      <div class="d-more">Открыть →</div>
    </a>
  </div>
</section>
