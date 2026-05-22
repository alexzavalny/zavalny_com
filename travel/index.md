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

<section class="travel-map-section reveal">
  <div class="travel-map-head">
    <div>
      <span class="tag">География архива</span>
      <h2>Карта поездок</h2>
    </div>
    <p>Точки ведут к фотоотчётам. Координаты сохранены в frontmatter каждой записи.</p>
  </div>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
  <div id="travel-map" class="travel-map" aria-label="Карта путешествий zavalny.com"></div>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script>
    (function () {
      if (!window.L) return;
      var points = [
        {% for post in travel_posts %}
          {% if post.gps %}
            {
              title: {{ post.title | jsonify }},
              label: {{ post.gps.label | default: post.title | jsonify }},
              url: {{ post.url | relative_url | jsonify }},
              lat: {{ post.gps.lat }},
              lon: {{ post.gps.lon }}
            }{% unless forloop.last %},{% endunless %}
          {% endif %}
        {% endfor %}
      ];
      var map = L.map('travel-map', { scrollWheelZoom: false, worldCopyJump: true }).setView([34, 18], 2);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '&copy; OpenStreetMap'
      }).addTo(map);
      var bounds = [];
      points.forEach(function (point) {
        var marker = L.circleMarker([point.lat, point.lon], {
          radius: 7,
          color: '#f3ede0',
          weight: 2,
          fillColor: '#c43821',
          fillOpacity: 0.95
        }).addTo(map);
        marker.bindPopup('<strong>' + point.title + '</strong><br><span>' + point.label + '</span><br><a href="' + point.url + '">Открыть фотоотчёт →</a>');
        marker.on('click', function () { window.location.href = point.url; });
        bounds.push([point.lat, point.lon]);
      });
      if (bounds.length) map.fitBounds(bounds, { padding: [22, 22] });
    }());
  </script>
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
