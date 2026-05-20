---
layout: default
title: Архив путешествий
---

<section class="hero">
  <h1>Архив путешествий zavalny.com</h1>
  <p>Семейные поездки, города, отели и пляжи — аккуратно восстановленный фотоархив старого zavalny.com.</p>
  <a class="cta" href="{{ '/travel/' | relative_url }}">Смотреть путешествия →</a>
</section>

<h2>Последние путешествия</h2>

<div class="travel-grid">
{% assign travel_posts = site.posts | where_exp: "post", "post.categories contains 'travel'" | slice: 0, 9 %}
{% for post in travel_posts %}
  {% assign image = nil %}
  {% assign chunks = post.content | split: '<img src="' %}
  {% if chunks.size > 1 %}
    {% assign image = chunks[1] | split: '"' | first %}
  {% endif %}
  <article class="travel-card">
    <a href="{{ post.url | relative_url }}">
      {% if image %}<img class="travel-card__image" src="{{ image }}" alt="{{ post.title | escape }}" loading="lazy">{% endif %}
      <div class="travel-card__body">
        <span class="travel-card__title">{{ post.title }}</span>
        <span class="travel-card__date">{{ post.date | date: "%Y" }}</span>
      </div>
    </a>
  </article>
{% endfor %}
</div>
