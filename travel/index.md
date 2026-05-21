---
layout: default
title: Путешествия
permalink: /travel/
masthead_left:
  - "Раздел II"
  - "Путешествия"
  - "Архив 2016–2019"
masthead_right:
  - "Полный архив"
  - "zavalny.com"
---

{% assign travel_posts = site.posts | where_exp: "p", "p.categories contains 'travel'" | sort: "date" | reverse %}
{% assign travel_posts_asc = site.posts | where_exp: "p", "p.categories contains 'travel'" | sort: "date" %}
{% assign first_year = travel_posts_asc.first.date | date: "%Y" | plus: 0 %}
{% assign last_year = travel_posts.first.date | date: "%Y" | plus: 0 %}

<section class="page-hero">
  <div class="h-left">
    <span class="tag reveal">Раздел II · Полный архив</span>
    <h1 class="split-line">Путе<em>шествия</em></h1>
  </div>
  <div class="h-right reveal">
    <p class="h-stand">
      Все восстановленные фотоотчёты: Европа, Азия, острова, отели и семейные приключения.
    </p>
    <div class="h-figures">
      <div class="fig"><strong>{{ travel_posts | size }}</strong><span class="tag">записей</span></div>
      <div class="fig"><strong>{{ first_year }}</strong><span class="tag">начало</span></div>
      <div class="fig"><strong>{{ last_year }}</strong><span class="tag">конец</span></div>
    </div>
  </div>
</section>

{% assign grouped = travel_posts | group_by_exp: "p", "p.date | date: '%Y'" %}
{% for group in grouped %}
  <section class="year-section reveal">
    <div class="y-mark">{{ group.name }}<small>{{ group.items | size }} записей</small></div>
    <div class="contents">
      {% for post in group.items %}
        {% assign image = post.hero_image %}
        {% assign chunks = post.content | split: '](' %}
        {% if image == nil and chunks.size > 1 %}
          {% assign image = chunks[1] | split: ')' | first %}
        {% endif %}
        <a href="{{ post.url | relative_url }}" class="entry">
          <span class="e-num">{{ forloop.index | prepend: "0" | slice: -2, 2 }}.</span>
          <span class="e-title">{{ post.title }}</span>
          <span class="e-place">Путешествия</span>
          <span class="e-year">{{ post.date | date: "%B" }}</span>
          <span class="e-thumb {% unless image %}placeholder{% endunless %}">
            {% if image %}<img src="{{ image }}" alt="" loading="lazy">{% endif %}
          </span>
        </a>
      {% endfor %}
    </div>
  </section>
{% endfor %}
