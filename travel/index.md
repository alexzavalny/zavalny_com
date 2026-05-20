---
layout: page
title: Путешествия
permalink: /travel/
---

# Путешествия

Восстановленные отчёты с прежнего сайта zavalny.com из Web Archive.

<ul class="post-list">
{% assign travel_posts = site.posts | where_exp: "post", "post.categories contains 'travel'" %}
{% for post in travel_posts %}
  <li><a href="{{ post.url | relative_url }}">{{ post.title }}</a> <span class="post-date">{{ post.date | date: "%Y-%m-%d" }}</span></li>
{% endfor %}
</ul>
