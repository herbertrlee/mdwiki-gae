Search
======

<form action="/search" method="POST">
    <input class="form-control" type="text" aria-label="Search" 
    name="search" {% if search_term %}value="{{ search_term }}"{% else %}placeholder="Search"{% endif %}
    >
</form>

{% if search_term %}
Search Results for "{{ search_term }}":
-----
{% if results %}
{% for result in results %}
* [{{ result.title }}]({{  result.name }})
{% endfor %}
{% else %}
No results found.
{% endif %}
{% endif %}
