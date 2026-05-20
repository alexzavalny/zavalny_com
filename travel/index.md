---
layout: default
title: Путешествия
permalink: /travel/
---

<section class="hero">
  <h1>Путешествия</h1>
  <p>Все восстановленные фотоотчёты: Европа, Азия, острова, отели и семейные приключения.</p>
</section>

<div class="travel-grid">
{% assign travel_posts = site.posts | where_exp: "post", "post.categories contains 'travel'" %}
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
